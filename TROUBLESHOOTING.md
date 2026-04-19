# TROUBLESHOOTING - Solución de problemas

Guía completa de errores comunes y cómo resolverlos.

## 🔴 Error durante la instalación

### "python: command not found" / "python is not recognized"

**Causa:** Python no está instalado o no se agregó a PATH

**Solución:**
1. Desinstala Python completamente
2. Descarga Python 3.11+ desde https://www.python.org
3. **MUY IMPORTANTE**: Al instalar, MARCA "Add Python to PATH"
4. Reinicia PowerShell/CMD
5. Verifica: `python --version`

---

### "Could not find module" o error de permisos

**Causa:** Falta ejecutar como administrador o problemas de permisos

**Solución (Windows):**
1. Click derecho en PowerShell
2. "Run as Administrator" (Ejecutar como administrador)
3. Repite: `.\setup.bat`

---

## 🟡 Errores al ejecutar el bot

### "ModuleNotFoundError: No module named 'playwright'"

**Causa:** Las dependencias no se instalaron correctamente

**Solución:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

### "playwright: command not found"

**Causa:** Los navegadores de Playwright no se instalaron

**Solución:**
```powershell
playwright install
```

Si sigue sin funcionar:
```powershell
python -m playwright install
```

---

### "No such file or directory: facturas.xlsx"

**Causa:** El archivo Excel no existe

**Solución:**
```powershell
python main.py --crear-ejemplo
```

Esto crea un Excel de prueba con datos de ejemplo.

---

### "No section: 'AFIP_CUIT' in .env"

**Causa:** El archivo `.env` no tiene la configuración

**Solución:**
1. Copia: `copy .env.example .env`
2. Abre `.env` en un editor
3. Rellena AFIP_CUIT y AFIP_PASSWORD
4. Guarda

---

## 🔴 El bot falla en AFIP

### El navegador se abre pero no hace nada

**Causa posible:** Timeout en la cargar de la página

**Solución:**
1. Verifica tu conexión a internet
2. Prueba manualmente en https://auth.afip.gov.ar/contribuyente_/login.xhtml
3. En `.env` cambia: `HEADLESS=false` para ver qué ocurre
4. Si el sitio carga lentamente, AFIP puede estar bajo mucha carga

---

### "Selector not found" o "element not found"

**Causa:** AFIP cambió su interfaz HTML

**Solución:**
1. Edita `.env`: `HEADLESS=false`
2. Ejecuta: `python main.py --ahora`
3. Observa dónde exactamente falla
4. Abre `bot.py` y busca el método `_seleccionar_tipo_comprobante` (o el que falle)
5. Actualiza el selector (puedes inspeccionar con F12 en el navegador)
6. Si es complicado, contacta o abre un issue

---

### "Login fallido - URL inesperada"

**Causa:** Las credenciales son incorrectas o AFIP bloqueó la cuenta

**Solución:**
1. Verifica que el CUIT está correcto (sin guiones): `20123456789`
2. Verifica que la contraseña es tu "Clave Fiscal" (no es el usuario del sitio)
3. Intenta login manualmente en AFIP para verificar
4. Si AFIP tiene captcha, el bot no puede procesar (necesitarías login manual)

---

### "Factura generada pero CAE no encontrado"

**Causa:** La factura se emitió pero el bot no supo extraer el CAE de la respuesta

**Solución:**
1. Verifica manualmente en AFIP que la factura existe
2. Copia el CAE manualmente en el Excel
3. Edita `bot.py` método `_extraer_cae()` y ajusta el patrón de búsqueda

---

## 🟡 El Excel no se actualiza

### La factura se emite pero el Excel no cambia

**Causa:** AFIP emitió la factura pero el bot no pudo guardar en Excel

**Solución:**
1. Verifica que `facturas.xlsx` no esté abierto en Excel (LOCK del archivo)
2. Cierra Excel si está abierto
3. Ejecuta de nuevo: `python main.py --ahora`

---

### "Permission denied" para `facturas.xlsx`

**Causa:** El archivo está abierto o no tienes permisos de escritura

**Solución:**
1. Cierra `facturas.xlsx` si está abierto en Excel
2. Verifica que No está marcado como "Read-only" (click derecho > propiedades)
3. Intenta de nuevo

---

## 🟢 Problemas de rendimiento

### El bot es muy lento

**Causa:** Timeouts muy cortos o conexión lenta

**Solución:**
1. Verifica tu conexión a internet
2. En `config.py` puedes aumentar los timeouts:
   ```python
   TIMEOUT_GENERAL = 60000  # Aumenta de 30000 a 60000
   ```

---

### Se ejecuta pero tarda mucho en el login

**Causa:** Probablemente AFIP está bajo mucha carga

**Solución:**
- Intenta en otro horario
- AFIP puede estar saturado en horarios pico

---

## 🔵 Logs y debugging

### Ver qué está haciendo el bot

**Opción 1 - Modo visual:**
```powershell
# Edita .env
HEADLESS=false

# Ejecuta
python main.py --ahora
```

**Opción 2 - Ver logs detallados:**
```powershell
# Edita .env
LOG_LEVEL=DEBUG

# Ejecuta
python main.py --ahora

# Verifica el archivo en logs/
```

---

### Encontrar el último log

```powershell
# Windows
Get-ChildItem logs/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content

# Linux/Mac
tail -f logs/facturador_*.log
```

---

## 📸 Screenshots en caso de error

Si hay un error inesperado, el bot automáticamente guarda un screenshot en `logs/`

**Ejemplo:**
- `logs/login_error_20260402_090000.png`
- `logs/factura_error_20260402_090015.png`

Abre estas imágenes para ver dónde exactamente falló.

---

## 🚀 Configuración avanzada

### Cambiar horario del scheduler

En `main.py`:
```python
scheduler = Scheduler(tarea_facturador_programada, hora="14:30", dia_semana="monday")
```

Opciones de días: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`

---

### Ejecutar en background (Windows)

Crea un archivo `run_background.bat`:
```batch
@echo off
start pythonw main.py
```

Ejecuta el `.bat` y se ejecutará en background.

---

### Ejecutar en background (Linux/Mac)

```bash
nohup python main.py > facturador.log 2>&1 &
```

---

## 📞 Checklist si nada funciona

- [ ] Python instalado y en PATH
- [ ] `.env` configurado con CUIT correcto (sin guiones)
- [ ] Clave Fiscal correcta (no contraseña de usuario)
- [ ] Dependencias instaladas: `pip install -r requirements.txt`
- [ ] Navegadores Playwright instalados: `playwright install`
- [ ] `facturas.xlsx` existe
- [ ] Filas en Excel con estado `PENDIENTE`
- [ ] Conexión a internet funcionando
- [ ] Puedes hacer login manual en https://auth.afip.gov.ar
- [ ] AFIP no tiene captcha activo

---

## 🔗 Recursos útiles

- **Portal AFIP:** https://auth.afip.gov.ar/contribuyente_/login.xhtml
- **Python:** https://www.python.org
- **Playwright docs:** https://playwright.dev/python/
- **OpenPyXL docs:** https://openpyxl.readthedocs.io/

---

**¿Aún con problemas?** Revisa:
1. El archivo `.{operation}_error_*.png` en `logs/`
2. El archivo `facturador_*.log` en `logs/`
3. Los últimos mensajes en la consola

Busca palabras clave del error en este documento o adapta el código según lo necesites.
