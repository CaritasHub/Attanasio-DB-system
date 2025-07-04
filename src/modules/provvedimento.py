from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder

provvedimento_bp = Blueprint('provvedimento', __name__, url_prefix='/provvedimenti')
qb = QueryBuilder('Provvedimento')


@provvedimento_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_all())
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@provvedimento_bp.route('/', methods=['POST'])
@login_required
@role_required('editor', 'founder')
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    fields = {
        'utente_id': data.get('utente_id'),
        'sede_id': data.get('sede_id'),
        'tipo': data.get('tipo'),
        'data_inizio': data.get('data_inizio'),
        'data_fine': data.get('data_fine'),
    }
    sql, values = qb.insert(fields)
    cur.execute(sql, values)
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@provvedimento_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, {'stato': data.get('stato')})
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@provvedimento_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(qb.delete(), (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
