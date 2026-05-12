# PLAN DE INTEGRACIÓN - Calculador ↔ Facturador AFIP

## Objetivo
Integrar facturador_calculador con facturador_afip manteniendo ambos desacoplados.

---

## 1. ARQUITECTURA GENERAL

```
┌──────────────────────────────────────┐
│ FACTURADOR CALCULADOR                │
│ (Nuevo proyecto)                     │
│ - Flask web                          │
│ - Gestiona JSON (april_2026.json)    │
│ - Interfaz usuario                   │
└──────────────────────────────────────┘
              │
              │ (Interface: CSV)
              │
              ↓
       [facturas.csv]
    (Intermediario compartido)
              ↑
              │ (Interface: CSV)
              │
┌──────────────────────────────────────┐
│ FACTURADOR AFIP                      │
│ (Existente - NO MODIFICAR)           │
│ - Python async/await                 │
│ - Genera facturas en AFIP            │
│ - Lee/escribe CSV                    │
└──────────────────────────────────────┘
```

---

## 2. FLUJO COMPLETO DE FACTURACIÓN

### 2.1 Estado Inicial (Usuario en Calculador)

```
april_2026.json
{
  "viernes": [
    {"fecha": "05/04/2026", "monto": 50000, "estado": "PENDIENTE", ...},
    {"fecha": "12/04/2026", "monto": 52000, "estado": "PENDIENTE", ...},
  ]
}

facturas.csv (vacío o con datos anteriores)
```

### 2.2 Usuario Clickea "APROBAR Y FACTURAR"

```python
# CALCULADOR - app/routes.py

@app.route('/api/facturas/procesar', methods=['POST'])
def procesar_facturas():
    """Coordina facturación entre calculador y facturador_afip"""
    
    import time
    import subprocess
    from datetime import datetime
    
    # ========================================
    # PASO 1: Obtener datos del mes
    # ========================================
    mes_data = MesData.cargar_mes("april", 2026)
    viernes_pendientes = [f for f in mes_data["viernes"] 
                          if f["estado"] == "PENDIENTE"]
    
    if not viernes_pendientes:
        return {"error": "No hay facturas pendientes"}, 400
    
    # ========================================
    # PASO 2: Generar CSV en MEMORIA
    # ========================================
    csv_lineas = [
        "FECHA,CODIGO,PRODUCTO SERVICO:,PRECIO UNITARIO,CUIT_CLIENTE,NOMBRE_CLIENTE,ESTADO,CAE,NRO_COMPROBANTE"
    ]
    
    for viernes in viernes_pendientes:
        linea = (
            f"{viernes['fecha']},"
            f"{viernes['codigo_facturacion']},"
            f"servicios informatiicos y capacitacion DB,"
            f"{viernes['monto']},"
            f"99999999999,"
            f"Consumidor Final,"
            f"PENDIENTE,,"
        )
        csv_lineas.append(linea)
    
    csv_contenido = "\n".join(csv_lineas)
    
    # ========================================
    # PASO 3: Escribir CSV en facturador_afip
    # ========================================
    ruta_csv = Path("../facturador_afip/Facturas/facturas.csv")
    with open(ruta_csv, 'w', encoding='utf-8-sig') as f:
        f.write(csv_contenido)
    
    logger.info(f"CSV generado: {ruta_csv} con {len(viernes_pendientes)} filas")
    
    # ========================================
    # PASO 4: Ejecutar facturador_afip
    # ========================================
    tiempo_inicio_total = time.time()
    
    try:
        resultado = subprocess.run(
            [sys.executable, "../facturador_afip/main.py", "--ahora"],
            capture_output=True,
            timeout=300,  # 5 minutos
            cwd="../facturador_afip"
        )
        
        if resultado.returncode != 0:
            error_msg = resultado.stderr.decode('utf-8', errors='ignore')
            logger.error(f"Facturador AFIP error: {error_msg}")
            return {
                "error": "Facturador AFIP falló",
                "detalles": error_msg
            }, 500
        
        logger.info("Facturador AFIP completó exitosamente")
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout esperando facturador AFIP (5 min)")
        return {
            "error": "Timeout facturando (más de 5 minutos)"
        }, 504
    
    # ========================================
    # PASO 5: Leer CSV resultado
    # ========================================
    facturas_procesadas = []
    
    with open(ruta_csv, 'r', encoding='utf-8-sig') as f:
        lineas = f.readlines()
    
    # Saltar header
    for linea in lineas[1:]:
        campos = linea.strip().split(',')
        
        if len(campos) >= 9:
            fecha_csv = campos[0]
            cae_csv = campos[7]
            nro_csv = campos[8]
            estado_csv = campos[6]
            
            if estado_csv == "PROCESADO" and cae_csv:
                facturas_procesadas.append({
                    "fecha": fecha_csv,
                    "cae": cae_csv,
                    "nro": nro_csv,
                    "estado": "PROCESADO"
                })
    
    logger.info(f"Procesadas {len(facturas_procesadas)} facturas")
    
    # ========================================
    # PASO 6: Actualizar JSON con timing
    # ========================================
    for factura_procesada in facturas_procesadas:
        for viernes in mes_data["viernes"]:
            if viernes["fecha"] == factura_procesada["fecha"]:
                
                # Calcula timing (aproximado)
                tiempo_duracion = round(
                    (time.time() - tiempo_inicio_total) / len(facturas_procesadas)
                )
                
                # Actualiza viernes
                viernes["estado"] = "PROCESADO"
                viernes["cae"] = factura_procesada["cae"]
                viernes["nro_comprobante"] = factura_procesada["nro"]
                viernes["timing"] = {
                    "inicio_procesamiento": datetime.now().isoformat(),
                    "fin_procesamiento": datetime.now().isoformat(),
                    "duracion_segundos": tiempo_duracion,
                    "espera_proxima_segundos": 0
                }
    
    # ========================================
    # PASO 7: Guardar JSON actualizado
    # ========================================
    tiempo_total_segundos = round(time.time() - tiempo_inicio_total)
    
    mes_data["estadisticas_procesamiento"] = {
        "fecha_facturacion": datetime.now().strftime("%Y-%m-%d"),
        "hora_inicio": datetime.now().strftime("%H:%M:%S"),
        "hora_fin": datetime.now().strftime("%H:%M:%S"),
        "tiempo_total_segundos": tiempo_total_segundos,
        "duracion_promedio_por_factura": round(
            tiempo_total_segundos / len(facturas_procesadas)
        ) if facturas_procesadas else 0,
        "cantidad_exitosas": len(facturas_procesadas),
        "cantidad_errores": 0
    }
    
    MesData.guardar_mes("april", 2026, mes_data)
    
    logger.info(f"JSON actualizado con {len(facturas_procesadas)} facturas procesadas")
    
    # ========================================
    # PASO 8: Retornar al frontend
    # ========================================
    return {
        "success": True,
        "facturas_procesadas": facturas_procesadas,
        "estadisticas": mes_data["estadisticas_procesamiento"],
        "tiempo_total_segundos": tiempo_total_segundos
    }, 200
```

