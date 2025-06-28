from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd
import requests
from io import StringIO
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secreto123'  # Cambia esto en producción

# ====================================
# 🔐 Múltiples usuarios permitidos
# ====================================
USUARIOS = {
    'geo': 'akira',
    'campo': '1234',
    'admin': 'adminpass'
}

# ====================================
# 🔄 Función para obtener clientes CSV
# ====================================
def obtener_clientes():
    try:
        url = "https://docs.google.com/spreadsheets/d/1YCEuaC-E-pSPsT-VnitCDBT5cc5k_qh3_2wxtbTuCOs/export?format=csv"
        response = requests.get(url)
        response.raise_for_status()

        df = pd.read_csv(StringIO(response.text))

        # Normalizar nombres de columnas
        df.rename(columns=lambda x: x.strip().replace(" ", "_").lower(), inplace=True)

        columnas = ['nombre', 'direccion', 'latitud', 'longitud', 'distrito', 'telefono',
                    'estado', 'prioridad', 'procesal', 'contactabilidad', 'negocio',
                    'asesor', 'nro_asesor', 'id_deudor']

        for col in columnas:
            if col not in df.columns:
                df[col] = ''

        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df = df.dropna(subset=['latitud', 'longitud'])

        for col in ['estado', 'prioridad', 'procesal', 'contactabilidad', 'negocio', 'asesor', 'nro_asesor']:
            df[col] = df[col].astype(str).str.strip().str.lower()

        return df.to_dict(orient='records')

    except Exception as e:
        print("❌ Error al cargar clientes:", e)
        return []

# ==============================
# 🔐 Sistema de autenticación
# ==============================
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
        if usuario in USUARIOS and clave == USUARIOS[usuario]:
            session['usuario'] = usuario
            return redirect('/dashboard')
        return 'Credenciales incorrectas'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('dashboard.html', usuario=session['usuario'])

# ====================================
# 📍 Ruta principal del mapa
# ====================================
@app.route('/mapa')
def mapa():
    if 'usuario' not in session:
        return redirect('/login')

    clientes = obtener_clientes()

    prioridades = sorted(set(c['prioridad'].lower() for c in clientes if c.get('prioridad')))
    procesales = sorted(set(c['procesal'].lower() for c in clientes if c.get('procesal')))
    contactabilidades = sorted(set(c['contactabilidad'].lower() for c in clientes if c.get('contactabilidad')))
    negocios = sorted(set(c['negocio'].lower() for c in clientes if c.get('negocio')))

    return render_template(
        'mapa.html',
        clientes=clientes,
        prioridades=prioridades,
        procesales=procesales,
        contactabilidades=contactabilidades,
        negocios=negocios
    )

# ===========================
# 🧪 Ruta de depuración JSON
# ===========================
@app.route('/debug-clientes')
def debug_clientes():
    clientes = obtener_clientes()
    return jsonify(clientes)

# =============================================
# 📤 Ruta para guardar ubicación en Google Sheet
# =============================================
@app.route('/guardar-ubicacion', methods=['POST'])
def guardar_ubicacion():
    data = request.get_json()
    lat = data.get("latitud")
    lng = data.get("longitud")
    user = session.get("usuario", "anónimo")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open("credenciales.json") as f:
            credenciales = json.load(f)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales, scope)
        client = gspread.authorize(creds)

        sheet = client.open_by_key("1Y1Vw_-ij3-hWYam1nG8R30uhbX6PNUyvcdoUQN9WfE0").sheet1
        sheet.append_row([fecha, user, lat, lng])

        return jsonify({"ok": True})
    except Exception as e:
        print("❌ Error al guardar ubicación:", e)
        return jsonify({"error": "No se pudo guardar"}), 500

# ===========================
# 🚀 Ejecutar servidor local
# ===========================
if __name__ == '__main__':
    app.run(debug=True)
