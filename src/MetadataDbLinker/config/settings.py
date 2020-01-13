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
import sys
from .qgissettingmanager import (
    SettingManager,
    String,
    Scope
)
from qgis.PyQt import QtCore

class Settings(SettingManager):
    settings_updated = QtCore.pyqtSignal()

    def __init__(self):
        SettingManager.__init__(self, 'Metadata-DB-Linker')
        self.add_setting(String('host', Scope.Global, ''))
        self.add_setting(String('database', Scope.Global, ''))
        self.add_setting(String('port', Scope.Global, ''))
        self.add_setting(String('schema', Scope.Global, 'public'))
        self.add_setting(String('sourcetable', Scope.Global, ''))
        self.add_setting(String('username', Scope.Global, ''))
        self.add_setting(String('password', Scope.Global, ''))
        self.add_setting(String('taxonUrl', Scope.Global, ''))
        self.add_setting(String('taxonTaxonomy', Scope.Global, ''))

    def verify_settings_set(self):
        errors = ''
        if not self.value('host'):
            errors += '{}\n'.format('Missing host in settings')
        if not self.value('port'):
            errors += '{}\n'.format('Missing port in settings')
        if not self.value('database'):
            errors += '{}\n'.format('Missing database in settings')
        if not self.value('schema'):
            errors += '{}\n'.format('Missing schema in settings')
        if not self.value('sourcetable'):
            errors += '{}\n'.format('Missing table in settings')
        if not self.value('username'):
            errors += '{}\n'.format('Missing username in settings')
        if not self.value('password'):
            errors += '{}\n'.format('Missing password in settings')

        if errors:
            return errors

        return None

    def emit_updated(self):
        self.settings_updated.emit()
