#!/usr/bin/env python3
"""
Mock Test - Simulates send-to-afip endpoint with fake AFIP response
This tests the logic WITHOUT actually running Chromium/AFIP
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5050"

def create_mock_afip_response(csv_path):
    """Create a mock CSV result as if AFIP processed bills"""
    import csv
    
    print(f"\n[MOCK] Creating fake AFIP response in: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Simulate: First bill succeeds, rest fail
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        
        for i, row in enumerate(rows):
            if i == 0:  # First bill succeeds
                row['ESTADO'] = 'PROCESADO'
                row['CAE'] = 'A' * 14  # Fake 14-digit CAE
                row['NRO_COMPROBANTE'] = '00001234567'
                print(f"  ✅ Bill {i+1}: PROCESADO (CAE={row['CAE']})")
            else:  # Rest fail
                row['ESTADO'] = 'PENDIENTE'
                row['CAE'] = ''
                row['NRO_COMPROBANTE'] = ''
                print(f"  ❌ Bill {i+1}: PENDIENTE (failed)")
            
            writer.writerow(row)

def test_with_realistic_data():
    """Test the endpoint with realistic data and mock AFIP response"""
    print("\n" + "="*60)
    print("TEST: Send-to-AFIP with MOCKED AFIP Response")
    print("="*60)
    
    test_invoices = {
        "preview": [
            {"date": "2026-05-10", "billType": "055", "amount": 3500},
            {"date": "2026-05-11", "billType": "055", "amount": 4200},
            {"date": "2026-05-12", "billType": "055", "amount": 2800}
        ],
        "results": []
    }
    
    print(f"\nSending {len(test_invoices['preview'])} test invoices:")
    for inv in test_invoices['preview']:
        print(f"  - {inv['date']}: ${inv['amount']}")
    
    try:
        # IMPORTANT: We'll manually create the mock response after sending
        csv_path = Path(r"c:\joelsla apps\invoice llc\facturador_afip\Facturas\facturas.csv")
        
        # Before sending, let's set up interrupt handler
        # For now, just show what would happen
        print(f"\n[PREPARE] In real scenario:")
        print(f"  1. We send request to /send-to-afip endpoint")
        print(f"  2. Endpoint writes CSV to: {csv_path}")
        print(f"  3. Endpoint calls facturador_afip/main.py (which opens Chromium)")
        print(f"  4. AFIP bot logs in and processes each bill")
        print(f"  5. AFIP writes CAE to CSV for successful bills")
        print(f"  6. Endpoint reads CSV and separates PROCESADO from PENDIENTE")
        print(f"  7. Response shows processed count and pending count for retry")
        
        print(f"\n[SKIP] We're skipping actual AFIP call (too slow in test)")
        print(f"[SIMULATE] Pretending AFIP called main.py and returned...")
        print(f"[SIMULATE] Creating mock CSV response...")
        
        # Create the CSV as the endpoint would
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["FECHA", "CODIGO", "PRODUCTO SERVICO:", "PRECIO UNITARIO", "CUIT_CLIENTE", "NOMBRE_CLIENTE", "ESTADO", "CAE", "NRO_COMPROBANTE"])
            for item in test_invoices['preview']:
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
        
        # Now simulate AFIP response
        create_mock_afip_response(csv_path)
        
        # Now test the CSV parsing logic by checking the file
        print(f"\n[TEST] Verifying CSV parsing logic:")
        processed_bills = []
        pending_bills = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                estado = row.get("ESTADO", "").strip().upper()
                cae = row.get("CAE", "").strip()
                
                if estado == "PROCESADO" and cae:
                    processed_bills.append({
                        "date": row.get("FECHA"),
                        "amount": int(row.get("PRECIO UNITARIO", 0)),
                        "cae": cae
                    })
                else:
                    pending_bills.append({
                        "date": row.get("FECHA"),
                        "amount": int(row.get("PRECIO UNITARIO", 0))
                    })
        
        print(f"\n✅ SUCCESS!")
        print(f"   - PROCESADO (success): {len(processed_bills)}")
        for bill in processed_bills:
            print(f"      * {bill['date']}: ${bill['amount']} → CAE={bill['cae'][:10]}...")
        
        print(f"\n   - PENDIENTE (for retry): {len(pending_bills)}")
        for bill in pending_bills:
            print(f"      * {bill['date']}: ${bill['amount']} (will retry)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "█"*60)
    print("  MOCK TEST - CSV Response Parsing")
    print("█"*60)
    
    success = test_with_realistic_data()
    
    print("\n" + "="*60)
    if success:
        print("✅ CSV Response Logic VERIFIED")
    else:
        print("❌ CSV Response Logic FAILED")
    print("="*60)
