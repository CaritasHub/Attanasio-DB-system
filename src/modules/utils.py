from functools import wraps
from flask import session, redirect, url_for, request
from mysql.connector import errorcode, errors
from werkzeug.security import generate_password_hash
from db import get_db_connection
import os
import smtplib
from email.message import EmailMessage


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session or session.get('role') not in roles:
                return redirect(url_for('auth.login'))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def log_access(user_id, ip):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO AccessLog (user_id, ip) VALUES (%s, %s)',
        (user_id, ip)
    )
    conn.commit()
    cur.close()


def log_event(user_id, event):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO EventLog (user_id, event) VALUES (%s, %s)',
        (user_id, event)
    )
    conn.commit()
    cur.close()


def send_email(to, subject, body):
    server = os.getenv('SMTP_SERVER')
    if not server or not to:
        return
    port = int(os.getenv('SMTP_PORT', '25'))
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASSWORD')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = user or 'noreply@example.com'
    msg['To'] = to
    msg.set_content(body)
    with smtplib.SMTP(server, port) as s:
        if user and pwd:
            s.starttls()
            s.login(user, pwd)
        s.send_message(msg)


def remove_fk_references(conn, table, record_id):
    """Remove or nullify foreign key references to a record.

    This function queries ``information_schema`` for all foreign keys
    pointing to ``table`` and either deletes or nulls the referencing rows
    depending on the constraint's ``DELETE_RULE``.
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT k.TABLE_NAME, k.COLUMN_NAME, rc.DELETE_RULE
        FROM information_schema.KEY_COLUMN_USAGE k
        JOIN information_schema.REFERENTIAL_CONSTRAINTS rc
          ON k.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
         AND k.TABLE_SCHEMA = rc.CONSTRAINT_SCHEMA
         AND k.TABLE_NAME = rc.TABLE_NAME
        WHERE k.REFERENCED_TABLE_SCHEMA = DATABASE()
          AND k.REFERENCED_TABLE_NAME = %s
        """,
        (table,),
    )
    refs = cur.fetchall()
    for ref in refs:
        tbl = ref["TABLE_NAME"]
        col = ref["COLUMN_NAME"]
        rule = ref["DELETE_RULE"]
        if rule == "SET NULL":
            cur.execute(f"UPDATE {tbl} SET {col}=NULL WHERE {col}=%s", (record_id,))
        else:
            cur.execute(f"DELETE FROM {tbl} WHERE {col}=%s", (record_id,))
    conn.commit()
    cur.close()

