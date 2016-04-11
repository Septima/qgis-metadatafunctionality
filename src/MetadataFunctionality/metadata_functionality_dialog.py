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

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QSettings, QAbstractTableModel, Qt

# TODO: Remove after debug phase.
from qgis.core import QgsMessageLog

from db_manager.db_tree import DBTree
from db_manager.db_plugins.plugin import TableField

# from . import MetadataFunctionalityQSettingsings

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

class MetadataFunctionalityDialog(QtGui.QDialog, FORM_CLASS):

    field_def = ['Dato', 'Navn', 'Beskrivelse', ' J.nr.', ' Center/Medarbejder', 'Projekt/wor']

    data_list = [
        ('01.01.2016', 'Gylletank fjernet', '....', '2016-1.2.345', 'Frank Jensen', 'gylletanke'),
        ('15.12.2015', 'Merge', '....', '2016-1.2.345', 'Frank Jensen', 'gylletanke'),
        ('01.12.2015', 'Clean', '....', '2016-1.2.345', 'Henrik Sass', 'gylletanke'),
    ]

    def __init__(self, parent=None):
        """Constructor."""
        super(MetadataFunctionalityDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


        # we add the DBTree component into the treeDock widget,
        self.tree = DBTree(self)
        self.treeDock.setWidget(self.tree)

        # and set up the grid
        table_model = MetaTableModel(self, self.data_list, self.field_def)
        self.tableView.setModel(table_model)

        self.buttonBox.accepted.connect(self.doSave)

    def doSave(self):
        QgsMessageLog.logMessage("Saving data.")
        navn = self.navnEdit.text()
        beskrivelse = self.beskrivelseEdit.text()
        journalnr = self.journalnrEdit.text()
        dato = self.datoEdit.text()
        rette_dato = self.retteDatoEdit.text()
        ansvarlig_center_medarbejder = self.ansvarligCenterMedarbejderEdit.text()
        projekter_wor = self.projekterWorEdit.text()

        # TODO: save into DB


class MetadataFunctionalitySettingsDialog(QtGui.QDialog, SETTINGS_FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(MetadataFunctionalitySettingsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)

        self.settings = QSettings()

        self.table_name = self.settings.value('/MetadataFunctionality/table_name', None, str)
        if not self.table_name:
            self.settings.setValue('/MetadataFunctionality/table_name', 'metadata' )
            self.table_name = 'metadata'

        self.tree = DBTree(self)
        self.treeDock.setWidget(self.tree)

        self.createMetadataTableButton.clicked.connect(self.createDB)

    def createDB(self):

        current_database = self.tree.currentDatabase()

        if current_database:

            QgsMessageLog.logMessage("test", "General")

            conn_info = current_database.publicUri().connectionInfo()

            table_names = [n.name for n in current_database.tables()]

            if "MetadataFunctionality" in table_names:

                QMessageBox.information(self, self.tr("Please!"), self.tr("Metadata table already exists in this db."))

            else:

                self.table_name = self.settings.value('/MetadataFunctionality/conn_info', None, str)
                if not self.table_name:
                    self.settings.setValue('/MetadataFunctionality/conn_info', conn_info)

                guid_field = TableField(None)
                guid_field.name = 'guid'
                guid_field.dataType = 'varchar'
                guid_field.notNull = True

                handle_to_tabel_field = TableField(None)
                handle_to_tabel_field.name = 'table'
                handle_to_tabel_field.dataType = 'varchar'
                handle_to_tabel_field.notNull = True

                timestamp_field = TableField(None)
                timestamp_field.name = 'time'
                timestamp_field.dataType = 'timestamp'
                timestamp_field.notNull = True

                name_field = TableField(None)
                name_field.name = 'name'
                name_field.dataType = 'varchar'
                name_field.notNull = True

                description_field = TableField(None)
                description_field.name = 'description'
                description_field.dataType = 'varchar'
                description_field.notNull = True

                journal_nr_field = TableField(None)
                journal_nr_field.name = 'journal_nr'
                journal_nr_field.dataType = 'varchar'
                journal_nr_field.notNull = True

                resp_center_officer_field = TableField(None)
                resp_center_officer_field.name = 'resp_center_off'
                resp_center_officer_field.dataType = 'varchar'
                resp_center_officer_field.notNull = True

                projects_wor_field = TableField(None)
                projects_wor_field.name = 'proj_wor'
                projects_wor_field.dataType = 'varchar'
                projects_wor_field.notNull = True

                table = current_database.createTable(
                    "MetadataFunctionality", [
                        guid_field,
                        handle_to_tabel_field,
                        timestamp_field,
                        name_field,
                        description_field,
                        journal_nr_field,
                        resp_center_officer_field,
                        projects_wor_field
                    ]
                )
                QMessageBox.information(self, self.tr("Please!"), self.tr(str(table)))



        else:
            QMessageBox.information(self, self.tr("Please!"), self.tr("Please select a database and schema."))






