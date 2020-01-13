# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataDbLinker
                                 A QGIS plugin
 MetadataDbLinker
                              -------------------
        begin                : 2016-04-04
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Septima P/S
        email                : kontakt@septima.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import unicode_literals
import os.path
from qgis.core import QgsMessageLog,QgsApplication
from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    qVersion,
    QCoreApplication,
    Qt,
    QFileInfo
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QMenu,
    QMessageBox
)
from qgis.PyQt.QtGui import QIcon, QCursor
from db_manager.db_plugins.plugin import (
    DBPlugin,
    Schema,
    Table
)
from db_manager.db_plugins.postgis import connector
from db_manager.dlg_create_table import DlgCreateTable
from db_manager.dlg_import_vector import DlgImportVector
from db_manager.db_tree import DBTree

# Initialize Qt resources from file resources.py
#import resources

from .core.pluginmetadata import plugin_metadata
# Import the code for the dialog
from .ui.dialog_metadata import MetadataDialog

#from .core.myseptimasearchprovider import MySeptimaSearchProvider
from .layerlocatorfilter import LayerLocatorFilter
# Settings and config
from .config import *

def showMetadataDialogue(table=None, uri=None, schema=None, close_dialog=False):
    # Now show table metadata editor for the newly created table
    QgsApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
    dialog = MetadataDialog(
        table=table,
        uri=uri,
        schema=schema,
        close_dialog=close_dialog
    )
    dialog.exec_()
    QgsApplication.restoreOverrideCursor()


def patched_createTable(self):
    table = self.editName.text()
    self.original_createTable()

    if isinstance(self.db.connector, connector.PostGisDBConnector):
        showMetadataDialogue(
            table=table,
            uri=self.db.connector._uri,
            schema=self.item.name,
            close_dialog=True
        )


def new_accept(self):
    showMetadataDialogue(
        table=self.cboTable.currentText(),
        uri=self.db.uri(),
        schema=self.cboSchema.currentText(),
        close_dialog=True
    )
    result = DlgImportVector.accept_original(self)
    return result


def newContextMenuEvent(self, ev):
    index = self.indexAt(ev.pos())
    if not index.isValid():
        return

    if index != self.currentIndex():
        self.itemChanged(index)

    item = self.currentItem()

    menu = QMenu(self)

    if isinstance(item, (Table, Schema)):
        menu.addAction(self.tr("Rename"), self.rename)
        menu.addAction(self.tr("Delete"), self.delete)

        if isinstance(item, Table) and item.canBeAddedToCanvas():
            menu.addSeparator()
            menu.addAction(self.tr("Add to canvas"), self.addLayer)

    elif isinstance(item, DBPlugin):
        if item.database() is not None:
            menu.addAction(self.tr("Re-connect"), self.reconnect)
        menu.addAction(self.tr("Remove"), self.delete)

    elif not index.parent().isValid() and item.typeName() == "spatialite":
        menu.addAction(self.tr("New Connection..."), self.newConnection)

    if isinstance(item, (Table, DBPlugin)):
        menu.addSeparator()
        menu.addAction(self.tr("Metadata..."), self.fireMetadataDlg)

    if not menu.isEmpty():
        menu.exec_(ev.globalPos())

    menu.deleteLater()


def fireMetadataDlg(self):
    item = self.currentItem()
    showMetadataDialogue(
        table=item.name,
        uri=item.uri(),
        schema=item.uri().schema(),
        close_dialog=True
    )


class MetadataDbLinker(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        self.plugin_metadata = plugin_metadata()

        # initialize locale. Default to Danish
        self.config = QSettings()
        localePath = ""
        try:
            locale = self.config.value("locale/userLocale")[0:2]
        except:
            locale = 'da'

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QgsApplication.installTranslator(self.translator)
        
        # Locator
        self.layer_locator_filter = LayerLocatorFilter(self.iface)
        self.iface.registerLocatorFilter(self.layer_locator_filter)

        # new config method 
        self.settings = Settings()
        self.options_factory = OptionsFactory(self.settings)
        self.options_factory.setTitle("MetadataDbLinker") #TODO: Skal det hedde dette?
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # Create the dialog (after translation) and keep reference
        self.dlg = MetadataDialog(iface)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&{}'.format(self.plugin_metadata['name']))

        # Initialize the fixes to DlgCreateTable class
        if not getattr(DlgCreateTable, 'original_createTable', None):
            DlgCreateTable.original_createTable = DlgCreateTable.createTable
            QgsMessageLog.logMessage("Adding the createTable patch.")

        DlgCreateTable.createTable = patched_createTable

        if not getattr(connector.PostGisDBConnector, 'accept_original', None):
            DlgImportVector.accept_original = DlgImportVector.accept

        DlgImportVector.accept = new_accept

        # menu
        DBTree.fireMetadataDlg = fireMetadataDlg
        DBTree.contextMenuEvent = newContextMenuEvent

        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(
            'MetadataDbLinker',
            message
        )



    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.editmetadata_action = QAction(
            QIcon(os.path.join(os.path.dirname(__file__),'./resources/metadata.png')),
            self.tr(u'Enter or edit metadata'),
            self.iface.mainWindow()
        )
        self.editmetadata_action.triggered.connect(self.run)
        self.editmetadata_action.setEnabled(True)
        self.iface.addPluginToMenu(self.menu, self.editmetadata_action)
        self.iface.addToolBarIcon(self.editmetadata_action)
        self.actions.append(self.editmetadata_action)
        # Old way of putting settings

        #self.settings_action = QAction(
        #    QIcon(os.path.join(os.path.dirname(__file__),'./resources/settings.png')),
        #    self.tr(u'Settings'),
        #    self.iface.mainWindow()
        #)
        #self.settings_action.triggered.connect(self.settings_run)
        #self.settings_action.setEnabled(True)
        #self.iface.addPluginToMenu(self.menu, self.settings_action)
        #self.actions.append(self.settings_action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&{}'.format(self.plugin_metadata['name'])),
                action
            )
            self.iface.removeToolBarIcon(action)
        # Remove locator
        if self.layer_locator_filter:
            self.iface.deregisterLocatorFilter(self.layer_locator_filter)
            self.layer_locator_filter = None

        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

    def run(self):
        """Run method that performs all the real work"""

        errors = self.settings.verify_settings_set()

        if errors:
            QMessageBox.critical(
                None,
                u'Missing settings.',
                u'{}'.format(errors)
            )
            return None

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
