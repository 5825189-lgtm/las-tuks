from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# -------------------------------------------------
# 🔗 CONEXIÓN A POSTGRES (Render o local)
# -------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "las_tuks_db"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "admin"),
        port=os.environ.get("DB_PORT", 5432)
    )

# -------------------------------------------------
# 🔐 LOGIN DEL ADMINISTRADOR
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        # Usuario y contraseña del administrador
        if usuario == "admin" and password == "1234":
            session["usuario"] = usuario
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")

# -------------------------------------------------
# 🍽️ MENÚ PÚBLICO (CLIENTES)
# -------------------------------------------------
@app.route("/menu")
def menu():
    return render_template("menu.html")

# -------------------------------------------------
# 💾 GUARDAR PEDIDO EN LA BASE DE DATOS
# -------------------------------------------------
@app.route("/realizar_pedido", methods=["POST"])
def realizar_pedido():
    data = request.get_json()
    cliente = data.get("cliente")
    pedido = data.get("pedido")
    total = data.get("total")

    if not cliente or not pedido or not total:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Crear tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                cliente VARCHAR(100),
                pedido TEXT,
                total NUMERIC,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insertar pedido
        cur.execute(
            "INSERT INTO pedidos (cliente, pedido, total) VALUES (%s, %s, %s)",
            (cliente, pedido, total)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "✅ Pedido guardado exitosamente"}), 200

    except Exception as e:
        print("⚠️ Error guardando pedido:", e)
        return jsonify({"error": "Error al guardar el pedido"}), 500

# -------------------------------------------------
# 🧾 PANEL ADMINISTRADOR
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
        print("⚠️ Error cargando pedidos:", e)
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
# 🚀 INICIO LOCAL
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
