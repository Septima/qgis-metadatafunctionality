# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataDialog
                                 A QGIS plugin
 MetadataDbLinker
                             -------------------
        begin                : 2016-04-04
        git sha              : $Format:%H$
        copyright            : (C) 2016 Septima P/S
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
import os
import uuid
from datetime import datetime

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QMessageBox
)
from qgis.PyQt.QtCore import (
    QAbstractTableModel,
    Qt,
    pyqtSignal,
    QObject,
    pyqtSlot
)
from qgis.core import (
    QgsBrowserModel,
    QgsLayerItem,
    QgsDataSourceUri
)
from qgis.gui import QgsBrowserTreeView, QgsActionMenu

#from ..core.taxonclassifier import TaxonClassifier
from ..core.qgislogger import QgisLogger
from .. import MetadataDbLinkerSettings
from ..core import MetadataDbLinkerTool

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'dialog_metadata.ui'
    )
)


class MetaTableModel(QAbstractTableModel):
    """
    The model for the table view
    """
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


class MetadataDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None, table=None, uri=None, schema=None, close_dialog=False):
        """Constructor."""
        super(MetadataDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.field_def = []
        self.data_list = []

        if type(table) == tuple:
            table = table[1]

        self.schema = schema
        self.close_dialog = close_dialog
        self.settings = MetadataDbLinkerSettings()
        self.db_tool = MetadataDbLinkerTool()
        self.logger = QgisLogger('Metadata-DB-Linker')

        self.setupUi(self)

        self.model = QgsBrowserModel()
        self.model.addRootItems()
        self.tree = QgsBrowserTreeView()
        self.tree.setModel(self.model)

        self.treeDock.setWidget(self.tree)
        self.dateEdit.setDateTime(datetime.now())

#        QObject.connect(
#            self.tree.selectionModel(),
#            pyqtSignal("selectionChanged(QItemSelection, QItemSelection)"),
#            self.selection_changed
#        )

        self.tree.selectionModel().selectionChanged.connect(self.selection_changed)

        self.saveRecordButton.clicked.connect(self.save_record)
        self.deleteRecordButton.clicked.connect(self.delete_record)

        self.kleNoLookupBtn.clicked.connect(self.lookup_kle_number)
        self.kleSuggestions.setReadOnly(True)

        self.selected_item = None
        self.guids = []
        self.currentlySelectedLine = None

        if self.close_dialog:
            self.saveRecordButton.setText(self.tr('Save metadata and close'))

        if table:
            self.treeDock.setEnabled(False)
            self.selected_item = SelectedItemProxy(table, uri)
            self.update_grid()
            self.tableView.selectRow(0)
            self.activate_fields()

    def lookup_kle_number(self):
        taxon_url = self.settings.value('taxonUrl')
        taxon_taxonomy = self.settings.value('taxonTaxonomy')
        if not taxon_url or not taxon_taxonomy:
            self.logger.critical('No taxon url and/or taxonomy')
            QMessageBox.warning(
                self,
                self.tr("No taxon url and/or taxonomy"),
                self.tr("Please enter an url and taxonomy for Taxon service in settings.")
            )
            return False

        taxon = TaxonClassifier(
            taxon_url,
            taxon_taxonomy
        )
        taxon_results = taxon.get(
            self.descriptionEdit.toPlainText()
        )
        if taxon_results:
            presentation_str = ''
            kle_nrs = []
            for elem in taxon_results:
                tmp_presentation = u'{} {}\n'.format(
                    elem['kle'],
                    elem['title']
                )
                presentation_str += tmp_presentation
                kle_nrs.append(elem['kle'])
            # Set text in presentaion box
            self.kleSuggestions.setText(presentation_str)

            current_klr = self.kleNoEdit.text()
            str_klr_nrs = '{}'.format(', '.join(kle_nrs))

            # set text in kle input box
            if current_klr != str_klr_nrs:
                if not current_klr == '':
                    self.kleNoEdit.setText(
                        '{}, {}'.format(
                            self.kleNoEdit.text(),
                            ', '.join(kle_nrs)
                        )
                    )
                else:
                    self.kleNoEdit.setText(
                        '{}'.format(', '.join(kle_nrs))
                    )
        else:
            self.kleSuggestions.setText('No results from Taxon Classifier.')
            self.logger.info('No results from taxon service')

    def exec_(self):
        if self.db_tool.validate_structure():
            super(MetadataDialog, self).exec_()
        else:
            QMessageBox.information(
                self,
                self.tr("Please!"),
                self.tr("Either database is unavailable, table with metadata does not exist or wrong access rights.")
            )

    def get_selected_uri(self):
        """
        :return:
        """
        return self.selected_item.uri()

    def get_selected_db(self):
        return QgsDataSourceUri(self.selected_item.uri()).database()

    def get_selected_port(self):
        return QgsDataSourceUri(self.selected_item.uri()).port()

    def get_selected_host(self):
        return QgsDataSourceUri(self.selected_item.uri()).host()

    def get_selected_schema(self):
        """
        :return:
        """
        if self.schema is None or self.schema == '':
            return 'public'
        else:
            return self.schema

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

        if self.close_dialog:
            self.close()

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

            try:
                results = self.db_tool.select({'guid': guid})
            except RuntimeError:
                QMessageBox.critical(
                    self,
                    self.tr('Error selecting data.'),
                    self.tr('See log for error details.')
                )

            if len(results) == 1:
                results = results[0]

                self.schema = results.get('schema')

                if 'name' in list(results):
                    self.nameEdit.setText(results.get('name'))

                if 'description' in list(results):
                    self.descriptionEdit.setText(results.get('description'))

                if 'ts_timezone' in list(results):
                    d = results.get('ts_timezone')
                    da = datetime.strptime(d, '%d/%m-%Y %H:%M')
                    self.dateEdit.setDate(da)

                if 'kle_no' in list(results):
                    self.kleNoEdit.setText(results.get('kle_no'))

                if 'responsible' in list(results):
                    self.responsibleEdit.setText(results.get('responsible'))

                if 'project' in list(results):
                    self.projectEdit.setPlainText(results.get('project'))

        else:
            self.currentlySelectedLine = None

    def delete_record(self):
        """
        Delete a record given its GUID.
        Empties the fields.
        """
        selected_rows = self.tableView.selectionModel().selectedRows()
        for row in selected_rows:
            guid = self.guids[row.row()]
            try:
                self.db_tool.delete({'guid': guid})
            except RuntimeError:
                QMessageBox.critical(
                    self,
                    self.tr('Error deleting data.'),
                    self.tr('See log for error details.')
                )
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
        self.nameEdit.setEnabled(True)
        self.descriptionEdit.setEnabled(True)
        self.kleNoEdit.setEnabled(True)
        self.kleNoLookupBtn.setEnabled(True)
        self.responsibleEdit.setEnabled(True)
        self.projectEdit.setEnabled(True)
        self.dateEdit.setEnabled(True)
        self.saveRecordButton.setEnabled(True)
        self.deleteRecordButton.setEnabled(True)
        # self.tableView.setEnabled(True)

    def deactivate_fields(self):
        """
        Deactivates all fields and buttons.
        :return:
        """
        self.nameEdit.setEnabled(False)
        self.descriptionEdit.setEnabled(False)
        self.kleNoEdit.setEnabled(False)
        self.kleNoLookupBtn.setEnabled(False)
        self.responsibleEdit.setEnabled(False)
        self.projectEdit.setEnabled(False)
        self.dateEdit.setEnabled(False)
        self.saveRecordButton.setEnabled(False)
        self.deleteRecordButton.setEnabled(False)
        # self.tableView.setEnabled(False)

    @pyqtSlot("QItemSelection")
    def selection_changed(self, newSelection):
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

                self.schema = QgsDataSourceUri(b.uri()).schema()

                self.selected_item = b
                self.update_grid()
                self.activate_fields()

                if self.has_table_data:
                    self.tableView.selectRow(0)
                else:
                    self.tableView.setModel(None)
                    self.currentlySelectedLine = None
                    self.dateEdit.setDateTime(datetime.now())
            else:
                self.deactivate_fields()

    def empty_fields(self):
        """
        Empties all fields.
        :return:
        """
        self.nameEdit.setText('')
        self.descriptionEdit.setText('')
        self.responsibleEdit.setText('')
        self.kleNoEdit.setText('')
        self.projectEdit.setPlainText('')
        self.kleSuggestions.setText('')

    def update_grid(self):
        """
        Updates the grid.
        :return:
        """

        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()

        results = []

        try:
            results = self.db_tool.select(
                {
                    'db': db,
                    'port': port,
                    'schema': schema,
                    'sourcetable': table,
                },
                order_by={'field': 'ts_timezone', 'direction': 'DESC'}
            )
        except RuntimeError:
            QMessageBox.critical(
                self,
                self.tr('Error selecting data.'),
                self.tr('See log for error details.')
            )

        if len(results) > 0:

            labels = [
                self.db_tool.get_field_def().get(f).get('label') for f in self.db_tool.field_order if
                'label' in self.db_tool.get_field_def().get(f)
            ]

            fields = self.db_tool.field_order

            rws = []
            self.guids = []
            for result in results:
                t = []
                for k in fields:
                    t.append(result.get(k))
                rws.append(tuple(t))
                self.guids.append(result.get('guid'))

            table_model = MetaTableModel(self, rws, labels)

            table_model.data(
                table_model.createIndex(0, 0),
                Qt.DisplayRole
            )

            self.tableView.setModel(table_model)
            self.tableView.selectionModel().selectionChanged.connect(
                self.table_row_selected
            )
            self.has_table_data = True
            # self.deleteRecordButton.setEnabled(True)
        else:
            self.has_table_data = False
            self.tableView.setModel(None)
            self.tableView.selectionModel().selectionChanged.disconnect()
            # self.deleteRecordButton.setEnabled(False)

    def show(self):
        super(MetadataDialog, self).show()

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

        try:
            self.db_tool.update(
                {
                    'db': db,
                    'port': port,
                    'host': host,
                    'schema': schema,
                    'sourcetable': table,
                    'guid': self.currentlySelectedLine,
                    'name': self.nameEdit.text(),
                    'description': self.descriptionEdit.toPlainText(),
                    'ts_timezone': self.dateEdit.text(),
                    'kle_no': self.kleNoEdit.text(),
                    'responsible': self.responsibleEdit.text(),
                    'project': self.projectEdit.toPlainText()
                }
            )
        except RuntimeError:
            QMessageBox.critical(
                self,
                self.tr('Error updating data.'),
                self.tr('See log for error details.')
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
            try:
                self.db_tool.insert(
                    {
                        'guid': guid,
                        'db': db,
                        'port': port,
                        'schema': schema,
                        'host': host,
                        'sourcetable': table,
                        'name': self.nameEdit.text(),
                        'description': self.descriptionEdit.toPlainText(),
                        'ts_timezone': self.dateEdit.text(),
                        'kle_no': self.kleNoEdit.text(),
                        'responsible': self.responsibleEdit.text(),
                        'project': self.projectEdit.toPlainText()
                    }
                )
            except RuntimeError:
                QMessageBox.critical(
                    self,
                    self.tr('Error inserting data.'),
                    self.tr('See log for error details.')
                )
            self.currentlySelectedLine = guid
            self.update_grid()
            self.tableView.selectRow(0)
        else:
            QMessageBox.information(
                self,
                self.tr("Please!"),
                self.tr("Remember to select a table.")
            )
