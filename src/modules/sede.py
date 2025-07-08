"""REST API for the ``Sede`` table."""

from flask import Blueprint, request, jsonify
from mysql.connector import errors, errorcode
from db import get_db_connection
from .utils import login_required, role_required
from .query_builder import QueryBuilder
import csv
import io

sede_bp = Blueprint('sede', __name__, url_prefix='/sedi')
qb = QueryBuilder('Sede')


@sede_bp.route('/', methods=['GET'])
@login_required
def list_or_search():
    """Return records with optional search and pagination."""
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
        cur.execute('SHOW COLUMNS FROM Sede')
        cols = [r[0] for r in cur.fetchall()]
        like_parts = [f"{c} LIKE %s" for c in cols]
        clauses = ' WHERE ' + ' OR '.join(like_parts)
        values.extend(['%' + query + '%'] * len(cols))

    count_sql = f'SELECT COUNT(*) FROM Sede{clauses}'
    cur.execute(count_sql, values)
    total = cur.fetchone()['COUNT(*)']

    base_sql += clauses + ' LIMIT %s OFFSET %s'
    values.extend([per_page, (page - 1) * per_page])
    cur.execute(base_sql, values)
    rows = cur.fetchall()
    cur.close()
    return jsonify({'rows': rows, 'total': total})


@sede_bp.route('/', methods=['POST'])
@login_required
@role_required('editor', 'founder')
def create():
    """Create new records via JSON body or CSV file."""
    conn = get_db_connection()
    cur = conn.cursor()

    if 'file' in request.files:
        file = request.files['file']
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        cols = reader.fieldnames or []
        placeholders = ','.join(['%s'] * len(cols))
        sql = f"INSERT INTO Sede ({','.join(cols)}) VALUES ({placeholders})"
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


@sede_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('editor', 'founder')
def update(id):
    """Update an existing record with arbitrary fields."""
    data = request.json or {}
    conn = get_db_connection()
    cur = conn.cursor()
    sql, values = qb.update(id, data)
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    return jsonify({'status': 'updated'})


@sede_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('editor', 'founder')
def delete(id):
    """Delete a record."""
    # Remove one row by id
    force = request.args.get('force') == '1'
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(qb.delete(), (id,))
        conn.commit()
    except errors.IntegrityError as e:
        if e.errno == errorcode.ER_ROW_IS_REFERENCED_2:
            if not force:
                cur.close()
                return jsonify({'error': 'foreign_key'}), 409
            cur.execute('DELETE FROM Provvedimento WHERE sede_id=%s', (id,))
            conn.commit()
            cur.execute(qb.delete(), (id,))
            conn.commit()
        else:
            cur.close()
            return jsonify({'error': str(e)}), 400
    cur.close()
    return jsonify({'status': 'deleted'})
