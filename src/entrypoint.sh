#!/bin/sh
set -e
python /app/init_db.py
exec python /app/app.py
