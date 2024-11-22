from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import pymysql

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(host='localhost', user='root', password='', database='league_of_legends')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE username=%s AND password=MD5(%s)", (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        session['username'] = user['username']
        session['role'] = user['role']
        if user['role'] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user'))
    else:
        flash('Credenciales incorrectas.')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Ruta de administrador
@app.route('/admin')
def admin():
    if 'role' in session and session['role'] == 'admin':
        return render_template('admin.html')
    else:
        flash('Acceso denegado.')
        return redirect(url_for('index'))

# Operaciones CRUD 
@app.route('/api/usuarios', methods=['GET', 'POST'])
def manage_usuarios():
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(usuarios)

    if request.method == 'POST':
        data = request.json
        username = data['username']
        role = data['role']
    
        password = '1234'  # esto es para que tengan una clave pasword por defecto dado el caso
        cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (%s, MD5(%s), %s)", (username, password, role))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Usuario creado con éxito'}), 201

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'DELETE'])
def update_delete_usuario(id):
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    if request.method == 'PUT':
        data = request.json
        username = data['username']
        role = data['role']
        cursor.execute("UPDATE usuarios SET username=%s, role=%s WHERE id=%s", (username, role, id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Usuario actualizado con éxito'})

    if request.method == 'DELETE':
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Usuario eliminado con éxito'})

# Nueva ruta para buscar usuarios por nombre
@app.route('/api/usuarios/buscar', methods=['GET'])
def buscar_usuario():
    username = request.args.get('username')
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
    usuario = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(usuario)

if __name__ == "__main__":
    app.run(debug=True)
