# -*- coding: utf-8 -*-
from qgis.core import QgsLocatorFilter, QgsLocatorResult, QgsDataSourceUri
from .core.metadatadblinkertool import MetadataDbLinkerTool
from .core.qgislogger import QgisLogger
from qgis.PyQt import (
    QtCore,
    QtSql
)

class LayerLocatorFilter(QgsLocatorFilter):
    def __init__(self, iface, data=None):
        super(LayerLocatorFilter, self).__init__()
        if data is None:
            self.data = LayerLocatorFilterData(iface)
        else:
            self.data = data
        self.iface = iface
        self.logger = QgisLogger('Metadata-DB-linker')

    def clone(self):
        return LayerLocatorFilter(self.iface,data=self.data)

    def name(self):
        return "MetadataDbLinker"

    def displayName(self):
        return self.tr("Metadata-DB-Linker")

    def priority(self):
        return QgsLocatorFilter.Low

    def prefix(self):
        return "MetadataDbLinker"

    def flags(self):
        return QgsLocatorFilter.FlagFast

    def fetchResults(self, query, context, feedback):
        matching_layers = self.data.fetch_matching_layers(query)
        for layer in matching_layers["results"]:
            result = QgsLocatorResult()
            result.filter = self
            result.displayString = " ".join((layer["title"], "(Metadata)"))
            result.userData = layer
            result.score = 0

            self.resultFetched.emit(result)


    def triggerResult(self, result):
        uri = self.data.get_vector_layer_from_metadata(result)

        if uri is None:
            self.logger.critical('Could not add result to canvas!')
            return None

        self.iface.addVectorLayer(
            uri.uri(),
            result.userData['title'],
            'postgres'
        )

class LayerLocatorFilterData:
    def __init__(self,iface):
        self.db_tool = MetadataDbLinkerTool()
        self.logger = QgisLogger('Metadata-DB-linker')
        self.iface = iface

    # Searches the database with the given query
    def fetch_matching_layers(self,query):
        db = self.db_tool.get_db()
        if not(self._test_db_connection(db)):
            return
        
        sql_count = u'select count(1) from ({from_clause}) xxx'.format(from_clause= self._get_from_clause(query))
        q = QtSql.QSqlQuery(db)

        metadata_count = None

        if not q.exec_(sql_count):
            self.logger.critical('Failed to get count.')
            self.logger.critical(q.lastError().text())
            return
        else:
            while q.next():
                metadata_count = q.value(0)

        sql = u'select xxx.* from ({from_clause}) xxx'.format(from_clause=self._get_from_clause(query))

        search_results = []

        if not q.exec_(sql):
            self.logger.critical('Failed to select data.')
            sql_error = q.lastError().text()
            self.logger.critical(sql_error)
            return
        else:
            while q.next():
                search_results.append(
                    {
                        'title': q.value(0),
                        'description': q.value(1),
                        'geometry': None,
                        'host': q.value(2),
                        'db': q.value(3),
                        'port': q.value(4),
                        'schema': q.value(5),
                        'table': q.value(6)
                    }
                )

        result = {}
        result['hits'] = metadata_count
        result['results'] = search_results

        return result

    def get_vector_layer_from_metadata(self, result):
        result = result.userData
        geometry_columns = self._get_geometry_columns(
            result['host'],
            result['port'],
            result['db'],
            result['schema'],
            result['table']
        )

        if geometry_columns is None or len(geometry_columns) < 1:
            self.logger.critical('Could not get geometry!')
            return None

        uri = QgsDataSourceUri()
        # set host, port, database name, username and password
        uri.setConnection(
            result['host'],
            str(result['port']),
            result['db'],
            self.db_tool.settings.value("username"),
            self.db_tool.settings.value("password")
        )
        # set schema, table and geometry column
        uri.setDataSource(
            result['schema'],
            result['table'],
            geometry_columns[0]
        )
        return uri

    def _test_db_connection(self,db):
        # Check if we can open the database
        if not db.open():
            self.logger.critical('Unable to open database in Locator.')
            self.logger.critical(db.lastError().text())
            return False
        else:
            return True
    
    def _get_geometry_columns(self, host, port, database, schema, table):

        db = QtSql.QSqlDatabase.addDatabase('QPSQL')
        db.setHostName(host)
        db.setPort(int(port))
        db.setDatabaseName(database)
        db.setUserName(self.db_tool.settings.value("username"))
        db.setPassword(self.db_tool.settings.value("password"))

        if not db.open():
            return None

        q = QtSql.QSqlQuery(db)

        sql = u'''
            SELECT
              f_geometry_column
            FROM
              geometry_columns
            WHERE
              f_table_catalog = '{database}'
              and f_table_schema = '{schema}'
              and f_table_name = '{table}';
        '''.format(
            database=database,
            schema=schema,
            table=table
        )

        columns = []

        if not q.exec_(sql):
            self.iface.messageBar().pushMessage("Error", q.lastError().text(), level=2)
            return None
        else:
            while q.next():
                columns.append(q.value(0))

        return columns
        
    def _get_from_clause(self,query):
        return u'''
        WITH QUERY AS (
            SELECT '{query}'::text AS VALUE
        ),
        st AS (
            SELECT REGEXP_SPLIT_TO_TABLE(value, ' ') search_token
            FROM QUERY
        )
        SELECT
        name,
        description,
        host,
        db,
        port,
        schema,
        sourcetable
        FROM {schema}.{table} m1
        WHERE NOT EXISTS
        (
            SELECT *
            FROM st
            WHERE NOT EXISTS
            (
                SELECT 1
                FROM {schema}.{table} m2
                WHERE
                (
                m2.responsible ILIKE search_token
                OR m2.description ILIKE search_token || '%' -- Matches beginning of word in string
                OR m2.description ILIKE '% ' || search_token || '%' -- Matches word embedded in string
                OR m2.name ILIKE search_token || '%'
                OR m2.name ILIKE '% ' || search_token || '%'
                OR m2.db ILIKE search_token
                OR m2.sourcetable ILIKE search_token || '%'
                OR m2.project ILIKE search_token || '%'
                OR 'metadata' ILIKE search_token || '%'
                )
            AND m1.guid = m2.guid
            )
        )
        '''.format(
            schema=self.db_tool.get_schema(),
            table=self.db_tool.get_table(),
            query=query
        )