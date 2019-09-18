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

from __future__ import unicode_literals
import codecs
from qgis.core import (Qgis, QgsMessageLog)


class QgisLogger(object):

    def __init__(self, plugin_name):
        self.pluginname = plugin_name

    def log(self, message, level=Qgis.Info):
        QgsMessageLog.logMessage(
            '{}'.format(message),
            self.pluginname,
            level
        )

    def info(self, message):
        self.log(message, level=Qgis.Info)

    def warning(self, message):
        self.log(message, level=Qgis.Warning)

    def critical(self, message):
        self.log(message, level=Qgis.Critical)

    def log_to_file(self, message):
        with codecs.open("/tmp/metadatadblinker.log", "w", "utf-8") as log:
            log.write(message)
