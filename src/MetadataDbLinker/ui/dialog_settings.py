# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SettingsDialog
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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QMessageBox,
    QDialog
)

from db_manager.db_plugins.postgis.plugin import PGTable

from .. import MetadataDbLinkerSettings
from ..core import MetadataDbLinkerTool
from ..qgissettingmanager import SettingDialog
from ..ui.dialog_settings_db_def import SettingsDbDefDialog

SETTINGS_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'dialog_settings.ui'
    )
)


class SettingsDialog(QDialog, SETTINGS_FORM_CLASS, SettingDialog):

    def __init__(self, parent=None):
        """Constructor."""
        super(QDialog, self).__init__(parent)
        self.db_tool = MetadataDbLinkerTool()

        self.setupUi(self)

        self.settings = MetadataDbLinkerSettings()
        SettingDialog.__init__(self, self.settings)

        self.db_def_dlg = SettingsDbDefDialog()

        self.table_name = self.settings.value('sourcetable')

        self.testConnectionButton.clicked.connect(self.test_connection)

        self.databaseDefinitionButton.clicked.connect(self.show_db_def)

        self.table_structure_ok = False
        self.current_item = None

        self.host.textChanged.connect(self.activate_test_button)
        self.database.textChanged.connect(self.activate_test_button)
        self.port.textChanged.connect(self.activate_test_button)
        self.schema.textChanged.connect(self.activate_test_button)
        self.sourcetable.textChanged.connect(self.activate_test_button)
        self.username.textChanged.connect(self.activate_test_button)
        self.password.textChanged.connect(self.activate_test_button)

        self.testConnectionButton.setEnabled(self.all_fields_filled())

    def show_db_def(self):
        """
        Opens the dialogue that shows the sql code.
        :return:
        """
        self.db_def_dlg.exec_()

    def item_changed(self, item):
        self.current_item = item
        if type(item) in [PGTable]:
            db = self.tree.currentDatabase().publicUri().connectionInfo()
            self.table_structure_ok = self.db_tool.validate_structure(
                db,
                item.name
            )
            self.activate_test_button()

    def all_fields_filled(self):

        host = self.host.text()
        database = self.database.text()
        port = self.port.text()
        schema = self.schema.text()
        sourcetable = self.sourcetable.text()
        username = self.username.text()
        password = self.password.text()

        return host != '' and database != '' and port != '' and schema != '' and sourcetable != '' and username != '' and password != ''

    def activate_test_button(self):
        """
        Activates the test connection test button when
        :return:
        """
        self.testConnectionButton.setEnabled(self.all_fields_filled())

    def test_connection(self):
        """
        :return:
        """
        self.settings.set_value('host', self.host.text())
        self.settings.set_value('port', self.port.text())
        self.settings.set_value('schema', self.schema.text())
        self.settings.set_value('database', self.database.text())
        self.settings.set_value('username', self.username.text())
        self.settings.set_value('password', self.password.text())
        if self.db_tool.validate_structure():
            QMessageBox.information(
                self,
                self.tr("Information"),
                self.tr("DB structure and connection OK.")
            )
        else:
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Either structure of database or connection is broken")
            )
