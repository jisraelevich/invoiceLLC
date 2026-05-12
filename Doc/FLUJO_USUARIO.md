# FLUJO DE USUARIO - Facturador Calculador

## Escenario 1: Primeros Pasos (Mes Actual)

### 1. Abrir Aplicación
```
Usuario abre: http://localhost:5000
                    ↓
            App detecta mes actual (April 2026)
                    ↓
        Carga datos de april_2026.json (si existe)
                    ↓
        Renderiza DASHBOARD con tabs
```

**Pantalla:**
```
┌──────────────────────────────────────────────────────┐
│ FACTURADOR CALCULADOR                     [ADMIN]    │
│                                                      │
│ [APRIL 2026] [Ver anterior: ▼]                      │
│                                                      │
│ 📊 RESUMEN DEL MES                                   │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Monto Estimado a Facturar: [$____________]       │ │
│ │                                                  │ │
│ │ • Facturado:   $0     (0%)   ░░░░░░░░░░          │ │
│ │ • Pendiente:   $0     (0%)   ░░░░░░░░░░          │ │
│ │ • Estimado:    $0                                │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

### 2. Ingresar Monto Estimado
```
Usuario:
1. Ve input "Monto Estimado"
2. Ingresa: 200000
3. Clickea campo siguiente (onChange)

App:
1. Guarda en april_2026.json
2. Actualiza "Estimado: 200,000"
3. Recalcula porcentajes
4. Muestra "• Facturado: $0 (0%)"
5. Muestra "• Pendiente: $200,000 (100%)"
```

**Pantalla actualizada:**
```
│ • Facturado:   $0        (0%)   ░░░░░░░░░░          │
│ • Pendiente:   $200,000  (100%) ██████████          │
│ • Estimado:    $200,000                             │
│                                                      │
│ ✓ Dentro del estimado                               │
```

---

### 3. Pegar y Procesar Datos

```
Usuario ve:
┌──────────────────────────────────────────────────────┐
│ 📝 PEGAR DATOS DE FACTURAS                           │
│                                                      │
│ [TEXTAREA]                                           │
│ 5/2/2026 65000                                      │
│ 5/3/2026 78000                                      │
│ 5/12/2026 103000                                    │
│                                                      │
│ [PARSE]                                             │
└──────────────────────────────────────────────────────┘

App:
- Clickea [PARSE]
- Sistema parsea líneas
- Extrae fecha, monto, tipo (default 55)
- Valida fechas y montos
- Suma autom. 65k+78k+103k = 246,000
- Compara vs estimado: 246,000 > 200,000 ⚠️
- Muestra alerta si excede
```

---

### 4. Previsualizar Facturas

```
Usuario: Clickea [CALCULAR Y PREVISUALIZAR]

App:
1. Lee montos de april_2026.json
2. Lee facturas.csv para ver qué ya se facturó
3. Genera grilla de PENDIENTES
4. Valida monto total

Pantalla:
┌──────────────────────────────────────────────────────┐
│ 📊 GRILLA DE FACTURAS PENDIENTES (PREVIEW)           │
│                                                      │
│ ┌────┬─────────┬───────┬──────────────────────────┐ │
│ │Fec │ Monto   │ Código│ Concepto                 │ │
│ ├────┼─────────┼───────┼──────────────────────────┤ │
│ │5/4 │$50,000  │  55   │ Servicios informáticos  │ │
│ │12/4│$52,000  │  55   │ Servicios informáticos  │ │
│ │19/4│$48,000  │  55   │ Servicios informáticos  │ │
│ │26/4│$45,000  │  55   │ Servicios informáticos  │ │
│ └────┴─────────┴───────┴──────────────────────────┘ │
│                                                      │
│ Total: $195,000 (Dentro del estimado ✓)             │
│                                                      │
│ [← EDITAR] [✓ APROBAR Y FACTURAR]                   │
└──────────────────────────────────────────────────────┘
```

---

### 5. Aprobar y Facturar

```
Usuario: Clickea [✓ APROBAR Y FACTURAR]

