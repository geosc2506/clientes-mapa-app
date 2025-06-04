from flask import Flask, render_template, request, redirect, session
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)
app.secret_key = 'secreto123'  # Cambiar en producción

# Credenciales fijas
USUARIO = 'geo'
CLAVE = 'akira'

# Función para leer datos desde Google Sheets
def obtener_clientes():
    try:
        url = "https://docs.google.com/spreadsheets/d/1YCEuaC-E-pSPsT-VnitCDBT5cc5k_qh3_2wxtbTuCOs/export?format=csv"
        response = requests.get(url)
        response.raise_for_status()

        df = pd.read_csv(StringIO(response.text))

        # Asegura columnas esperadas
        columnas = ['nombre', 'direccion', 'latitud', 'longitud', 'distrito', 'telefono']
        for col in columnas:
            if col not in df.columns:
                df[col] = ''

        return df.to_dict(orient='records')
    except Exception as e:
        print("❌ Error al cargar clientes:", e)
        return []

# Rutas
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect('/dashboard')
    return redirect('/login')

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

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('dashboard.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

@app.route('/mapa')
def mapa():
    if 'usuario' not in session:
        return redirect('/login')
    clientes = obtener_clientes()
    return render_template('mapa.html', clientes=clientes)

if __name__ == '__main__':
    app.run(debug=True)
