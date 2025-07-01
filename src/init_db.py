import os
import time
import mysql.connector

DB_NAME = os.getenv('MYSQL_DATABASE', 'Attanasio')
DB_HOST = os.getenv('MYSQL_HOST', 'db')
DB_PORT = int(os.getenv('MYSQL_PORT', '3306'))
DB_USER = os.getenv('MYSQL_USER', 'Antonella')
DB_PASS = os.getenv('MYSQL_PASSWORD', 'attanasio')
ROOT_PASS = os.getenv('MYSQL_ROOT_PASSWORD', '')

# Use root credentials when available, as some scripts may require it
USE_ROOT = bool(ROOT_PASS)

def wait_for_db():
    while True:
        try:
            mysql.connector.connect(host=DB_HOST, port=DB_PORT,
                                   user=DB_USER if not USE_ROOT else 'root',
                                   password=DB_PASS if not USE_ROOT else ROOT_PASS)
            return
        except mysql.connector.Error:
            time.sleep(2)

def run_sql_script(conn, path):
    with open(path, 'r') as f:
        sql = f.read()
    # remove comment lines
    lines = []
    for line in sql.splitlines():
        striped = line.strip()
        if not striped.startswith('--'):
            lines.append(line)
    sql = '\n'.join(lines)
    # split statements by semicolon
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    cur = conn.cursor()
    for stmt in statements:
        cur.execute(stmt)
    conn.commit()
    cur.close()

def ensure_tables():
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT,
                                   user=DB_USER if not USE_ROOT else 'root',
                                   password=DB_PASS if not USE_ROOT else ROOT_PASS,
                                   database=DB_NAME)
    cur = conn.cursor()
    cur.execute("SHOW TABLES LIKE 'Specialista'")
    exists = cur.fetchone()
    if not exists:
        # run the sql script
        run_sql_script(conn, '/app/DBScript.sql')
    cur.close()
    conn.close()

if __name__ == '__main__':
    wait_for_db()
    ensure_tables()
