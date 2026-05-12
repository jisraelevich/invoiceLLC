# ESPECIFICACIONES - Facturador Calculador

## Visión General
Aplicación web Flask para calcular y gestionar facturas mensuales antes de enviarlas al sistema AFIP.

**Estado:** En diseño / Por iniciar
**Fecha:** Abril 2026
**Público:** Usuario facturador

---

## 1. FUNCIONALIDAD PRINCIPAL

### 1.1 Dashboard por Mes
- **Acceso:** Se abre la app en el mes actual (ej: April 2026)
- **Autonavío:** El mes anterior se carga automáticamente en JSON si no existe
- **Tab switching:** Dropdown para revisar meses anteriores
- **Persistencia:** Todo guardado en JSON por mes/año

### 1.2 Panel de Control (Top)

```
📊 RESUMEN DEL MES
┌─────────────────────────────────────────┐
│ Monto Estimado a Facturar: [$_________] │
│                                         │
│ • Facturado:   XXX,XXX (XX%)  ████░░   │
│ • Pendiente:   XXX,XXX (XX%)  ██░░░░   │
│ • Estimado:    XXX,XXX                 │
│                                         │
│ ⚠️  ADVERTENCIA:                        │
│    [Indicador de validación]            │
└─────────────────────────────────────────┘
```

**Lógica:**
- Input de monto estimado (guardar en JSON)
- Lee facturas.csv para obtener "Facturado"
- Calcula "Pendiente" = Estimado - Facturado
- Muestra % de avance
- **ALERTA:** Si pendiente + input > estimado → Mostrar warning en ROJO

---

## 2. ENTRADA DE DATOS

### 2.1 Textarea: Pegue de Datos
```
📝 PEGAR DATOS DE FACTURAS (una por línea)
Formato: FECHA MONTO [TIPO]

Ejemplo:
5/2/2026 65000
5/3/2026 78000
5/12/2026 103000

[TEXTAREA para pegar datos]

[PARSE] - Procesar datos
```

**Funcionamiento:**
- Usuario pega líneas con: FECHA MONTO [TIPO opcionalal]
- Default tipo: 55 (Servicios informáticos y capacitación DB)
- Clickea [PARSE] para procesar
- Sistema parsea cada línea y extrae: fecha, monto, tipo
- Los valores se guardan EN VIVO en JSON (onChange)

---

## 3. CÁLCULO Y PREVISUALIZACIÓN

### 3.1 Botón "Calcular y Previsualizar"
Genera grilla de facturas PENDIENTES que se facturarán.

**Entrada:**
- 4 montos ingresados
- 4 códigos seleccionados

**Salida:**
```
📊 GRILLA DE FACTURAS PENDIENTES (PREVIEW)

┌────────┬──────────┬───────┬──────────────────────┐
│ Fecha  │ Monto    │ Código│ Concepto             │
├────────┼──────────┼───────┼──────────────────────┤
│05/04   │ $50,000  │  55   │ Servicios informáticos
│12/04   │ $52,000  │  55   │ Servicios informáticos
│19/04   │ $48,000  │  55   │ Servicios informáticos
│26/04   │ $45,000  │  55   │ Servicios informáticos
└────────┴──────────┴───────┴──────────────────────┘

Total: $195,000 (Dentro del estimado ✓)
```

---

## 4. APROBACIÓN Y FACTURACIÓN

### 4.1 Botones de Acción
- **[← EDITAR]** → Vuelve a inputs, cancela preview
- **[✓ APROBAR Y FACTURAR]** → Ejecuta facturación

### 4.2 Proceso de Facturación
1. Genera CSV temporal o usa `facturas.csv` del facturador_afip
2. Llama a FacturarAhora.bat (ejecutable desde Python)
3. Espera resultado
4. Refleja facturas procesadas en tab "RESULTADOS"

---

## 5. RESULTADOS (FACTURAS PROCESADAS)

```
✅ FACTURAS YA EMITIDAS EN AFIP

┌────────┬──────────┬───────┬──────────────────────┬──────────────┐
│ Fecha  │ Monto    │ Código│ Concepto             │ CAE          │
├────────┼──────────┼───────┼──────────────────────┼──────────────┤
│24/04   │ $58,000  │  55   │ Servicios informáticos│ 974262938362
│24/04   │ $64,000  │  55   │ Servicios informáticos│ 790786905824
└────────┴──────────┴───────┴──────────────────────┴──────────────┘
```

