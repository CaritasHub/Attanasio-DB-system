from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required

specialista_bp = Blueprint('specialista', __name__, url_prefix='/specialists')


@specialista_bp.route('/', methods=['GET'])
@login_required
def list_all():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM Specialista')
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@specialista_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_one(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM Specialista WHERE id=%s', (id,))
    row = cur.fetchone()
    cur.close()
    return jsonify(row or {})


@specialista_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO Specialista (nome, cognome, ruolo) VALUES (%s, %s, %s)',
        (data.get('nome'), data.get('cognome'), data.get('ruolo')),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@specialista_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE Specialista SET nome=%s, cognome=%s, ruolo=%s WHERE id=%s',
        (data.get('nome'), data.get('cognome'), data.get('ruolo'), id),
    )
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@specialista_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Specialista WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
