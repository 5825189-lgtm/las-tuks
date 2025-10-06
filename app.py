from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "clave_super_secreta_local")

# -------------------------------------------------
# 🔗 CONEXIÓN A POSTGRES (usa variables de entorno)
# -------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "las_tuks2"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        port=int(os.environ.get("DB_PORT", 5432))
    )

# -------------------------------------------------
# 🔐 LOGIN
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")
        if usuario == "admin" and password == "1234":
            session["usuario"] = usuario
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html")

# -------------------------------------------------
# 🏠 MENÚ PÚBLICO
# -------------------------------------------------
@app.route("/menu")
def menu():
    return render_template("menu.html")

# -------------------------------------------------
# 💾 GUARDAR PEDIDO EN BASE DE DATOS
# -------------------------------------------------
@app.route("/realizar_pedido", methods=["POST"])
def realizar_pedido():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido o vacío"}), 400

    cliente = data.get("cliente")
    pedido = data.get("pedido")
    total = data.get("total")

    # Validaciones mínimas
    if not cliente or not pedido or total is None:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        # Creación de tabla si no existe
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

        mensaje = f"Gracias {cliente}, tu pedido fue recibido por un total de ${float(total):.2f}. ¡Las Tuks te desea buen provecho!"
        return jsonify({"message": mensaje}), 200

    except Exception as e:
        print("❌ Error guardando pedido:", e)
        return jsonify({"error": "Error al guardar el pedido"}), 500

# -------------------------------------------------
# 🧾 PANEL ADMIN
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
        print("Error cargando pedidos:", e)
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
    # para desarrollo
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
