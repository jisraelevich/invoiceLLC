# 📚 ÍNDICE - Documentación completa

Bienvenido al **Facturador Automático AFIP**. Esta es la guía para orientarte en toda la documentación disponible.

---

## 🚀 Por dónde empezar

### Si solo tienes 5 minutos
👉 Lee [QUICKSTART.md](QUICKSTART.md) - Instalación y ejecución en 5 pasos

### Si es tu primera vez
👉 Lee [INSTALACION.md](INSTALACION.md) - Guía paso a paso detallada

### Si ya lo instalaste
👉 Ejecuta: `python main.py --ahora`

---

## 📖 Documentación disponible

### 🎯 Inicio rápido
| Documento | Tiempo | Contenido |
|-----------|--------|----------|
| [QUICKSTART.md](QUICKSTART.md) | 5 min | Instalación rápida, setup básico |
| [INSTALACION.md](INSTALACION.md) | 20 min | Instalación paso a paso (con imágenes mentales) |

### ⚙️ Referencia técnica
| Documento | Contenido |
|-----------|----------|
| [README.md](README.md) | Documentación completa del proyecto |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Cómo funciona internamente, módulos, flujos |
| [TESTING.md](TESTING.md) | Checklist de pruebas antes de producción |

### 🆘 Ayuda y problemas
| Documento | Para qué |
|-----------|----------|
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Solución de errores comunes |

---

## 📂 Archivos del proyecto

### 🔧 Configuración
```
.env                    ← TUS CREDENCIALES (EDITAR Y RELLENAR)
.env.example           ← Template de .env (no editar)
requirements.txt       ← Dependencias Python
config.py              ← Configuración centralizada
```

### 💻 Código principal
```
main.py                ← Punto de entrada (lo que ejecutas)
bot.py                 ← Automatización con Playwright
excel_handler.py       ← Lectura/escritura de Excel
scheduler.py           ← Ejecución automática
utils.py               ← Funciones compartidas
```

### 📊 Datos
```
facturas.xlsx          ← TUS FACTURAS (Excel que se completa)
logs/                  ← Carpeta de logs y screenshots
```

### 🔨 Instalación
```
setup.bat              ← Instalador automático (Windows)
setup.sh               ← Instalador automático (Linux/Mac)
```

---

## 🎯 Flujos según tu situación

### 📥 "Acabo de descargar los archivos"
1. Lee [QUICKSTART.md](QUICKSTART.md) (5 min)
2. Ejecuta `setup.bat` (o `setup.sh` en Linux/Mac)
3. Edita `.env` con tus credenciales AFIP
4. Ejecuta `python main.py --ahora`

### ⚙️ "Necesito entender cómo funciona"
1. Lee [README.md](README.md) - Visión general
2. Lee [ARQUITECTURA.md](ARQUITECTURA.md) - Detalles técnicos
3. Abre los archivos `.py` y explora el código