App - Backend:
1. Genera facturas_temp.csv con 4 rows (PENDIENTE)
2. Escribe en ../facturador_afip/Facturas/facturas.csv
3. Ejecuta: python ../facturador_afip/main.py --ahora
4. Espera ~1 minuto (muestra spinner en frontend)
5. Facturador AFIP genera las 4 facturas
6. Lee resultado de facturas.csv actualizado
7. Extrae CAEs de filas PROCESADO
8. Actualiza april_2026.json:
   - Estado: PENDIENTE → PROCESADO
   - Agrega CAE a cada fila
9. Retorna {"success": true, "facturas_procesadas": 4}

Frontend:
- Muestra spinner "Facturando..."
- Cuando termina, refresca la página
- Muestra tab "RESULTADOS"
```

**Pantalla - RESULTADOS:**
```
┌──────────────────────────────────────────────────────┐
│ ✅ FACTURAS YA EMITIDAS EN AFIP                       │
│                                                      │
│ ┌────┬─────────┬───────┬──────────────────────────┬──│
│ │Fec │ Monto   │ Código│ Concepto                 │CA│
│ ├────┼─────────┼───────┼──────────────────────────┼──│
│ │24/4│$50,000  │  55   │ Servicios informáticos  │97│
│ │24/4│$52,000  │  55   │ Servicios informáticos  │79│
│ │24/4│$48,000  │  55   │ Servicios informáticos  │12│
│ │24/4│$45,000  │  55   │ Servicios informáticos  │33│
│ └────┴─────────┴───────┴──────────────────────────┴──│
│                                                      │
│ ✓ 4 facturas procesadas exitosamente               │
└──────────────────────────────────────────────────────┘

📊 RESUMEN DEL MES (ACTUALIZADO)
│ • Facturado:   $195,000  (97%)  ██████████░         │
│ • Pendiente:   $5,000    (3%)   █░░░░░░░░░          │
│ • Estimado:    $200,000                             │
│                                                      │
│ ✓ Dentro del estimado                               │
```

---

## Escenario 2: Revisar Mes Anterior

### 1. Cambiar de Mes
```
Usuario: Clickea [Ver anterior: ▼]

Dropdown muestra:
- April 2026 (actual)
- March 2026
- February 2026

Usuario: Selecciona "March 2026"

App:
1. Lee march_2026.json
2. Renderiza dashboard con datos históricos
3. Todos los campos en modo READ-ONLY (o deshabilitados)
4. Muestra RESULTADOS de marzo
```

**Pantalla:**
```
[MARCH 2026] ← Datos históricos (consulta)

📊 RESUMEN DEL MES
│ • Facturado:   $150,000  (75%)
│ • Pendiente:   $50,000   (25%)
│ • Estimado:    $200,000

[Los inputs están DESHABILITADOS]

✅ FACTURAS EMITIDAS EN MARCH
[Tabla con todas las facturadas de marzo]
```

---

## Escenario 3: Alerta de Sobrecarga

### 1. Ingresar Monto Superior al Estimado

```
Usuario:
1. Asigna Estimado: $200,000
2. Ingresa montos:
   - Viernes 5:  $60,000
   - Viernes 12: $60,000
   - Viernes 19: $60,000
   - Viernes 26: $60,000
   Total: $240,000

App - Validación:
$240,000 > $200,000 (EXCESO: $40,000)

Pantalla:
│ 📊 RESUMEN DEL MES
│ ┌──────────────────────────────────────────────────┐
│ │ Monto Estimado a Facturar: [$200,000]            │
│ │                                                  │
│ │ • Facturado:   $0        (0%)   ░░░░░░░░░░       │
│ │ • Pendiente:   $240,000  (120%)  ████████████     │
│ │ • Estimado:    $200,000                          │
│ │                                                  │
│ │ ⚠️  ADVERTENCIA:                                 │
│ │    ❌ SUPERAS el estimado en $40,000             │
│ │    Revisa los montos antes de facturar            │
│ └──────────────────────────────────────────────────┘
```

**Comportamiento:**
- Fondo de ALERTA en ROJO
- Botón "APROBAR Y FACTURAR" deshabilitado (o con confirmación)
- Usuario debe editar montos para continuar

---

## Escenario 4: Tab Admin

### 1. Ver y Actualizar Precio/Línea

```
Usuario: Clickea tab [ADMIN]

