# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataDBlinker
                                 A QGIS plugin
 MetadataDBlinker
                             -------------------
        begin                : 2016-04-04
        copyright            : (C) 2016 Septima P/S
        email                : kontakt@septima.dk
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

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MetadataDbLinker class from file metadata_db_linker.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .metadata_db_linker import MetadataDbLinker
    return MetadataDbLinker(iface)