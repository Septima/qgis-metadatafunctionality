# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2016-04-04
        copyright            : (C) 2016 by Septima P/S
        email                : stephan@septima.dk
        git sha              : $Format:%H$
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

from qgis.core import QgsMessageLog


class QgisLogger(object):

    def __init__(self, plugin_name):
        self.pluginname = plugin_name

    def log(self, message, level=QgsMessageLog.INFO):
        QgsMessageLog.logMessage(
            '{}'.format(message),
            self.pluginname,
            level
        )

    def info(self, message):
        self.log(message, level=QgsMessageLog.INFO)

    def warning(self, message):
        self.log(message, level=QgsMessageLog.WARNING)

    def critical(self, message):
        self.log(message, level=QgsMessageLog.CRITICAL)
