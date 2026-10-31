import datetime
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "karobar.db")


def connect():
    return sqlite3.connect(DB)


def setup():
    con = connect()
    con.execute("""CREATE TABLE IF NOT EXISTS invoices (
        invoice_no TEXT PRIMARY KEY,
        vendor TEXT,
        date TEXT,
        due_date TEXT,
        subtotal REAL,
        gst REAL,
        total REAL,
        paid INTEGER DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        item TEXT,
        qty REAL,
        rate REAL,
        gst_percent REAL,
        amount REAL,
        FOREIGN KEY(invoice_no) REFERENCES invoices(invoice_no))""")
    con.execute("""CREATE TABLE IF NOT EXISTS inventory (
        item TEXT PRIMARY KEY,
        qty REAL)""")
    con.commit()
    con.close()


def invoice_exists(invoice_no):
    if not invoice_no:
        return False
    con = connect()
    row = con.execute(
        "SELECT 1 FROM invoices WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))",
        (str(invoice_no),),
    ).fetchone()
    con.close()
    return row is not None


def get_invoice(invoice_no):
    con = connect()
    row = con.execute(
        """SELECT invoice_no, vendor, date, due_date, subtotal, gst, total, paid
           FROM invoices WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))""",
        (str(invoice_no),),
    ).fetchone()
    con.close()
    if row:
        return {
            "invoice_no": row[0],
            "vendor": row[1],
            "date": row[2],
            "due_date": row[3],
            "subtotal": float(row[4] or 0),
            "gst": float(row[5] or 0),
            "total": float(row[6] or 0),
            "paid": int(row[7] or 0),
        }
    return None


def get_invoice_items(invoice_no):
    con = connect()
    rows = con.execute(
        """SELECT item, qty, rate, gst_percent, amount
           FROM invoice_items WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?)) ORDER BY id ASC""",
        (str(invoice_no),),
    ).fetchall()
    con.close()
    items = []
    for r in rows:
        items.append({
            "item": r[0],
            "qty": float(r[1] or 0),
            "rate": float(r[2] or 0),
            "gst_percent": float(r[3] or 0),
            "amount": float(r[4] or 0),
        })
    return items


def save_invoice(invoice_no, vendor, date, due_date, subtotal, gst, items=None, overwrite=False):
    con = connect()
    subtotal = float(subtotal or 0)
    gst = float(gst or 0)
    total = subtotal + gst
    inv_clean = str(invoice_no).strip()

    if overwrite:
        con.execute("DELETE FROM invoice_items WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))", (inv_clean,))
        con.execute("DELETE FROM invoices WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))", (inv_clean,))

    con.execute(
        """INSERT INTO invoices
           (invoice_no, vendor, date, due_date, subtotal, gst, total, paid)
           VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
        (inv_clean, vendor.strip(), str(date), str(due_date), subtotal, gst, total),
    )

    if items:
        for it in items:
            item_name = str(it.get("item", "")).strip()
            if not item_name:
                continue
            qty = float(it.get("qty", 0))
            rate = float(it.get("rate", 0))
            gst_p = float(it.get("gst_percent", 0))
            amount = float(it.get("amount", qty * rate))

            con.execute(
                """INSERT INTO invoice_items (invoice_no, item, qty, rate, gst_percent, amount)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (inv_clean, item_name, qty, rate, gst_p, amount),
            )
            con.execute(
                """INSERT INTO inventory (item, qty) VALUES (?, ?)
                   ON CONFLICT(item) DO UPDATE SET qty = qty + excluded.qty""",
                (item_name, qty),
            )

    con.commit()
    con.close()


def mark_paid(invoice_no, paid=1):
    con = connect()
    con.execute(
        "UPDATE invoices SET paid = ? WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))",
        (int(paid), str(invoice_no)),
    )
    con.commit()
    con.close()


def delete_invoice(invoice_no):
    con = connect()
    con.execute("DELETE FROM invoice_items WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))", (str(invoice_no),))
    con.execute("DELETE FROM invoices WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))", (str(invoice_no),))
    con.commit()
    con.close()


def get_inventory():
    con = connect()
    rows = con.execute("SELECT item, qty FROM inventory ORDER BY item").fetchall()
    con.close()
    return rows