Pantalla:
┌──────────────────────────────────────────────────────┐
│ ⚙️ ADMINISTRACIÓN                                     │
│                                                      │
│ Precio por Línea de Código: [$2.00]                 │
│ [Guardar]                                            │
│                                                      │
│ 📜 HISTÓRICO DE PRECIO                               │
│ ┌──────────────────┬──────────┐                     │
│ │ Fecha            │ Precio   │                     │
│ ├──────────────────┼──────────┤                     │
│ │ 24/04/2026 15:45 │ $2.00    │                     │
│ │ 20/04/2026 10:15 │ $1.50    │                     │
│ │ 15/03/2026 14:30 │ $1.50    │                     │
│ └──────────────────┴──────────┘                     │
└──────────────────────────────────────────────────────┘
```

### 2. Cambiar Precio

```
Usuario:
1. Borra $2.00
2. Ingresa $2.50
3. Clickea [Guardar]

App:
1. Valida input (number, > 0)
2. Escribe en precios_historico.json:
   {
     "fecha_cambio": "24/04/2026 16:00:00",
     "precio_linea_codigo": 2.50
   }
3. Actualiza histórico en pantalla
4. Retorna {"success": true}
```

**Histórico actualizado:**
```
│ ┌──────────────────┬──────────┐
│ │ Fecha            │ Precio   │
│ ├──────────────────┼──────────┤
│ │ 24/04/2026 16:00 │ $2.50    │ ← Nuevo
│ │ 24/04/2026 15:45 │ $2.00    │
│ │ 20/04/2026 10:15 │ $1.50    │
│ │ 15/03/2026 14:30 │ $1.50    │
│ └──────────────────┴──────────┘
```

---

## Escenario 5: Transición a Mes Siguiente

### 1. Cambio de Mes (Automático)

```
Fecha actual: 30/04/2026 (fin de abril)
Usuario abre app

App:
1. Detecta que es mayo
2. Verifica si mayo_2026.json existe
3. NO EXISTE → Crea automáticamente:
   {
     "mes": "May",
     "año": 2026,
     "mes_completo": "may_2026",
     "monto_estimado": 0,  # Vacío para que complete
     "viernes": [
       {"fecha": "03/05/2026", "monto": 0, "codigo": 55, "estado": "PENDIENTE"},
       {"fecha": "10/05/2026", "monto": 0, "codigo": 55, "estado": "PENDIENTE"},
       {"fecha": "17/05/2026", "monto": 0, "codigo": 55, "estado": "PENDIENTE"},
       {"fecha": "24/05/2026", "monto": 0, "codigo": 55, "estado": "PENDIENTE"}
     ]
   }
4. Renderiza dashboard vacío para mayo
```

**Pantalla:**
```
[MAY 2026] [Ver anterior: ▼ APRIL 2026]

📊 RESUMEN DEL MES
│ Monto Estimado a Facturar: [$_____________]
│ 
│ • Facturado: $0 (0%)
│ • Pendiente: $0 (0%)
│ • Estimado:  $0

📝 MONTOS A FACTURAR POR VIERNES
│ Viernes 3:  [_____] [▼ 55]
│ Viernes 10: [_____] [▼ 55]
│ Viernes 17: [_____] [▼ 55]
│ Viernes 24: [_____] [▼ 55]
```

---

## Errores y Recuperación

### Error 1: Facturador AFIP No Responde
```
Usuario: Clickea [✓ APROBAR Y FACTURAR]

App - Backend:
- Se queda esperando respuesta
- Timeout 5 minutos
- Retorna: {"error": "Timeout facturando", "code": 504}

Frontend:
- Spinner se detiene
- Muestra modal:
  "❌ Error: Timeout durante facturación
   Por favor reintentar o revisar el servidor AFIP"
- Botones: [Reintentar] [Cancelar]
```

### Error 2: CSV Malformado
```
App detecta: CSV output de facturador_afip sin CAE

Frontend - Modal:
"❌ Error: Facturación completada pero sin CAE
 Las facturas pueden no haber sido registradas"
```

### Error 3: Monto Negativo o Inválido
```
Usuario ingresa: -5000 o "abc"

App - Validación:
x = float(input)
if x <= 0: return {"error": "Monto debe ser > 0"}

Frontend:
- Campo se marca en ROJO
- Muestra: "⚠️ Ingresa un monto válido (> 0)"
```

---

**Versión:** 1.0
**Estado:** Flujo completo documentado
