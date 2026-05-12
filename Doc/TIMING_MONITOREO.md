# MONITOREO DE TIEMPOS - Facturador Calculador

## Requerimiento
Mostrar tiempos de procesamiento por cada factura y espera para la siguiente, sin identificar como "bot" sino como procesamiento automatizado del sistema.

---

## 1. DATOS A REGISTRAR POR FACTURA

Para cada factura se capturan:

```json
{
  "fecha": "05/04/2026",
  "monto": 50000,
  "codigo_facturacion": 55,
  "estado": "PROCESADO",
  "cae": "974262938362",
  
  "timing": {
    "inicio_procesamiento": "24/04/2026 21:13:00",    // Timestamp exacto
    "fin_procesamiento": "24/04/2026 21:13:45",       // Timestamp exacto
    "duracion_segundos": 45,                            // 45 segundos
    "espera_proxima_segundos": 30                       // Esperar 30seg antes de siguiente
  }
}
```

---

## 2. PANTALLA DE RESULTADOS CON TIEMPOS

### 2.1 Tabla de Facturas Emitidas

```
✅ FACTURAS YA EMITIDAS EN AFIP

┌────┬─────────┬────────┬──────────────────┬──────────┬──────────────┐
│Fec │ Monto   │Código  │ CAE              │ Duración │ Tipo         │
├────┼─────────┼────────┼──────────────────┼──────────┼──────────────┤
│5/4 │$50,000  │ 55     │974262938362      │ 45 seg   │ Procesado    │
│12/4│$52,000  │ 55     │790786905824      │ 38 seg   │ Procesado    │
│19/4│$48,000  │ 55     │123456789012      │ 52 seg   │ Procesado    │
│26/4│$45,000  │ 55     │345678901234      │ 41 seg   │ Procesado    │
└────┴─────────┴────────┴──────────────────┴──────────┴──────────────┘

⏱️ ESTADÍSTICAS DE PROCESAMIENTO:
   • Promedio por factura: 44 segundos
   • Más rápida: 38 segundos
   • Más lenta: 52 segundos
   • Tiempo total: 2 minutos 56 segundos
```

---

## 2.2 Detalles Expandibles

Al hacer click en una fila:

```
📌 FACTURA DEL 05/04/2026 - $50,000

Información:
├─ Monto: $50,000
├─ Código: 55 (Servicios informáticos)
├─ CAE: 974262938362
├─ NRO: 00001
└─ Estado: ✓ PROCESADO

⏱️ TIEMPO DE PROCESAMIENTO:
├─ Inicio:     14:13:00 (24/04/2026)
├─ Fin:        14:13:45 (24/04/2026)
├─ Duración:   45 segundos
├─ Espera:     30 segundos (antes de siguiente)
└─ Status:     Completado exitosamente

📝 Notas:
   Procesada por sistema automatizado en AFIP
```

---

## 3. PANTALLA EN VIVO DURANTE FACTURACIÓN

### 3.1 Mientras Se Facturan

```
🔄 FACTURANDO... (3/4 completadas)

COMPLETADAS:
║ 05/04 │ $50,000 │ CAE: 974262938362    │ 45 seg   ✓
║ 12/04 │ $52,000 │ CAE: 790786905824    │ 38 seg   ✓
║ 19/04 │ $48,000 │ CAE: 123456789012    │ 52 seg   ✓

EN PROCESO:
║ 26/04 │ $45,000 │ Generando...
║        Tiempo transcurrido: 35 seg
║        [Spinner animado]

PRÓXIMAS:  (ninguna)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tiempo total: 2 min 15 seg
Estimado restante: ~45 seg
```

---

## 4. LÓGICA DE TIMING EN BACKEND

### 4.1 Captura en app/utils.py

```python
import time
from datetime import datetime

def procesar_lote_facturas(viernes_data, callback=None):
    """
    Procesa facturas y captura tiempos
    callback: function para actualizar UI en vivo
    """
    
    resultados = []
    tiempo_inicial_lote = time.time()
    
    for idx, factura in enumerate(viernes_data):
        # Timestamp de inicio para THIS factura
        inicio = datetime.now()
        tiempo_inicio = time.time()
        
        print(f"[{idx+1}/{len(viernes_data)}] Iniciando: {factura['fecha']}")
        
        try:
            # Generar CSV temporal con SOLO esta factura
            generar_csv_solo_factura(factura)
            
            # Ejecutar facturador AFIP
            resultado = ejecutar_facturador_afip()
            
            # Leer CAE del resultado
            cae = extraer_cae_de_csv(resultado)
            
            # Timestamp de fin
            fin = datetime.now()
            tiempo_fin = time.time()
            duracion_segundos = round(tiempo_fin - tiempo_inicio)
            
            # Calcular espera (30 seg entre facturas, menos en la última)
            espera = 30 if idx < len(viernes_data) - 1 else 0
            
            # Guardar resultado
            resultado_factura = {
                'fecha': factura['fecha'],
                'monto': factura['monto'],
                'codigo': factura['codigo_facturacion'],
                'estado': 'PROCESADO',
                'cae': cae,
                'timing': {
                    'inicio_procesamiento': inicio.isoformat(),
                    'fin_procesamiento': fin.isoformat(),
                    'duracion_segundos': duracion_segundos,
                    'espera_proxima_segundos': espera
                }
            }
            
            resultados.append(resultado_factura)
            
            # Callback para actualizar UI en vivo
            if callback:
                callback({
                    'completadas': len(resultados),
                    'total': len(viernes_data),
                    'factura_actual': resultado_factura,
                    'en_espera': espera
                })
            
            # Esperar antes de siguiente
            if espera > 0:
                tiempo_espera_inicial = time.time()
                while time.time() - tiempo_espera_inicial < espera:
                    tiempo_restante = espera - (time.time() - tiempo_espera_inicial)
                    if callback and tiempo_restante > 0:
                        callback({
                            'completadas': len(resultados),
                            'total': len(viernes_data),
                            'esperando': round(tiempo_restante),
                            'proxima_factura': viernes_data[idx+1]
                        })
                    time.sleep(1)
        
        except Exception as e:
            resultado_factura = {
                'fecha': factura['fecha'],
                'monto': factura['monto'],
                'estado': 'ERROR',
                'error': str(e),
                'timing': {
                    'inicio_procesamiento': inicio.isoformat(),
                    'duracion_segundos': round(time.time() - tiempo_inicio)
                }
            }
            resultados.append(resultado_factura)
    
    tiempo_total = round(time.time() - tiempo_inicial_lote)
    
    return {
        'exitoso': True,
        'facturas': resultados,
        'estadisticas': {
            'total_procesadas': len([r for r in resultados if r['estado'] == 'PROCESADO']),
            'total_errores': len([r for r in resultados if r['estado'] == 'ERROR']),
            'tiempo_total_segundos': tiempo_total,
            'duracion_promedio': round(tiempo_total / len(viernes_data)) if viernes_data else 0
        }
    }
```

