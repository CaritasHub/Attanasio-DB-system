from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required

provvedimento_bp = Blueprint('provvedimento', __name__, url_prefix='/provvedimenti')


@provvedimento_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM Provvedimento')
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@provvedimento_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO Provvedimento (utente_id, sede_id, tipo, data_inizio, data_fine) VALUES (%s, %s, %s, %s, %s)',
        (
            data.get('utente_id'),
            data.get('sede_id'),
            data.get('tipo'),
            data.get('data_inizio'),
            data.get('data_fine'),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@provvedimento_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE Provvedimento SET stato=%s WHERE id=%s',
        (data.get('stato'), id),
    )
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@provvedimento_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Provvedimento WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
