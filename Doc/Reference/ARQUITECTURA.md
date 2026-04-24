# ARQUITECTURA - Estructura del Proyecto

Explicación de cómo funciona el bot internamente y cómo se estructura el código.

## 📦 Estructura de archivos

```
facturador_afip/
├── .env                    # Tus credenciales (NO en Git)
├── .env.example            # Template de .env
├── .gitignore              # Archivos a ignorar en Git
│
├── main.py                 # 🎯 Punto de entrada principal
├── config.py               # ⚙️  Configuración centralizada
├── utils.py                # 🛠️  Utilidades compartidas
│
├── bot.py                  # 🤖 Playwright - Automatización AFIP
├── excel_handler.py        # 📊 Lectura/escritura de Excel
├── scheduler.py            # ⏰ Ejecución automática
│
├── requirements.txt        # 📋 Dependencias Python
├── setup.bat               # 🔧 Instalación automática (Windows)
├── setup.sh                # 🔧 Instalación automática (Unix)
│
├── README.md               # 📖 Documentación completa
├── INSTALACION.md          # 📖 Guía de instalación paso a paso
├── QUICKSTART.md           # 🚀 Guía rápida (5 minutos)
├── TROUBLESHOOTING.md      # 🆘 Solución de problemas
├── ARQUITECTURA.md         # 📐 Este archivo
│
├── facturas.xlsx           # 📑 Excel con facturas (se completa automáticamente)
└── logs/                   # 📜 Logs de ejecución
    ├── facturador_20260402_090000.log
    ├── login_error_20260402_090000.png
    └── factura_error_20260402_090015.png
```

---

## 🔄 Flujo de ejecución

```
┌─────────────────────────────────────┐
│      main.py (Punto de entrada)     │
│                                     │
│  - Parsea argumentos (--ahora, etc) │
│  - Cargar config.py                 │
│  - Validar ambiente                 │
└─────────────┬───────────────────────┘
              │
              ├─→ Si --ahora: ejecuta_facturador() directamente
              │
              └─→ Si sin args: inicia scheduler (viernes 9 AM)
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
              ┌─────▼──────────────────────────────┐ │
              │   ejecutar_facturador()            │ │
              │                                    │ │
              │  1. Valida credenciales en .env    │ │
              │  2. Carga excel_handler.py         │ │
              │  3. Lee facturas con estado PEND.  │ │
              │  4. Para cada fila:                │ │
              │     - Llama bot.generar_factura()  │ │
              │     - Obtiene CAE y número         │ │
              │     - Actualiza Excel              │ │
              │  5. Guarda Excel                   │ │
              └─────┬──────────────────────────────┘ │
                    │                                 │
        ┌───────────▼─────────────┐                  │
        │  config.py              │                  │
        │  - AFIP_CUIT            │ (centralizado)   │
        │  - AFIP_PASSWORD        │                  │
        │  - HEADLESS             │                  │
        │  - TIMEOUT_GENERAL      │                  │
        │  - LOG settings         │                  │
        └─────────────────────────┘                  │
                                                    │
    ┌────────────────────────────────────────┐      │
    │ Para cada factura pendiente:           │      │
    │                                        │      │
    │  ┌──────────────────────────────────┐  │      │
    │  │    bot.ejecutar_bot_factura()    │  │      │
    │  │                                  │  │      │
    │  │ 1. iniciar_navegador()           │  │      │
    │  │    - Lanza Playwright Chrome     │  │      │
    │  │ 2. login(CUIT, PASSWORD)         │  │      │
    │  │    - Va a AFIP                   │  │      │
    │  │    - Completa credenciales       │  │      │
    │  │ 3. navegar_a_comprobantes()      │  │      │
    │  │    - Abre el servicio            │  │      │
    │  │ 4. generar_factura(datos)        │  │      │
    │  │    - Genera Factura C            │  │      │
    │  │    - Ingresa datos del Excel     │  │      │
    │  │    - Confirma                    │  │      │
    │  │ 5. _extraer_cae()                │  │      │
    │  │    - Obtiene CAE + número        │  │      │
    │  │ 6. cerrar()                      │  │      │
    │  │    - Cierra navegador            │  │      │
    │  │                                  │  │      │
    │  └──────────┬───────────────────────┘  │      │
    │             │                          │      │
    │    ┌────────▼────────────┐             │      │
    │    │  Retorna (CAE, Nro) │             │      │
    │    └─────────────────────┘             │      │
    │                                        │      │
    │    ┌───────────────────────────────┐   │      │
    │    │ excel_handler.actualizar()    │   │      │
    │    │ - Actualiza fila en Excel     │   │      │
    │    │ - Guarda CAE y número         │   │      │
    │    │ - Marca como EMITIDA (verde)  │   │      │
    │    └───────────────────────────────┘   │      │
    │                                        │      │
    └────────────────────────────────────────┘      │
                    │                              │
                    └──────────────────────────────┘
                                    │
                    ┌───────────────▼──────────────┐
                    │ Guarda Excel                 │
                    │ Log de resumen               │
                    │ Limpia logs antiguos (7 días)│
                    └──────────────────────────────┘
```

