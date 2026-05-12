
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash
import json
from pathlib import Path
import subprocess
import importlib.util
import sys
import base64
from datetime import datetime

# Cargar configuración desde config.py
spec = importlib.util.spec_from_file_location("config", str(Path(__file__).parent / "config.py"))
config = importlib.util.module_from_spec(spec)
sys.modules["config"] = config
spec.loader.exec_module(config)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

JSON_PATH = Path(config.JSON_PATH)
GEN_CSV_SCRIPT = Path(config.GEN_CSV_SCRIPT)

def convert_date_mm_dd_to_dd_mm(date_str):
    """Convert MM/DD/YYYY to DD/MM/YYYY"""
    if not date_str:
        return ""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            mm = parts[0].zfill(2)
            dd = parts[1].zfill(2)
            yyyy = parts[2]
            return f"{dd}/{mm}/{yyyy}"
    except:
        pass
    return date_str

def convert_date_dd_mm_to_mm_dd(date_str):
    """Convert DD/MM/YYYY back to MM/DD/YYYY"""
    if not date_str:
        print(f"[DATE-CONVERT] Empty date_str")
        return ""
    try:
        parts = date_str.strip().split('/')
        if len(parts) == 3:
            dd = parts[0].zfill(2)
            mm = parts[1].zfill(2)
            yyyy = parts[2]
            result = f"{mm}/{dd}/{yyyy}"
            print(f"[DATE-CONVERT] {date_str} -> {result}")
            return result
    except Exception as e:
        print(f"[DATE-CONVERT] ERROR converting {date_str}: {e}")
        pass
    return date_str

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save", methods=["POST"])
def save():
    try:
        mes = request.form.get("mes", "")
        anio = request.form.get("anio", "")
        facturas = []
        rows = int(request.form.get("rows", 0))
        for i in range(rows):
            f = {
                "cliente": request.form.get(f"cliente_{i}", ""),
                "cuit": request.form.get(f"cuit_{i}", ""),
                "concepto": request.form.get(f"concepto_{i}", ""),
                "fecha_planificada": request.form.get(f"fecha_planificada_{i}", ""),
                "monto": request.form.get(f"monto_{i}", ""),
                "tipo": request.form.get(f"tipo_{i}", ""),
                "estado": request.form.get(f"estado_{i}", "pendiente")
            }
            facturas.append(f)
        data = {"mes": mes, "anio": anio, "facturas": facturas}
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        flash("Plan saved successfully.")
    except Exception as e:
        flash(f"Error saving: {e}")
    return redirect(url_for("index"))

@app.route("/generar_csv", methods=["POST"])
def generar_csv():
    try:
        result = subprocess.run([
            sys.executable, str(GEN_CSV_SCRIPT)
        ], capture_output=True, text=True, cwd=GEN_CSV_SCRIPT.parent.parent)
        if result.returncode == 0:
            flash("facturas.csv generado correctamente.")
        else:
            flash(f"Error al generar CSV: {result.stderr}")
    except Exception as e:
        flash(f"Error al ejecutar script: {e}")
    return redirect(url_for("index"))

# ============================================================================
# API ENDPOINTS - Monthly Invoice Management
# ============================================================================

