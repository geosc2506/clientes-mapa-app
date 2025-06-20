import pandas as pd
import requests
from io import StringIO

# URL de tu Google Sheet
url = "https://docs.google.com/spreadsheets/d/1YCEuaC-E-pSPsT-VnitCDBT5cc5k_qh3_2wxtbTuCOs/export?format=csv"

# Descargar CSV
response = requests.get(url)
response.raise_for_status()

# Leer CSV
df = pd.read_csv(StringIO(response.text), dtype=str)

# Obtener lista de columnas
cols = df.columns.tolist()

# Mostrar total de columnas
print(f"\n📋 Total columnas: {len(cols)}\n")

# Detectar columnas vacías (sin nombre)
empty_cols = [i for i, c in enumerate(cols) if not c.strip()]
if empty_cols:
    print(f"🚨 Columnas vacías (sin nombre): {empty_cols}")
else:
    print("✅ No hay columnas vacías")

# Detectar columnas duplicadas
dups = df.columns[df.columns.duplicated()].unique()
if len(dups) > 0:
    print(f"🚨 Columnas duplicadas: {dups.tolist()}")
else:
    print("✅ No hay columnas duplicadas")

# Mostrar nombres de columnas
print("\n📝 Nombres de columnas recibidas:")
for i, col in enumerate(cols):
    print(f"{i}: {repr(col)}")
