# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataFunctionalityDialog
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

import os
import uuid
from datetime import datetime

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QSettings, QAbstractTableModel, Qt, SIGNAL

# TODO: Remove after debug phase.
from qgis.core import QgsMessageLog
from qgis.core import QgsDataSourceURI

from db_manager.db_tree import DBTree
from db_manager.db_plugins.plugin import TableField
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PGVectorTable, PGTable

# from . import MetadataFunctionalityQSettingsings
from MetadataFunctionality import MetadataFunctionalitySettings
from MetadataFunctionality.core import MetaManDBTool

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_base.ui'))

SETTINGS_FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_settings.ui'))

class MetaTableModel(QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def setData(self, d):
        self.mylist = d

class MetadataFunctionalityDialog(QtGui.QDialog, FORM_CLASS):

    field_def = []
    data_list = []

    def __init__(self, parent=None):
        """Constructor."""
        super(MetadataFunctionalityDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.settings = MetadataFunctionalitySettings()
        self.db_tool = MetaManDBTool()

        self.setupUi(self)

        # we add the DBTree component into the treeDock widget,
        self.tree = DBTree(self)
        self.treeDock.setWidget(self.tree)

        self.datoEdit.setDateTime(datetime.now())

        self.buttonBox.accepted.connect(self.doSave)

        self.connect(self.tree, SIGNAL("selectedItemChanged"), self.itemChanged)
        self.deleteRecordButton.clicked.connect(self.deleteRecord)
        self.saveRecordButton.clicked.connect(self.saveRecord)

        self.selected_item = None
        self.guids = []
        self.currentlySelectedLine = None

    def saveRecord(self):
        QgsMessageLog.logMessage("addRecord")
        if self.currentlySelectedLine is None:
            self.addRecord()
        else:
            QgsMessageLog.logMessage("UPDATE")
            self.updateRecord()

    def tableRowSelected(self, a, b):
        v = []
        idxs = a.indexes()
        for idx in idxs:
            r = idx.row()
            if r not in v:
                v.append(r)
        if 1==1:
            guid = self.guids[v[0]]

            self.currentlySelectedLine = guid

            results = self.db_tool.select({'guid': guid})

            if len(results) == 1:
                results = results[0]

                if 'name' in list(results):
                    self.navnEdit.setText(results.get('name'))

                if 'timestamp' in list(results):
                    d = results.get('timestamp')
                    da = datetime.strptime(d,'%d/%m/%Y %H.%M')
                    self.datoEdit.setDate(da)

                QgsMessageLog.logMessage(str(results))

                if 'journal_nr' in list(results):
                    self.journalnrEdit.setText(results.get('journal_nr'))

                if 'resp_center_off' in list(results):
                    self.ansvarligCenterMedarbejderEdit.setText(results.get('resp_center_off'))

                if 'proj_wor' in list(results):
                    self.projekterWorEdit.setText(results.get('proj_wor'))

    def deleteRecord(self):
        selected_rows = self.tableView.selectionModel().selectedRows()
        for row in selected_rows:
            guid = self.guids[row.row()]
            self.db_tool.delete({'guid': guid})
            self.update_grid()

    def activate_fields(self):
        self.addRecordButton.setEnabled(True)
        self.deleteRecordButton.setEnabled(True)
        self.saveRecordButton.setEnabled(True)
        self.datoEdit.setEnabled(True)
        self.navnEdit.setEnabled(True)
        self.projekterWorEdit.setEnabled(True)
        self.ansvarligCenterMedarbejderEdit.setEnabled(True)
        self.tableView.setEnabled(True)

    def deactivate_fields(self):
        self.datoEdit.setEnabled(False)
        self.deleteRecordButton.setEnabled(False)
        self.addRecordButton.setEnabled(False)
        self.saveRecordButton.setEnabled(False)
        self.navnEdit.setEnabled(False)
        self.projekterWorEdit.setEnabled(False)
        self.ansvarligCenterMedarbejderEdit.setEnabled(False)
        self.tableView.setEnabled(False)

    def itemChanged(self, item):
        """
        Run on when the user selects stuff in the database tree.
        :param item:
        :return:
        """
        if type(item) in [PGTable, PGVectorTable]:
            self.selected_item = item
            self.update_grid()
            self.activate_fields()
        else:
            self.deactivate_fields()
            self.tableView.setModel(None)

    def update_grid(self):
        """
        Updates the grid.
        :return:
        """

        table = self.selected_item.name
        db = self.tree.currentDatabase().publicUri().connectionInfo()
        results = self.db_tool.select({'table': table, 'db': db})

        if len(results) > 0:

            labels = [self.db_tool.get_field_def().get(f).get('label') for f in list(self.db_tool.get_field_def()) if
                      'label' in self.db_tool.get_field_def().get(f)]
            fields = [f for f in list(self.db_tool.get_field_def()) if 'label' in self.db_tool.get_field_def().get(f)]

            rws = []
            for result in results:
                t = []
                for k in fields:
                    t.append(result.get(k))
                rws.append(tuple(t))
                self.guids.append(result.get('guid'))

            table_model = MetaTableModel(self, rws, labels)

            self.tableView.setModel(table_model)
            self.tableView.selectionModel().selectionChanged.connect(self.tableRowSelected)

        else:
            self.tableView.setModel(None)
            self.tableView.selectionModel().selectionChanged.disconnect()

    def show(self):
        super(MetadataFunctionalityDialog, self).show()
        self.db_tool.connect()

    def doSave(self):
        navn = self.navnEdit.text()
        beskrivelse = self.beskrivelseEdit.text()
        journalnr = self.journalnrEdit.text()
        dato = self.datoEdit.text()

        # rette_dato = self.retteDatoEdit.text()

        ansvarlig_center_medarbejder = self.ansvarligCenterMedarbejderEdit.text()
        projekter_wor = self.projekterWorEdit.text()

    def updateRecord(self):
        """
            Adds a record to the table.
            :return:
            """
        table = self.tree.currentTable()
        if table:
            schema = table.schema().name
            table_name = table.name
            current_database = self.tree.currentDatabase().publicUri().connectionInfo()
            self.db_tool.update(
                {'table': table_name,
                 'guid': str(uuid.uuid4()),
                 'db': current_database,
                 'name': self.navnEdit.text(),
                 'timestamp': self.datoEdit.text(),
                 'journal_nr': self.journalnrEdit.text(),
                 'resp_center_off': self.ansvarligCenterMedarbejderEdit.text(),
                 'proj_wor': self.projekterWorEdit.text()
                 }
            )
            self.update_grid()

    def addRecord(self):
        """
        Adds a record to the table.
        :return:
        """
        table = self.tree.currentTable()
        if table:
            schema = table.schema().name
            table_name = table.name
            current_database = self.tree.currentDatabase().publicUri().connectionInfo()
            self.db_tool.insert(
                {'table': table_name,
                 'guid': str(uuid.uuid4()),
                 'db': current_database,
                 'name': self.navnEdit.text(),
                 'timestamp': self.datoEdit.text(),
                 'journal_nr': self.journalnrEdit.text(),
                 'resp_center_off': self.ansvarligCenterMedarbejderEdit.text(),
                 'proj_wor': self.projekterWorEdit.text()
                 }
            )
            self.update_grid()
        else:
            QMessageBox.information(self, self.tr("Please!"), self.tr("Husk at stille dig på en table foroven."))


class MetadataFunctionalitySettingsDialog(QtGui.QDialog, SETTINGS_FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(MetadataFunctionalitySettingsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.db_tool = MetaManDBTool()

        self.setupUi(self)

        self.settings = MetadataFunctionalitySettings()

        self.table_name = self.settings.value('table_name')
        if not self.table_name:
            self.settings.setValue('table_name', 'metadata')
            self.table_name = 'metadata'

        self.tree = DBTree(self)
        self.treeDock.setWidget(self.tree)

        self.createMetadataTableButton.clicked.connect(self.createDB)

    def createDB(self):

        current_database = self.tree.currentDatabase()

        if current_database:

            conn_info = current_database.publicUri().connectionInfo()

            table_names = [n.name for n in current_database.tables()]

            # QgsMessageLog.logMessage("==>" + str(conn_info))

            if self.settings.value('table_name') in table_names:

                QMessageBox.information(self, self.tr("Please!"), self.tr("Metadata table already exists in this db."))

            else:

                self.table_name = self.settings.value('conn_info')
                if not self.table_name:
                    self.settings.setValue('conn_info', conn_info)

                self.db_tool.create_metaman_table(current_database)


        else:
            QMessageBox.information(self, self.tr("Please!"), self.tr("Please select a database and schema."))






