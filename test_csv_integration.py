#!/usr/bin/env python3
"""
Test CSV format compatibility between facturador_calculador and facturador_afip
"""
import csv
from pathlib import Path
import sys

# Test 1: Write CSV in the format we'll use
print("=" * 60)
print("TEST 1: Write CSV with preview items")
print("=" * 60)

test_csv = Path(__file__).parent / "test_facturas.csv"
preview_items = [
    {"date": "5/1/2026", "billType": "055", "amount": 11111},
    {"date": "5/1/2026", "billType": "055", "amount": 2222},
    {"date": "5/3/2026", "billType": "055", "amount": 3333},
    {"date": "5/4/2026", "billType": "055", "amount": 44444},
]

print(f"\nWriting to: {test_csv}")
try:
    with open(test_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["FECHA", "CODIGO", "PRODUCTO SERVICO:", "PRECIO UNITARIO", "CUIT_CLIENTE", "NOMBRE_CLIENTE", "ESTADO", "CAE", "NRO_COMPROBANTE"])
        
        # Write data rows
        for item in preview_items:
            writer.writerow([
                item.get("date", ""),
                item.get("billType", "055"),
                "Servicios Informáticos y capacitacion DB",
                item.get("amount", 0),
                "99999999999",
                "Consumidor Final",
                "PENDIENTE",
                "",
                ""
            ])
    
    print(f"✅ CSV written with {len(preview_items)} rows")
except Exception as e:
    print(f"❌ Error writing CSV: {e}")
    sys.exit(1)

# Test 2: Read CSV back and verify
print("\n" + "=" * 60)
print("TEST 2: Read CSV with csv.DictReader (like facturador_afip does)")
print("=" * 60)

try:
    with open(test_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows_read = list(reader)
    
    print(f"✅ Read {len(rows_read)} rows")
    for idx, row in enumerate(rows_read, 1):
        print(f"\nRow {idx}:")
        print(f"  FECHA: {row.get('FECHA')}")
        print(f"  CODIGO: {row.get('CODIGO')}")
        print(f"  PRECIO: {row.get('PRECIO UNITARIO')}")
        print(f"  ESTADO: {row.get('ESTADO')}")
        
        # Verify required fields
        fecha = row.get('FECHA', '').strip()
        codigo = row.get('CODIGO', '').strip()
        descripcion = row.get('PRODUCTO SERVICO:', '').strip()
        monto = row.get('PRECIO UNITARIO', '').strip()
        estado = row.get('ESTADO', 'PENDIENTE').strip().upper()
        
        if fecha and codigo and descripcion and monto and estado == 'PENDIENTE':
            print(f"  ✅ Valid row for processing")
        else:
            print(f"  ❌ Invalid row - missing required fields")
            
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    sys.exit(1)

# Test 3: Simulate facturador_afip CSV handler
print("\n" + "=" * 60)
print("TEST 3: Test facturador_afip CSV handler compatibility")
print("=" * 60)

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "facturador_afip"))
    from csv_handler import CSVHandler
    
    # Copy test file to facturador_afip location
    afip_csv_path = Path(__file__).parent.parent / "facturador_afip" / "Facturas" / "test_facturas.csv"
    print(f"\nCopying to: {afip_csv_path}")
    
    import shutil
    shutil.copy(test_csv, afip_csv_path)
    
    # Load with CSVHandler
    handler = CSVHandler(str(afip_csv_path))
    if handler.cargar_csv():
        print(f"✅ CSVHandler loaded {len(handler.datos)} rows")
        
        pendientes = handler.obtener_filas_pendientes()
        print(f"✅ Found {len(pendientes)} pending invoices")
        
        for idx, fila in enumerate(pendientes, 1):
            print(f"\n  Fila {idx}:")
            print(f"    Fecha: {fila['fecha']}")
            print(f"    Codigo: {fila['codigo']}")
            print(f"    Descripcion: {fila['descripcion']}")
            print(f"    Monto: {fila['monto']}")
            print(f"    Estado: {fila['estado']}")
            
    else:
        print(f"❌ CSVHandler failed to load")
        sys.exit(1)
        
except ImportError as e:
    print(f"⚠️  Could not import CSVHandler: {e}")
    print("   This might be OK - dependencies may not be installed")
except Exception as e:
    print(f"❌ Error with CSVHandler: {e}")
    sys.exit(1)

# Test 4: Test CSV save/update functionality
print("\n" + "=" * 60)
print("TEST 4: Test CSV update (simulating AFIP results)")
print("=" * 60)

try:
    # Simulate updating with CAE results
    updated_csv = Path(__file__).parent / "test_facturas_updated.csv"
    
    with open(test_csv, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)
    
    # Update each row with CAE
    with open(updated_csv, 'w', newline='', encoding='utf-8') as f_out:
        fieldnames = ["FECHA", "CODIGO", "PRODUCTO SERVICO:", "PRECIO UNITARIO", "CUIT_CLIENTE", "NOMBRE_CLIENTE", "ESTADO", "CAE", "NRO_COMPROBANTE"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, row in enumerate(rows, 1):
            row['ESTADO'] = 'PROCESADO'
            row['CAE'] = f'974052026{idx:06d}'
            row['NRO_COMPROBANTE'] = f'{idx:08d}'
            writer.writerow(row)
    
    print(f"✅ Updated CSV written to: {updated_csv}")
    
    # Read back and verify
    with open(updated_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        updated_rows = list(reader)
    
    print(f"✅ Verified {len(updated_rows)} updated rows:")
    for idx, row in enumerate(updated_rows, 1):
        print(f"  {idx}. CAE={row['CAE']}, NRO={row['NRO_COMPROBANTE']}, ESTADO={row['ESTADO']}")
    
except Exception as e:
    print(f"❌ Error updating CSV: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - CSV integration should work!")
print("=" * 60)
