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

# TODO: Remove after debug phase.
from qgis.core import QgsMessageLog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'metadata_functionality_dialog_base.ui'))


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
