import psycopg2
import sys
import string
try:
    conn = psycopg2.connect("dbname='QGIS' user='postgres' host='localhost' password='postgres'")
except:
    print("I am unable to connect to the database")
    sys.exit()

cur = conn.cursor()
cur.execute("""
            SELECT column_name
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'metadata_test' 
            """)

out_sql = open("insert_gui_table.sql","w+")
rows = cur.fetchall()

for row in rows:
    s = """
        INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
        VALUES ('{metadata_col_name}','text','false','true','true','{displayname}','true');
        """.format(metadata_col_name=row[0],displayname=string.capwords(row[0].replace("_"," ")))
    out_sql.write(s)

