# TESTING - Checklist de pruebas antes de usar en producción

Guía completa para probar el bot antes de usarlo con facturas reales.

---

## ✅ Checklist PRE-INSTALACIÓN

- [ ] Python 3.8+ instalado
- [ ] Python está en PATH (probaste `python --version`)
- [ ] Tienes usuario y contraseña AFIP correctos
- [ ] Tienes acceso a internet para AFIP
- [ ] 2GB de espacio libre en disco
- [ ] PowerShell o Terminal con permisos suficientes

---

## ✅ Checklist POST-INSTALACIÓN

Después de ejecutar `.\setup.bat` o `bash setup.sh`:

- [ ] No hubo errores en la instalación (viste "INSTALACION COMPLETADA")
- [ ] Se creó carpeta `logs/`
- [ ] Se creó `facturas.xlsx` con datos de ejemplo
- [ ] Se creó `.env` (copiado desde `.env.example`)
- [ ] Carpeta `venv/` existe y contiene entorno virtual
- [ ] `pip list` muestra: playwright, openpyxl, python-dotenv, schedule

**Comando para verificar:**
```powershell
ls -Force
pip list | Select-String "playwright|openpyxl|python-dotenv|schedule"
```

---

## ✅ Checklist CONFIGURACIÓN

- [ ] Abriste `.env` en editor de texto
- [ ] Llenaste `AFIP_CUIT` (sin guiones)
- [ ] Llenaste `AFIP_PASSWORD` (Clave Fiscal, no usuario)
- [ ] `AFIP_PUNTO_VENTA=1` (o tu número correcto)
- [ ] `HEADLESS=false` (para ver el navegador en pruebas)
- [ ] Guardaste `.env`
- [ ] **NO** compartiste el contenido de `.env` con nadie

---

## ✅ Checklist EXCEL DE EJEMPLO

Abre `facturas.xlsx`:

- [ ] Tiene columnas: fecha, descripcion, monto, cuit_cliente, nombre_cliente, estado, cae, nro_comprobante
- [ ] Hay al menos 2 filas con datos de ejemplo
- [ ] Las filas tienen estado `PENDIENTE`
- [ ] Las fechas están en formato `dd/mm/aaaa`
- [ ] Los montos son números sin separadores (5000, no 5.000,00)
- [ ] Hay al menos una fila con CUIT=99999999999 (consumidor final)

---

## ✅ PRUEBA 1: Validación de ambiente

**Comando:**
```powershell
python main.py --entorno
```

**Verificar salida:**
```
Variables de entorno:
  AFIP_CUIT: 201...89
  AFIP_PASSWORD: ***OCULTO***
  AFIP_PUNTO_VENTA: 1
  HEADLESS: false
```

**✓ Si ves esto = OK**
**✗ Si ves "NO CONFIGURADO" = Edita .env**

---

## ✅ PRUEBA 2: Crear Excel

**Comando:**
```powershell
python main.py --crear-ejemplo
```

**Verificar:**
- [ ] Crea `facturas.xlsx` (o actualiza si existe)
- [ ] Contiene datos de prueba válidos
- [ ] No hay errores en la consola

---

## ✅ PRUEBA 3: Login AFIP (SIN EXCEL)

**Propósito:** Verificar que tus credenciales funcionan sin procesar facturas

**Comando:**
```powershell
# Renombra facturas.xlsx temporalmente
Rename-Item facturas.xlsx facturas.xlsx.bak

# Ejecuta
python main.py --ahora

# Si log dice "Sin facturas pendientes" = OK, credenciales funcionan
```

**Verificar en log:**
```
Configuración cargada: ✓
CUIT: 201...89 ✓
Sin facturas pendientes ✓
```

**Si falla:**
- [ ] Verifica el CUIT (sin guiones)
- [ ] Verifica la contraseña (es la Clave Fiscal)
- [ ] Intenta login manual en https://auth.afip.gov.ar
- [ ] Revisa `logs/login_error_*.png` si existe

**Cuando funcione:**
```powershell
Rename-Item facturas.xlsx.bak facturas.xlsx
```

---

## ✅ PRUEBA 4: Primera factura (CRÍTICA)

**Propósito:** Emitir una factura de prueba real

**Preparar Excel:**
1. Abre `facturas.xlsx`
2. Borra todas las filas de prueba excepto UNA
3. Verifica que sea Consumidor Final (CUIT=99999999999):
```
fecha           | descripcion              | monto | cuit_cliente | nombre_cliente    | estado
02/04/2026      | FACTURA DE PRUEBA        | 100   | 99999999999  | Consumidor Final  | PENDIENTE
```
4. Guarda Excel

**Ejecutar:**
```powershell
python main.py --ahora
```

**Observar mientras se ejecuta:**
- [ ] Abre navegador Chrome
- [ ] Navega a https://auth.afip.gov.ar
- [ ] Ingresa tu CUIT
- [ ] Ingresa tu contraseña
- [ ] Se loguea y vai a Comprobantes en Línea
- [ ] Llena el formulario automáticamente
- [ ] Clickea Confirmar
- [ ] Aparece la factura con CAE y número

**Después de ejecutar - Verificar Excel:**
- [ ] `estado` cambió a `EMITIDA`
- [ ] `cae` tiene 11 dígitos (ej: 12345678990)
- [ ] `nro_comprobante` tiene 8 dígitos (ej: 00000001)
- [ ] La fila está con fondo VERDE

**Si todo OK:**
```
✅ ¡ÉXITO! El bot funciona correctamente
```

**Si algo falla:**
1. Abre el log más reciente:
   ```powershell
   Get-Content logs/facturador_*.log -Tail 30
   ```
