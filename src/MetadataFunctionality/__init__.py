# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataFunctionality
                                 A QGIS plugin
 MetadataFunctionality
                             -------------------
        begin                : 2016-04-04
        copyright            : (C) 2016 by Bernhard Snizek (Septima P/S)
        email                : bernhard@septima.dk
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
 This script initializes the plugin, making it known to QGIS.
"""

from .qgissettingmanager import SettingManager


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MetadataFunctionality class from file MetadataFunctionality.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .metadata_functionality import MetadataFunctionality
    return MetadataFunctionality(iface)

pluginName = "MetaMan"


class MetadataFunctionalitySettings(SettingManager):

    def __init__(self):
        SettingManager.__init__(self, pluginName)
        self.addSetting("host", "string", "global", "")
        self.addSetting("database", "string", "global", "")
        self.addSetting("port", "string", "global", "")
        self.addSetting("schema", "string", "global", "public")
        self.addSetting("table", "string", "global", "metaman")
        self.addSetting("username", "string", "global", "")
        self.addSetting("password", "string", "global", "")
