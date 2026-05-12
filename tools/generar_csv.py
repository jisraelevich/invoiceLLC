import json
import csv
from pathlib import Path

# Ruta de ejemplo para el JSON de entrada (ajusta si lo necesitas)
JSON_PATH = Path("..") / "data" / "2026" / "april_2026.json"
# Ruta de salida para el CSV generado
CSV_PATH = Path("..") / "Facturas" / "facturas_test.csv"

# Configuración por defecto
CODIGO_DEFECTO = 55
CONCEPTO_DEFECTO = "servicios informatiicos y capacitacion DB"
CUIT_DEFECTO = "99999999999"
NOMBRE_DEFECTO = "Consumidor Final"

HEADER = [
    "FECHA","CODIGO","PRODUCTO SERVICO:","PRECIO UNITARIO",
    "CUIT_CLIENTE","NOMBRE_CLIENTE","ESTADO","CAE","NRO_COMPROBANTE"
]

def main():
    if not JSON_PATH.exists():
        print(f"[ERROR] No se encontró el JSON de entrada: {JSON_PATH}")
        return
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    facturas = data.get("facturas", [])
    pendientes = [v for v in facturas if v.get("estado", "").lower() == "pendiente"]
    if not pendientes:
        print("No hay facturas pendientes en el JSON.")
        return
    # Asegura que el directorio de salida exista
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for v in pendientes:
            writer.writerow([
                v.get("fecha_planificada"),
                v.get("codigo_facturacion", CODIGO_DEFECTO),
                v.get("concepto", CONCEPTO_DEFECTO),
                v.get("monto"),
                v.get("cuit", CUIT_DEFECTO),
                v.get("cliente", NOMBRE_DEFECTO),
                "PENDIENTE", "", ""
            ])
    print(f"[OK] CSV generado: {CSV_PATH} ({len(pendientes)} filas)")

    # Integración: copiar/conformar a facturas.csv para facturador_afip
    FACTURADOR_CSV = Path("facturas.csv")
    with open(CSV_PATH, encoding="utf-8-sig") as src, open(FACTURADOR_CSV, "w", newline='', encoding="utf-8-sig") as dst:
        for line in src:
            # Convierte estado a mayúsculas para compatibilidad
            if ",pendiente," in line:
                line = line.replace(",pendiente,", ",PENDIENTE,")
            dst.write(line)
    print(f"[OK] facturas.csv actualizado para facturador_afip ({len(pendientes)} filas)")

if __name__ == "__main__":
    main()
