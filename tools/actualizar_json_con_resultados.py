import json
import csv
from pathlib import Path

# Rutas de archivos
JSON_PATH = Path("..") / "data" / "2026" / "april_2026.json"
FACTURAS_CSV = Path("facturas.csv")

# Cargar JSON de planificación
with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

# Indexar facturas por (fecha, monto, cuit, cliente) para emparejar
facturas_json = data.get("facturas", [])
index = {}
for f in facturas_json:
    key = (
        f.get("fecha_planificada"),
        float(f.get("monto", 0)),
        f.get("cuit"),
        f.get("cliente")
    )
    index[key] = f

# Leer facturas.csv y actualizar JSON
with open(FACTURAS_CSV, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (
            row["FECHA"],
            float(row["PRECIO UNITARIO"]),
            row["CUIT_CLIENTE"],
            row["NOMBRE_CLIENTE"]
        )
        if key in index:
            factura = index[key]
            factura["estado"] = row["ESTADO"].lower()
            factura["cae"] = row.get("CAE", "")
            factura["nro_comprobante"] = row.get("NRO_COMPROBANTE", "")
            factura["fecha_emision"] = row["FECHA"]

# Guardar JSON actualizado
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] JSON actualizado con resultados de facturación: {JSON_PATH}")
