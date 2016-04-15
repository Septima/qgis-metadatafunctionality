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
from PyQt4.QtGui import QMessageBox, QTreeView
from PyQt4.QtCore import QSettings, QAbstractTableModel, Qt, SIGNAL, QObject

# TODO: Remove QgsMessageLog after debug phase.
from qgis.core import QgsMessageLog, QgsProject, QgsBrowserModel, QgsLayerItem, QgsDataSourceURI
from qgis.gui import QgsBrowserTreeView

from .. import MetadataFunctionalitySettings
from ..core import MetaManDBTool

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog.ui'))

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

class SelectedItemProxy(object):

    def __init__(self, table, uri):
        self.table = table
        self._uri = uri

    def layerName(self):
        return self.table

    def uri(self):
        return self._uri


class MetadataFunctionalityDialog(QtGui.QDialog, FORM_CLASS):

    field_def = []
    data_list = []

    def exec_(self):
        if self.db_tool.validate_structure():
            super(MetadataFunctionalityDialog, self).exec_()
        else:
            QMessageBox.information(self, self.tr("Please!"), self.tr("Metadata table does not exist or wrong access rights."))

    def __init__(self, parent=None, table=None, uri=None):
        """Constructor."""
        super(MetadataFunctionalityDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        if type(table) == tuple:
            table = table[1]

        print("New table: " + str(table))

        self.settings = MetadataFunctionalitySettings()
        self.db_tool = MetaManDBTool()

        self.setupUi(self)

        # root = QgsProject.instance().layerTreeRoot()
        # root = None
        # QgsMessageLog.logMessage(str(dir(root)))

        self.model = QgsBrowserModel()

        if True is False:
            index = self.model.index(5, 0)
            print("....")

            idx2 = index.child(1, 0)

            print(self.model.data(idx2))
            print(self.model.dataItem(idx2).paramWidget())

            idx3 = idx2.child(0, 0)

            print(":" + str(self.model.dataItem(idx3)))

        self.model.reload()

        # self.tree = QTreeView()
        self.tree = QgsBrowserTreeView()
        self.tree.setModel(self.model)

        # self.tree.removeRow(index.row())

        self.treeDock.setWidget(self.tree)

        self.datoEdit.setDateTime(datetime.now())

        self.buttonBox.accepted.connect(self.save_record)

        QObject.connect(self.tree.selectionModel(), SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.selection_changed)

        self.saveRecordButton.clicked.connect(self.save_record)
        self.deleteRecordButton.clicked.connect(self.delete_record)

        # self.addRecordButton.clicked.connect(self.add_record)

        self.selected_item = None
        self.guids = []
        self.currentlySelectedLine = None

        if table:
            self.treeDock.setEnabled(False)
            self.selected_item = SelectedItemProxy(table, uri)
            self.update_grid()
            self.tableView.selectRow(0)
            self.activate_fields()

    def get_selected_uri(self):
        """
        :return:
        """
        QgsMessageLog.logMessage(self.selected_item.uri())
        return self.selected_item.uri()

    def get_selected_db(self):
        return QgsDataSourceURI(self.selected_item.uri()).database()

    def get_selected_port(self):
        return QgsDataSourceURI(self.selected_item.uri()).port()

    def get_selected_host(self):
        return QgsDataSourceURI(self.selected_item.uri()).host()

    def get_selected_schema(self):
        """
        :return:
        """
        s = QgsDataSourceURI(self.selected_item.uri()).schema()
        if s==None or s=='':
            return 'public'
        else:
            return s

    def get_selected_table(self):
        """
        :return:
        """
        return self.selected_item.layerName()

    def save_record(self):
        if self.currentlySelectedLine is None:
            self.add_record()
        else:
            self.update_record()

    def table_row_selected(self, a, b):

        v = []
        idxs = a.indexes()
        for idx in idxs:
            r = idx.row()
            if r not in v:
                v.append(r)

        if len(v) > 0:

            guid = self.guids[v[0]]
            self.currentlySelectedLine = guid
            results = self.db_tool.select({'guid': guid})

            if len(results) == 1:
                results = results[0]

                if 'name' in list(results):
                    self.navnEdit.setText(results.get('name'))

                if 'beskrivelse' in list(results):
                    self.beskrivelseEdit.setText(results.get('beskrivelse'))

                if 'timestamp' in list(results):
                    d = results.get('timestamp')
                    da = datetime.strptime(d,'%d/%m/%Y %H.%M')
                    self.datoEdit.setDate(da)

                if 'journal_nr' in list(results):
                    self.journalnrEdit.setText(results.get('journal_nr'))

                if 'resp_center_off' in list(results):
                    self.ansvarligCenterMedarbejderEdit.setText(results.get('resp_center_off'))

                if 'proj_wor' in list(results):
                    self.projekterWorEdit.setText(results.get('proj_wor'))

    def delete_record(self):
        """
        Delete a record given its GUID.
        Empties the fields.
        """
        selected_rows = self.tableView.selectionModel().selectedRows()
        for row in selected_rows:
            guid = self.guids[row.row()]
            self.db_tool.delete({'guid': guid})
            self.update_grid()
            if self.has_table_data:
                self.tableView.selectRow(0)
        self.empty_fields()
        self.deleteRecordButton.setEnabled(False)

    def activate_fields(self):
        """
        Activates all fields and buttons.
        :return:
        """
        # self.addRecordButton.setEnabled(True)
        self.saveRecordButton.setEnabled(True)
        self.deleteRecordButton.setEnabled(True)
        self.datoEdit.setEnabled(True)
        self.navnEdit.setEnabled(True)
        self.projekterWorEdit.setEnabled(True)
        self.ansvarligCenterMedarbejderEdit.setEnabled(True)
        # self.tableView.setEnabled(True)
        self.journalnrEdit.setEnabled(True)
        self.beskrivelseEdit.setEnabled(True)

    def deactivate_fields(self):
        """
        Deactivates all fields and buttons.
        :return:
        """
        self.datoEdit.setEnabled(False)
        self.addRecordButton.setEnabled(False)
        self.deleteRecordButton.setEnabled(False)
        self.saveRecordButton.setEnabled(False)
        self.navnEdit.setEnabled(False)
        self.projekterWorEdit.setEnabled(False)
        self.ansvarligCenterMedarbejderEdit.setEnabled(False)
        self.tableView.setEnabled(False)
        self.journalnrEdit.setEnabled(False)
        self.beskrivelseEdit.setEnabled(False)

    def selection_changed(self, newSelection, oldSelection):
        """
        Triggered when the user clicks on a postgresql table in the tree.
        :param newSelection:
        :param oldSelection:
        :return:
        """
        self.empty_fields()
        selected = newSelection.indexes()
        if len(selected) > 0:

            b = self.model.dataItem(selected[0])

            if type(b) == QgsLayerItem:
                self.selected_item = b
                self.update_grid()
                self.activate_fields()
                if self.has_table_data:
                    self.tableView.selectRow(0)
                else:
                    self.tableView.setModel(None)
            else:
                self.deactivate_fields()

    def empty_fields(self):
        """
        Empties all fields.
        :return:
        """
        self.navnEdit.setText('')
        self.projekterWorEdit.setText('')
        self.ansvarligCenterMedarbejderEdit.setText('')
        self.navnEdit.setText('')
        self.journalnrEdit.setText('')
        self.beskrivelseEdit.setText('')

    def update_grid(self):
        """
        Updates the grid.
        :return:
        """

        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()

        results = self.db_tool.select(
            {
                'db': db,
                'port': port,
                'schema': schema,
                'table': table,
            }, order_by={'field':'ts', 'direction':'DESC'})

        if len(results) > 0:

            labels = [self.db_tool.get_field_def().get(f).get('label') for f in list(self.db_tool.get_field_def()) if
                      'label' in self.db_tool.get_field_def().get(f)]
            fields = [f for f in list(self.db_tool.get_field_def()) if 'label' in self.db_tool.get_field_def().get(f)]

            rws = []
            self.guids = []
            for result in results:
                t = []
                for k in fields:
                    t.append(result.get(k))
                rws.append(tuple(t))
                self.guids.append(result.get('guid'))

            table_model = MetaTableModel(self, rws, labels)

            xx = table_model.data(table_model.createIndex(0, 0), Qt.DisplayRole)
            QgsMessageLog.logMessage(str(xx))

            # if self.currentlySelectedLine:
            #     for irow in xrange(table_model.rowCount()):
            #         row = []
            #         for icol in xrange(table_model.columnCount()):
            #             cell = table_model.data(table_model.createIndex(irow, icol))
            #             row.append(cell)

            self.tableView.setModel(table_model)
            self.tableView.selectionModel().selectionChanged.connect(self.table_row_selected)
            self.has_table_data = True
            # self.deleteRecordButton.setEnabled(True)
        else:
            self.has_table_data = False
            self.tableView.setModel(None)
            self.tableView.selectionModel().selectionChanged.disconnect()
            # self.deleteRecordButton.setEnabled(False)

    def show(self):
        super(MetadataFunctionalityDialog, self).show()

    def update_record(self):
        """
            Adds a record to the table.
            :return:
            """

        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()
        host = self.get_selected_host()

        self.db_tool.update(
            {
                'db': db,
                'port': port,
                'host': host,
                'schema': schema,
                'table': table,
                'guid': self.currentlySelectedLine,
                'name': self.navnEdit.text(),
                'beskrivelse': self.beskrivelseEdit.toPlainText(),
                'timestamp': self.datoEdit.text(),
                'journal_nr': self.journalnrEdit.text(),
                'resp_center_off': self.ansvarligCenterMedarbejderEdit.text(),
                'proj_wor': self.projekterWorEdit.text()
            }
        )
        self.update_grid()

    def add_record(self):
        """
        Adds a record to the table.
        :return:
        """

        guid = str(uuid.uuid4())

        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()
        host = self.get_selected_host()

        if table:
            self.db_tool.insert(
                {
                    'guid': guid,
                    'db': db,
                    'port': port,
                    'schema': schema,
                    'host': host,
                    'table': table,
                    'name': self.navnEdit.text(),
                    'beskrivelse': self.beskrivelseEdit.toPlainText(),
                    'timestamp': self.datoEdit.text(),
                    'journal_nr': self.journalnrEdit.text(),
                    'resp_center_off': self.ansvarligCenterMedarbejderEdit.text(),
                    'proj_wor': self.projekterWorEdit.text()
                }
            )
            self.currentlySelectedLine = guid
            self.update_grid()
            self.tableView.selectRow(0)
        else:
            QMessageBox.information(self, self.tr("Please!"), self.tr("Husk at stille dig på en table foroven."))









