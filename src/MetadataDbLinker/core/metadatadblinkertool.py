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
from qgis.PyQt import QtSql
from qgis.core import QgsDataSourceUri
from ..config.settings import Settings
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
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': True
        },
        'name': {
            'type': 'varchar',
            'label': 'Name',
            'required': False,
            'editable': True,
            'is_shown': True
            
        },
        'description': {
            'type': 'varchar',
            'label': 'Description',
            'required': False,
            'editable': True,
            'is_shown': True
        },
        'kle_no': {
            'label': 'KLE-numbering',
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': True
        },
        'responsible': {
            'label': 'Responsible Center or Employee',
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': True
        },
        'project': {
            'label': 'Project',
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': True
        },
        'host': {
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': False
        },
        'db': {
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': False
        },
        'port': {
            'type': 'int',
            'required': False,
            'editable': True,
            'is_shown': False
        },
        'schema': {
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': False
        },
        'sourcetable': {
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': False
        },
        'ts_timezone': {
            'label': 'Date',
            'type': 'varchar',
            'required': False,
            'editable': True,
            'is_shown': False
        },
        'geodatainfo_uuid': {
            'label': 'Geodata-info UUID',
            'type': 'uuid',
            'required': False,
            'editable': True,
            'is_shown': True
        },
        
    }

    field_order = [
        'name',
        'description',
        'kle_no',
        'ts_timezone',
        'responsible',
        'geodatainfo_uuid',
        'project'
    ]

    def __init__(self):
        """
        Constructor.
        Connects to the QGIS settings.
        """
        self.plugin_metadata = plugin_metadata()
        self.logger = QgisLogger(self.plugin_metadata['name'])
        self.settings = Settings()

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
        try:
            db.setHostName(self.settings.value("host"))
            db.setPort(int(self.settings.value("port")))
            db.setDatabaseName(self.settings.value("database"))
            db.setUserName(self.settings.value("username"))
            db.setPassword(self.settings.value("password"))
        except ValueError:
            raise RuntimeWarning("Could not set database connection, missing settings")


        return db

    def get_table(self):
        return self.settings.value("sourcetable")

    def get_gui_table(self):
        # TODO: implement settings value
        return "gui_table"

    def get_schema(self):
        return self.settings.value("schema")

    # As far as i can tell, this function is never used
    # TODO: look into creating a button in the settings menu to call this method
    def create_metadata_table(self, db):
        """
        Creates the table to store metadata.
        :return:
        """

        uri = QgsDataSourceUri(db.publicUri())
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

    def format_fields_to_lists(self, data, formatting='bind'):
        fields_bind = []
        fields = []
        for field in list(data):
                fields_bind.append(':{}'.format(field))
                fields.append("{}".format(field))

        return fields_bind, fields

    def insert(self, data={}):
        """
        :param data:
        :return:
        """

        db = self.get_db()

        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

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

        self.logger.info(query.boundValues())

        if not query.exec_():
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
            
            try:                
                d_type = self.field_def.get(k).get("type")
            except Exception: # TODO: handle additional_fields
                continue
               # d_type = 'varchar'
            flds.append(self._quote(k))
            if d_type in ['varchar']:
                vls.append(
                    self._single_quote(
                        data.get(k)
                    )
                )
            elif d_type in ['uuid']:
                if len(data.get(k)) == 0 or data.get(k) == "NULL":
                    vls.append(data.get(k)) # Dont single quote
                else:
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
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError(query.lastError().text().split("\n")[0])
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

        # Add in valid additional fields when selecting
        flds = (list(self.field_def) + list(self.get_additional_fields().keys()))

        if "metadata_odk_guid" in flds:
            flds.remove("metadata_odk_guid")

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
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to select data: ' + query.lastError().databaseText().split("\n")[0])
        else:
            while query.next():
                r = {}
                for index in range(len(flds)):
                    r[flds[index]] = query.value(index)
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
        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

        query = QtSql.QSqlQuery(db)
        if not query.exec_(s):
            self.logger.critical(query.lastError().text())
            raise RuntimeError('Failed to delete data. ' + query.lastError().databaseText().split("\n")[0])
        db.commit()
        db.close()


    def validate_structure(self):
        """
        Returns true if all field names are contained in the table.
        Does not check the type of the fields. 

        For any additional_fields checks the gui_table to see if they are defined there.
        
        Runs first metadata dialog is opened

        Returns:
            bool
        """

        fld_names = list(self.field_def)
        if "metadata_odk_guid" in fld_names:
            fld_names.remove("metadata_odk_guid")
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
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            raise Exception(db.lastError().text().split("\n")[0])

        query = QtSql.QSqlQuery(db)

        if query.exec_(s):
            while query.next():
                f = query.value(0)
                try:
                    fld_names.remove(f)
                except:
                    pass
            
            return len(fld_names) == 0

        raise Exception('Could not get metadata table or schema information')

    def validate_gui_table(self):
        
        db = self.get_db()
        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            raise Exception(db.lastError().text())
        # check if the gui_table exists
        query = QtSql.QSqlQuery(db)
        s = """
            SELECT
              id, metadata_col_name, type, required, editable, is_shown
            FROM
              {schema}.{table}
            """.format(
                table=self.get_gui_table(),
                schema=self.get_schema()
        )

        if query.exec_(s):
            while query.next():
                f = query.value(1)
                if not f or f is "":
                    raise Exception('Column "metadata_col_name" was empty, check gui_table configuration')
        else:
            raise Exception('Could not access gui_table \n' + str(query.lastError().text()))

        return True

        

    def get_field_def_properties(self):
        """
        Returns:
            dict (key,bool)
        """
        field_def_properties = self.get_field_def()
        try:
            db = self.get_db()
        except RuntimeWarning as e:
            self.logger.critical('Unable to connect to database.')
            raise Exception(str(e))

        if not db.open():
            self.logger.critical('Unable to connect to database.')
            self.logger.critical(db.lastError().text())
            raise Exception('Unable to connect to database.')

        # check if the table exists
        query = QtSql.QSqlQuery(db)
        s = """
            SELECT
              metadata_col_name, required, editable, is_shown
            FROM
              {schema}.{table}
            WHERE is_shown
            """.format(
                table=self.get_gui_table(),
                schema=self.get_schema()
        )
        if query.exec_(s):
            while query.next():
                row = query
                try:
                    field_def_properties[row.value(0)]["required"] = row.value(1)
                    field_def_properties[row.value(0)]["editable"] = row.value(2)
                    field_def_properties[row.value(0)]["is_shown"] = row.value(3)
                except:
                    if row.value(0) == 'metadata_odk_guid': # ODENSE SPECIFIC
                        field_def_properties[row.value(0)] = {
                            "required": row.value(1),
                            "editable": row.value(2),
                            "is_shown": row.value(3),
                            "type": "uuid"
                        }
                    else: # If extra_field are ever to implemented they should be added here instead of passing
                        pass

        return field_def_properties

    def get_additional_fields(self):
        """
        Returns: list of str
        """
        # get all extra fields that are described in gui_table, exists in metadata table and is classified as an extra_field
        db = self.get_db()
        
        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return False

        # TODO: combine into one query

        # check if the table exists
        query = QtSql.QSqlQuery(db)
        s1 = """
        SELECT * FROM 
            (SELECT column_name FROM information_schema.columns
             WHERE table_name = '{metatable}'
             AND table_schema='{schema}') as t1
        WHERE EXISTS
            (SELECT metadata_col_name 
             FROM {schema}.{guitable} as t2 WHERE t2.metadata_col_name = t1.column_name and t2.extra_field)
        """.format(
                metatable=self.get_table(),
                guitable=self.get_gui_table(),
                schema=self.get_schema()
        )
        extra_fields = []
        if query.exec_(s1):
            while query.next():
                extra_fields.append(query.value(0))

        # Build properties for the extra fields
        s2 = """
        SELECT metadata_col_name, required, editable, type, displayname, is_shown
        FROM {schema}.{guitable}
        WHERE is_shown
        """.format(
                guitable=self.get_gui_table(),
                schema=self.get_schema()
        )
        extra_fields_properties = {}

        if query.exec_(s2):
            while query.next():
                if query.value(0) in extra_fields:
                    extra_fields_properties[query.value(0)] = {
                        "required": query.value(1),
                        "editable": query.value(2),
                        "type": query.value(3),
                        "displayname": query.value(4),
                        "is_shown": query.value(5)
                    }

        return extra_fields_properties

    #### These methods relate to extra_fields not described in field_def
    def select_extra_fields(self):
        pass