# QUICK START - Guía Rápida

Para los que ya saben qué hacer. Paso a paso en 5 minutos.

## 1️⃣ Instalación (Una sola vez)

**Windows PowerShell:**
```powershell
cd facturador_afip
.\setup.bat
```

**Linux/Mac:**
```bash
cd facturador_afip
bash setup.sh
```

Espera a que diga "INSTALACION COMPLETADA"

---

## 2️⃣ Configurar credenciales

Edita `.env`:
```ini
AFIP_CUIT=20123456789          # Tu CUIT (11 dígitos, sin guiones)
AFIP_PASSWORD=tu_clave_fiscal   # Tu Clave Fiscal
AFIP_PUNTO_VENTA=1              # Tu punto de venta
HEADLESS=false                  # false = ver navegador, true = sin interfaz
```

---

## 3️⃣ Preparar Excel

Abre `facturas.xlsx` y rellena:

```
fecha           | descripcion              | monto | cuit_cliente | nombre_cliente    | estado
02/04/2026      | Servicio consultoría     | 5000  | 99999999999  | Consumidor Final  | PENDIENTE
03/04/2026      | Soporte técnico          | 2500  | 20988776655  | Empresa ACME SRL  | PENDIENTE
```

**Reglas importantes:**
- `estado`: debe ser exactamente `PENDIENTE`
- `monto`: solo números (5000, no 5.000)
- `fecha`: formato `dd/mm/aaaa`
- `cuit_cliente`: 11 dígitos (99999999999 = consumidor final)

---

## 4️⃣ Ejecutar

**Primera vez (prueba con 1 factura):**
```powershell
python main.py --ahora
```

**Automático (viernes 9 AM):**
```powershell
python main.py
```

---

## 5️⃣ Verificar resultados

Abre `facturas.xlsx` y verifica:
- `estado`: cambió a `EMITIDA`
- `cae`: tiene 11 dígitos
- `nro_comprobante`: tiene 8 dígitos
- Fila está de color verde

✅ **¡Éxito!**

---

## 📋 Comandos útiles

```powershell
# Ver configuración
python main.py --entorno

# Crear Excel de ejemplo
python main.py --crear-ejemplo

# Ver logs (últimas 50 líneas)
Get-Content logs/facturador_*.log -Tail 50

# Ejecutar con logs detallados
# (edita .env: LOG_LEVEL=DEBUG)
```

---

## 🆘 Si algo falla

```powershell
# Edita .env
HEADLESS=false

# Ejecuta
python main.py --ahora

# Observa el navegador para ver dónde falla
# Abre el log más reciente: logs/facturador_*.log
```

---

## 🔐 Seguridad

⚠️ **NUNCA**:
- Subas `.env` a GitHub/Git
- Compartas el contenido de `.env`
- Escribas la contraseña en plain text en otros archivos

El `.env` ya está en `.gitignore` ✓

---

## 🚀 Listo para producción

Una vez que funcione una factura:
1. Agrega todas las facturas al Excel
2. Ejecuta: `python main.py --ahora`
3. O deja que se ejecute automáticamente los viernes a las 9 AM

---

## 📞 Problemas comunes

| Problema | Solución |
|----------|----------|
| "command not found" | Python no en PATH - reinstala marcando PATH |
| "No module named" | `pip install -r requirements.txt` |
| "playwright not found" | `playwright install` |
| "facturas.xlsx not found" | `python main.py --crear-ejemplo` |
| Falla en AFIP | Edita `.env`: `HEADLESS=false` y ve qué ocurre |
| No actualiza Excel | Cierra Excel y repite |

---

**¿Listo?** Ejecuta: `python main.py --ahora` 🚀
