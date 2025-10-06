from flask import Flask, render_template, request, jsonify
import psycopg
import os

app = Flask(__name__)

# -------------------------------
# Conexión a PostgreSQL en Render
# -------------------------------
def get_connection():
    return psycopg.connect(
        host=os.environ.get("DB_HOST"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", 5432)
    )

# -----------------------------------
# Ruta principal - página de pedidos
# -----------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------------
# Ruta para registrar un pedido
# -----------------------------------
@app.route('/pedido', methods=['POST'])
def pedido():
    try:
        data = request.json
        nombre = data['nombre']
        telefono = data['telefono']
        pedido = data['pedido']
        total = float(data['total'])

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                nombre TEXT,
                telefono TEXT,
                pedido TEXT,
                total NUMERIC(10,2),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute(
            "INSERT INTO pedidos (nombre, telefono, pedido, total) VALUES (%s, %s, %s, %s)",
            (nombre, telefono, pedido, total)
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Pedido recibido correctamente."})

    except Exception as e:
        print("Error al guardar pedido:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------------------
# Panel de administración
# -----------------------------------
@app.route('/admin')
def admin():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pedidos ORDER BY fecha DESC")
    pedidos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', pedidos=pedidos)

# -----------------------------------
# Ejecutar la app
# -----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
