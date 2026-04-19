# Facturador Automático AFIP - Python + Playwright

Bot que automatiza la emisión de Facturas C en el portal AFIP/ARCA usando Python y Playwright.

## 📋 Requisitos previos

- **Python 3.8+** (recomendado 3.10 o superior)
- **Usuario y contraseña AFIP** (Clave Fiscal)
- **Monotributista emitiendo Facturas C**
- Acceso a https://auth.afip.gov.ar/contribuyente_/login.xhtml

## 🚀 Instalación

### 1. Clonar el repositorio o descargar los archivos

```bash
cd facturador_afip
```

### 2. Crear entorno virtual

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala:
- `playwright`: Automatización de navegador
- `openpyxl`: Lectura/escritura de Excel
- `python-dotenv`: Gestión de variables de entorno
- `schedule`: Ejecución automática de tareas

### 4. Descargar navegadores de Playwright

```bash
playwright install
```

### 5. Configurar variables de entorno

**Crear `.env` desde `.env.example`:**

```bash
# Linux/Mac
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

**Editar `.env` con tus datos:**

```ini
# Tus datos de AFIP (clave fiscal)
AFIP_CUIT=20123456789
AFIP_PASSWORD=mi_clave_fiscal_aqui

# Número de punto de venta (generalmente 1)
AFIP_PUNTO_VENTA=1

# Modo sin interfaz gráfica (false para ver el navegador durante desarrollo)
HEADLESS=false

# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

⚠️ **IMPORTANTE**: Nunca subas `.env` a Git. Ya está en `.gitignore`.

## 📝 Preparar Excel de entrada

### Opción A: Crear un Excel de ejemplo

```bash
python main.py --crear-ejemplo
```

Esto crea `facturas.xlsx` con 2 filas de prueba.

### Opción B: Crear manualmente en Excel

**Estructura requerida:**

| fecha | descripcion | monto | cuit_cliente | nombre_cliente | estado | cae | nro_comprobante |
|-------|-------------|-------|--------------|----------------|--------|-----|-----------------|
| 02/04/2026 | Servicio de consultoría | 5000 | 99999999999 | Consumidor Final | PENDIENTE | | |
| 02/04/2026 | Soporte técnico | 2500 | 20123456789 | Empresa XYZ | PENDIENTE | | |

**Notas:**
- **fecha**: Formato `dd/mm/aaaa` (ej: 02/04/2026)
- **descripcion**: Concepto del servicio
- **monto**: Número SIN punto ni coma de miles (ej: 5000, no 5.000,00)
- **cuit_cliente**: 
  - `99999999999` para Consumidor Final
  - Documento real para empresa (ej: 20123456789)
- **nombre_cliente**: Razón social o nombre
- **estado**: `PENDIENTE` (el bot solo procesa filas con este estado)
- **cae**: Se completa automáticamente al emitir
- **nro_comprobante**: Se completa automáticamente al emitir

**El archivo DEBE llamarse `facturas.xlsx` y estar en la carpeta raíz del proyecto.**

## ▶️ Uso

### Ejecución inmediata

```bash
python main.py --ahora
```

Procesa todas las facturas pendientes de inmediato.

### Ejecución automática (viernes 9 AM)

```bash
python main.py
```

El bot se mantiene en espera y ejecuta automáticamente cada viernes a las 9:00 AM.

**Detener:** Presiona `Ctrl+C`

### Otros comandos útiles

```bash
# Ver variables de entorno configuradas
python main.py --entorno

# Crear Excel de ejemplo
python main.py --crear-ejemplo
```

## 🔍 Desarrollo: Ver el navegador

Si quieres ver qué está haciendo el bot mientras ejecuta (recomendado para resolver problemas):

1. Edita `.env`:
   ```ini
   HEADLESS=false
   ```

2. Ejecuta:
   ```bash
   python main.py --ahora
   ```

Verás una ventana del navegador Chrome mostrando cada paso del bot.

## 📋 Flujo del bot (paso a paso)

1. ✓ Leer `facturas.xlsx` y filtrar filas con `estado = PENDIENTE`
2. ✓ Para c/u fila:
   - Abrir https://auth.afip.gov.ar/contribuyente_/login.xhtml
   - Login con CUIT + contraseña
   - Ir a "Comprobantes en Línea"
   - Generar Factura C
   - Cargar datos: fecha, cliente, descripción, monto
   - Confirmar y obtener CAE
   - Actualizar Excel con CAE y número de comprobante
   - Marcar como `EMITIDA` (con fundo verde)
3. ✓ Guardar cambios en Excel
4. ✓ Generar logs en `logs/facturador_YYYYMMDD_HHMMSS.log`

## 📁 Estructura de directorios

```
facturador_afip/
├── .env                      # Variables de entorno (NO subir a Git)
├── .env.example              # Plantilla de .env
├── .gitignore                # Archivos a ignorar en Git
├── requirements.txt          # Dependencias Python
├── facturas.xlsx             # Excel con facturas (se completa con CAE)
├── README.md                 # Este archivo
├── main.py                   # Punto de entrada
├── bot.py                    # Lógica de Playwright (login + navegación)
├── excel_handler.py          # Lectura y actualización de Excel
├── scheduler.py              # Ejecución automática
└── logs/                     # Carpeta de logs (se crea automáticamente)
    ├── facturador_20260402_090000.log     # Log de ejecución
    └── [screenshots en caso de error]
```

## 🐛 Solución de problemas

### Error: "ModuleNotFoundError" al ejecutar