---

## 3. JSON RESULTANTE (april_2026.json)

### 3.1 Antes
```json
{
  "viernes": [
    {
      "fecha": "05/04/2026",
      "monto": 50000,
      "codigo_facturacion": 55,
      "estado": "PENDIENTE"
    }
  ]
}
```

### 3.2 Después (COMPLETO CON TIEMPOS)
```json
{
  "mes": "April",
  "año": 2026,
  "viernes": [
    {
      "fecha": "05/04/2026",
      "monto": 50000,
      "codigo_facturacion": 55,
      "estado": "PROCESADO",
      "cae": "974262938362",
      "nro_comprobante": "00001",
      "timing": {
        "inicio_procesamiento": "2026-04-24T21:13:00.000000",
        "fin_procesamiento": "2026-04-24T21:13:45.000000",
        "duracion_segundos": 45,
        "espera_proxima_segundos": 30
      }
    },
    {
      "fecha": "12/04/2026",
      "monto": 52000,
      "codigo_facturacion": 55,
      "estado": "PROCESADO",
      "cae": "790786905824",
      "nro_comprobante": "00001",
      "timing": {
        "inicio_procesamiento": "2026-04-24T21:14:15.000000",
        "fin_procesamiento": "2026-04-24T21:14:53.000000",
        "duracion_segundos": 38,
        "espera_proxima_segundos": 30
      }
    }
  ],
  "estadisticas_procesamiento": {
    "fecha_facturacion": "2026-04-24",
    "hora_inicio": "21:13:00",
    "hora_fin": "21:14:53",
    "tiempo_total_segundos": 113,
    "duracion_promedio_por_factura": 56,
    "cantidad_exitosas": 2,
    "cantidad_errores": 0
  }
}
```

---

## 4. ARCHIVOS CSV INTERMEDIARIOS

### 4.1 CSV Generado por Calculador (ENTRADA)

```
FECHA,CODIGO,PRODUCTO SERVICO:,PRECIO UNITARIO,CUIT_CLIENTE,NOMBRE_CLIENTE,ESTADO,CAE,NRO_COMPROBANTE
05/04/2026,55,servicios informatiicos y capacitacion DB,50000,99999999999,Consumidor Final,PENDIENTE,,
12/04/2026,55,servicios informatiicos y capacitacion DB,52000,99999999999,Consumidor Final,PENDIENTE,,
```

