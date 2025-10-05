from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = "tuks_secret_key"

# Configuración de la base de datos
DB_NAME = "las_tuks2"

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="inframen2025",  # tu contraseña si tienes
        database='las_tuks2'
    )

# --- RUTAS ---
@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/pedido', methods=['POST'])
def pedido():
    data = request.get_json()
    nombre = data.get('nombre')
    telefono = data.get('telefono')
    items = data.get('items')
    total = data.get('total')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (customer_name, customer_phone, items, total, estado)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, telefono, json.dumps(items), total, "Pendiente"))
    conn.commit()
    cur.close()
    conn.close()

    mensaje = f"Gracias {nombre}, tu pedido fue recibido por un total de ${total:.2f}. ¡Las Tuks te desea buen provecho!"
    return jsonify({"message": mensaje})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if usuario == "admin" and password == "12345":
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM orders ORDER BY fecha DESC")
    pedidos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', pedidos=pedidos)

@app.route('/marcar_entregado/<int:pedido_id>', methods=['POST'])
def marcar_entregado(pedido_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET estado='Entregado' WHERE id=%s", (pedido_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route('/eliminar_pedido/<int:pedido_id>', methods=['POST'])
def eliminar_pedido(pedido_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id=%s", (pedido_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
