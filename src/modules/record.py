"""Record detail and edit views."""

from flask import Blueprint, render_template, request, abort, session
from db import get_db_connection
from .utils import login_required
from .query_builder import QueryBuilder

# Map URL segment to table name
TABLE_MAP = {
    'users': 'Utente',
    'specialists': 'Specialista',
    'sedi': 'Sede',
}

record_bp = Blueprint('record', __name__, url_prefix='/record')

@record_bp.route('/<name>/<int:rec_id>', methods=['GET', 'POST'])
@login_required
def record_view(name, rec_id):
    """Display and optionally update a single record."""
    table = TABLE_MAP.get(name)
    if not table:
        abort(404)
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    qb = QueryBuilder(table)

    # Update record when allowed
    editable = session.get('role') in ('editor', 'founder')
    if request.method == 'POST' and editable:
        data = {k: v for k, v in request.form.items() if k != 'csrf_token'}
        sql, values = qb.update(rec_id, data)
        cur.execute(sql, values)
        conn.commit()

    cur.execute(qb.select_one(), (rec_id,))
    row = cur.fetchone()
    cur.close()
    if not row:
        abort(404)
    return render_template('record.html', row=row, name=name, editable=editable)
