from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "hm_secret"
DB = "oficios.db"

# ===============================
# DB
# ===============================
def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        usuario TEXT UNIQUE,
        password TEXT,
        tipo INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS oficios (
        id INTEGER PRIMARY KEY,
        consecutivo INTEGER,
        anio INTEGER,
        fecha TEXT,
        destinatario TEXT,
        concepto TEXT,
        creado_por TEXT
    )
    """)

    cur.execute("INSERT OR IGNORE INTO usuarios VALUES (1,'HSALCIDO','123',0)")
    cur.execute("INSERT OR IGNORE INTO usuarios VALUES (2,'VHERRERA','123',1)")
    cur.execute("INSERT OR IGNORE INTO usuarios VALUES (3,'BMALDONADO','123',1)")

    conn.commit()
    conn.close()

# 🔥 CRÍTICO PARA RENDER
init_db()

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
# LOGIN
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
    body {
        margin:0;
        font-family:'Segoe UI';
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }
    .card {
        backdrop-filter: blur(15px);
        background: rgba(255,255,255,0.1);
        padding:30px;
        border-radius:16px;
        width:90%;
        max-width:320px;
    }
    input {width:100%; padding:12px; margin:10px 0; border-radius:10px; border:none;}
    button {width:100%; padding:12px; background:#3b82f6; color:white; border:none; border-radius:10px;}
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
# NAVBAR (REUTILIZABLE)
# ===============================
def navbar():
    return f"""
    <div class='navbar'>
        <div class='logo'>📄 Sistema Oficios</div>

        <div class='menu'>
            <a href='/asignar'>Asignación</a>
            <a href='/consulta'>Consulta</a>
        </div>

        <div class='user'>{session['usuario']}</div>
    </div>
    """

# ===============================
# CONSULTA
# ===============================
@app.route('/consulta')
def consulta():
    if 'usuario' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM oficios ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()

    html = f"""
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body {{
        margin:0;
        font-family:'Segoe UI';
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color:white;
    }}
    .navbar {{
        display:flex;
        justify-content:space-between;
        padding:15px;
        background: rgba(0,0,0,0.3);
    }}
    .menu a {{
        margin:0 10px;
        color:#93c5fd;
        text-decoration:none;
    }}
    .container {{padding:20px;}}
    .card {{
        background: rgba(255,255,255,0.1);
        padding:20px;
        border-radius:12px;
    }}
    table {{width:100%;}}
    </style>

    {navbar()}

    <div class='container'>
    <div class='card'>

    <h3>Últimos Oficios</h3>
    <a href='/asignar'>+ Nuevo Oficio</a>

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
        html += f"<tr><td>{oficio}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td></tr>"

    html += "</table></div></div>"
    return html

# ===============================
# ASIGNAR (CON COMBOBOX)
# ===============================
@app.route('/asignar', methods=['GET', 'POST'])
def asignar():
    if 'usuario' not in session:
        return redirect('/')

    anio = datetime.now().year

    if request.method == 'POST':
        consecutivo = siguiente_consecutivo(anio)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO oficios (consecutivo, anio, fecha, destinatario, concepto, creado_por)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (consecutivo, anio, request.form['fecha'], request.form['enviado'], request.form['concepto'], session['usuario']))
        conn.commit()
        conn.close()

        return redirect('/consulta')

    consecutivo = siguiente_consecutivo(anio)
    oficio = f"{consecutivo:03d}/{anio}"

    return f"""
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body {{
        margin:0;
        font-family:'Segoe UI';
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color:white;
    }}
    .card {{
        margin:50px auto;
        background: rgba(255,255,255,0.1);
        padding:25px;
        border-radius:16px;
        width:90%;
        max-width:400px;
    }}
    input {{
        width:100%;
        padding:12px;
        margin:10px 0;
        border-radius:10px;
        border:none;
    }}
    button {{
        width:100%;
        padding:12px;
        background:#3b82f6;
        color:white;
        border:none;
        border-radius:10px;
    }}
    </style>

    {navbar()}

    <div class='card'>
        <h3>Asignar Oficio</h3>
        <b>Oficio:</b> {oficio}<br><br>

        <form method='POST'>
            Fecha:<input name='fecha' value='{datetime.now().date()}'>

            Enviado a:
            <input list="destinatarios" name="enviado" placeholder="Escribe o selecciona">
            <datalist id="destinatarios">
                <option value="Rosa Isela Moreno">
                <option value="Angélica Hernández Belmon">
                <option value="Víctor Herrera">
                <option value="Belén Maldonado">
            </datalist>

            Concepto:<input name='concepto'>

            <button>Asignar</button>
        </form>
    </div>
    """

# ===============================
# RUN
# ===============================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
