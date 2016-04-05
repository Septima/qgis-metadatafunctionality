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

from PyQt4.QtCore import QSettings

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MetadataFunctionality class from file MetadataFunctionality.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .metadata_functionality import MetadataFunctionality
    return MetadataFunctionality(iface)

class MetaDataFunctionalitySettings(object):
    """
    The central config object
    """

    GROUP_ID = 'MetadataFunctionality'

    data = {}

    fields = {
        'table_name': {
            'default': 'metadata',
            'type': str
        },
        'db_path': {
            'default': '',
            'type': str
        },
        'db_name': {
            'default': '',
            'type': str
        }
    }

    def __init__(self):
        """
        We create the keys if they are not there and load the keys that are there into self.data
        """

        self.settings = QSettings()

        for field_name in self.fields.keys():
            v = self.settings.value('/%s/%s' % (self.GROUP_ID, field_name), None, self.fields.get(field_name).type)
            if not v:
                self.settings.setValue('/%s/%s' % (self.GROUP_ID, field_name), self.fields.get(field_name).default, self.fields.get(field_name).t)
            else:
                self.data.get[field_name] = self.settings.value('/%s/%s' % (self.GROUP_ID, field_name))

    def field_names(self):
        """
        Returns the field names as a list.
        """
        return self.fields.keys()

    def data_names(self):
        """
        Returns the field names of the data.
        """
        return self.data.keys()

    def value(self, field_name):
        """
        Returns the value of the field given by field_name
        :field_name the name of the field (str)
        """
        if field_name in self.field_names() and field_name in self.data_names():
            return self.data.get(field_name)