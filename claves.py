from flask import Flask, request
import sqlite3, hashlib

app = Flask(__name__)
DB = "usuarios.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

@app.route("/")
def index():
    return "<h1>Sistema de Gestión de Claves DRY7122</h1>", 200

@app.route("/register", methods=["POST"])
def register():
    user = request.args.get("username")
    pw   = request.args.get("password")
    if not user or not pw:
        return "Faltan parametros", 400
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "INSERT INTO users (username,password) VALUES (?,?)",
            (user, hash_pw(pw))
        )
        conn.commit()
        return f"Usuario {user} registrado.", 200
    except sqlite3.IntegrityError:
        return "Usuario ya existe.", 409
    finally:
        conn.close()

@app.route("/login", methods=["GET"])
def login():
    user = request.args.get("username")
    pw   = request.args.get("password")
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user, hash_pw(pw))
    ).fetchone()
    conn.close()
    return (f"Acceso concedido: {user}", 200) if row \
           else ("Credenciales incorrectas", 401)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
