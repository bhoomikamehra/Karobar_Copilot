def read_invoice(file_bytes):
    # TEMPORARY: returns sample data.
    # Later we will replace this with a real Claude call.
    return {
        "vendor": "Sharma Traders",
        "invoice_no": "INV-1042",
        "date": "2026-09-15",
            
        "due_date": "2026-10-15",
        "items": [
            {"item": "Cotton thread", "qty": 50, "rate": 120, "gst_percent": 12},
            {"item": "Zip pack", "qty": 30, "rate": 90, "gst_percent": 12},
        ],
    }