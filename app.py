from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3, json

app = Flask(__name__)
app.secret_key = "tuks_secret_key"

# --- Conexión a la base de datos ---
def get_connection():
    conn = sqlite3.connect("las_tuks.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- Crear tabla si no existe ---
with get_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            items TEXT,
            total REAL,
            estado TEXT DEFAULT 'Pendiente'
        )
    """)
    conn.commit()

# --- Rutas ---
@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/pedido", methods=["POST"])
def pedido():
    data = request.get_json()
    nombre = data.get("nombre")
    telefono = data.get("telefono")
    items = data.get("items")
    total = data.get("total")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_name, customer_phone, items, total, estado) VALUES (?, ?, ?, ?, ?)",
            (nombre, telefono, json.dumps(items), total, "Pendiente"),
        )
        conn.commit()
        mensaje = f"Gracias {nombre}, tu pedido fue recibido por un total de ${total:.2f}. ¡Las Tuks te desea buen provecho!"
        return jsonify({"message": mensaje})
    except Exception as e:
        return jsonify({"message": f"Error al procesar pedido: {e}"})
    finally:
        conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        if user == "admin" and password == "12345":
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))
    conn = get_connection()
    pedidos = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return render_template("admin.html", pedidos=pedidos)

@app.route("/marcar_entregado/<int:id>")
def marcar_entregado(id):
    conn = get_connection()
    conn.execute("UPDATE orders SET estado='Entregado' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/eliminar_pedido/<int:id>")
def eliminar_pedido(id):
    conn = get_connection()
    conn.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
