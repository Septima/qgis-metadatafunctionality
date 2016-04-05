# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DbManagerPlus
                                 A QGIS plugin
 Adds some functionality to DB Manager
                              -------------------
        begin                : 2016-02-09
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Asger Sigurd Skovbo Petersen, Septima
        email                : asger@septima.dk
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from db_manager_plus_dialog import DbManagerPlusDialog
import os.path
from PyQt4.QtCore import Qt

# Access to variables
from qgis.core import QgsExpressionContextUtils
#QgsExpressionContextUtils.projectScope().variableNames()

# Import and override postgis create table
from db_manager.db_plugins.postgis import connector

# TODO: Check that db_manager version is as expected (We are in potential trouble when db_manager gets updated)
# ----------------------------------------------------------------
#   Monkey patch PostGisDBConnector._execute
# ----------------------------------------------------------------
# create backup of old _execute first time
if not getattr(connector.PostGisDBConnector, 'createTable_monkeypatch_original', None):
    connector.PostGisDBConnector.createTable_monkeypatch_original = connector.PostGisDBConnector.createTable

def monkey_patched_createTable(self, table, field_defs, pkey):
    print "Monkey patched createTable called"

    result =  connector.PostGisDBConnector.createTable_monkeypatch_original(self, table, field_defs, pkey)
    # TODO: Now show table metadata editor for the newly created table

connector.PostGisDBConnector.createTable = monkey_patched_createTable

# ----------------------------------------------------------------
#   Monkey patch PostGisDBConnector.createTable
# ----------------------------------------------------------------
# create backup of old _execute first time
if not getattr(connector.PostGisDBConnector, '_execute_monkeypatch_original', None):
    connector.PostGisDBConnector._execute_monkeypatch_original = connector.PostGisDBConnector._execute

def monkey_patched_execute(self, cursor, sql):
    print "Monkey patched executor. SQL: ", sql
    return connector.PostGisDBConnector._execute_monkeypatch_original(self, cursor, sql)
connector.PostGisDBConnector._execute = monkey_patched_execute


class DbManagerPlus:
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
            'DbManagerPlus_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = None #DbManagerPlusDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Db Manager Plus')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DbManagerPlus')
        self.toolbar.setObjectName(u'DbManagerPlus')

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
        return QCoreApplication.translate('DbManagerPlus', message)


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

        icon_path = ':/plugins/DbManagerPlus/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Activate DbManagerPlus'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Db Manager Plus'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar





    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        #import db_manager
        #dbman = db_manager.classFactory(self.iface)
        #dbman.setWindowTitle('Hej hej DB Manager PLUS her!')
        #dbman.run()


        # keep opened only one instance
        if self.dlg is None:
            from db_manager.db_manager import DBManager

            self.dlg = DBManager(self.iface)
            #QObject.connect(self.dlg, SIGNAL("destroyed(QObject *)"), self.onDestroyed)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.setWindowTitle('Hej hej DB Manager PLUS her!')
        self.dlg.setWindowState(self.dlg.windowState() & ~Qt.WindowMinimized)
        self.dlg.activateWindow()

    def onDestroyed(self, obj):
        self.dlg = None
