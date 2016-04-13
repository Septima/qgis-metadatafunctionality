from MetadataFunctionality import MetadataFunctionalitySettings
from db_manager.db_plugins.connector import DBConnector
from qgis.core import QgsVectorLayer, QgsDataSourceURI
from PyQt4 import QtSql

from qgis.core import QgsMessageLog

class MetaManDBTool(object):
    """
    The tool responsible for reading and writing to the database.
    """

    # The handle to the metadata table
    table = None

    field_def = {
        'guid': {
            'type': 'varchar'},
        'name':
            { 'type': 'varchar',
              'label': 'Name'},
        'beskrivelse':
            {'type': 'varchar',
             'label': 'Beskrivelse'},
        'db':
            { 'type': 'varchar'},
        'schema':{
            'type': 'varchar'},
        'table': {
            'type': 'varchar'},
        'timestamp': {
            'label': 'Dato',
            'type': 'varchar'},
        'journal_nr': {
            'label': 'Journal nr.',
            'type': 'varchar'},
        'resp_center_off': {
            'label':'Center',
            'type': 'varchar'},
        'proj_wor': {
            'label': u'projekt / WOR',
            'type': 'varchar'}
    }


    def __init__(self):
        self.settings = MetadataFunctionalitySettings()
        self.conn_info = self.settings.value("conn_info")
        self.table = self.settings.value("table_name")
        self.connect()

    def get_field_def(self):
        return self.field_def

    def _quote(self, s):
        return '"%s"' % s

    def _single_quote(self, s):
        return "'%s'" % s

    def connect(self):
        conn = DBConnector(self.conn_info)
        # self.table = QgsVectorLayer(self.conn_info, self.table, "postgres")

    def _create_db_creation_statement(self):
        """
        Creates the create table SQL statement.
        :return:
        """

        b = [self._quote(f) + ' ' + self.field_def.get(f).get('type') for f in list(self.field_def)]

        return 'CREATE TABLE %s (%s)' % (self.table, ",".join(b))

    def get_db(self):
        """
        Returns a database object from the settings in the config.
        :return:
        """

        uri = QgsDataSourceURI(self.conn_info)

        db = QtSql.QSqlDatabase.addDatabase('QPSQL')

        db.setHostName(uri.host())
        db.setPort(int(uri.port()))
        db.setDatabaseName(uri.database())
        db.setUserName(uri.username())
        db.setPassword(uri.password())

        return db

    def create_metaman_table(self, db):
        """
        Creates the metaman table.
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

        db.open()

        s = self._create_db_creation_statement()

        if not query.exec_(s):
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
                # vls.append(self._quote(str(data.get(k))))
                vls.append(self._single_quote(str(data.get(k)).replace('"', '\\"').replace("'", "''")))

            else:
                vls.append(str(data.get(k)))

        s = 'INSERT INTO %s (%s) VALUES (%s)' % (self.table, ','.join(flds), ','.join(vls))

        db.open()

        query = QtSql.QSqlQuery(db)

        if not query.exec_(s):
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
                vls.append(self._single_quote(str(data.get(k)).replace('"', '\\"').replace("'", "''")))

            else:
                vls.append(str(data.get(k)))

        s = 'UPDATE %s SET (%s) = (%s) WHERE guid=%s' % (self.table, ','.join(flds), ','.join(vls), self._single_quote(data.get('guid')));

        QgsMessageLog.logMessage(s)

        db = self.get_db()
        db.open()
        query = QtSql.QSqlQuery(db)
        result = query.exec_(s)
        if not result:
            raise RuntimeError('Failed to udpate data.')
        db.commit()
        db.close()

    def select(self, d={}):
        """
        Returns records as a list of dicts: [{<field1>: <value1>, <field2>: value2,..}, {...}, ...]
        :param d:
        :return:
        """
        c = []
        results = []

        for k in list(d):
            if self.field_def.get(k).get("type") in ['varchar']:
                c.append("%s=%s" % (self._quote(k), self._single_quote((d.get(k)).replace('"', '\\"').replace("'", "''"))))

        flds = [self._quote(f) for f in list(self.field_def)]
        s = 'SELECT %s FROM %s WHERE %s' % (','.join(flds), self.table, ' AND '.join(c))
        db = self.get_db()
        db.open()
        query = QtSql.QSqlQuery(db)
        result = query.exec_(s)
        if not result:
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

        d = {'blabla': 1} -> DELETE FROM foo where blabla = 1;

        :param d:
        :return:
        """

        c = []

        for k in list(d):
            if self.field_def.get(k).get("type") in ['varchar']:
                c.append(
                    "%s=%s" % (self._quote(k), self._single_quote((d.get(k)).replace('"', '\\"').replace("'", "''"))))

        flds = [self._quote(f) for f in list(self.field_def)]

        s = 'DELETE FROM %s WHERE %s' % (self.table, ' AND '.join(c))

        db = self.get_db()
        db.open()
        query = QtSql.QSqlQuery(db)
        result = query.exec_(s)
        if not query.exec_(s):
            raise RuntimeError('Failed to delete data.')
        db.commit()
        db.close()

    def validate_structure(self, db_conn, table):
        """
        Returns true if all field names are contained in the table.
        Does not check the type of the fields. TODO: implement
        :return:
        """

        fld_names = list(self.field_def)

        s = "SELECT column_name FROM information_schema.columns WHERE table_name = '%s'" % table

        uri = QgsDataSourceURI(db_conn)

        db = QtSql.QSqlDatabase.addDatabase('QPSQL')

        db.setHostName(uri.host())
        db.setPort(int(uri.port()))
        db.setDatabaseName(uri.database())
        db.setUserName(uri.username())
        db.setPassword(uri.password())

        db.open()

        query = QtSql.QSqlQuery(db)
        result = query.exec_(s)
        if not result:
            raise RuntimeError('Failed to select data.')
        else:
            while query.next():
                f = query.value(0)
                try:
                    fld_names.remove(f)
                except:
                    return False

            return len(fld_names) == 0