### 🐛 "Algo no funciona"
1. Revisa los últimos 50 líneas del log: `Get-Content logs/facturador_*.log -Tail 50`
2. Busca el error en [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Si no aparece, prueba con `HEADLESS=false` para ver el navegador

### ✅ "Quiero pasar a producción"
1. Lee [TESTING.md](TESTING.md) - Todas las pruebas necesarias
2. Ejecuta todas las pruebas en orden
3. Cuando pasen todas: `python main.py` (sin --ahora para automático)

---

## 🔐 ¿Qué NO hacer?

❌ No subas `.env` a Git
❌ No compartas el contenido de `.env`
❌ No edites manualmente valores de CAE en Excel (el bot lo hace)
❌ No uses el bot con certificados digitales (no está diseñado para eso)
❌ No personalices AFIP_PASSWORD de forma visible

---

## ✅ Pre-requisitos

- ✓ Python 3.8+ (descargar de python.org)
- ✓ Usuario AFIP con Clave Fiscal
- ✓ Excel
- ✓ Conexión a internet

No necesitas:
- ✗ Certificado digital (se usa portal web)
- ✗ Web services AFIP (se usa Playwright)
- ✗ UiPath o RPA costoso

---

## 🚀 Ejecución

### Modo inmediato (para probar)
```powershell
python main.py --ahora
```
Procesa todas las facturas pendientes de inmediato.

### Modo automático (producción)
```powershell
python main.py
```
Se ejecuta cada viernes a largo 9:00 AM. Presiona `Ctrl+C` para detener.

### Otros comandos
```powershell
python main.py --crear-ejemplo      # Crear Excel de prueba
python main.py --entorno            # Ver configuración cargada
python main.py --logs               # Ver estadísticas de logs
```

---

## 📊 Estructura de directorios

```
facturador_afip/
├── 📖 Documentación
│   ├── README.md               ← Documentación completa
│   ├── INSTALACION.md          ← Guía de instalación
│   ├── QUICKSTART.md           ← Start rápido (5 min)
│   ├── ARQUITECTURA.md         ← Cómo funciona internamente
│   ├── TESTING.md              ← Checklist de pruebas
│   ├── TROUBLESHOOTING.md      ← Solución de errores
│   └── INDEX.md                ← Este archivo
│
├── 🔧 Configuración
│   ├── .env                    ← TUS DATOS (RELLENAR)
│   ├── .env.example            ← Template
│   ├── requirements.txt        ← Dependencias
│   └── config.py               ← Configuración centralizada
│
├── 💻 Código
│   ├── main.py                 ← Ejecutable principal
│   ├── bot.py                  ← Playwright (AFIP automation)
│   ├── excel_handler.py        ← Manejo de Excel
│   ├── scheduler.py            ← Scheduler automático
│   └── utils.py                ← Funciones compartidas
│
├── 📊 Datos
│   ├── facturas.xlsx           ← TUS FACTURAS
│   └── logs/                   ← Logs y screenshots
│
└── 🔨 Setup
    ├── setup.bat               ← Instalador (Windows)
    └── setup.sh                ← Instalador (Linux/Mac)
```

---

## 🔍 Búsqueda de ayuda

### Si necesitas... busca en:
| Necesidad | Documento |
|-----------|----------|
| Instrucciones paso a paso | [INSTALACION.md](INSTALACION.md) |
| Referencia rápida | [QUICKSTART.md](QUICKSTART.md) |
| Entender el código | [ARQUITECTURA.md](ARQUITECTURA.md) |
| Mensaje de error | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Probar antes de producción | [TESTING.md](TESTING.md) |
| Visión general | [README.md](README.md) |

---

## 💡 Tips importantes

1. **Prueba con 1 factura primero** - No hagas lote masivo en tu primer intento
2. **Usa HEADLESS=false inicialmente** - Para ver qué hace el bot en el navegador
3. **Revisa los logs** - Guardan toda la información de cada ejecución
4. **Respalda tus CAEs** - Copia los CAEs emitidos a un txt por si Excel se corrompe
5. **AFIP cambia seguido** - Si falla, probablemente cambió su interfaz (edita los selectores)

---

## 🆘 ¿Necesitas ayuda?

1. **Primero:** Revisa [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Luego:** Mira el log más reciente en `logs/`
3. **Tercero:** Verifica tus datos en `.env`
4. **Último:** Abre un issue o contacta al soporte

---

## ✨ Una vez que funcione...

Felicidades, ya tienes:
- ✓ Bot de facturación automática
- ✓ Excel con CAEs y números de comprobantes poblados automáticamente
- ✓ Logs de auditoría de cada factura emitida
- ✓ Ejecución automática cada viernes
- ✓ Manejo de errores y retries inteligentes

🎉 **¡Facturación AFIP sin intervención manual!**

---

## 📞 Resumen de comandos útiles

```powershell
# Instalación
.\setup.bat                          # Windows
bash setup.sh                        # Linux/Mac

# Ejecución
python main.py --ahora               # Inmediato
python main.py                       # Automático (viernes 9 AM)
python main.py --crear-ejemplo       # Crear Excel de prueba
python main.py --entorno             # Ver configuración

# Ver logs
Get-Content logs/facturador_*.log -Tail 50     # Windows
tail -50 logs/facturador_*.log                 # Linux/Mac

# Editar configuración
notepad .env                         # Windows
nano .env                            # Linux/Mac
```

---

**🚀 Comienza por [QUICKSTART.md](QUICKSTART.md) o [INSTALACION.md](INSTALACION.md) según tu experiencia**

**¡Buena suerte! 🍀**
