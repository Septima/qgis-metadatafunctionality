# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2016-04-04
        copyright            : (C) 2016 by Septima P/S
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
"""
from __future__ import unicode_literals
from PyQt4 import QtSql
from qgis.core import QgsDataSourceURI
from .. import MetadataDbLinkerSettings
from .qgislogger import QgisLogger
from .pluginmetadata import plugin_metadata


class MetadataDbLinkerTool(object):
    """
    The tool responsible for reading and writing to the database.
    """

    # The handle to the metadata table
    table = None

    field_def = {
        'guid': {
            'type': 'varchar'
        },
        'name': {
            'type': 'varchar',
            'label': 'Name'
        },
        'description': {
            'type': 'varchar',
            'label': 'Description'
        },
        'kle_no': {
            'label': 'KLE-numbering',
            'type': 'varchar'
        },
        'responsible': {
            'label': 'Responsible Center or Employee',
            'type': 'varchar'
        },
        'project': {
            'label': 'Project',
            'type': 'varchar'
        },
        'host': {
            'type': 'varchar'
        },
        'db': {
            'type': 'varchar'
        },
        'port': {
            'type': 'int'
        },
        'schema': {
            'type': 'varchar'
        },
        'sourcetable': {
            'type': 'varchar'
        },
        'ts_timezone': {
            'label': 'Date',
            'type': 'varchar'
        },
    }

    field_order = [
        'name',
        'description',
        'kle_no',
        'ts_timezone',
        'responsible',
        'project'
    ]

    def __init__(self):
        """
        Constructor.
        Connects to the QGIS settings.
        """
        self.plugin_metadata = plugin_metadata()
        self.logger = QgisLogger(self.plugin_metadata['name'])
        self.settings = MetadataDbLinkerSettings()

    def get_field_def(self):
        return self.field_def

    def _quote(self, s):
        return '"%s"' % s

    def _single_quote(self, s):
        return "'%s'" % s

    def _create_db_creation_statement(self):
        """
        Creates the create table SQL statement.
        :return:
        """

        b = [
            self._quote(f) + ' ' + self.field_def.get(f).get('type') for f in list(self.field_def)
        ]
        return 'CREATE TABLE "%s"."%s" (%s)' % (
            self.get_schema(),
            self.get_table(),
            ",".join(b)
        )

    def get_db(self):
        """
        Returns a database object from the settings in the config.
        :return:
        """

        db = QtSql.QSqlDatabase.addDatabase('QPSQL')
        db.setHostName(self.settings.value("host"))
        db.setPort(int(self.settings.value("port")))
        db.setDatabaseName(self.settings.value("database"))
        db.setUserName(self.settings.value("username"))
        db.setPassword(self.settings.value("password"))

        return db

    def get_table(self):
        return self.settings.value("sourcetable")

    def get_schema(self):
        return self.settings.value("schema")

    def create_metadata_table(self, db):
        """
        Creates the table to store metadata.
        :return:
        """

        uri = QgsDataSourceURI(db.publicUri())
        db = QtSql.QSqlDatabase.addDatabase('QPSQL')
        db.setHostName(uri.host())
        db.setPort(int(uri.port()))
        db.setDatabaseName(uri.database())
        db.setUserName(uri.username())
        db.setPassword(uri.password())
        query = QtSql.QSqlQuery(db)

        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

        s = self._create_db_creation_statement()

        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to create database')

        db.commit()
        db.close()

    def insert(self, data={}):
        """
        :param data:
        :return:
        """

        db = self.get_db()

        flds = []
        vls = []

        for k in list(data):

            flds.append(self._quote(k))

            if self.field_def.get(k).get("type") in ['varchar']:
                vls.append(
                    self._single_quote(
                        data.get(k)
                    )
                )

            else:
                vls.append(data.get(k))

        s = 'INSERT INTO "%s"."%s" (%s) VALUES (%s)' % (
            self.get_schema(),
            self.get_table(),
            ','.join(flds),
            ','.join(vls)
        )

        db.open()

        query = QtSql.QSqlQuery(db)

        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to insert data.')

        db.commit()
        db.close()

    def update(self, data={}):
        """
        Update a record.
        :param d:
        :return:
        """

        db = self.get_db()

        flds = []
        vls = []

        for k in list(data):

            flds.append(self._quote(k))

            if self.field_def.get(k).get("type") in ['varchar']:
                vls.append(
                    self._single_quote(
                        data.get(k)
                    )
                )

            else:
                vls.append(data.get(k))

        s = 'UPDATE "%s"."%s" SET (%s) = (%s) WHERE guid=%s' % (
            self.get_schema(),
            self.get_table(),
            ','.join(flds),
            ','.join(vls),
            self._single_quote(data.get('guid'))
        )
        db = self.get_db()
        db.open()
        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to update data.')
        db.commit()
        db.close()

    def select(self, d, order_by={}):
        """
        Returns records as a list of dicts:
            [{<field1>: <value1>, <field2>: value2,..}, {...}, ...]
        :param d:
        :return:
        """

        c = []
        results = []

        for k in list(d):
            if self.field_def.get(k).get("type") in ['varchar']:
                c.append(
                    "%s=%s" % (
                        self._quote(k),
                        self._single_quote((d.get(k)))
                    )
                )

        flds = [self._quote(f) for f in list(self.field_def)]
        s = 'SELECT %s FROM "%s"."%s" WHERE %s' % (
            ','.join(flds),
            self.get_schema(),
            self.get_table(),
            ' AND '.join(c)
        )

        if order_by != {}:
            s += ' ORDER BY %s %s' % (
                order_by.get('field'),
                order_by.get('direction')
            )

        db = self.get_db()
        db.open()
        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to select data.')
        else:
            while query.next():
                r = {}
                for index in range(len(list(self.field_def))):
                    r[list(self.field_def)[index]] = query.value(index)
                results.append(r)

        db.commit()
        db.close()
        return results

    def delete(self, d={}):
        """
        Deletes from the table given criteria as a dict.

        d = {'sometext': 1} -> DELETE FROM foo where sometext = 1;

        :param d:
        :return:
        """

        c = []

        for k in list(d):
            if self.field_def.get(k).get("type") in ['varchar']:
                c.append(
                    "%s=%s" % (
                        self._quote(k),
                        self._single_quote((d.get(k)))
                    )
                )

        # TODO: Figure out what the jebus this is
        # flds = [
            # self._quote(f) for f in list(self.field_def)
        # ]

        s = 'DELETE FROM "%s"."%s" WHERE %s' % (
            self.get_schema(),
            self.get_table(),
            ' AND '.join(c)
        )

        db = self.get_db()
        db.open()
        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to delete data.')
        db.commit()
        db.close()

    def validate_structure(self):
        """
        Returns true if all field names are contained in the table.
        Does not check the type of the fields. TODO: implement
        :return:
        """

        fld_names = list(self.field_def)
        db = self.get_db()

        s = """
            SELECT
              column_name
            FROM
              information_schema.columns
            WHERE
              table_name = '%s'
            AND
              table_schema='%s';
            """ % (
                self.get_table(),
                self.get_schema()
        )

        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

        query = QtSql.QSqlQuery(db)

        if query.exec_(s):
            while query.next():
                f = query.value(0)
                try:
                    fld_names.remove(f)
                except:
                    pass

            return len(fld_names) == 0

        return False
