# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CreateMetadataTableDialog
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
from PyQt4 import uic
from PyQt4.QtGui import QDialog
import os

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'create_metadata_table_dialog.ui'
    )
)


class CreateMetadataTableDialog(QDialog, FORM_CLASS):

    def __init__(self, parent=None, create_func=None):
        super(CreateMetadataTableDialog, self).__init__(parent)
        self.setupUi(self)

        self.create_function = create_func
        self.accepted.connect(self.create_function)
