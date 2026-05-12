# ARQUITECTURA - Facturador Calculador

## Estructura del Proyecto

```
facturador_calculador/
│
├── README.md                    # Overview rápido
├── requirements.txt             # Dependencias
├── main.py / run.py            # Entry point Flask
│
├── app/                         # Aplicación Flask
│   ├── __init__.py             # Inicialización Flask
│   ├── models.py               # Datos/JSON (lectura/escritura)
│   ├── routes.py               # Rutas HTTP (GET/POST)
│   ├── utils.py                # Helpers (cálculos, validaciones)
│   └── logger.py               # Logging
│
├── data/                        # Almacenamiento JSON
│   ├── 2026/
│   │   ├── april_2026.json
│   │   ├── may_2026.json
│   │   └── ...
│   └── config/
│       └── precios_historico.json
│
├── templates/                   # HTML
│   ├── base.html               # Base template
│   ├── dashboard.html          # Tab principal
│   └── admin.html              # Tab admin
│
├── static/                      # Assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js              # Lógica frontend
│   └── img/
│       └── [iconos]
│
├── logs/                        # Logs de app
│   └── app.log
│
└── Doc/                         # Documentación
    ├── ESPECIFICACIONES.md
    ├── ARQUITECTURA.md (este)
    ├── FLUJO_USUARIO.md
    └── JSON_SCHEMA.md
```

---

## Módulos Principales

### 1. app/__init__.py
```python
from flask import Flask
def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # Registrar blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
```

**Responsabilidad:** Inicializar y configurar aplicación Flask.

---

### 2. app/models.py
```python
class MesData:
    @staticmethod
    def cargar_mes(mes, año):
        # Leer JSON de data/YYYY/mes_YYYY.json
        # Retornar dict con datos del mes
        
    @staticmethod
    def guardar_mes(mes, año, datos):
        # Escribir JSON
        
    @staticmethod
    def crear_mes_actual():
        # Auto-crear mes si no existe
        
    @staticmethod
    def listar_meses_disponibles():
        # Retornar lista de meses en JSON
```

**Responsabilidad:** Persistencia de datos (JSON).

---

### 3. app/routes.py
```python
@app.route('/', methods=['GET'])
def dashboard():
    # Carga mes actual
    # Renderiza dashboard.html
    # Pasa datos: {"mes": "april", "datos": {...}}

@app.route('/api/mes/<mes>/<año>', methods=['GET'])
def get_mes(mes, año):
    # API: Retorna JSON del mes
    
@app.route('/api/mes', methods=['POST'])
def guardar_mes():
    # API: Guarda cambios en JSON (entrada montos)
    # Body: {"mes": "april", "año": 2026, "viernes": [...]}

@app.route('/api/facturas/previsualizar', methods=['POST'])
def previsualizar():
    # Calcula grilla de PENDIENTES
    # Lee facturas.csv para contar facturados
    
@app.route('/api/facturas/procesar', methods=['POST'])
def procesar_facturas():
    # Ejecuta subprocess a facturador_afip
    # Espera resultado
    # Actualiza JSON con CAEs
    
@app.route('/api/admin/precio', methods=['POST'])
def guardar_precio():
    # Guarda nuevo precio en precios_historico.json
```

**Responsabilidad:** Endpoints HTTP.

---

### 4. app/utils.py
```python
def calcular_resumen_mes(mes_data, facturas_csv):
    # Retorna:
    # {
    #   "facturado": 122000,
    #   "pendiente": 78000,
    #   "estimado": 200000,
    #   "porcentaje": 61
    # }

def validar_monto_total(pendiente, nuevo_monto, estimado):
    # Retorna: {"valido": True/False, "mensaje": "..."}
    
def generar_csv_temporal(viernes_data):
    # Crea CSV para facturador_afip con los viernes
    
def ejecutar_facturador_afip():
    # subprocess.run(['python', '../facturador_afip/main.py', '--ahora'])
    # Espera y retorna resultado
```

**Responsabilidad:** Lógica de negocio.

---

### 5. app/logger.py
```python
def setup_logger():
    # Logger centralizado
    # Archivo: logs/app.log
    # Console output también
```

**Responsabilidad:** Logging de la app.

---

## Flujo de Datos

