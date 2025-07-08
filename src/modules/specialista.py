"""REST endpoints for the ``Specialista`` table."""

from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder

specialista_bp = Blueprint('specialista', __name__, url_prefix='/specialists')
qb = QueryBuilder('Specialista')


@specialista_bp.route('/', methods=['GET'])
@login_required
def list_all():
    """Return all ``Specialista`` rows."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_all())
    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@specialista_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_one(id):
    """Return a single record."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(qb.select_one(), (id,))
    row = cur.fetchone()
    cur.close()
    return jsonify(row or {})


@specialista_bp.route('/', methods=['POST'])
@login_required
@role_required('editor', 'founder')
def create():
    """Insert a new record."""
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.insert({'nome': data.get('nome'),
                             'cognome': data.get('cognome'),
                             'ruolo': data.get('ruolo')})
    cur.execute(sql, values)
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@specialista_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    """Update an existing record."""
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, {'nome': data.get('nome'),
                                 'cognome': data.get('cognome'),
                                 'ruolo': data.get('ruolo')})
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@specialista_bp.route('/<int:id>', methods=['DELETE'])
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
