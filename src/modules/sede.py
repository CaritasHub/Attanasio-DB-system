from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder

sede_bp = Blueprint('sede', __name__, url_prefix='/sedi')
qb = QueryBuilder('Sede')


@sede_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_all())
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@sede_bp.route('/', methods=['POST'])
@login_required
@role_required('editor', 'founder')
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.insert({'nome': data.get('nome'), 'indirizzo': data.get('indirizzo')})
    cur.execute(sql, values)
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@sede_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, {'nome': data.get('nome'), 'indirizzo': data.get('indirizzo')})
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@sede_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(qb.delete(), (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