### Lectura (GET /)
```
Usuario abre app
    ↓
Flask determina mes actual (April 2026)
    ↓
app/models.py → MesData.cargar_mes("april", 2026)
    ↓
Lee data/2026/april_2026.json
    ↓
app/routes.py → dashboard() obtiene datos
    ↓
Renderiza templates/dashboard.html
    ↓
HTML + JS + datos JSON → navegador
    ↓
JS renderiza tabla, cálculos, alertas
```

### Guardado (POST /api/mes)
```
Usuario ingresa montos + clickea campo
    ↓
JavaScript (onChange) envía POST
    ↓
app/routes.py → guardar_mes()
    ↓
app/models.py → MesData.guardar_mes()
    ↓
Escribe data/2026/april_2026.json
    ↓
Retorna {"success": true}
    ↓
JS actualiza UI (sin refresh)
```

### Facturación (POST /api/facturas/procesar)
```
Usuario clickea "APROBAR Y FACTURAR"
    ↓
app/routes.py → procesar_facturas()
    ↓
app/utils.py → generar_csv_temporal()
    ↓
Escribe .../facturador_afip/Facturas/facturas.csv
    ↓
app/utils.py → ejecutar_facturador_afip()
    ↓
subprocess.run(['python', '../facturador_afip/main.py', '--ahora'])
    ↓
Espera resultado (TIMEOUT 5 min)
    ↓
Lee .../facturador_afip/Facturas/facturas.csv resultante
    ↓
Extrae CAEs de filas PROCESADO
    ↓
app/models.py → actualiza april_2026.json
    ↓
Cambia estado PENDIENTE → PROCESADO + agrega CAE
    ↓
Retorna {"success": true, "caes": [...]}
    ↓
JS renderiza "RESULTADOS" con facturas procesadas
```

---

## Integración con Facturador AFIP

### Puntos de Conexión

**1. CSV Input**
```
facturador_calculador/
    → Escribe: ../facturador_afip/Facturas/facturas.csv
```

Formato esperado por facturador_afip:
```
FECHA,CODIGO,PRODUCTO SERVICO:,PRECIO UNITARIO,CUIT_CLIENTE,NOMBRE_CLIENTE,ESTADO,CAE,NRO_COMPROBANTE
24/04/2026,55,servicios informatiicos y capacitacion DB,58000,99999999999,Consumidor Final,PENDIENTE,,
24/04/2026,55,servicios informatiicos y capacitacion DB,64000,99999999999,Consumidor Final,PENDIENTE,,
```

**2. Ejecución**
```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '../facturador_afip/main.py', '--ahora'],
    capture_output=True,
    timeout=300  # 5 minutos
)
```

**3. CSV Output**
```
Lee: ../facturador_afip/Facturas/facturas.csv (después de procesar)
Extrae: CAE, NRO_COMPROBANTE para filas con ESTADO=PROCESADO
```

---

## Configuración

### config.py
```python
import os

FLASK_ENV = 'development'
DEBUG = True
HOST = 'localhost'
PORT = 5000

# Rutas
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FACTURADOR_AFIP_PATH = os.path.join(
    os.path.dirname(__file__), 
    '..', 
    'facturador_afip'
)
FACTURAS_CSV = os.path.join(
    FACTURADOR_AFIP_PATH, 
    'Facturas', 
    'facturas.csv'
)

# Timeouts
SUBPROCESS_TIMEOUT = 300  # 5 min
```

---

## Dependencias

### requirements.txt
```
Flask==2.3.0
Werkzeug==2.3.0
python-dotenv==1.0.0
```

---

## Deployment

### Desarrollo
```bash
cd facturador_calculador
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m flask run
# Acceder: http://localhost:5000
```

### Producción (Opcional)
```bash
pip install gunicorn
gunicorn --workers 1 --bind 0.0.0.0:5000 main:app
```

---

## Seguridad

| Aspecto | Medida |
|--------|--------|
| Validación de datos | Sanitizar monto (float), código (int) |
| CSRF | Flask CSRF token en forms |
| Path Traversal | Validar mes/año (regex: `\d{4}/\w+`) |
| Errorhandling | Try/except en rutas, retornar 400/500 apropiado |

---

## Testing (Futuro)

```
tests/
├── test_models.py          # Lectura/escritura JSON
├── test_routes.py          # Endpoints
├── test_utils.py           # Validaciones
└── test_integration.py     # Integración con AFIP
```

---

**Versión:** 1.0
**Próxima revisión:** Después de MVP
