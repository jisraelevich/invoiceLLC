# 🎯 START HERE - Empieza aquí

¡Bienvenido al **Facturador Automático AFIP**! 🚀

Este archivo te guía en 30 segundos sobre por dónde empezar.

---

## ¿Cuál es tu situación?

### 👤 "Acabo de descargar esto y no sé nada"

**Haz esto:**
1. Lee [QUICKSTART.md](QUICKSTART.md) (5 minutos)
2. Ejecuta `setup.bat` en PowerShell (o `setup.sh` en Linux/Mac)
3. Edita `.env` con tus datos AFIP
4. Ejecuta: `python main.py --ahora`

**Tiempo total:** 15 minutos

---

### 👨‍💼 "Entiendo de Python y quiero saber cómo funciona"

**Haz esto:**
1. Mira [README.md](README.md) - Visión general
2. Lee [ARQUITECTURA.md](ARQUITECTURA.md) - Cómo está construido
3. Abre el código en VS Code y explora `main.py`, `bot.py`, `excel_handler.py`

**Tiempo total:** 60 minutos

---

### ⚙️ "Necesito instalar en una máquina específica"

**Haz esto:**
1. Lee [INSTALACION.md](INSTALACION.md) - Instrucciones detalladas

**Para Windows:**
```powershell
.\setup.bat
```

**Para Linux/Mac:**
```bash
bash setup.sh
```

**Tiempo total:** 5 minutos (setup automático)

---

### 🐛 "Algo no funciona"

**Haz esto:**
1. Abre el log más reciente:
   ```powershell
   Get-Content logs/facturador_*.log -Tail 50
   ```
