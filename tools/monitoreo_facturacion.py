import json
from pathlib import Path
from datetime import datetime

# Ruta al JSON de planificación
JSON_PATH = Path("..") / "data" / "2026" / "april_2026.json"

# Cargar datos
with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

facturas = data.get("facturas", [])

hoy = datetime.now().date()
pendientes = []
vencidas = []
errores = []

for f in facturas:
    estado = f.get("estado", "").lower()
    fecha_plan = f.get("fecha_planificada", "")
    cae = f.get("cae", "")
    try:
        fecha_plan_dt = datetime.strptime(fecha_plan, "%Y-%m-%d").date()
    except Exception:
        fecha_plan_dt = None
    if estado == "pendiente":
        pendientes.append(f)
        if fecha_plan_dt and fecha_plan_dt < hoy:
            vencidas.append(f)
    if estado == "emitida" and not cae:
        errores.append(f)

print("\n--- MONITOREO DE FACTURACIÓN ---")
print(f"Facturas pendientes: {len(pendientes)}")
if pendientes:
    for f in pendientes:
        print(f"  - {f.get('cliente','')} | {f.get('concepto','')} | Planificada: {f.get('fecha_planificada','')}")
print(f"Facturas vencidas (no emitidas a tiempo): {len(vencidas)}")
if vencidas:
    for f in vencidas:
        print(f"  - {f.get('cliente','')} | {f.get('concepto','')} | Planificada: {f.get('fecha_planificada','')}")
print(f"Facturas emitidas SIN CAE: {len(errores)}")
if errores:
    for f in errores:
        print(f"  - {f.get('cliente','')} | {f.get('concepto','')} | Fecha emisión: {f.get('fecha_emision','')}")
print("--- FIN DEL MONITOREO ---\n")
