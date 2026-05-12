# JSON SCHEMA - Facturador Calculador

## Overview
Define la estructura exacta de los archivos JSON utilizados por la aplicación.

---

## 1. SCHEMA: april_2026.json (Mes Actual)

```json
{
  "mes": "April",                    // Nombre del mes en inglés
  "año": 2026,                       // Año numérico
  "mes_completo": "april_2026",      // Identificador único (lowercase_YYYY)
  
  "monto_estimado": 200000,          // Monto total a facturar en el mes
  
  "viernes": [
    {
      "fecha": "05/04/2026",         // DD/MM/YYYY del viernes
      "monto": 50000,                // Monto a facturar esa semana
      "codigo_facturacion": 55,      // Código de servicio (int)
      "estado": "PENDIENTE",         // PENDIENTE | PROCESADO | ERROR
      
      // Campos opcionales (solo si estado = PROCESADO)
      "cae": "974262938362",         // CAE de AFIP
      "nro_comprobante": "00001",    // Número de comprobante
      
      // Timing
      "timing": {
        "inicio_procesamiento": "2026-04-24T21:13:00.000000",    // ISO 8601
        "fin_procesamiento": "2026-04-24T21:13:45.000000",       // ISO 8601
        "duracion_segundos": 45,                                   // int
        "espera_proxima_segundos": 30                              // int
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
    // ... más viernes
  ],
  
  "estadisticas_procesamiento": {
    "fecha_facturacion": "2026-04-24",           // Fecha cuando se facturó (DD/MM/YYYY)
    "hora_inicio": "21:13:00",                   // HH:MM:SS
    "hora_fin": "21:15:15",                      // HH:MM:SS
    "tiempo_total_segundos": 135,                // int: total de segundos
    "duracion_promedio_por_factura": 34,         // int: segundos promedio
    "cantidad_exitosas": 4,                      // int
    "cantidad_errores": 0                        // int
  },
  
  "ultima_actualizacion": "2026-04-24T21:15:15"  // ISO 8601 timestamp
}
```

---

## 2. SCHEMA: precios_historico.json

```json
{
  "precios": [
    {
      "fecha_cambio": "2026-04-24T16:00:00",    // ISO 8601
      "precio_linea_codigo": 2.50                // float: precio en $/línea
    },
    {
      "fecha_cambio": "2026-04-24T15:45:00",
      "precio_linea_codigo": 2.00
    },
    {
      "fecha_cambio": "2026-04-20T10:15:00",
      "precio_linea_codigo": 1.50
    }
  ],
  
  "precio_actual": 2.50,                         // El último precio vigente
  "ultima_actualizacion": "2026-04-24T16:00:00"  // ISO 8601
}
```

---

## 3. SCHEMA: config.json (Configuración Global)

```json
{
  "version_app": "1.0.0",
  "fecha_creacion": "2026-04-24",
  
  "parametros_facturacion": {
    "punto_venta": 1,                    // Punto de venta AFIP
    "codigo_facturacion_default": 55,    // Default cuando se abre
    "cuit_cliente": "99999999999",       // Cliente consumidor final
    "nombre_cliente": "Consumidor Final"
  },
  
  "rutas": {
    "facturador_afip_path": "../facturador_afip",
    "facturas_csv": "../facturador_afip/Facturas/facturas.csv"
  },
  
  "datos_conceptos": [
    {
      "codigo": 55,
      "nombre": "Servicios informáticos y capacitación DB",
      "descripcion": "Servicios de asesoramiento y capacitación en base de datos"
    }
  ],
  
  "timeouts": {
    "procesamiento_factura_segundos": 300,    // 5 minutos
    "espera_entre_facturas_segundos": 30      // 30 segundos
  }
}
```

---

## 4. SCHEMA ERROR (error tracking)

Cuando hay un error en una factura:

```json
{
  "fecha": "05/04/2026",
  "monto": 50000,
  "codigo_facturacion": 55,
  "estado": "ERROR",
  
  "error": {
    "codigo": "TIMEOUT_AFIP",                   // Código único de error
    "mensaje": "Timeout esperando respuesta de AFIP",
    "detalles": "Facturador AFIP tardó más de 5 minutos",
    "fecha_error": "2026-04-24T21:20:00",
    "intento": 1,
    "reintentable": true
  },
  
  "timing": {
    "inicio_procesamiento": "2026-04-24T21:13:00",
    "duracion_segundos": 300,
    "razon_cierre": "TIMEOUT"
  }
}
```

