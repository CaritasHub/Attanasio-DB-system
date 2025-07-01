from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required
from werkzeug.security import generate_password_hash

users_table_bp = Blueprint('users_table', __name__, url_prefix='/loginusers')


@users_table_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT id, username FROM Users')
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@users_table_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO Users (username, password_hash) VALUES (%s, %s)',
        (data.get('username'), generate_password_hash(data.get('password'))),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@users_table_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Users WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