2. Busca el error en [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Ejecuta nuevamente observando el navegador:
   ```
   .env: HEADLESS=false
   python main.py --ahora
   ```

---

### ✅ "Quiero verificar que funciona antes de usarlo en producción"

**Haz esto:**
1. Lee [TESTING.md](TESTING.md) - Checklist completo de pruebas
2. Ejecuta todas las pruebas en orden (incluye prueba con 1 factura)

---

## 📚 Documentación rápida

```
INDEX.md               ← Índice de toda la documentación
├── QUICKSTART.md      ← 5 minutos para empezar
├── INSTALACION.md     ← Instalación paso a paso
├── README.md          ← Documentación completa
├── ARQUITECTURA.md    ← Cómo funciona internamente
├── TESTING.md         ← Pruebas antes de producción
├── TROUBLESHOOTING.md ← Solución de problemas
└── STATUS.md          ← Estado del proyecto
```

**👉 Si solo tienes 5 min:** Lee [QUICKSTART.md](QUICKSTART.md)
**👉 Si tienes 20 min:** Lee [INSTALACION.md](INSTALACION.md)
**👉 Si tienes 1 hora:** Lee todos los documentos en orden

---

## 🚀 Quick start (30 segundos)

**Windows:**
```powershell
cd facturador_afip
.\setup.bat
# Edita .env con tus datos AFIP
python main.py --ahora
```

**Linux/Mac:**
```bash
cd facturador_afip
bash setup.sh
# Edita .env con tus datos AFIP
python main.py --ahora
```

---

## ✨ Qué hace este bot

```
1. Lee facturas.xlsx
   ↓
2. Filtra filas con estado = PENDIENTE
   ↓
3. Para cada factura:
   - Abre portal AFIP
   - Se loguea automáticamente
   - Genera Factura C
   - Obtiene CAE y número
   ↓
4. Actualiza Excel con:
   - CAE
   - Número de comprobante
   - Marca como EMITIDA (verde)
   ↓
5. Guarda logs de todo
```

---

## 🎯 Pasos para empezar HOY

**Paso 1 - Instalación (5 min):**
```powershell
.\setup.bat
```

**Paso 2 - Configuración (2 min):**
Edita `.env`:
```ini
AFIP_CUIT=TU_CUIT_SIN_GUIONES
AFIP_PASSWORD=TU_CLAVE_FISCAL
```

**Paso 3 - Primera factura (10 min):**
```powershell
python main.py --ahora
```

**Observa el navegador mientras ocurre la magia ✨**

---

## ❌ NO necesitas

- ❌ Certificado digital (se usa portal web)
- ❌ Web Services AFIP (se usa Playwright)
- ❌ UiPath, Blue Prism u otro RPA caro
- ❌ Conocimientos avanzados de programación

## ✅ Necesitas

- ✅ Python 3.8+ instalado
- ✅ Usuario y contraseña AFIP
- ✅ Conexión a internet
- ✅ 5 minutos de tu tiempo

---

## 🆘 Problemas comunes

### "No encuentro Python"
👉 Descarga de https://www.python.org
👉 **IMPORTANTE**: Marca "Add Python to PATH" al instalar

### "El bot no se conecta a AFIP"
👉 Verifica que el CUIT sea correcto (sin guiones)
👉 Verifica que la Clave Fiscal sea correcta
👉 Intenta login manual en https://auth.afip.gov.ar

### "No actualiza el Excel"
👉 Cierra Excel
👉 Ejecuta de nuevo

### "No puedo ejecutar setup.bat"
👉 Click derecho en PowerShell
👉 "Run as Administrator" (Ejecutar como administrador)

---

## 🗂️ Estructura completa

```
facturador_afip/
├── 📖 DOCUMENTACIÓN (empieza aquí)
│   ├── START_HERE.md        ← TÚ ESTÁS AQUÍ
│   ├── QUICKSTART.md        ← 5 minutos
│   ├── INSTALACION.md       ← Paso a paso
│   ├── README.md            ← Documentación completa
│   ├── ARQUITECTURA.md      ← Detalles técnicos
│   ├── TESTING.md           ← Pruebas
│   ├── TROUBLESHOOTING.md   ← Errores
│   ├── INDEX.md             ← Índice
│   └── STATUS.md            ← Estado del proyecto
│
├── 🔧 CONFIGURACIÓN
│   ├── .env                 ← EDITAR CON TUS DATOS
│   ├── .env.example         ← Template
│   └── requirements.txt
│
├── 💻 CÓDIGO
│   ├── main.py
│   ├── bot.py
│   ├── excel_handler.py
│   ├── scheduler.py
│   ├── config.py
│   └── utils.py
│
├── 🚀 INSTALACIÓN
│   ├── setup.bat            ← Windows
│   └── setup.sh             ← Linux/Mac
│
└── 📊 DATA
    ├── facturas.xlsx        ← TUS FACTURAS
    └── logs/                ← Logs y screenshots
```

---

## 📞 Próximos pasos

1. **Ahora mismo:** Lee [QUICKSTART.md](QUICKSTART.md) (5 min)
2. **En 5 min:** Ejecuta `setup.bat`
3. **En 10 min:** Edita `.env` con tus credenciales
4. **En 15 min:** Ejecuta `python main.py --ahora`
5. **¡Listo!** Facturación automática 🎉

---

## 💡 Consejo final

⚠️ **Prueba con UNA sola factura primero.**
No hagas lote masivo en tu primer intento.

Una vez que veas que funciona → Confía en el bot y déjalo ejecutarse automáticamente cada viernes. ✨

---

## 🎯 Bottom line

| Acción | Tiempo |
|--------|--------|
| Instalar | 5 min |
| Configurar | 2 min |
| Hacerlo funcionar | 10 min |
| **TOTAL** | **17 minutos** |

Después: **Automatización completa.** Sin intervención manual.

---

## ✅ Checklist rápido

```
[ ] Descargué los archivos
[ ] Ejecuté setup.bat (o setup.sh)
[ ] Edité .env con mis datos AFIP
[ ] Ejecuté python main.py --ahora
[ ] Veo el navegador abrirse y completar facturas
[ ] El Excel se actualiza con CAE y números
[ ] ¡ÉXITO!
```

---

**¿Listo? 👉** Lee [QUICKSTART.md](QUICKSTART.md) ahora.

**Questions?** 👉 Revisa [INDEX.md](INDEX.md) para navegar la documentación.

**Problemas?** 👉 Consulta [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

🚀 **¡Comienza tu automatización AFIP ahora!**