```bash
# Verifica que el entorno virtual esté activado
# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Luego reinstala dependencias:
pip install -r requirements.txt
```

### Error: ".env not found"

El bot busca `.env` en la carpeta raíz. Si vuelve a fallar, copia `.env.example`:

```bash
cp .env.example .env
```

Luego completa tus datos.

### El bot no encuentra los campos en AFIP

AFIP actualiza su portal con frecuencia. Los selectores HTML pueden cambiar.

**Soluciones:**

1. Edita `.env` y cambia a:
   ```ini
   HEADLESS=false
   ```

2. Ejecuta:
   ```bash
   python main.py --ahora
   ```

3. Verás el navegador en acción. Si falla, toma nota del paso exacto y los elementos de la pantalla.

4. Abre `bot.py` y busca el método que falla (ej: `_seleccionar_tipo_comprobante`)

5. Actualiza el selector usando las herramientas de desarrollador de tu navegador (F12)

6. Contacta o abre un issue con los detalles

### Screenshots en caso de error

Si ocurre un error inesperado, el bot automáticamente toma un screenshot guardándolo en `logs/`.

## 📊 Logs y monitoreo

Los logs se guardan en `logs/facturador_YYYYMMDD_HHMMSS.log`

**Ejemplo de salida exitosa:**

```
2026-04-02 09:15:32,123 - __main__ - INFO - Iniciando Facturador AFIP
2026-04-02 09:15:33,456 - __main__ - INFO - ✓ Configuración cargada
2026-04-02 09:15:35,789 - excel_handler - INFO - Workbook cargado: facturas.xlsx
2026-04-02 09:15:36,012 - excel_handler - INFO - Se encontraron 2 facturas pendientes
2026-04-02 09:15:50,345 - bot - INFO - Factura generada exitosamente: CAE=12345678990, Nro=00000001
2026-04-02 09:15:52,678 - excel_handler - INFO - Fila 2 actualizada: CAE=12345678990, Nro=00000001
2026-04-02 09:16:08,901 - bot - INFO - Factura generada exitosamente: CAE=12345678991, Nro=00000002
2026-04-02 09:16:10,234 - excel_handler - INFO - Fila 3 actualizada: CAE=12345678991, Nro=00000002
```

Para ver todo en tiempo real:

```bash
# Linux/Mac
tail -f logs/facturador_*.log

# Windows PowerShell
Get-Content logs/facturador_*.log -Wait
```

## ⚠️ Consideraciones importantes

### 1. Portal AFIP cambia frecuentemente

Si el bot falla repentinamente, probablemente AFIP cambió algo en su interfaz.

**Procedimiento:**

1. Edita `.env`: `HEADLESS=false`
2. Corre con una factura de prueba
3. Observa dónde falla exactamente
4. Ajusta los selectores en `bot.py` (busca los métodos de `_` prefix)

### 3. Prueba con UNA factura primero

Nunca ejecutes el bot con 100 facturas la primera vez:

1. Crea `facturas.xlsx` con UNA sola fila
2. Ejecuta: `python main.py --ahora`
3. Verifica que el CAE se obtuvo correctamente
4. Una vez que funcione, agrega más filas

### 3. Resguarda tus datos en `.env`

⚠️ **NUNCA compartas `.env`** contiene tu CUIT y contraseña.

Verifica que `.gitignore` incluya `.env`:

```bash
grep ".env" .gitignore
```

## 🔧 Personalización

### Cambiar horario de ejecución automática

Edita `main.py`, busca:

```python
scheduler = Scheduler(tarea_facturador_programada, hora="09:00", dia_semana="friday")
```

Cambia:
- `hora="09:00"` → Usa formato `HH:MM` (ej: `"14:30"`)
- `dia_semana="friday"` → Usa nombre en inglés (ej: `"monday"`, `"wednesday"`)

### Cambiar punto de venta

En `.env`:

```ini
AFIP_PUNTO_VENTA=2  # O el número que uses
```

### Cambiar nivel de logging

En `.env`:

```ini
LOG_LEVEL=DEBUG  # Para más detalle, o WARNING/ERROR para menos
```

## 📚 Dependencias y versiones

```
playwright==1.40.0         # Automatización de navegador
openpyxl==3.11.0          # Manejo de Excel
python-dotenv==1.0.0      # Variables de entorno
schedule==1.2.0           # Ejecución automática
```

## 📄 Licencia

Este proyecto es de uso interno. No se incluye licencia.

## 👨‍💻 Autor

Desarrollado como automatización personalizada para AFIP Argentina.

## 🆘 Errores comunes

| Error | Solución |
|-------|----------|
| `playwright: command not found` | Ejecuta: `playwright install` |
| `No such file or directory: facturas.xlsx` | Ejecuta: `python main.py --crear-ejemplo` |
| `Selector not found` | AFIP cambió su sitio. Ejecuta con `HEADLESS=false` e inspecciona los cambios. |
| `Login fallido` | Verifica CUIT y contraseña en `.env` |
| `Module not found: openpyxl` | Ejecuta: `pip install -r requirements.txt` |

## 📞 Soporte

Si el bot falla, revisa:

1. El log más reciente en `logs/`
2. Los screenshots en `logs/` (si hay errores)
3. La consola donde ejecutaste `python main.py --ahora`
4. Que `.env` tenga CUIT y contraseña correctos
5. Que hayas ejecutado `playwright install`

---

**¡Listo para usar!** 🚀 Ejecuta `python main.py --ahora` para tu primer factura.
