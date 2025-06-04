from flask import Flask, render_template, request, redirect, session
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)
app.secret_key = 'secreto123'  # Reemplazar por una clave segura

USUARIO = 'geo'
CLAVE = 'akira'

def obtener_clientes():
    try:
        url = "https://docs.google.com/spreadsheets/d/1YCEuaC-E-pSPsT-VnitCDBT5cc5k_qh3_2wxtbTuCOs/export?format=csv"
        response = requests.get(url)
        response.raise_for_status()  # Lanza error si no carga

        df = pd.read_csv(StringIO(response.text))

        columnas = ['nombre', 'direccion', 'latitud', 'longitud', 'distrito', 'telefono']
        for col in columnas:
            if col not in df.columns:
                df[col] = ''

        # Asegura que lat y lng sean números
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')

        return df.dropna(subset=['latitud', 'longitud']).to_dict(orient='records')

    except Exception as e:
        print("❌ Error al obtener clientes:", e)
        return []

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['clave'] == CLAVE:
            session['usuario'] = request.form['usuario']
            return redirect('/dashboard')
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
