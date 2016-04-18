import os

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox, QTreeView

from db_manager.db_plugins.postgis.plugin import PGVectorTable, PGTable

from .. import MetadataFunctionalitySettings
from ..core import MetaManDBTool
from ..qgissettingmanager.settingdialog import SettingDialog
from ..ui.metadata_functionality_dialog_settings_db_def import \
    MetadataFunctionalitySettingsDBDefDialog

SETTINGS_FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_settings.ui'))

class MetadataFunctionalitySettingsDialog(QtGui.QDialog, SETTINGS_FORM_CLASS, SettingDialog):

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
        SettingDialog.__init__(self, self.settings)

        self.db_def_dlg = MetadataFunctionalitySettingsDBDefDialog()

        self.table_name = self.settings.value('table')

        self.testConnectionButton.clicked.connect(self.test_connection)

        self.databaseDefinitionButton.clicked.connect(self.show_db_def)

        self.table_structure_ok = False
        self.current_item = None

        self.host.textChanged.connect(self.activate_test_button)
        self.database.textChanged.connect(self.activate_test_button)
        self.port.textChanged.connect(self.activate_test_button)
        self.schema.textChanged.connect(self.activate_test_button)
        self.table.textChanged.connect(self.activate_test_button)
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
            self.table_structure_ok = self.db_tool.validate_structure(db, item.name)
            self.activate_test_button()

    def all_fields_filled(self):

        host = self.host.text()
        database = self.database.text()
        port = self.port.text()
        schema = self.schema.text()
        table = self.table.text()
        username = self.username.text()
        password = self.password.text()

        return host != '' and database != '' and port != '' and schema != '' and table != '' and username != '' and password != ''

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
        self.settings.setValue('host', self.host.text())
        self.settings.setValue('port', self.port.text())
        self.settings.setValue('schema', self.schema.text())
        self.settings.setValue('database', self.database.text())
        self.settings.setValue('username', self.username.text())
        self.settings.setValue('password', self.password.text())
        mmt = MetaManDBTool()
        if mmt.validate_structure():
            QMessageBox.information(self, self.tr("Please!"), self.tr("DB structure and connection OK."))
