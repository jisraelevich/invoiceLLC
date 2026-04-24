# INSTALACIÓN Y SETUP - Facturador AFIP

Guía paso a paso para instalar y ejecutar el Facturador por primera vez.

## 🔧 Requisitos previos

- **Windows 10+** o **Linux/Mac** con Python 3.8+
- **Usuario AFIP** con Clave Fiscal (no certificado digital)
- **Excel** para editar facturas.xlsx (o cualquier editor compatible)

## 📥 PASO 1: Descargar e instalar Python

### En Windows:

1. Ve a https://www.python.org/downloads/
2. Descarga "Python 3.11" (o versión más reciente)
3. ⚠️ **IMPORTANTE**: Al instalar, marca la opción **"Add Python to PATH"**
4. Completa la instalación

**Verificar que Python está instalado:**
- Abre PowerShell (`Win + R`, escribe `powershell`)
- Ejecuta: `python --version`
- Deberías ver algo como: `Python 3.11.x`

---

## 📂 PASO 2: Preparar la carpeta del proyecto

1. Coloca la carpeta `facturador_afip` en un lugar seguro (ej: `C:\Users\TuUsuario\Desktop\facturador_afip`)
2. Abre PowerShell
3. Navega a la carpeta:
   ```powershell
   cd C:\Users\TuUsuario\Desktop\facturador_afip
   ```

---

## ⚙️ PASO 3: Ejecutar instalación automática (RECOMENDADO)

### En Windows (PowerShell):

```powershell
.\setup.bat
```

El script hará automáticamente:
- ✓ Crear entorno virtual
- ✓ Instalar todas las dependencias
- ✓ Instalar navegadores Playwright
- ✓ Crear Excel de ejemplo
- ✓ Copiar `.env.example` a `.env`

**Si todo va bien, verás: "INSTALACION COMPLETADA"**

---

## 🔐 PASO 4: Configurar credenciales AFIP

1. Abre el archivo `.env` con un editor de texto (Notepad+, VS Code, etc.)
2. Rellena tus datos:

```ini
AFIP_CUIT=20123456789
AFIP_PASSWORD=mi_clave_fiscal_aqui
AFIP_PUNTO_VENTA=1
HEADLESS=false
```

⚠️ **IMPORTANTE**: 
- Usa tu CUIT real (sin guiones)
- La contraseña es tu "Clave Fiscal" de AFIP
- **NUNCA compartas este archivo .env**

---

## 📊 PASO 5: Preparar Excel de facturas

El script de instalación ya creó `facturas.xlsx` con ejemplos.

**Editing the Excel:**

Abre `facturas.xlsx` y completa:

| fecha | descripcion | monto | cuit_cliente | nombre_cliente | estado |
|-------|-------------|-------|--------------|----------------|--------|
| 02/04/2026 | Servicio consultoría | 5000 | 99999999999 | Consumidor Final | PENDIENTE |

**Notas importantes:**
- **fecha**: Formato riguroso `dd/mm/aaaa`
- **monto**: Solo números, sin puntos ni comas (ej: `5000` no `5.000`)
- **cuit_cliente**: 
  - Consumidor Final: `99999999999` (11 nines)
  - Empresa: su CUIT real (ej: `20123456789`)
- **estado**: Escribir exactamente `PENDIENTE` (ayuda a filtrar)

---

## ▶️ PASO 6: Ejecutar por primera vez

### Modo INMEDIATO (recomendado para probar):

```powershell
python main.py --ahora
```

Debería:
1. Abrir un navegador Chrome
2. Ir a login de AFIP
3. Completar el formulario automáticamente
4. Emitir la factura
5. Guardar CAE en el Excel

**Observa el navegador mientras se ejecuta para detectar cambios en AFIP.**

---

## 🔄 PASO 7 (Opcional): Ejecutar automáticamente los viernes

Una vez que confirmes que funciona:

```powershell
python main.py
```

El bot se quedará esperando. **Cada viernes a las 9:00 AM ejecutará automáticamente.**

Presiona `Ctrl+C` para detener.

---

## ❌ SOLUCIÓN DE PROBLEMAS

### Error: "python: command not found"
- Python no está en PATH
- Solución:
  1. Desinstala Python
  2. Reinstala marcando "Add Python to PATH"
  3. Reinicia PowerShell

### Error: "ModuleNotFoundError: openpyxl"
```powershell
pip install -r requirements.txt
```

### Error: "playwright: command not found"
```powershell
playwright install
```

### Error: "El archivo .env no encontrado"
```powershell
copy .env.example .env
```

### El bot falla en AFIP
1. Edita `.env`: `HEADLESS=false`
2. Ejecuta nuevamente: `python main.py --ahora`
3. Mira el navegador para ver dónde falla
4. Verifica que los datos del Excel sean correctos
5. Posible que AFIP cambió su interfaz (consulta el README.md)

### El navegador no se abre
- Verifica que `HEADLESS=false` en `.env`
- Asegúrate de haber ejecutado: `playwright install`

---

## ✅ HITO: Primera factura exitosa

Cuando veas en el Excel:
```
estado: EMITIDA
cae: 12345678990
nro_comprobante: 00000001
```

Y el fondo de la fila está verde → **¡ÉXITO! El bot funciona.**

---

## 📖 Próximos pasos

1. **Agregar más facturas** al Excel
2. **Ejecutar nuevamente**: `python main.py --ahora`
3. **Ver logs**: Abre archivos en carpeta `logs/`
4. Cuando funcione perfectamente, ejecuta sin `--ahora` para automático

---

## 📞 Tips finales

- **Prueba con 1-2 facturas primero**, no todo el lote
- **Guarda las CAE/nros de comprobante** para tus registros
- **Revisa los logs** si algo falla
- **AFIP cambia frecuentemente**, si falla revisa con `HEADLESS=false`
- **Respalda tu `.env`** pero nunca lo compartas

¡Listo para facturar automáticamente! 🚀
