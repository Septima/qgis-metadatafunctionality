# This is an example of how to make your plugin searchable through septima search
# Your plugin MUST have an attribute 'SeptimaSearchProvider' with this signature
# Example: self.SeptimaSearchProvider = MySeptimaSearchProvider()

from PyQt4 import (
    QtCore,
    QtSql
)
from qgis.core import (
    QgsMessageLog,
    QgsDataSourceURI
)

import json
from ..core import MetadataDbLinkerTool

class MySeptimaSearchProvider(QtCore.QObject):
    
    def __init__(self, iface):
        # Mandatory because your search provider MUST extend QtCore.QObject
        QtCore.QObject.__init__(self)
        # Do other initialization here
        self.db_tool = MetadataDbLinkerTool()
        self.iface = iface


    # Mandatory slot        
    @QtCore.pyqtSlot(str, int, result=str)
    def query(self, query, limit):
        db = self.db_tool.get_db()

        # Check if we can open the database
        if not db.open():
            self.logger.critical('Unable to open database.')
            self.logger.critical(db.lastError().text())
            return

        sql_count = '''
            SELECT COUNT(1) FROM {schema}._getMetaDataMatches('{query}');
        '''.format(
            schema=self.db_tool.get_schema(),
            query=query
        )

        q = QtSql.QSqlQuery(db)

        metadata_count = None

        if not q.exec_(sql_count):
            self.logger.critical('Failed to get count.')
            self.logger.critical(q.lastError().text())
            return
        else:
            while q.next():
                metadata_count = q.value(0)

        sql = '''
            SELECT * FROM {schema}._getMetaDataMatches('{query}', {limit});
        '''.format(
            schema=self.db_tool.get_schema(),
            query=query,
            limit=limit
        )

        search_results = []

        if not q.exec_(sql):
            self.logger.critical('Failed to select data.')
            self.logger.critical(q.lastError().text())
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

        if not metadata_count:
            return json.dumps(search_results)

        result = {}
        result['status'] = 'ok'
        result['hits'] = metadata_count
        result['results'] = search_results

        return json.dumps(result)
    # Mandatory        
    def definition(self):
        # Return basic information about your self
        # iconURI is any valid URI, including a data URL:
        # eg.: {'singular': 'school', 'plural': 'school' [, 'iconURI': iconurl]} 
        return    {
            'singular': 'Tabel',
            'plural': 'Tabeller',
            'iconURI': "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4iICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmVyc2lvbj0iMS4xIiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTQsM0gyMEEyLDIgMCAwLDEgMjIsNVYyMEEyLDIgMCAwLDEgMjAsMjJINEEyLDIgMCAwLDEgMiwyMFY1QTIsMiAwIDAsMSA0LDNNNCw3VjEwSDhWN0g0TTEwLDdWMTBIMTRWN0gxME0yMCwxMFY3SDE2VjEwSDIwTTQsMTJWMTVIOFYxMkg0TTQsMjBIOFYxN0g0VjIwTTEwLDEyVjE1SDE0VjEySDEwTTEwLDIwSDE0VjE3SDEwVjIwTTIwLDIwVjE3SDE2VjIwSDIwTTIwLDEySDE2VjE1SDIwVjEyWiIgLz48L3N2Zz4="
        }
    
    # Mandatory        
    def on_select(self, result):
        # The selected result is returned to you
        # Do your thing
        self.add_vector_layer_from_metadata(self.iface, result)
        
    def add_vector_layer_from_metadata(self, iface, result):
        #result = result['data']
        metaDataHost = self.db_tool.settings.value("host")
    
        if result['host'] != metaDataHost:
            QMessageBox.information(
                iface.mainWindow(),
                "Error in hosts",
                'Host in result from postgres isnt equal to the host in the '
                'metadata plugin settings'
            )
            return
    
        geometry_columns = self.get_geometry_columns(
            result['host'],
            result['port'],
            result['db'],
            result['schema'],
            result['table']
        )
    
        uri = QgsDataSourceURI()
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
        layer = iface.addVectorLayer(
            uri.uri(),
            result['title'],
            'postgres'
        )
        return layer
    
    
    def get_geometry_columns(self, host, port, database, schema, table):
    
        db = QtSql.QSqlDatabase.addDatabase('QPSQL')
        db.setHostName(host)
        db.setPort(int(port))
        db.setDatabaseName(database)
        db.setUserName(self.db_tool.settings.value("username"))
        db.setPassword(self.db_tool.settings.value("password"))
    
        if not db.open():
            return None
    
        q = QtSql.QSqlQuery(db)
    
        sql = '''
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
            return None
        else:
            while q.next():
                columns.append(q.value(0))
    
        return columns

