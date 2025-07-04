from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder
from werkzeug.security import generate_password_hash

users_table_bp = Blueprint('users_table', __name__, url_prefix='/loginusers')
qb = QueryBuilder('Users')


@users_table_bp.route('/', methods=['GET'])
@login_required
@role_required('founder')
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT id, username FROM Users')
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@users_table_bp.route('/', methods=['POST'])
@login_required
@role_required('founder')
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    fields = {
        'username': data.get('username'),
        'password_hash': generate_password_hash(data.get('password')),
        'email': data.get('email'),
        'role': data.get('role', 'viewer'),
    }
    sql, values = qb.insert(fields)
    cur.execute(sql, values)
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@users_table_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('founder')
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(qb.delete(), (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
