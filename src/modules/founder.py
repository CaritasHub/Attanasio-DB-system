from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection
from .utils import login_required, role_required, log_event, send_email

founder_bp = Blueprint('founder', __name__, url_prefix='/founder')

@founder_bp.route('/')
@login_required
@role_required('founder')
def panel():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT A.timestamp, U.username, A.ip FROM AccessLog A JOIN Users U ON A.user_id=U.id ORDER BY A.timestamp DESC")
    access_logs = cur.fetchall()
    cur.execute("SELECT E.timestamp, U.username, E.event FROM EventLog E JOIN Users U ON E.user_id=U.id ORDER BY E.timestamp DESC")
    event_logs = cur.fetchall()
    cur.close()
    return render_template('founder_panel.html', access_logs=access_logs, event_logs=event_logs)


@founder_bp.route('/users', methods=['POST'])
@login_required
@role_required('founder')
def add_user():
    data = request.form or request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'viewer')
    if not username or not password:
        return redirect(url_for('founder.panel'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO Users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)',
        (username, generate_password_hash(password), email, role)
    )
    conn.commit()
    cur.close()
    send_email(email, 'Account creato', f"Il tuo account {username} è stato creato.")
    log_event(session['user_id'], f'created user {username}')
    return redirect(url_for('founder.panel'))