2. Busca la línea con ERROR
3. Consulta [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. Si hay screenshot de error, ábrelo para ver visualmente

---

## ✅ PRUEBA 5: Múltiples facturas

**Propósito:** Verificar que procesa varias en lote

**Preparar Excel con 3 facturas:**
```
fecha      | descripcion                | monto  | cuit_cliente | nombre_cliente      | estado
02/04/2026 | Prueba 1 - Consumidor     | 500    | 99999999999  | Consumidor Final    | PENDIENTE
03/04/2026 | Prueba 2 - Empresa        | 1000   | 20123456789  | EMPRESA XYZ SRL     | PENDIENTE
04/04/2026 | Prueba 3 - Otra empresa   | 2000   | 27987654321  | CONSULTORES ABC SRL | PENDIENTE
```

**Ejecutar:**
```powershell
python main.py --ahora
```

**Verificar:**
- [ ] Procesa las 3 facturas secuencialmente
- [ ] Todas se emiten correctamente
- [ ] Todas tienen CAE y nro_comprobante
- [ ] Todas están en verde (EMITIDA)
- [ ] El log muestra: "RESUMEN: 3 exitosa(s), 0 fallida(s)"

---

## ✅ PRUEBA 6: Factura con error (simulada)

**Propósito:** Verificar que el bot maneja errores correctamente

**Preparar Excel con factura INVÁLIDA:**
```
fecha      | descripcion        | monto | cuit_cliente | nombre_cliente | estado
02/04/2026 | TEST CON ERROR     | XYZ   | INVALIDO     | TEST           | PENDIENTE
```

**Ejecutar:**
```powershell
python main.py --ahora
```

**Verificar:**
- [ ] El bot intenta procesar
- [ ] Falla al validar datos
- [ ] Loguea el error específico
- [ ] **NO** crashea, **CONTINÚA** si hubiese más facturas
- [ ] El Excel NO se modifica para la factura fallida

---

## ✅ PRUEBA 7: Logs y debugging

**Cambiar a modo DEBUG:**
```powershell
# Edita .env
LOG_LEVEL=DEBUG

# Ejecuta
python main.py --ahora

# Verifica el log detallado
Get-Content logs/facturador_*.log -Tail 50
```

**Verificar log tiene:**
- [ ] Timestamps de cada acción
- [ ] Información de selectors encontrados/no encontrados
- [ ] Valores de campos ingresados
- [ ] Respuestas de AFIP
- [ ] Resumen final

---

## ✅ PRUEBA 8: Modo headless

**Propósito:** Verificar que funciona sin interfaz gráfica

**Cambiar en .env:**
```ini
HEADLESS=true
```

**Ejecutar:**
```powershell
python main.py --ahora
```

**Verificar:**
- [ ] No se abre ningún navegador visible
- [ ] El bot sigue funcionando (no hay error)
- [ ] Las facturas se emiten correctamente
- [ ] El Excel se actualiza normalmente

**Revertir para producción:**
```ini
HEADLESS=true  # Dejar en true para producción
```

---

## ✅ PRUEBA 9: Scheduler (automático)

**Propósito:** Verificar que se ejecuta automáticamente

**Ejecutar:**
```powershell
python main.py
```

**Verificar:**
- [ ] Muestra: "Próxima ejecución: viernes ..."
- [ ] Muestra: "Presione Ctrl+C para detener"
- [ ] Se queda esperando sin hacer nada

**Detener:**
```powershell
Ctrl + C
```

---

## ✅ PRUEBA 10: Logs y limpieza

**Verificar logs:**
```powershell
ls logs/
Get-Content logs/facturador_*.log -Tail 1
```

**Verificar limpieza automática:**
```powershell
# El bot automáticamente borra logs >7 días
# Verifica que solo hay logs recientes en logs/
```

---

## 🎯 CHECKLIST FINAL - READY FOR PRODUCTION

- [ ] Todas las pruebas 1-10 pasaron ✓
- [ ] El bot emite facturas correctamente
- [ ] Genera CAE y números de comprobante válidos
- [ ] Excel se actualiza automáticamente
- [ ] No hay errores no manejados
- [ ] Logs se generan correctamente
- [ ] HEADLESS=true en .env
- [ ] `.env` NO está en Git (verificar `.gitignore`)
- [ ] Respaldaste tus primeros CAEs para referencia
- [ ] Probaste con datos reales (al menos 3 facturas)

---

## 📋 Checklist de SEGURIDAD

Antes de cualquier uso en producción:

- [ ] `.env` tiene permisos restrictivos (solo tu usuario puede leer)
- [ ] `.env` está en `.gitignore`
- [ ] No compartiste `.env` con nadie
- [ ] No grabaste `.env` en screenshot o email
- [ ] Tienes backup de tus CAEs emitidos (por si el Excel se corrompe)
- [ ] El usuario AFIP tiene solo permisos necesarios
- [ ] La máquina donde se ejecuta es segura

---

## 📞 Si algo falla en pruebas

**Pasos sistemáticos:**

1. **Anota el error exacto** (importante)
2. **Revisa el log completo**: `logs/facturador_*.log`
3. **Si hay screenshot**: Abre y observa visualmente
4. **Consulta [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
5. **Intenta de nuevo con cambios mínimos**

---

## 🚀 Ready to deploy!

Cuando todas las pruebas pasen:

```powershell
# Cambiar a headless
# .env: HEADLESS=true

# Ejecutar automáticamente cada viernes
python main.py

# O ejecutar bajo demanda
python main.py --ahora
```

**Monitorear:**
- Verifica logs periódicamente
- Confirma que las facturas se emiten
- Revisa Excel actualizado
- Guarda referencias de CAEs

🎉 **¡Bot en producción!**
