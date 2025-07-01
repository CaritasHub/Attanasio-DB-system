from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "Antonella"),
        password=os.getenv("MYSQL_PASSWORD", "attanasio"),
        database=os.getenv("MYSQL_DATABASE", "Attanasio"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
    )

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/specialists")
def list_specialists():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Specialista")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

