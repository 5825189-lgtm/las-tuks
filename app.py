from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

# === Conexión a la base de datos externa (Render) ===
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://las_tuks2_ucmi_user:QbtTaCpUB42eG6UItxQxX1FFL8dKhbsK@dpg-d3hmfi9rofns73cgnrbg-a.oregon-postgres.render.com/las_tuks2_ucmi"
)

def get_connection():
    return psycopg.connect(DATABASE_URL)

# === Página de inicio (login) ===
@app.route("/")
def login():
    return render_template("login.html")

# === Ruta de validación del login ===
@app.route("/login", methods=["POST"])
def validar_login():
    usuario = request.form["usuario"]
    contrasena = request.form["contrasena"]

    if usuario == "admin" and contrasena == "1234":
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("menu"))

# === Página del menú (cliente) ===
@app.route("/menu")
def menu():
    return render_template("menu.html")

# === Guardar pedido en la base de datos ===
@app.route("/guardar_pedido", methods=["POST"])
def guardar_pedido():
    data = request.get_json()
    nombre = data.get("nombre")
    telefono = data.get("telefono")
    pedido = data.get("pedido")
    total = data.get("total")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pedidos (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT,
                        telefono TEXT,
                        pedido TEXT,
                        total NUMERIC,
                        fecha TIMESTAMP
                    )
                """)
                cur.execute("""
                    INSERT INTO pedidos (nombre, telefono, pedido, total, fecha)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nombre, telefono, pedido, total, fecha))
                conn.commit()
        return jsonify({"status": "success", "message": "Pedido guardado correctamente."})
    except Exception as e:
        print("❌ Error al guardar pedido:", e)
        return jsonify({"status": "error", "message": str(e)})

# === Panel de administración ===
@app.route("/admin")
def admin():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM pedidos ORDER BY fecha DESC")
                pedidos = cur.fetchall()
        return render_template("admin.html", pedidos=pedidos)
    except Exception as e:
        return f"Error cargando pedidos: {e}"

# === Servidor ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