---

## 📚 Módulos principales

### 1. `main.py`
**Responsabilidad:** Orquestación y punto de entrada

**Funciones clave:**
- `main()` - Parsea argumentos CLI
- `ejecutar_facturador()` - Loop principal async
- `procesar_factura()` - Procesa una factura individual
- `tarea_facturador_programada()` - Wrapper para scheduler

**Entrada:** Argumentos CLI (`--ahora`, `--crear-ejemplo`, etc)
**Salida:** Ejecuta bot, actualiza Excel, genera logs

---

### 2. `config.py`
**Responsabilidad:** Configuración centralizada

**Variables:**
- Rutas (BASE_DIR, LOGS_DIR, EXCEL_FILE)
- Credenciales AFIP (cargadas de .env)
- Timeouts (TIMEOUT_GENERAL, TIMEOUT_CORTO, TIMEOUT_LARGO)
- URLs (AFIP_URL_LOGIN, AFIP_URL_COMPROBANTES)

**Patrón:** Singleton - se importa una sola vez

---

### 3. `utils.py`
**Responsabilidad:** Funciones compartidas

**Clases:**
- `LoggerFactory` - Crea loggers con configuración uniforme

**Funciones:**
- `validar_ambiente()` - Valida que .env esté correcto
- `crear_excel_si_no_existe()` - Crea Excel de ejemplo
- `listar_logs()` - Lista todos los logs
- `limpiar_logs_antiguos()` - Borra logs de hace >7 días

---

### 4. `bot.py`
**Responsabilidad:** Automatización con Playwright

**Clase:** `BotAFIP`

**Métodos públicos:**
- `iniciar_navegador()` - Lanza Playwright
- `login()` - Login en AFIP
- `navegar_a_comprobantes()` - Va al servicio
- `generar_factura()` - Genera factura (orquesta todo)
- `cerrar()` - Cierra navegador

**Métodos privados:**
- `_clickear_generar_comprobante()`
- `_seleccionar_tipo_comprobante()`
- `_seleccionar_punto_venta()`
- ... etc (cada paso del formulario)
- `_extraer_cae()` - Parsea respuesta AFIP
- `_extraer_nro_comprobante()` - Parsea respuesta AFIP
- `tomar_screenshot()` - Debugging visual

**Patrón:** Espera explícita (`wait_for_selector`) en lugar de `time.sleep()`

---

### 5. `excel_handler.py`
**Responsabilidad:** Manejo de Excel

**Clase:** `ExcelHandler`

**Métodos:**
- `cargar_workbook()` - Abre facturas.xlsx
- `obtener_filas_pendientes()` - Filtra por estado=PENDIENTE
- `actualizar_fila()` - Guarda CAE, número, marca como EMITIDA
- `guardar()` - Escribe cambios al disco
- `cerrar()` - Libera recursos

**Función auxiliar:**
- `crear_excel_ejemplo()` - Crea Excel de prueba

---

### 6. `scheduler.py`
**Responsabilidad:** Ejecución automática

**Clase:** `Scheduler`

**Métodos:**
- `programar()` - Crea tarea (viernes 9 AM)
- `ejecutar_loop()` - Loop while que verifica cada minuto
- `detener()` - Cancela la tarea
- `obtener_fecha_proxima_ejecucion()` - Información

**Usa librería:** `schedule` (no cron, más portable)

---

## 🔐 Flujo de credenciales

```
.env (archivo)
    │
    └─→ config.py (carga via python-dotenv)
           │
           ├─→ AFIP_CUIT
           ├─→ AFIP_PASSWORD
           └─→ AFIP_PUNTO_VENTA
                │
                └─→ main.py
                       │
                       └─→ bot.py (usa para login)
```

**Seguridad:**
- `.env` NO se versionea (en `.gitignore`)
- Contraseña nunca se loguea en logs
- `validar_ambiente()` verifica que no esté vacío

---

## 📊 Flujo de datos del Excel

```
facturas.xlsx
    │
    └─→ excel_handler.cargar_workbook()
           │
           ├─ Lee headers: fecha, descripcion, monto, ...
           │
           └─→ obtener_filas_pendientes()
                  │
                  └─ Filtra estado = "PENDIENTE"
                     Retorna: List[Dict]
                        │
                        ├─ {fecha: "02/04/2026", 
                        │   descripcion: "Consultoría",
                        │   ...
                        │   numero_fila: 2}
                        │
                        └─→ procesar_factura()
                               │
                               └─→ bot.generar_factura()
                                      │
                                      Retorna: (CAE, nro_comprobante)
                                      │
                               ┌──────▼─────────┐
                               │                │
                        ┌──────▼───────┐      Si OK
                        │ excel_handler│
                        │.actualizar() │
                        │              │
                        │ Escribe:     │
                        │ - cae: "xxx" │
                        │ - nro: "yyy" │
                        │ - estado:    │
                        │   "EMITIDA"  │
                        │              │
                        │ Rellena de   │
                        │ verde la fila│
                        └──────┬───────┘
                               │
                        ┌──────▼────────┐
                        │ excel_handler │
                        │.guardar()     │
                        │               │
                        │ Escribe disco │
                        └───────────────┘

facturas.xlsx (actualizado)
```

