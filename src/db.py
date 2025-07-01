import os
import mysql.connector
from flask import g


def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'db'),
            user=os.getenv('MYSQL_USER', 'Antonella'),
            password=os.getenv('MYSQL_PASSWORD', 'attanasio'),
            database=os.getenv('MYSQL_DATABASE', 'Attanasio'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
        )
    return g.db_conn


def close_db(e=None):
    conn = g.pop('db_conn', None)
    if conn is not None:
        conn.close()
