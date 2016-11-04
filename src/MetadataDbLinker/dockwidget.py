# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DockWidget
                                 A QGIS plugin
 This plugin lets the user browse and open qlr files
                             -------------------
        begin                : 2015-11-26
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Asger Skovbo Petersen, Septima
        email                : asger@septima.dk
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
from PyQt4.QtCore import QFileInfo, QDir, pyqtSignal, pyqtSlot, Qt, QTimer, QSettings
from qgis._gui import QgsMessageBar

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dockwidget.ui'))

class DockWidget(QtGui.QDockWidget, FORM_CLASS):
    """The DockWidget class for the Qlr Panel.
    """
    iconProvider = QtGui.QFileIconProvider()

    closingPlugin = pyqtSignal()

    itemStateChanged = pyqtSignal(object, bool)

    def __init__(self, iface=None):
        """
        Constructor.
        Sets the parent, sets up the UI and fills the tree.
        """
        parent = None if iface is None else iface.mainWindow()
        super(DockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.config = QSettings()
        self.readconfig()

        self.setupUi(self)

        self.iface = iface

