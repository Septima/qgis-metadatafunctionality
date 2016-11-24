# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2016-11-16
        copyright            : (C) 2016 by Septima P/S
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
"""
from __future__ import unicode_literals
from PyQt4 import QtSql
from .. import MetadataDbLinkerSettings
from .qgislogger import QgisLogger
from .pluginmetadata import plugin_metadata


class MetadataDatabaseTool(object):
    """ The tool responsible for communicating with the database.

    Throws:
        RuntimeError if insert/delete/update fails
        DatabaseConnectionError if connection to database fails
        DatabaseInconsistencyError if the table differs from the expected
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
        """ Initialize the  """
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
        """ Creates the create table SQL statement. """

        b = [
            self._quote(f) + ' ' + self.field_def.get(f).get('type') for f in list(self.field_def)
        ]
        return 'CREATE TABLE "%s"."%s" (%s)' % (
            self.get_schema(),
            self.get_table(),
            ",".join(b)
        )

    def get_db(self):
        """ Returns a database object from the settings in the config. """

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

    def create_metadata_table(self):
        """ Creates the table to store metadata. """

        db = self.get_db()
        if not db.open():
            raise DatabaseConnectionError(db.lastError().text())

        query = QtSql.QSqlQuery(db)
        sql_statement = self._create_db_creation_statement()

        if not query.exec_(sql_statement):
            raise RuntimeError("{type}: {text}".format(
                    type=db.lastError().type(),
                    text=db.lastError().text()
                )
            )

        db.commit()
        db.close()

    def format_fields_to_lists(self, data, formatting='bind'):
        fields_bind = []
        fields = []
        for field in list(data):
                fields_bind.append(':{}'.format(field))
                fields.append("{}".format(field))

        return fields_bind, fields

    def insert(self, data={}):
        """ Inserts into the database. Raises RuntimeError. """
        db = self.get_db()

        if not db.open():
            raise DatabaseConnectionError(db.lastError().text())

        # prepare query
        query = QtSql.QSqlQuery(db)
        bind_fields, quoted_fields = self.format_fields_to_lists(data)
        query.prepare(
            """
            INSERT INTO "{schema}"."{table}" ({fields}) VALUES ({binds})
            """.format(
                schema=self.get_schema(),
                table=self.get_table(),
                fields=','.join(quoted_fields),
                binds=','.join(bind_fields)
            )
        )

        for k in list(data):
            query.bindValue(
                ':{}'.format(k),
                data.get(k)
            )

        if not query.exec_():
            raise RuntimeError(
                'Failed to insert data: {}'.format(db.lastError().text())
            )

        db.commit()
        db.close()

    def update(self, data={}):
        """ Updates a record in the database. Raises RuntimeError. """

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
        if not db.open():
            raise DatabaseConnectionError(db.lastError().text())

        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            raise RuntimeError(
                'Failed to update data: {}'.format(db.lastError().text())
            )

        db.commit()
        db.close()

    def select(self, d, order_by={}):
        """ Returns records as a list of dicts:
            [{<field1>: <value1>, <field2>: value2,..}, {...}, ...]
            Raises RuntimeError.
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
        if not db.open():
            raise DatabaseConnectionError(db.lastError().text())

        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            raise RuntimeError(
                'Failed to select data: {}'.format(query.lastError().text())
            )
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
        """ Deletes from the table given criteria as a dict.
                d = {'sometext': 1} -> DELETE FROM foo where sometext = 1;
            Raises RuntimeError.
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

        s = 'DELETE FROM "%s"."%s" WHERE %s' % (
            self.get_schema(),
            self.get_table(),
            ' AND '.join(c)
        )

        db = self.get_db()
        if not db.open():
            raise DatabaseConnectionError(db.lastError().text())

        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            raise RuntimeError(
                'Failed to delete data: {}'.format(db.lastError().text())
            )

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
              table_name = '{table}'
            AND
              table_schema='{schema}';
            """.format(
                table=self.get_table(),
                schema=self.get_schema()
        )

        if not db.open():
            raise DatabaseConnectionError(db.lastError().text())

        query = QtSql.QSqlQuery(db)

        if query.exec_(s):
            result = query.next()
            if not result:
                print(db.lastError().type())
                print(db.lastError().text())
                raise DatabaseInconsistencyError()

            while result:
                f = query.value(0)
                try:
                    fld_names.remove(f)
                except:
                    pass
                result = query.next()

            db.close()

            if len(fld_names) == 0:
                return True

            raise DatabaseConnectionError()

        db.close()
        raise DatabaseInconsistencyError()


# Definition of custom exceptions to catch for when using the db tool.
class DatabaseConnectionError(Exception):
    def __init__(self, message):
        self.message = 'Unable to open database: {}'.format(message)

    def __str__(self):
        return self.message


class DatabaseInconsistencyError(Exception):
    def __init__(self):
        self.message = 'Fields in database are not as expected.'

    def __str__(self):
        return self.message
