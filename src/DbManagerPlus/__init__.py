# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DbManagerPlus
                                 A QGIS plugin
 Adds some functionality to DB Manager
                             -------------------
        begin                : 2016-02-09
        copyright            : (C) 2016 by Asger Sigurd Skovbo Petersen, Septima
        email                : asger@septima.dk
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
    """Load DbManagerPlus class from file DbManagerPlus.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .db_manager_plus import DbManagerPlus
    return DbManagerPlus(iface)
