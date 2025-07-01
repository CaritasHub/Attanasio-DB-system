from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required

sede_bp = Blueprint('sede', __name__, url_prefix='/sedi')


@sede_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM Sede')
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@sede_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO Sede (nome, indirizzo) VALUES (%s, %s)',
        (data.get('nome'), data.get('indirizzo')),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@sede_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE Sede SET nome=%s, indirizzo=%s WHERE id=%s',
        (data.get('nome'), data.get('indirizzo'), id),
    )
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@sede_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Sede WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
