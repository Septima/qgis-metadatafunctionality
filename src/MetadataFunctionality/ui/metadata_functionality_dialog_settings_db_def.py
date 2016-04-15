import os

from PyQt4 import QtGui, uic

SETTINGS_DB_FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_settings_db_def.ui'))

class MetadataFunctionalitySettingsDBDefDialog(QtGui.QDialog, SETTINGS_DB_FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(MetadataFunctionalitySettingsDBDefDialog, self).__init__(parent)
        self.setupUi(self)
        self.load_db_def()

    def load_db_def(self):
        """
        :return:
        """

        nf = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sql','metaman.sql')
        with open(nf, 'r') as myfile:
            self.textEdit.setText(myfile.read())