@app.route("/api/month/<int:year>/<int:month>", methods=["GET"])
def get_month_data(year, month):
    """Load invoice data for a specific month"""
    try:
        month_file = Path(__file__).parent / "data" / "months" / f"{year}-{month:02d}.json"
        
        print(f"\n[FLASK GET] Loading {year}-{month:02d} from {month_file}")
        
        if month_file.exists():
            with open(month_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[FLASK GET] Found file. Preview items: {len(data.get('preview', []))}")
            print(f"[FLASK GET] Data: {json.dumps(data, indent=2)}")
        else:
            # Return default empty structure with defaultContent
            data = {
                "year": year,
                "month": month,
                "estimated": 0,
                "defaultContent": "",  # Empty by default, will be set by user
                "preview": [],
                "results": []
            }
            print(f"[FLASK GET] File not found, returning default data")
        
        return data, 200
    except Exception as e:
        print(f"[FLASK GET ERROR] {str(e)}")
        return {"error": str(e)}, 500

@app.route("/api/month/<int:year>/<int:month>", methods=["POST"])
def save_month_data(year, month):
    """Save invoice data for a specific month"""
    try:
        data = request.get_json()
        
        print(f"\n[FLASK POST] Saving {year}-{month:02d}")
        print(f"[FLASK POST] Preview items: {len(data.get('preview', []))}")
        print(f"[FLASK POST] Full data: {json.dumps(data, indent=2)}")
        
        # Create directory if not exists
        month_dir = Path(__file__).parent / "data" / "months"
        month_dir.mkdir(parents=True, exist_ok=True)
        
        month_file = month_dir / f"{year}-{month:02d}.json"
        
        with open(month_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[FLASK POST] Saved to {month_file}")
        return {"success": True, "message": f"Datos de {month}/{year} guardados"}, 200
    except Exception as e:
        print(f"[FLASK POST ERROR] {str(e)}")
        return {"error": str(e)}, 500

@app.route("/api/month/<int:year>/<int:month>/send-to-afip", methods=["POST"])
def send_to_afip(year, month):
    """Send invoices to facturador_afip for AFIP processing"""
    try:
        import csv
        import time
        
        data = request.get_json()
        preview_items = data.get("preview", [])
        
        print(f"[DEBUG] Received data from frontend:")
        print(f"[DEBUG] Number of preview items: {len(preview_items)}")
        if preview_items:
            print(f"[DEBUG] First item DATE before conversion: {preview_items[0].get('date')}")
            converted_date = convert_date_mm_dd_to_dd_mm(preview_items[0].get('date', ''))
            print(f"[DEBUG] First item DATE after conversion: {converted_date}")
        
        if not preview_items:
            return {"error": "No invoices to process"}, 400
        
        # Path to facturador_afip
        facturador_afip_path = Path(__file__).parent.parent / "facturador_afip"
        csv_file = facturador_afip_path / "Facturas" / "facturas.csv"
        
        print(f"\n[FACTURATE] Processing {len(preview_items)} invoices")
        print(f"[FACTURATE] Writing to: {csv_file}")
        
        # Write preview items to CSV in facturador_afip format
        # CSV columns: FECHA,CODIGO,PRODUCTO SERVICO:,PRECIO UNITARIO,CUIT_CLIENTE,NOMBRE_CLIENTE,ESTADO,CAE,NRO_COMPROBANTE
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["FECHA", "CODIGO", "PRODUCTO SERVICO:", "PRECIO UNITARIO", "CUIT_CLIENTE", "NOMBRE_CLIENTE", "ESTADO", "CAE", "NRO_COMPROBANTE"])
                
                # Write data rows
                for item in preview_items:
                    original_date = item.get("date", "")
                    converted_date = convert_date_mm_dd_to_dd_mm(original_date)
                    print(f"[CSV-WRITE] Original: '{original_date}' → Converted: '{converted_date}'")
                    
                    writer.writerow([
                        converted_date,  # Convert MM/DD → DD/MM
                        item.get("billType", "055"),
                        "Servicios Informáticos y capacitacion DB",  # Correct service description
                        item.get("amount", 0),
                        "99999999999",  # Default consumer
                        "Consumidor Final",
                        "PENDIENTE",
                        "",  # CAE will be filled by AFIP
                        ""   # NRO_COMPROBANTE will be filled by AFIP
                    ])
            
            print(f"[FACTURATE] ✅ CSV written with {len(preview_items)} rows")
        except Exception as e:
            print(f"[FACTURATE] ❌ Error writing CSV: {e}")
            return {"error": f"Error writing CSV: {str(e)}"}, 500
        
        # Call facturador_afip/main.py in background
        # Note: This subprocess will try to open Chromium and process bills via AFIP
        # WARNING: This can take 1-50 minutes depending on AFIP responsiveness
        print(f"[FACTURATE] Calling facturador_afip/main.py --ahora --modo 2")
        print(f"[FACTURATE] ⏳ VERY IMPORTANT: This may take 1-50 minutes (AFIP is slow)")
        print(f"[FACTURATE] Timeout set to 60 minutes max")
        try:
            result = subprocess.run(
                [sys.executable, str(facturador_afip_path / "main.py"), "--ahora", "--modo", "2"],
                cwd=str(facturador_afip_path),
                capture_output=True,
                text=True,
                timeout=3600  # 60 minutes timeout - AFIP can take up to 50min
            )
            
            print(f"[FACTURATE] Return code: {result.returncode}")
            if result.stdout:
                print(f"[FACTURATE] STDOUT:\n{result.stdout[:500]}")
            if result.stderr:
                print(f"[FACTURATE] STDERR:\n{result.stderr[:500]}")
            print(f"[FACTURATE] ✅ facturador_afip completed")
                
        except subprocess.TimeoutExpired:
            print(f"[FACTURATE] ⚠️  Timeout after 60min - this should not happen")
            print(f"[FACTURATE] ERROR: Main.py exceeded maximum timeout")
            return {"error": "AFIP processing exceeded 60 minute timeout"}, 500
        except Exception as e:
            print(f"[FACTURATE] ❌ Error calling main.py: {e}")
            return {"error": f"Error calling facturador_afip: {str(e)}"}, 500
        
        # Read updated CSV to separate PROCESADO from PENDIENTE
        print(f"[FACTURATE] Reading results from updated CSV: {csv_file}")
        print(f"[FACTURATE] CSV file exists: {csv_file.exists()}")
        processed_bills = []      # Bills with CAE (successful)
        pending_bills = []        # Bills still PENDIENTE (failed)
        
        try:
            # Use 'utf-8-sig' to strip BOM (Byte Order Mark) if present
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    print(f"[FACTURATE] Row {idx}: FECHA='{row.get('FECHA')}' ESTADO='{row.get('ESTADO')}' CAE='{row.get('CAE')}'")
                    estado = row.get("ESTADO", "").strip().upper()
                    cae = row.get("CAE", "").strip()
                    fecha_raw = row.get("FECHA")
                    print(f"[FACTURATE]   Processing: estado={estado}, cae={cae}, fecha_raw='{fecha_raw}'")
                    
                    if estado == "PROCESADO" and cae:
                        # Successfully processed - add to results
                        converted_date = convert_date_dd_mm_to_mm_dd(row.get("FECHA"))
                        processed_bills.append({
                            "date": converted_date,
                            "billType": row.get("CODIGO"),
                            "amount": int(row.get("PRECIO UNITARIO", 0)),
                            "cae": cae,
                            "nro_comprobante": row.get("NRO_COMPROBANTE")
                        })
                        print(f"[FACTURATE] OK Bill PROCESADO: {row.get('FECHA')} -> {converted_date} = ${row.get('PRECIO UNITARIO')} (CAE={cae[:8]}...)")
                    
                    else:
                        # Still PENDIENTE (failed) - keep for retry
                        converted_date = convert_date_dd_mm_to_mm_dd(row.get("FECHA"))
                        pending_bills.append({
                            "date": converted_date,
                            "billType": row.get("CODIGO", "055"),
                            "amount": int(row.get("PRECIO UNITARIO", 0)),
                            "status": "01"
                        })
                        print(f"[FACTURATE] PENDING Bill: {row.get('FECHA')} -> {converted_date} = ${row.get('PRECIO UNITARIO')} (will retry)")
            
            print(f"[FACTURATE] Summary: {len(processed_bills)} processed, {len(pending_bills)} pending")
            
        except Exception as e:
            print(f"[FACTURATE] ERROR reading results: {e}")
        
        # Load current month data
        month_dir = Path(__file__).parent / "data" / "months"
        month_dir.mkdir(parents=True, exist_ok=True)
        month_file = month_dir / f"{year}-{month:02d}.json"
        
        if month_file.exists():
            with open(month_file, "r", encoding="utf-8") as f:
                stored_data = json.load(f)
        else:
            stored_data = data
        
        # Update results with processed bills (ADD to existing, don't replace)
        if "results" not in stored_data:
            stored_data["results"] = []
        
        stored_data["results"].extend(processed_bills)
        
        # Keep only PENDING bills in preview (for retry)
        stored_data["preview"] = pending_bills
        
        print(f"[FACTURATE] Updating month data:")
        print(f"   - preview: {len(pending_bills)} items (for retry)")
        print(f"   - results: {len(stored_data['results'])} items total")
        
        # Save updated data
        with open(month_file, "w", encoding="utf-8") as f:
            json.dump(stored_data, f, ensure_ascii=False, indent=2)
        
        print(f"[FACTURATE] ✅ COMPLETE - {len(processed_bills)} processed, {len(pending_bills)} pending for retry")
        
        return {
            "success": True, 
            "message": f"Procesadas {len(processed_bills)} facturas, {len(pending_bills)} pendientes para reintentar",
            "data": stored_data, 
            "processed": len(processed_bills),
            "pending": len(pending_bills)
        }, 200
        
    except Exception as e:
        print(f"[FACTURATE] ❌ CRITICAL ERROR: {str(e)}")
        return {"error": str(e)}, 500

@app.route("/api/export-to-afip-csv", methods=["POST"])
def export_to_afip_csv():
    """Export preview invoices to CSV format for facturador_afip"""
    try:
        data = request.get_json()
        csv_content = data.get("csvContent")
        invoices = data.get("invoices", [])
        
        if not csv_content or not invoices:
            return {"success": False, "error": "No CSV content or invoices provided"}, 400
        
        # Path to facturador_afip folder
        facturador_afip_path = Path(__file__).parent.parent / "facturador_afip" / "Facturas"
        facturador_afip_path.mkdir(parents=True, exist_ok=True)
        
        # Save as facturas.csv (this is what FacturarAhora.bat reads)
        csv_file = facturador_afip_path / "facturas.csv"
        
        print(f"\n[EXPORT-CSV] Exporting {len(invoices)} invoices to {csv_file}")
        print(f"[EXPORT-CSV] CSV Content:\n{csv_content}")
        
        # Write CSV file
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write(csv_content)
        
        print(f"[EXPORT-CSV] ✅ CSV saved successfully to {csv_file}")
        
        return {
            "success": True, 
            "message": f"Exported {len(invoices)} invoices to CSV",
            "filepath": str(csv_file),
            "invoiceCount": len(invoices)
        }, 200
        
    except Exception as e:
        print(f"[EXPORT-CSV] ❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}, 500

# ============================================================================
# LOGGING ENDPOINT - Debug logging to file
# ============================================================================

@app.route("/api/logs/write", methods=["POST"])
def write_log():
    """Write debug logs to file"""
    try:
        data = request.get_json()
        message = data.get("message", "")
        log_type = data.get("type", "info")  # info, warning, error
        
        # Create logs directory
        logs_dir = Path(__file__).parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Append to log file
        log_file = logs_dir / "debug.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{log_type.upper()}] {message}\n")
        
        return {"success": True}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/logs/clear", methods=["POST"])
def clear_logs():
    """Clear all logs"""
    try:
        log_file = Path(__file__).parent / "logs" / "debug.log"
        if log_file.exists():
            log_file.unlink()
        return {"success": True, "message": "Logs cleared"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/images/save", methods=["POST"])
def save_image():
    """Save debug image/screenshot"""
    try:
        data = request.get_json()
        image_data = data.get("image", "")  # base64 data
        label = data.get("label", "debug")
        
        # Create images directory
        images_dir = Path(__file__).parent / "logs" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        image_file = images_dir / f"{label}_{timestamp}.png"
        
        # Decode and save base64 image
        if image_data.startswith("data:image"):
            # Remove data URI prefix
            image_data = image_data.split(",")[1]
        
        image_bytes = base64.b64decode(image_data)
        with open(image_file, "wb") as f:
            f.write(image_bytes)
        
        return {"success": True, "filename": image_file.name}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, port=config.PORT)
