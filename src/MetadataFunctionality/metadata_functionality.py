# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataFunctionality
                                 A QGIS plugin
 MetadataFunctionality
                              -------------------
        begin                : 2016-04-04
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Bernhard Snizek (Septima P/S)
        email                : bernhard@septima.dk
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject
from PyQt4.QtGui import QAction, QIcon, QDialog, QMenu
from qgis.core import QgsMessageLog

# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from .ui.metadata_functionality_dialog import MetadataFunctionalityDialog
from .ui.metadata_functionality_dialog_settings import MetadataFunctionalitySettingsDialog

import os.path

# Import and override postgis create table
from db_manager.db_plugins.postgis import connector
from db_manager.dlg_import_vector import DlgImportVector
from db_manager.db_plugins.plugin import DBPlugin, Schema, Table
from db_manager.db_tree import DBTree
# import inspect

# import monkey_patcher

# https://github.com/Oslandia/qgis-menu-builder/blob/master/menu_builder.py

# TODO: Check that db_manager version is as expected (We are in potential trouble when db_manager gets updated)
# ----------------------------------------------------------------
#   Monkey patch PostGisDBConnector._execute
# ----------------------------------------------------------------
# create backup of old _execute first time

def showMetadataDialogue(table=None, uri=None, schema=None):
    # Now show table metadata editor for the newly created table
    # dialog = QDialog()
    # dialog.ui = MetadataFunctionalityDialog(table=table, uri=uri)
    dialog = MetadataFunctionalityDialog(table=table, uri=uri, schema=schema)
    #MetadataFunctionalityDialog().exec_(table=table, uri=uri)
    # dialog.exec_(table=table, uri=uri)
    dialog.exec_()


if not getattr(connector.PostGisDBConnector, 'createTable_monkeypatch_original', None):
    connector.PostGisDBConnector.createTable_monkeypatch_original = connector.PostGisDBConnector.createTable
    QgsMessageLog.logMessage("Adding the createTable patch.")

def monkey_patched_createTable(self, table, field_defs, pkey):
    QgsMessageLog.logMessage("Monkey patched createTable called")
    result =  connector.PostGisDBConnector.createTable_monkeypatch_original(self, table, field_defs, pkey)
    showMetadataDialogue(table=table, uri=self.uri(), schema=table[0])

connector.PostGisDBConnector.createTable = monkey_patched_createTable

# ----------------------------------------------------------------
#   Monkey patch the import button of the DBManager
# ----------------------------------------------------------------
if not getattr(connector.PostGisDBConnector, 'accept_original', None):
    DlgImportVector.accept_original = DlgImportVector.accept

def new_accept(self):
    showMetadataDialogue(table=self.cboTable.currentText(),
                         uri=self.db.uri(),
                         schema=self.cboSchema.currentText())
    result = DlgImportVector.accept_original(self)
    return result

DlgImportVector.accept = new_accept

# ----------------------------------------------------------------
#   Monkey patch PostGisDBConnector.createTable
# ----------------------------------------------------------------
# create backup of old _execute first time
if not getattr(connector.PostGisDBConnector, '_execute_monkeypatch_original', None):
    connector.PostGisDBConnector._execute_monkeypatch_original = connector.PostGisDBConnector._execute

def monkey_patched_execute(self, cursor, sql):
    return connector.PostGisDBConnector._execute_monkeypatch_original(self, cursor, sql)

connector.PostGisDBConnector._execute = monkey_patched_execute


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
        menu.addAction(self.tr("Metadata..."), self.fireMetamanDlg)

    if not menu.isEmpty():
        menu.exec_(ev.globalPos())

    menu.deleteLater()

def fireMetaManDlg(self):
    item = self.currentItem()
    showMetadataDialogue(table=item.name, uri=item.uri())

# ---
# menu

DBTree.fireMetamanDlg = fireMetaManDlg
DBTree.contextMenuEvent = newContextMenuEvent


class MetadataFunctionality:
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
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MetadataFunctionality_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = MetadataFunctionalityDialog()
        self.settings_dlg = MetadataFunctionalitySettingsDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MetadataFunctionality')

        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'MetadataFunctionality')
        self.toolbar.setObjectName(u'MetadataFunctionality')

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
        return QCoreApplication.translate('MetadataFunctionality', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MetadataFunctionality/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'MetaMan Dialogue'),
            callback=self.run,
            parent=self.iface.mainWindow())

        icon_path2 = ':/plugins/MetadataFunctionality/icon.png'
        self.add_action(
            icon_path2,
            add_to_toolbar = False,
            text=self.tr(u'MetaMan Settings'),
            callback=self.settings_run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MetadataFunctionality'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def settings_run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.settings_dlg.show()
        # Run the dialog event loop
        result = self.settings_dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

# https://github.com/qgis/QGIS/blob/master/src/app/qgsbrowserdockwidget.h
# http://gis.stackexchange.com/questions/126903/in-qgis-is-there-a-keyboard-shortcut-to-open-close-the-layers-panel
# http://gis.stackexchange.com/questions/174008/how-to-set-keyboard-shortcuts-for-layers-and-browser-panels-in-qgis-2-12-1-l/174020
# def run():
#     QgsMessageLog.logMessage("XXXXXXX")
#
# from qgis.gui import QgsBrowserTreeView
#
# QObject.connect(QgsBrowserTreeView(), SIGNAL("treeExpanded()"), run)
