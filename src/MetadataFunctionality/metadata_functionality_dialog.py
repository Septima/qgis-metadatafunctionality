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
from PyQt4.QtCore import QSettings

# TODO: Remove after debug phase.
from qgis.core import QgsMessageLog

from db_manager.db_tree import DBTree
from db_manager.db_plugins.plugin import TableField

# from . import MetadataFunctionalityQSettingsings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_base.ui'))

SETTINGS_FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_settings.ui'))


class MetadataFunctionalityDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(MetadataFunctionalityDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

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

            QgsMessageLog.logMessage(str(current_database.uri().encodedUri()))

            table_names = [ n.name for n in current_database.tables()]

            if "MetadataFunctionality" in table_names:

                QMessageBox.information(self, self.tr("Please!"), self.tr("Metadata table already exists in this db."))

            else:
                f1 = TableField(None)
                f1.name = 'f1'
                f1.dataType = 'varchar'
                f1.notNull = True
                current_database.createTable("MetadataFunctionality", [f1])

        else:
            QMessageBox.information(self, self.tr("Please!"), self.tr("Please select a database and schema."))