def get_invoices(search=None, status_filter=None, sort_order="date_desc"):
    """
    Returns full lifetime history of invoices regardless of time duration.
    Allows optional search and status filtering.
    """
    con = connect()
    query = """SELECT invoice_no, vendor, date, due_date, subtotal, gst, total, paid
               FROM invoices WHERE 1=1"""
    params = []

    if search:
        search_term = f"%{search.strip()}%"
        query += " AND (invoice_no LIKE ? OR vendor LIKE ?)"
        params.extend([search_term, search_term])

    if status_filter == "paid":
        query += " AND paid = 1"
    elif status_filter == "unpaid":
        query += " AND paid = 0"
    elif status_filter == "overdue":
        today = datetime.date.today().isoformat()
        query += " AND paid = 0 AND due_date < ?"
        params.append(today)

    order_map = {
        "date_desc": "ORDER BY date DESC, invoice_no DESC",
        "date_asc": "ORDER BY date ASC, invoice_no ASC",
        "due_date_asc": "ORDER BY due_date ASC",
        "total_desc": "ORDER BY total DESC",
        "total_asc": "ORDER BY total ASC",
        "vendor_asc": "ORDER BY vendor ASC",
    }
    query += " " + order_map.get(sort_order, "ORDER BY date DESC")

    rows = con.execute(query, params).fetchall()
    con.close()
    return rows


def get_all_invoices_dicts(search=None, status_filter=None, sort_order="date_desc"):
    rows = get_invoices(search=search, status_filter=status_filter, sort_order=sort_order)
    result = []
    for r in rows:
        result.append({
            "invoice_no": r[0],
            "vendor": r[1],
            "date": r[2],
            "due_date": r[3],
            "subtotal": float(r[4] or 0),
            "gst": float(r[5] or 0),
            "total": float(r[6] or 0),
            "paid": int(r[7] or 0),
        })
    return result


def get_gst_totals():
    con = connect()
    row = con.execute(
        """SELECT COALESCE(SUM(subtotal), 0), COALESCE(SUM(gst), 0),
                  COALESCE(SUM(total), 0) FROM invoices"""
    ).fetchone()
    con.close()
    return row


def get_invoice_count():
    con = connect()
    n = con.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
    con.close()
    return n


def get_payment_summary():
    today = datetime.date.today().isoformat()
    con = connect()
    rows = con.execute("SELECT total, paid, due_date FROM invoices").fetchall()
    con.close()
    s = {
        "paid_count": 0, "pending_count": 0, "overdue_count": 0,
        "paid_amount": 0.0, "pending_amount": 0.0, "overdue_amount": 0.0,
    }
    for total, paid, due in rows:
        total = float(total or 0)
        if paid:
            key = "paid"
        elif due and due < today:
            key = "overdue"
        else:
            key = "pending"
        s[key + "_count"] += 1
        s[key + "_amount"] += total
    return s


def get_monthly_spend():
    con = connect()
    rows = con.execute(
        """SELECT substr(date, 1, 7), SUM(subtotal), SUM(gst), SUM(total)
           FROM invoices GROUP BY substr(date, 1, 7) ORDER BY 1"""
    ).fetchall()
    con.close()
    return rows


def get_recent_invoices(limit=5):
    con = connect()
    rows = con.execute(
        """SELECT invoice_no, vendor, date, total, paid
           FROM invoices ORDER BY date DESC, due_date DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    con.close()
    return rows


def get_vendor_spend():
    con = connect()
    rows = con.execute(
        """SELECT vendor, SUM(total) FROM invoices
           GROUP BY vendor ORDER BY 2 DESC"""
    ).fetchall()
    con.close()
    return rows


def get_top_inventory(limit=5):
    con = connect()
    rows = con.execute(
        "SELECT item, qty FROM inventory ORDER BY qty DESC LIMIT ?", (limit,)
    ).fetchall()
    con.close()
    return rows


def get_upcoming_dues(limit=10):
    con = connect()
    rows = con.execute(
        """SELECT invoice_no, vendor, due_date, total FROM invoices
           WHERE paid = 0 ORDER BY due_date ASC LIMIT ?""",
        (limit,),
    ).fetchall()
    con.close()
    return rows