---

## ⏱️ Timeouts utilizados

| Timeout | Duración | Uso |
|---------|----------|-----|
| `TIMEOUT_GENERAL` | 30s (30000 ms) | Navegación, logins, esperas generales |
| `TIMEOUT_CORTO` | 10s (10000 ms) | Selectores de elementos, campos cortos |
| `TIMEOUT_LARGO` | 60s (60000 ms) | Respuesta de AFIP después de confirmar |

**Razón:** Evitar `time.sleep()` fijo que es frágil. `wait_for_selector()` espera dinámicamente.

---

## 📝 Logging

**Niveles:**
- `DEBUG` - Información detallada (selectores, valores de campos)
- `INFO` - Operaciones principales (login OK, factura emitida)
- `WARNING` - Situaciones inesperadas (selector no encontrado, retry)
- `ERROR` - Fallos (login fallido, factura NO emitida)

**Formato:**
```
2026-04-02 09:15:32,123 - bot - INFO - Login exitoso
```

**Archivos:**
```
logs/facturador_20260402_090000.log
logs/login_error_20260402_090000.png
logs/factura_error_20260402_090015.png
```

---

## 🔄 Ciclo de vida de una ejecución

```
1. Usuario ejecuta: python main.py --ahora

2. main.py carga modules:
   - config.py (variables globales)
   - utils.py (logger, validación)
   - excel_handler.py
   - bot.py
   - scheduler.py

3. LoggerFactory crea logger
   - Log file: logs/facturador_TIMESTAMP.log
   - Console: stdout

4. Valida config de .env
   - Si CUIT vacío → ERROR + EXIT
   - Si PASSWORD vacío → ERROR + EXIT
   - Si facturas.xlsx no existe → WARN + CREAR

5. ExcelHandler.cargar()
   - Lee facturas.xlsx
   - Filtra PENDIENTE
   - Si ninguna → LOG "Sin facturas" + EXIT

6. Para cada fila PENDIENTE:
   - BotAFIP.iniciar_navegador()
   - BotAFIP.login()
   - BotAFIP.navegar_a_comprobantes()
   - BotAFIP.generar_factura()
   - ExcelHandler.actualizar_fila()
   - Si error en factura: LOG + CONTINUAR siguiente
   - Si error en login: LOG + EXIT (crítico)

7. ExcelHandler.guardar()
   - Escribe cambios al disco

8. Resumen en log:
   - Exitosas: N
   - Fallidas: M
   - Tiempo total

9. BotAFIP.cerrar()
   - Libera recursos Playwright

10. Logger guarda log a disco
```

---

## 🔌 Extensibilidad

### Agregar un nuevo campo a la factura

1. **.env:** Agrega variable si es necesaria
2. **excel_handler.py:** Agrega columna al Excel de ejemplo
3. **bot.py:** Agregá método `_ingresar_nuevo_campo()`
4. **main.py:** Pasa el dato en `procesar_factura()`

### Cambiar horario de scheduler

**config.py:**
```python
SCHEDULER_HORA = "14:30"  # Era "09:00"
SCHEDULER_DIA = "monday"  # Era "friday"
```

### Soporte para múltiples puntos de venta

Agregá columna en Excel:
```
punto_venta | fecha | descripcion | ...
2           | ...   | ...         | ...
```

---

## 🧪 Testing manual

```powershell
# Test: Crear instalación limpia
.\setup.bat

# Test: Verificar config
python main.py --entorno

# Test: Ver último log
Get-Content logs/facturador_*.log -Tail 20

# Test: Ejecutar con logs DEBUG
# Edita .env: LOG_LEVEL=DEBUG
python main.py --ahora

# Test: Ver Excel generado
python main.py --crear-ejemplo
# Abre facturas.xlsx
```

---

## 📦 Dependencias y versiones

| Librería | Versión | Uso |
|----------|---------|-----|
| `playwright` | 1.40.0 | Automatización de navegador |
| `openpyxl` | 3.11.0 | Lectura/escritura Excel |
| `python-dotenv` | 1.0.0 | Cargar variables de .env |
| `schedule` | 1.2.0 | Scheduler de tareas |

---

## 🚀 Performance

**Tiempo típico por factura:** 45-90 segundos
- Login: 15s
- Navegación a comprobantes: 10s
- Llenar formulario: 10s
- Confirmar: 15s
- Extraer información: 5s

**Optimizaciones:**
- Pausa de 2s entre facturas (evitar rate limiting)
- Screenshots solo en error (no ralentiza)
- Logs en archivo + consola simultáneamente

---

¡La arquitectura está diseñada para ser **mantenible**, **debuggueable** y **extensible**! 🎯
