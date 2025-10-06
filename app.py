from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# -------------------------------------------------
# 🔗 CONEXIÓN A LA BASE DE DATOS DE RENDER
# -------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", 5432)
    )

# -------------------------------------------------
# 🔐 LOGIN ADMIN
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == "admin" and password == "1234":
            session["usuario"] = usuario
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")

# -------------------------------------------------
# 🍽️ MENÚ PÚBLICO
# -------------------------------------------------
@app.route("/menu")
def menu():
    return render_template("menu.html")

# -------------------------------------------------
# 💾 GUARDAR PEDIDO EN POSTGRES
# -------------------------------------------------
@app.route("/guardar_pedido", methods=["POST"])
def guardar_pedido():
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        telefono = data.get("telefono", "")
        pedido = data.get("pedido")
        total = data.get("total")

        conn = get_connection()
        cur = conn.cursor()

        # Crear la tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                telefono VARCHAR(20),
                pedido TEXT,
                total NUMERIC,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insertar el pedido
        cur.execute("""
            INSERT INTO pedidos (nombre, telefono, pedido, total)
            VALUES (%s, %s, %s, %s)
        """, (nombre, telefono, pedido, total))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success", "message": "Pedido guardado exitosamente"})
    except Exception as e:
        print("❌ ERROR GUARDANDO PEDIDO:", e)
        return jsonify({"status": "error", "message": str(e)})

# -------------------------------------------------
# 🧾 PANEL ADMINISTRATIVO
# -------------------------------------------------
@app.route("/admin")
def admin():
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM pedidos ORDER BY fecha DESC")
        pedidos = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ ERROR CARGANDO PEDIDOS:", e)
        pedidos = []

    return render_template("admin.html", pedidos=pedidos)

# -------------------------------------------------
# 🚪 CERRAR SESIÓN
# -------------------------------------------------
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# -------------------------------------------------
# 🚀 INICIO DEL SERVIDOR
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