---

## 5. FRONTEND - WEBSOCKET PARA ACTUALIZACIÓN EN VIVO

### 5.1 HTML + JavaScript

```html
<div id="facturacion-viva" class="hidden">
  <div class="header">
    <h3>🔄 FACTURANDO...</h3>
    <span id="contador-vivo">0/4 completadas</span>
  </div>
  
  <div id="tabla-en-vivo">
    <!-- Se rellena dinámicamente -->
  </div>
  
  <div id="espera-info" class="hidden">
    <p>Esperando <span id="espera-countdown">30</span>s antes de siguiente...</p>
  </div>
</div>

<script>
// WebSocket para recibir actualizaciones en tiempo real
const ws = new WebSocket('ws://localhost:5000/api/facturas/procesar-vivo');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  if (data.completadas !== undefined) {
    document.getElementById('contador-vivo').textContent = 
      `${data.completadas}/${data.total} completadas`;
    
    // Agregar fila a la tabla
    agregarFilaFactura(data.factura_actual, data.duracion_segundos);
  }
  
  if (data.esperando !== undefined) {
    document.getElementById('espera-countdown').textContent = data.esperando;
  }
};
</script>
```

---

## 6. JSON RESULTANTE (en april_2026.json)

```json
{
  "mes": "April",
  "año": 2026,
  "mes_completo": "april_2026",
  "monto_estimado": 200000,
  "viernes": [
    {
      "fecha": "05/04/2026",
      "monto": 50000,
      "codigo_facturacion": 55,
      "estado": "PROCESADO",
      "cae": "974262938362",
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
    "hora_fin": "21:15:15",
    "tiempo_total_segundos": 135,
    "duracion_promedio_por_factura": 34,
    "mes_con_mayor_tiempo": "Viernes 19",
    "mes_con_menor_tiempo": "Viernes 12"
  }
}
```

---

## 7. NO MOSTRAR COMO "BOT"

### 7.1 Forma INCORRECTA (no hacer):
```
❌ "Factura generada por bot"
❌ "Procesada automáticamente por bot AFIP"
❌ "Bot facturador"
```

### 7.2 Forma CORRECTA (hacer):
```
✓ "Procesada por sistema"
✓ "Generada automáticamente"
✓ "Procesada por sistema automatizado de AFIP"
✓ "Completada mediante procesamiento automático"
✓ "Emitida automáticamente"
```

### 7.3 En UI:
```
Label: "✓ PROCESADO" (neutral)
NO: "✓ BOT executed"

Status: "Completada exitosamente"
NO: "Bot completed"

Generada: "Sistema automatizado"
NO: "Bot generated"
```

---

## 8. API ENDPOINT

### 8.1 POST /api/facturas/procesar

```javascript
POST /api/facturas/procesar
Content-Type: application/json

{
  "viernes": [
    {
      "fecha": "05/04/2026",
      "monto": 50000,
      "codigo_facturacion": 55
    }
  ],
  "callback_type": "websocket"  // o "polling"
}

Response:
{
  "success": true,
  "facturas_procesadas": [
    {
      "fecha": "05/04/2026",
      "monto": 50000,
      "cae": "974262938362",
      "timing": {
        "duracion_segundos": 45,
        "inicio_procesamiento": "2026-04-24T21:13:00",
        "fin_procesamiento": "2026-04-24T21:13:45"
      }
    }
  ],
  "estadisticas": {
    "total_segundos": 135,
    "promedio_por_factura": 34
  }
}
```

---

## 9. ALERTAS POR TIMING

Si una factura tarda anormalmente:

```
⚠️ ALERTA: Factura del 05/04 tardó 2 minutos (inusual)
   Promedio normalmente: 45 segundos
   Recomendación: Revisar conexión AFIP
```

Si es muy rápida (posible copia):
```
⚠️ ALERTA: Factura procesada en 5 segundos (muy rápido)
   Revisar que CAE sea válido
```

---

**Versión:** 1.0
**Status:** Especificación completa de timing
