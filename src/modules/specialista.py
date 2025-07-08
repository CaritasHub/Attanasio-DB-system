"""REST API for the ``Specialista`` table."""

from flask import Blueprint, request, jsonify
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder
import csv
import io

specialista_bp = Blueprint('specialista', __name__, url_prefix='/specialists')
qb = QueryBuilder('Specialista')


@specialista_bp.route('/', methods=['GET'])
@login_required
def list_or_search():
    """Return specialists list or single record."""
    rec_id = request.args.get('id', type=int)
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if rec_id:
        cur.execute(qb.select_one(), (rec_id,))
        row = cur.fetchone()
        cur.close()
        return jsonify(row or {})

    base_sql = qb.select_all()
    values = []
    clauses = ''
    if query:
        cur.execute('SHOW COLUMNS FROM Specialista')
        cols = [r[0] for r in cur.fetchall()]
        like_parts = [f"{c} LIKE %s" for c in cols]
        clauses = ' WHERE ' + ' OR '.join(like_parts)
        values.extend(['%' + query + '%'] * len(cols))

    count_sql = f'SELECT COUNT(*) FROM Specialista{clauses}'
    cur.execute(count_sql, values)
    total = cur.fetchone()['COUNT(*)']

    base_sql += clauses + ' LIMIT %s OFFSET %s'
    values.extend([per_page, (page-1) * per_page])
    cur.execute(base_sql, values)
    rows = cur.fetchall()
    cur.close()
    return jsonify({'rows': rows, 'total': total})


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
    """Insert records via JSON body or CSV file."""
    conn = get_db_connection()
    cur = conn.cursor()

    if 'file' in request.files:
        file = request.files['file']
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        cols = reader.fieldnames or []
        placeholders = ','.join(['%s'] * len(cols))
        sql = f"INSERT INTO Specialista ({','.join(cols)}) VALUES ({placeholders})"
        try:
            conn.start_transaction()
            for row in reader:
                cur.execute(sql, [row.get(c) for c in cols])
            conn.commit()
        except Exception as e:
            conn.rollback()
            cur.close()
            return jsonify({'error': str(e)}), 400
        cur.close()
        return jsonify({'status': 'imported'})

    data = request.json or {}
    sql, values = qb.insert(data)
    cur.execute(sql, values)
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({'id': new_id}), 201


@specialista_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    """Update a record with arbitrary columns."""
    data = request.json or {}
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, data)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@specialista_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(id):
    """Delete a record."""
    # Remove one entry by id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(qb.delete(), (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'deleted'})
