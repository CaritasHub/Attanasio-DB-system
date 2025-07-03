import os
import mysql.connector
from flask import g
from werkzeug.security import generate_password_hash


def _ensure_users_table(conn):
    """Create login table and default admin user if missing."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
        """
    )
    conn.commit()


    cur.execute("SELECT COUNT(*) FROM Users")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute(
            "INSERT INTO Users (username, password_hash) VALUES (%s, %s)",
            ("admin", generate_password_hash("admin123")),
        )
        conn.commit()
    cur.close()


def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'db'),
            user=os.getenv('MYSQL_USER', 'Antonella'),
            password=os.getenv('MYSQL_PASSWORD', 'attanasio'),
            database=os.getenv('MYSQL_DATABASE', 'Attanasio'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
        )
        _ensure_users_table(g.db_conn)
    return g.db_conn


def close_db(e=None):
    conn = g.pop('db_conn', None)
    if conn is not None:
        conn.close()
