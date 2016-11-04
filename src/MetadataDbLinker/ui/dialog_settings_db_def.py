# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SettingsDbDefDialog
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

import os

from PyQt4 import (
    QtGui,
    uic
)

SETTINGS_DB_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'dialog_settings_db_def.ui'
    )
)


class SettingsDbDefDialog(QtGui.QDialog, SETTINGS_DB_FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(SettingsDbDefDialog, self).__init__(parent)
        self.setupUi(self)
        self.load_db_def()

    def load_db_def(self):
        nf = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'sql',
            'metadata_table.sql'
        )
        with open(nf, 'r') as myfile:
            self.textEdit.setText(myfile.read())
