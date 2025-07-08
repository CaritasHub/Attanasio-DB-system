"""REST API for the ``Utente`` table."""

from flask import Blueprint, request, jsonify
from mysql.connector import errors, errorcode
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder
import csv
import io

utente_bp = Blueprint('utente', __name__, url_prefix='/users')
qb = QueryBuilder('Utente')


@utente_bp.route('/', methods=['GET'])
@login_required
def list_or_search():
    """Return records with optional search and pagination."""
    # Parse query parameters
    record_id = request.args.get('id', type=int)
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', default='asc').lower()

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if record_id:
        # Fetch a single record when id is provided
        cur.execute(qb.select_one(), (record_id,))
        row = cur.fetchone()
        cur.close()
        return jsonify(row or {})

    base_sql = qb.select_all()
    values = []
    clauses = ''
    if query:
        # Build LIKE search across all columns
        cur.execute('SHOW COLUMNS FROM Utente')
        cols = [r[0] for r in cur.fetchall()]
        like_parts = [f"{c} LIKE %s" for c in cols]
        clauses = ' WHERE ' + ' OR '.join(like_parts)
        values.extend(['%' + query + '%'] * len(cols))

    order_sql = 'DESC' if order == 'desc' else 'ASC'
    if sort_by:
        cur.execute('SHOW COLUMNS FROM Utente')
        valid_cols = [r[0] for r in cur.fetchall()]
        if sort_by not in valid_cols:
            sort_by = None

    # Total number of rows for pagination
    count_sql = f'SELECT COUNT(*) FROM Utente{clauses}'
    cur.execute(count_sql, values)
    total = cur.fetchone()['COUNT(*)']

    if sort_by:
        base_sql += f"{clauses} ORDER BY {sort_by} {order_sql} LIMIT %s OFFSET %s"
    else:
        base_sql += f"{clauses} LIMIT %s OFFSET %s"
    values.extend([per_page, (page - 1) * per_page])
    cur.execute(base_sql, values)
    rows = cur.fetchall()
    cur.close()
    return jsonify({'rows': rows, 'total': total})


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
    """Insert one or more records via JSON body or CSV file."""
    conn = get_db_connection()
    cur = conn.cursor()

    if 'file' in request.files:
        # CSV upload
        file = request.files['file']
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        cols = reader.fieldnames or []
        placeholders = ','.join(['%s'] * len(cols))
        sql = f"INSERT INTO Utente ({','.join(cols)}) VALUES ({placeholders})"
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


@utente_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    """Update an existing ``Utente`` record with arbitrary fields."""
    # Expect a JSON body with the columns to change
    data = request.json or {}
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, data)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@utente_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(id):
    """Delete a record."""
    # Called by the frontend when a row is removed
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(qb.delete(), (id,))
        conn.commit()
    except errors.IntegrityError as e:
        if e.errno == errorcode.ER_ROW_IS_REFERENCED_2:
            cur.close()
            return jsonify({'error': 'foreign_key'}), 409
        cur.close()
        return jsonify({'error': str(e)}), 400
    cur.close()
    return jsonify({'status': 'deleted'})
