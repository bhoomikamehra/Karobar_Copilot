import sqlite3

DB = "karobar.db"


def connect():
    return sqlite3.connect(DB)


def setup():
    con = connect()
    con.execute("""CREATE TABLE IF NOT EXISTS invoices (
        invoice_no TEXT PRIMARY KEY,
        vendor TEXT,
        date TEXT,
        subtotal REAL,
        gst REAL,
        total REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS inventory (
        item TEXT PRIMARY KEY,
        qty REAL)""")
    con.commit()
    con.close()


def invoice_exists(invoice_no):
    con = connect()
    row = con.execute(
        "SELECT 1 FROM invoices WHERE invoice_no = ?", (invoice_no,)
    ).fetchone()
    con.close()
    return row is not None


def save_invoice(invoice_no, vendor, date, subtotal, gst, items):
    con = connect()
    con.execute(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?)",
        (invoice_no, vendor, date, subtotal, gst, subtotal + gst),
    )
    for it in items:
        con.execute(
            """INSERT INTO inventory (item, qty) VALUES (?, ?)
               ON CONFLICT(item) DO UPDATE SET qty = qty + excluded.qty""",
            (it["item"], float(it["qty"])),
        )
    con.commit()
    con.close()


def get_inventory():
    con = connect()
    rows = con.execute("SELECT item, qty FROM inventory ORDER BY item").fetchall()
    con.close()
    return rows


def get_invoices():
    con = connect()
    rows = con.execute(
        "SELECT invoice_no, vendor, date, total FROM invoices ORDER BY date"
    ).fetchall()
    con.close()
    return rows