---

## 5. TIPOS DE DATOS

| Campo | Tipo | Restricción | Ejemplo |
|-------|------|------------|---------|
| `mes` | string | Inglés, único | "April" |
| `año` | int | 2000-2100 | 2026 |
| `fecha` | string | DD/MM/YYYY | "05/04/2026" |
| `monto` | float/int | > 0 | 50000 |
| `codigo_facturacion` | int | 1-999 | 55 |
| `estado` | enum | PENDIENTE, PROCESADO, ERROR | "PROCESADO" |
| `cae` | string | 13 dígitos | "974262938362" |
| `duracion_segundos` | int | >= 0 | 45 |
| `precio_linea_codigo` | float | > 0 | 2.50 |
| `timestamp` | string | ISO 8601 | "2026-04-24T21:13:00" |

---

## 6. EJEMPLO COMPLETO: april_2026.json

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
      "nro_comprobante": "00001",
      "timing": {
        "inicio_procesamiento": "2026-04-24T21:13:00",
        "fin_procesamiento": "2026-04-24T21:13:45",
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
        "inicio_procesamiento": "2026-04-24T21:14:15",
        "fin_procesamiento": "2026-04-24T21:14:53",
        "duracion_segundos": 38,
        "espera_proxima_segundos": 30
      }
    },
    {
      "fecha": "19/04/2026",
      "monto": 48000,
      "codigo_facturacion": 55,
      "estado": "PENDIENTE",
      "timing": {}
    },
    {
      "fecha": "26/04/2026",
      "monto": 45000,
      "codigo_facturacion": 55,
      "estado": "PENDIENTE",
      "timing": {}
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
  },
  
  "ultima_actualizacion": "2026-04-24T21:14:53"
}
```

---

## 7. MIGRACIÓN ENTRE VERSIONES

Si la estructura cambia en futuras versiones:

```python
def migrar_json_v1_a_v2(datos_v1):
    """Migra schema v1 al v2"""
    datos_v2 = {
        "version": "2.0",
        "mes": datos_v1["mes"],
        "año": datos_v1["año"],
        # Agregar nuevos campos con defaults
        "flags": {
            "facturado_exitoso": True,
            "requiere_revision": False
        }
    }
    return datos_v2
```

---

## 8. VALIDACIÓN

### Validar al Cargar
```python
import json
from jsonschema import validate, ValidationError

SCHEMA = {
  "type": "object",
  "properties": {
    "mes": {"type": "string"},
    "año": {"type": "integer", "minimum": 2000, "maximum": 2100},
    "viernes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "fecha": {"type": "string", "pattern": "^\d{2}/\d{2}/\d{4}$"},
          "monto": {"type": "number", "minimum": 0},
          "estado": {"enum": ["PENDIENTE", "PROCESADO", "ERROR"]}
        },
        "required": ["fecha", "monto", "estado"]
      }
    }
  },
  "required": ["mes", "año", "viernes"]
}

def validar_mes_json(datos):
    try:
        validate(instance=datos, schema=SCHEMA)
        return True, None
    except ValidationError as e:
        return False, str(e)
```

---

## 9. ESTRUCTURA DE DIRECTORIOS DE JSON

```
facturador_calculador/data/
├── 2026/
│   ├── april_2026.json         ← Mes actual + completados
│   ├── may_2026.json           ← Mes futuro (se crea auto)
│   ├── march_2026.json         ← Mes anterior (consulta)
│   └── ...
├── 2025/
│   ├── december_2025.json
│   └── ...
└── config/
    ├── precios_historico.json   ← Histórico de cambios de precio
    └── config.json              ← Configuración global
```

---

## 10. LECTURA/ESCRITURA EN PYTHON

### Lectura
```python
import json
from pathlib import Path

def cargar_mes(mes, año):
    path = Path(f"data/{año}/{mes}_{año}.json")
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Uso
datos = cargar_mes("april", 2026)
print(datos["monto_estimado"])
```

### Escritura
```python
def guardar_mes(mes, año, datos):
    path = Path(f"data/{año}/{mes}_{año}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

# Uso
datos_actualizado = {...}
guardar_mes("april", 2026, datos_actualizado)
```

---

**Versión:** 1.0
**Formato:** JSON v1 (UTF-8)
**Encoding:** UTF-8 sin BOM
