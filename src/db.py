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
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            role ENUM('founder','editor','viewer') NOT NULL DEFAULT 'viewer'
        )
        """
    )
    conn.commit()

    # ensure optional columns in case of upgrades
    cur.execute("SHOW COLUMNS FROM Users LIKE 'email'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE Users ADD COLUMN email VARCHAR(255)")
    cur.execute("SHOW COLUMNS FROM Users LIKE 'role'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE Users ADD COLUMN role ENUM('founder','editor','viewer') NOT NULL DEFAULT 'viewer'")
        conn.commit()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS AccessLog (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            ip VARCHAR(45),
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS EventLog (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            event TEXT,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ColumnConfig (
            id INT AUTO_INCREMENT PRIMARY KEY,
            table_name VARCHAR(255) NOT NULL,
            column_name VARCHAR(255) NOT NULL,
            visible BOOLEAN NOT NULL DEFAULT TRUE,
            display_order INT DEFAULT 0,
            UNIQUE KEY table_col (table_name, column_name)
        )
        """
    )
    conn.commit()


    cur.execute("SELECT COUNT(*) FROM Users")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute(
            "INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, %s)",
            ("admin", generate_password_hash("admin123"), "founder"),
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
