from functools import wraps
from flask import session, redirect, url_for, request
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

