"""Record detail and edit views."""

from flask import Blueprint, render_template, request, abort, session
from db import get_db_connection
from .utils import login_required
from .query_builder import QueryBuilder

# Mapping of foreign key columns to referenced tables
FK_MAP = {
    'operatore_id': 'Specialista',
    'consenso_operatore_id': 'Specialista',
    'utente_id': 'Utente',
    'specialista_id': 'Specialista',
    'sede_id': 'Sede',
}

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

    # Get column types for date detection
    cur.execute(f"SHOW COLUMNS FROM {table}")
    cols_info = {row['Field']: row['Type'] for row in cur.fetchall()}
    date_fields = [k for k, t in cols_info.items() if 'date' in str(t).lower()]

    # Update record when allowed
    editable = session.get('role') in ('editor', 'founder')
    if request.method == 'POST' and editable:
        data = {}
        for k, v in request.form.items():
            if k == 'csrf_token':
                continue
            data[k] = v if v != '' else None
        sql, values = qb.update(rec_id, data)
        cur.execute(sql, values)
        conn.commit()

    cur.execute(qb.select_one(), (rec_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        abort(404)

    options = {}
    for col, ref_table in FK_MAP.items():
        if col in row:
            cur.execute(
                'SELECT column_name FROM ColumnConfig WHERE table_name=%s AND highlight=1 ORDER BY display_order',
                (ref_table,)
            )
            highlight_cols = [r['column_name'] for r in cur.fetchall()]
            cols = ['id'] + highlight_cols if highlight_cols else ['id']
            cur.execute(f"SELECT {', '.join(cols)} FROM {ref_table}")
            opts = []
            for r in cur.fetchall():
                label = ' '.join(str(r[h]) for h in highlight_cols) if highlight_cols else str(r['id'])
                opts.append({'id': r['id'], 'label': label})
            options[col] = opts

    cur.close()
    return render_template('record.html', row=row, name=name, editable=editable,
                           options=options, date_fields=date_fields)
