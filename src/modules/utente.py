from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required

utente_bp = Blueprint('utente', __name__, url_prefix='/users')


@utente_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM Utente')
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@utente_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_one(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM Utente WHERE id=%s', (id,))
    row = cur.fetchone()
    cur.close()
    return jsonify(row or {})


@utente_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO Utente (operatore_id, data_inserimento, riferimento, nome, cognome, codice_fiscale) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (
            data.get('operatore_id'),
            data.get('data_inserimento'),
            data.get('riferimento'),
            data.get('nome'),
            data.get('cognome'),
            data.get('codice_fiscale'),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@utente_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE Utente SET nome=%s, cognome=%s WHERE id=%s',
        (data.get('nome'), data.get('cognome'), id),
    )
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@utente_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Utente WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
