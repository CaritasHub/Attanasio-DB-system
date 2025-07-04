from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder

afferenza_bp = Blueprint('afferenza', __name__, url_prefix='/afferenze')
qb = QueryBuilder('Afferenza')


@afferenza_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_all())
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@afferenza_bp.route('/', methods=['POST'])
@login_required
@role_required('editor', 'founder')
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    fields = {
        'utente_id': data.get('utente_id'),
        'specialista_id': data.get('specialista_id'),
        'ruolo': data.get('ruolo'),
        'data_inizio': data.get('data_inizio'),
    }
    sql, values = qb.insert(fields)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'created'}), 201


@afferenza_bp.route('/<int:utente_id>/<int:specialista_id>/<data_inizio>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(utente_id, specialista_id, data_inizio):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Afferenza WHERE utente_id=%s AND specialista_id=%s AND data_inizio=%s',
                (utente_id, specialista_id, data_inizio))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
