from flask import Flask, render_template, request, jsonify
import psycopg
from datetime import datetime
import os

app = Flask(__name__)

# === Conexión directa a tu base de datos de Render ===
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://las_tuks2_user:3dapkOqNluDXZholXSsFDS9NTBNYRBDE@dpg-d3hjsc95pdvs73fb1ekg-a.oregon-postgres.render.com/las_tuks2"
)

def get_connection():
    return psycopg.connect(DATABASE_URL)

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

# === Iniciar servidor ===
if __name__ == "__main__":
    app.run(debug=True)
