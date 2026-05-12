# FACTURADOR CALCULADOR - Documentación Completa

## 📚 Índice de Documentación

### 1. **[ESPECIFICACIONES.md](ESPECIFICACIONES.md)** - Qué hace el app
Describe la visión general, funcionalidades principales, y requisitos del sistema.

**Temas cubiertos:**
- Dashboard por mes
- Panel de control con montos
- Entrada de datos (4 viernes)
- Cálculo y previsualización
- Aprobación y facturación
- Tab de resultados
- Tab admin (precios)
- JSON y persistencia

**Leer si:** Quieres entender QUÉ es el app y para QUÉ sirve.

---

### 2. **[ARQUITECTURA.md](ARQUITECTURA.md)** - Cómo está hecho
Describe la estructura del código, módulos, y flujo de datos.

**Temas cubiertos:**
- Estructura de carpetas
- Módulos principales (models, routes, utils)
- Flujo de datos (lectura, guardado, facturación)
- Integración con facturador_afip
- Configuración
- Dependencias
- Testing

**Leer si:** Quieres entender CÓMO está construido internamente.

---

### 3. **[FLUJO_USUARIO.md](FLUJO_USUARIO.md)** - Cómo se usa
Describe paso a paso cómo el usuario interactúa con el app.

**Escenarios cubiertos:**
1. Primeros pasos (mes actual)
2. Revisar mes anterior
3. Alerta de sobrecarga
4. Tab admin
5. Transición a mes siguiente
6. Errores y recuperación

**Leer si:** Quieres ver CÓMO USA el usuario la app, con capturas de pantalla.

---

### 4. **[TIMING_MONITOREO.md](TIMING_MONITOREO.md)** - Medición de tiempos
Describe cómo se capturan y muestran los tiempos de procesamiento.

**Temas cubiertos:**
- Datos de timing por factura
- Pantalla de resultados con tiempos
- Pantalla en vivo durante facturación
- Lógica de backend (captura de tiempos)
- Frontend con WebSocket
- No mostrar como "bot"
- Alertas por timing inusual

**Leer si:** Quieres entender CÓMO SE MUESTRAN LOS TIEMPOS y CÓMO SE CAPTURAN.

---

### 5. **[JSON_SCHEMA.md](JSON_SCHEMA.md)** - Estructura de datos
Define exactamente cómo se estructuran los archivos JSON.

**Temas cubiertos:**
- Schema mensual (april_2026.json)
- Schema de precios (precios_historico.json)
- Schema de config (config.json)
- Tipos de datos
- Ejemplos completos
- Validación en Python
- Migración entre versiones

**Leer si:** Quieres ENTENDER LA ESTRUCTURA DE JSON o necesitas parsear datos.

---

## 🎯 Mapa de Lectura Recomendado

### Para Entender el Proyecto (30 minutos)
1. **ESPECIFICACIONES.md** - Qué es
2. **FLUJO_USUARIO.md** - Cómo se ve
3. **TIMING_MONITOREO.md** - Datos adicionales

### Para Desarrollar el Proyecto (2-3 horas)
1. **ESPECIFICACIONES.md** - Requisitos
2. **ARQUITECTURA.md** - Estructura
3. **JSON_SCHEMA.md** - Formatos
4. **FLUJO_USUARIO.md** - Testing manual

### Para Debuggear/Mantener (1-2 horas)
1. **ARQUITECTURA.md** - Dónde está qué
2. **JSON_SCHEMA.md** - Validación
3. **TIMING_MONITOREO.md** - Logs

---

## 💾 Estructura de Carpetas Generada

```
facturador_calculador/
│
├── app.py                          ← Entry point
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── models.py                   ← Persistencia JSON
│   ├── routes.py                   ← Endpoints HTTP
│   ├── utils.py                    ← Lógica negocio
│   └── logger.py
│
├── data/
│   ├── 2026/
│   │   ├── april_2026.json
│   │   ├── may_2026.json
│   │   └── ...
│   └── config/
│       ├── precios_historico.json
│       └── config.json
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── admin.html
│
├── static/
│   ├── css/style.css
│   └── js/app.js
│
├── logs/
│   └── app.log
│
└── Doc/                            ← Documentación
    ├── README.md (este archivo)
    ├── ESPECIFICACIONES.md
    ├── ARQUITECTURA.md
    ├── FLUJO_USUARIO.md
    ├── TIMING_MONITOREO.md
    └── JSON_SCHEMA.md
```

---

## 🚀 Quick Start

### Instalación
```bash
cd facturador_calculador
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Ejecutar
```bash
python app.py
# Abre: http://localhost:5000
```

---

## 📋 Checklist de Desarrollo

### MVP (Mínimo Viable)
- [ ] Estructura Flask básica
- [ ] Dashboard con tab switcher
- [ ] Input de montos (4 viernes)
- [ ] Guardado en JSON
- [ ] Tabla de preview
- [ ] Botón facturar (mock)

### Integración
- [ ] Conectar con facturador_afip
- [ ] Captura de tiempos
- [ ] Mostrar CAEs
- [ ] Tab resultados

### Pulido
- [ ] Admin tab
- [ ] Validaciones
- [ ] Error handling
- [ ] Histórico
- [ ] WebSocket para tiempo real

---

## ⚙️ Configuración

Ver `data/config/config.json` para:
- Rutas a facturador_afip
- Conceptos de facturación
- Timeouts
- Puntos de venta AFIP

---

## 📞 Soporte

**Si tienes dudas sobre:**
- **QUÉ hace:** Lee ESPECIFICACIONES.md
- **CÓMO funciona:** Lee ARQUITECTURA.md
- **CÓMO usarlo:** Lee FLUJO_USUARIO.md
- **TIEMPOS:** Lee TIMING_MONITOREO.md
- **JSON:** Lee JSON_SCHEMA.md

---

## 📝 Historial

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-24 | Documentación inicial completa |

---

**Estado:** Documentación de especificación lista para desarrollo.
**Próximo paso:** Iniciar desarrollo de MVP.
