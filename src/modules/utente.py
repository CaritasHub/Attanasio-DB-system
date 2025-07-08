"""REST endpoints for the ``Utente`` table."""

from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder

utente_bp = Blueprint('utente', __name__, url_prefix='/users')
qb = QueryBuilder('Utente')


@utente_bp.route('/', methods=['GET'])
@login_required
def list_all():
    """Return all rows from ``Utente``."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_all())
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@utente_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_one(id):
    """Return a single record by id."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_one(), (id,))
    row = cur.fetchone()
    cur.close()
    return jsonify(row or {})


@utente_bp.route('/', methods=['POST'])
@login_required
@role_required('editor', 'founder')
def create():
    """Create a new ``Utente`` record."""
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    fields = {
        'operatore_id': data.get('operatore_id'),
        'data_inserimento': data.get('data_inserimento'),
        'riferimento': data.get('riferimento'),
        'nome': data.get('nome'),
        'cognome': data.get('cognome'),
        'codice_fiscale': data.get('codice_fiscale'),
    }
    sql, values = qb.insert(fields)
    cur.execute(sql, values)
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@utente_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    """Update an existing ``Utente`` record."""
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, {'nome': data.get('nome'),
                                 'cognome': data.get('cognome')})
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@utente_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(id):
    """Delete a record."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(qb.delete(), (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