### 4.2 CSV Procesado por Facturador AFIP (SALIDA)

```
FECHA,CODIGO,PRODUCTO SERVICO:,PRECIO UNITARIO,CUIT_CLIENTE,NOMBRE_CLIENTE,ESTADO,CAE,NRO_COMPROBANTE
05/04/2026,55,servicios informatiicos y capacitacion DB,50000,99999999999,Consumidor Final,PROCESADO,974262938362,00001
12/04/2026,55,servicios informatiicos y capacitacion DB,52000,99999999999,Consumidor Final,PROCESADO,790786905824,00001
```

---

## 5. MANEJO DE ERRORES

### 5.1 Si falla facturador_afip

```python
except subprocess.TimeoutExpired:
    # JSON NO se actualiza
    # Retorna error al frontend
    return {"error": "Timeout", "duración": 300}, 504

except Exception as e:
    # JSON NO se actualiza
    return {"error": str(e)}, 500
```

### 5.2 Si facturador_afip procesa PARCIAL

```python
# Ej: Procesa 2 de 4 facturas

facturas_procesadas = [
    {"fecha": "05/04", "cae": "974..."},  # OK
    {"fecha": "12/04", "cae": "790..."}   # OK
    # Falta 19/04 y 26/04
]

# Se actualiza JSON SOLO con las que están en PROCESADO
# Las otras quedan en PENDIENTE

mes_data["estadisticas_procesamiento"]["cantidad_exitosas"] = 2
mes_data["estadisticas_procesamiento"]["cantidad_errores"] = 2
```

---

## 6. VENTAJAS DE ESTE PLAN

✅ **Desacoplamiento total**
   - Calculador NO necesita saber cómo funciona facturador_afip
   - Facturador_afip NO necesita saber de calculador

✅ **Histórico en JSON**
   - Todos los tiempos guardados
   - Auditoría completa
   - Consultable por mes/año

✅ **CSV como contrato**
   - Interfaz clara entre sistemas
   - Fácil debuggear (exportar CSV)
   - Compatible con ambos sistemas

✅ **Robusto**
   - Si falla uno, el otro sigue funcionando
   - Reintentos manuales posibles
   - Logs claros

✅ **Sin modificar facturador_afip**
   - Sistema existente sigue igual
   - Probado y confiable
   - Cero cambios = cero riesgo

---

## 7. TECNOLOGÍAS

### Calculador necesita:
- Python 3.x
- Flask (web)
- pathlib (archivo CSV)
- subprocess (ejecutar facturador_afip)
- json (guardar histórico)
- datetime (tiempos)

### Facturador AFIP:
- YA EXISTE, no tocar

---

## 8. IMPLEMENTACIÓN PASO A PASO

### Fase 1: Backend
- [ ] Crear función `generar_csv_desde_json()`
- [ ] Crear función `parsear_csv_resultado()`
- [ ] Crear endpoint POST `/api/facturas/procesar`
- [ ] Manejar errores con try/except

### Fase 2: Frontend
- [ ] Spinner durante facturación
- [ ] Mostrar tabla de resultados
- [ ] Mostrar tiempos
- [ ] Actualizar JSON en pantalla

### Fase 3: Testing
- [ ] Mock de facturador_afip
- [ ] Prueba con 1 factura
- [ ] Prueba con 4 facturas
- [ ] Prueba de timeout

---

## 9. ARCHIVO DE CONFIGURACIÓN

### app/config.py

```python
import os
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent.parent
FACTURADOR_AFIP_PATH = BASE_DIR.parent / "facturador_afip"
FACTURAS_CSV_PATH = FACTURADOR_AFIP_PATH / "Facturas" / "facturas.csv"
DATA_DIR = BASE_DIR / "data"

# Timeouts
SUBPROCESS_TIMEOUT = 300  # 5 minutos
ESPERA_ENTRE_FACTURAS = 30  # 30 segundos

# Configuración AFIP
AFIP_PUNTO_VENTA = 1
AFIP_CUIT_CLIENTE = "99999999999"
AFIP_NOMBRE_CLIENTE = "Consumidor Final"

# Conceptos
CONCEPTOS_FACTURACION = {
    55: "Servicios informáticos y capacitación DB"
}
```

---

## CONCLUSIÓN

**CSV es el puente temporal entre ambos sistemas.**
**JSON es el histórico permanente del calculador.**
**Tiempos se capturan en ambos lugares (para auditoría).**

¿Confirmás este plan para empezar a codificar?

