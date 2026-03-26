# ===============================
# SISTEMA GESTIÓN DE OFICIOS
# UI DIF MODERNO RESPONSIVO
# ===============================

from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hm_secret"
DB = "oficios.db"

# ===============================
# DB
# ===============================

def get_db():
    return sqlite3.connect(DB)

# ===============================
# UTILIDADES
# ===============================

def siguiente_consecutivo(anio):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT MAX(consecutivo) FROM oficios WHERE anio=?", (anio,))
    row = cur.fetchone()
    conn.close()
    return 1 if row[0] is None else row[0] + 1

# ===============================
# LOGIN RESPONSIVO
# ===============================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        pwd = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT usuario, tipo FROM usuarios WHERE usuario=? AND password=?", (user, pwd))
        data = cur.fetchone()
        conn.close()

        if data:
            session['usuario'] = data[0]
            session['tipo'] = data[1]
            return redirect('/consulta')

    return """
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body {font-family: 'Segoe UI'; background:#0f172a; display:flex; justify-content:center; align-items:center; height:100vh; color:white; margin:0;}
    .card {background:#1e293b; padding:30px; border-radius:12px; width:90%; max-width:320px; box-shadow:0 10px 30px rgba(0,0,0,0.4);} 
    input {width:100%; padding:12px; margin:8px 0; border-radius:8px; border:none;}
    button {width:100%; padding:12px; background:#2563eb; color:white; border:none; border-radius:8px; font-weight:bold;}
    h2 {text-align:center;}
    </style>

    <div class='card'>
        <h2>🔐 Sistema Oficios</h2>
        <form method='POST'>
            <input name='usuario' placeholder='Usuario'>
            <input name='password' type='password' placeholder='Password'>
            <button>Entrar</button>
        </form>
    </div>
    """

# ===============================
# CONSULTA RESPONSIVA
# ===============================

@app.route('/consulta')
def consulta():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM oficios ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()

    html = f"""
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body {{font-family: 'Segoe UI'; margin:0; background:#f1f5f9;}}
    .navbar {{background:#0f172a; color:white; padding:15px; display:flex; justify-content:space-between; flex-wrap:wrap;}}
    .container {{padding:15px;}}
    .card {{background:white; padding:15px; border-radius:12px; box-shadow:0 5px 15px rgba(0,0,0,0.1);}}
    table {{width:100%; border-collapse:collapse;}}
    th, td {{padding:10px; font-size:14px;}}
    th {{background:#e2e8f0;}}
    tr:hover {{background:#f8fafc;}}
    .btn {{display:inline-block; background:#2563eb; color:white; padding:10px; border-radius:8px; text-decoration:none; margin-bottom:10px;}}

    /* RESPONSIVE TABLE */
    @media (max-width: 768px) {{
        table, thead, tbody, th, td, tr {{display:block;}}
        th {{display:none;}}
        td {{border-bottom:1px solid #ddd; position:relative; padding-left:50%;}}
        td:before {{position:absolute; left:10px; top:10px; font-weight:bold;}}
        td:nth-of-type(1):before {{content:"Oficio";}}
        td:nth-of-type(2):before {{content:"Fecha";}}
        td:nth-of-type(3):before {{content:"Enviado";}}
        td:nth-of-type(4):before {{content:"Concepto";}}
        td:nth-of-type(5):before {{content:"Usuario";}}
    }}
    </style>

    <div class='navbar'>
        <div>📄 Sistema Oficios</div>
        <div>{session['usuario']}</div>
    </div>

    <div class='container'>
        <div class='card'>
            <h3>Últimos Oficios</h3>
            <a class='btn' href='/asignar'>+ Nuevo Oficio</a>

            <table>
            <tr>
                <th>Oficio</th>
                <th>Fecha</th>
                <th>Enviado</th>
                <th>Concepto</th>
                <th>Usuario</th>
            </tr>
    """

    for r in rows:
        oficio = f"{r[1]:03d}/{r[2]}"
        html += f"<tr><td><a href='/detalle/{r[0]}'>{oficio}</a></td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[10]}</td></tr>"

    html += "</table></div></div>"
    return html

# ===============================
# ASIGNAR RESPONSIVO
# ===============================

@app.route('/asignar', methods=['GET', 'POST'])
def asignar():
    anio = datetime.now().year

    if request.method == 'POST':
        consecutivo = siguiente_consecutivo(anio)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO oficios (consecutivo, anio, fecha, destinatario, concepto, creado_por) VALUES (?, ?, ?, ?, ?, ?)",
                    (consecutivo, anio, request.form['fecha'], request.form['enviado'], request.form['concepto'], session['usuario']))
        conn.commit()
        conn.close()

        return redirect('/consulta')

    consecutivo = siguiente_consecutivo(anio)
    oficio = f"{consecutivo:03d}/{anio}"

    return f"""
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body {{font-family:'Segoe UI'; background:#f1f5f9; padding:15px;}}
    .card {{background:white; padding:20px; border-radius:12px; max-width:500px; margin:auto;}}
    input {{width:100%; padding:12px; margin:8px 0; border-radius:8px; border:1px solid #ccc;}}
    button {{background:#2563eb; color:white; padding:12px; border:none; border-radius:8px; width:100%;}}
    </style>

    <div class='card'>
        <h3>Asignar Oficio</h3>
        <b>Oficio:</b> {oficio}<br><br>

        <form method='POST'>
            Fecha:<input name='fecha' value='{datetime.now().date()}'><br>
            Enviado a:<input name='enviado'><br>
            Concepto:<input name='concepto'><br>
            <button>Asignar</button>
        </form>
    </div>
    """

# ===============================
# INIT
# ===============================

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE, password TEXT, tipo INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS oficios (id INTEGER PRIMARY KEY, consecutivo INTEGER, anio INTEGER, fecha TEXT, destinatario TEXT, concepto TEXT, num_control TEXT, fecha_envio TEXT, guia TEXT, paqueteria TEXT, creado_por TEXT)")

    cur.execute("INSERT OR IGNORE INTO usuarios VALUES (1,'HSALCIDO','123',0)")
    cur.execute("INSERT OR IGNORE INTO usuarios VALUES (2,'VHERRERA','123',1)")
    cur.execute("INSERT OR IGNORE INTO usuarios VALUES (3,'BMALDONADO','123',1)")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
