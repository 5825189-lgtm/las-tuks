from flask import Flask, render_template, request, jsonify
import psycopg
from datetime import datetime
import os

app = Flask(__name__)

# === URL de base de datos Render (modo Externo) ===
# ⚠️ Copia la URL EXACTA que aparece en Render -> "Database -> Info -> External"
# Ejemplo:
# postgresql://las_tuks2_ucmi_user:QbtTaCpUB42eG6UItxQYyV123@dpg-d3hmfi9r0fns73cgnrbg-a.oregon-postgres.render.com/las_tuks2_ucmi

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://las_tuks2_ucmi_user:QbtTaCpUB42eG6UtIxQhnIy4VSowC4hb@dpg-d3hmfi9r0fns73cgnrbg-a.oregon-postgres.render.com/las_tuks2_ucmi"
)

def get_connection():
    return psycopg.connect(DATABASE_URL, connect_timeout=10)

# === Página principal ===
@app.route("/")
def index():
    return render_template("index.html")

# === Guardar pedido ===
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

# === Ruta 404 personalizada ===
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# === Iniciar servidor ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