Datos extraídos de:
- Facturas con `ESTADO = PROCESADO` en facturas.csv
- Se actualiza después de facturar

---

## 6. ADMIN TAB

### 6.1 Gestión de Precios
```
⚙️ ADMINISTRACIÓN

Precio por Línea de Código:  [__________] $/línea
[Guardar]

📜 Histórico de Precios
┌──────────────┬──────────┐
│ Fecha        │ Precio   │
├──────────────┼──────────┤
│ 24/04/2026   │ $2.00    │
│ 20/04/2026   │ $1.50    │
│ 15/03/2026   │ $1.50    │
└──────────────┴──────────┘
```

**Lógica:**
- Input permitido
- Click "Guardar" → Guarda nuevo precio + fecha de modificación en JSON
- Muestra últimos 10 cambios
- El "último disponible" se usa por defecto en calculadora (futura extensión)

---

## 7. NAVEGACIÓN ENTRE MESES

### 7.1 Selector de Mes
```
[Ver Mes: April 2026 ▼]

Dropdown:
- April 2026   (actual)
- March 2026
- February 2026
- ...
```

**Comportamiento:**
- Carga tab anterior → `march_2026.json`
- Ver datos históricos sin modificar
- Cambios siempre en mes actual

---

## 8. PERSISTENCIA DE DATOS (JSON)

### 8.1 Estructura de Archivos
```
facturador_calculador/
├── data/
│   ├── 2026/
│   │   ├── april_2026.json
│   │   ├── may_2026.json
│   │   └── ...
│   └── config/
│       └── precios_historico.json
```

### 8.2 Formato april_2026.json
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
      "estado": "PENDIENTE"
    },
    {
      "fecha": "12/04/2026",
      "monto": 52000,
      "codigo_facturacion": 55,
      "estado": "PENDIENTE"
    },
    {
      "fecha": "19/04/2026",
      "monto": 48000,
      "codigo_facturacion": 55,
      "estado": "PROCESADO",
      "cae": "974262938362"
    },
    {
      "fecha": "26/04/2026",
      "monto": 45000,
      "codigo_facturacion": 55,
      "estado": "PROCESADO",
      "cae": "790786905824"
    }
  ],
  "ultima_actualizacion": "24/04/2026 21:13:56"
}
```

### 8.3 Formato precios_historico.json
```json
{
  "precios": [
    {
      "fecha_cambio": "24/04/2026 15:30:00",
      "precio_linea_codigo": 2.00
    },
    {
      "fecha_cambio": "20/04/2026 10:15:00",
      "precio_linea_codigo": 1.50
    }
  ]
}
```

---

## 9. INTEGRACIÓN CON FACTURADOR AFIP

### 9.1 Flujo de Datos
```
Facturador Calculador
    ↓
    Crea/actualiza facturas.csv
    ↓
Llama: python main.py --ahora
    (o subprocess a FacturarAhora.bat)
    ↓
Facturador AFIP procesa
    ↓
Lee resultado de facturas.csv
    ↓
Actualiza JSON con CAE + PROCESADO
```

---

## 10. VALIDACIONES Y ALERTAS

| Condición | Acción |
|-----------|--------|
| Monto pendiente + input > estimado | ⚠️ ALERTA ROJA |
| Fila ya facturada intenta refacturarse | ❌ BLOQUEADO |
| No hay datos en mes anterior | ✓ Crea JSON vacío |
| Cambio de mes → siguiente mes no existe | ✓ Auto-crea |

---

## 11. REQUISITOS TÉCNICOS

### 11.1 Stack
- **Backend:** Python 3.x + Flask
- **Frontend:** HTML5 + CSS3 + JavaScript (vanilla o Alpine.js)
- **Data:** JSON (sin DB)
- **Integration:** Subprocess a Python/batch

### 11.2 Dependencias
```
Flask==2.x
Werkzeug==2.x
```

### 11.3 Puertos
- **Local:** http://localhost:5000

---

## 12. FASES DE DESARROLLO

### Fase 1: MVP
- ✓ Dashboard básico
- ✓ Entrada 4 viernes
- ✓ Guardado en JSON
- ✓ Preview simple

### Fase 2: Integración
- ✓ Botón facturar
- ✓ Leer CSV resultado
- ✓ Mostrar CAEs

### Fase 3: Control Avanzado
- ✓ Admin tab
- ✓ Histórico precios
- ✓ Validaciones complejas

---

**Versión:** 1.0 - Inicial
**Próxima revisión:** Antes de desarrollo
