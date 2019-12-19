# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout
) 
from db_manager.db_plugins.postgis.plugin import PGTable

from ..core.metadatadblinkertool import MetadataDbLinkerTool
from .qgissettingmanager import *
from .dialog_settings_db_def import SettingsDbDefDialog, SettingsGuiTableDialog
from qgis.gui import (QgsOptionsPageWidget)
WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'settings.ui')
)

class ConfigOptionsPage(QgsOptionsPageWidget):

    def __init__(self, parent, settings):
        super(ConfigOptionsPage, self).__init__(parent)
        self.settings = settings
        self.config_widget = ConfigDialog(self.settings)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(0)
        self.setLayout(layout)
        layout.addWidget(self.config_widget)
        self.setObjectName('metadata-db-linker')

    def apply(self):
        self.config_widget.accept_dialog()
        self.settings.emit_updated()


class ConfigDialog(WIDGET, BASE,SettingDialog):

    def __init__(self, settings):
        """Constructor."""
        super(ConfigDialog, self).__init__(None)
        self.db_tool = MetadataDbLinkerTool()

        self.setupUi(self)

        self.settings = settings
        SettingDialog.__init__(self, self.settings)

        self.db_def_dlg = SettingsDbDefDialog()
        self.gui_table_def = SettingsGuiTableDialog()
        self.table_name = self.settings.value('sourcetable')

        self.testConnectionButton.clicked.connect(self.test_connection)

        self.databaseDefinitionButton.clicked.connect(self.show_db_def)
        self.databaseGuiDefinitionButton.clicked.connect(self.show_gui_table_def)
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

    def show_gui_table_def(self):
        """
        Opens the dialogue that shows the sql code.
        :return:
        """
        self.gui_table_def.exec_()


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
