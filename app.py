from flask import Flask, render_template, request, redirect, session
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)
app.secret_key = 'secreto123'  # Cambia esto en producción

# Credenciales fijas
USUARIO = 'geo'
CLAVE = 'akira'

# Función para leer datos desde Google Sheets
def obtener_clientes():
    url = "https://docs.google.com/spreadsheets/d/1YCEuaC-E-pSPsT-VnitCDBT5cc5k_qh3_2wxtbTuCOs/export?format=csv"
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    return df.to_dict(orient='records')

# Ruta raíz
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect('/dashboard')
    return redirect('/login')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        if usuario == USUARIO and clave == CLAVE:
            session['usuario'] = usuario
            return redirect('/dashboard')
        else:
            return 'Credenciales incorrectas'
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('dashboard.html', usuario=session['usuario'])

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

# Mapa con clientes
@app.route('/mapa')
def mapa():
    if 'usuario' not in session:
        return redirect('/login')
    clientes = obtener_clientes()
    return render_template('mapa.html', clientes=clientes)

# Ejecutar servidor
if __name__ == '__main__':
    app.run(debug=True)
