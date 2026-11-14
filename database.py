import datetime
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "karobar.db")


def connect():
    return sqlite3.connect(DB)


def setup():
    con = connect()
    # 1. Invoices & Inventory
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

    # 2. Suppliers (Vendors / Creditors)
    con.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT,
        email TEXT,
        gstin TEXT,
        address TEXT,
        created_at TEXT)""")

    # 3. Customers (Debtors / Khata)
    con.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        credit_limit REAL DEFAULT 10000.0,
        created_at TEXT)""")

    con.execute("""CREATE TABLE IF NOT EXISTS customer_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        date TEXT NOT NULL,
        type TEXT NOT NULL, /* 'SALE' (Debit/Udhar) or 'PAYMENT' (Credit/Jama) */
        amount REAL NOT NULL,
        notes TEXT,
        payment_mode TEXT, /* 'Cash', 'UPI', 'Bank Transfer', 'Cheque' */
        created_at TEXT,
        FOREIGN KEY(customer_name) REFERENCES customers(name))""")

    # 4. Expenses
    con.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        notes TEXT,
        payment_mode TEXT)""")

    # Auto-register vendors from existing invoices into suppliers table
    try:
        con.execute("""
            INSERT OR IGNORE INTO suppliers (name, created_at)
            SELECT DISTINCT vendor, date FROM invoices 
            WHERE vendor IS NOT NULL AND TRIM(vendor) != ''
        """)
    except Exception:
        pass

    con.commit()
    con.close()


# ══════════════════════════════════════════════════════════════════
#  INVOICE & INVENTORY FUNCTIONS
# ══════════════════════════════════════════════════════════════════

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
    vendor_clean = str(vendor).strip()

    if overwrite:
        con.execute("DELETE FROM invoice_items WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))", (inv_clean,))
        con.execute("DELETE FROM invoices WHERE LOWER(TRIM(invoice_no)) = LOWER(TRIM(?))", (inv_clean,))

    con.execute(
        """INSERT INTO invoices
           (invoice_no, vendor, date, due_date, subtotal, gst, total, paid)
           VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
        (inv_clean, vendor_clean, str(date), str(due_date), subtotal, gst, total),
    )

    # Ensure vendor is in suppliers directory
    if vendor_clean:
        con.execute(
            """INSERT OR IGNORE INTO suppliers (name, created_at)
               VALUES (?, ?)""",
            (vendor_clean, str(date) or datetime.date.today().isoformat()),
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


# ══════════════════════════════════════════════════════════════════
#  🏢 SUPPLIERS (VENDORS / B2B PAYABLES) PORTAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def add_supplier(name, phone="", email="", gstin="", address=""):
    name = str(name).strip()
    if not name:
        return False, "Supplier name cannot be empty."
    con = connect()
    try:
        con.execute(
            """INSERT INTO suppliers (name, phone, email, gstin, address, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, str(phone).strip(), str(email).strip(), str(gstin).strip().upper(), str(address).strip(), datetime.date.today().isoformat())
        )
        con.commit()
        return True, f"Supplier '{name}' added successfully."
    except sqlite3.IntegrityError:
        return False, f"Supplier '{name}' already exists."
    except Exception as e:
        return False, str(e)
    finally:
        con.close()


def delete_supplier(name):
    con = connect()
    con.execute("DELETE FROM suppliers WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (str(name),))
    con.commit()
    con.close()


def get_all_suppliers(search=None):
    con = connect()
    query = """
        SELECT 
            s.id,
            s.name,
            COALESCE(s.phone, '') as phone,
            COALESCE(s.email, '') as email,
            COALESCE(s.gstin, '') as gstin,
            COALESCE(s.address, '') as address,
            COUNT(i.invoice_no) as total_invoices,
            COALESCE(SUM(i.total), 0.0) as total_purchases,
            COALESCE(SUM(CASE WHEN i.paid = 1 THEN i.total ELSE 0 END), 0.0) as total_paid,
            COALESCE(SUM(CASE WHEN i.paid = 0 THEN i.total ELSE 0 END), 0.0) as pending_dues
        FROM suppliers s
        LEFT JOIN invoices i ON LOWER(TRIM(i.vendor)) = LOWER(TRIM(s.name))
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (s.name LIKE ? OR s.phone LIKE ? OR s.gstin LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    query += " GROUP BY s.id, s.name ORDER BY pending_dues DESC, s.name ASC"
    rows = con.execute(query, params).fetchall()
    con.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "phone": r[2],
            "email": r[3],
            "gstin": r[4],
            "address": r[5],
            "invoice_count": int(r[6] or 0),
            "total_purchases": float(r[7] or 0.0),
            "total_paid": float(r[8] or 0.0),
            "pending_dues": float(r[9] or 0.0),
        })
    return result


def get_supplier_invoices(vendor_name):
    con = connect()
    rows = con.execute(
        """SELECT invoice_no, vendor, date, due_date, subtotal, gst, total, paid
           FROM invoices 
           WHERE LOWER(TRIM(vendor)) = LOWER(TRIM(?))
           ORDER BY date DESC""",
        (str(vendor_name),)
    ).fetchall()
    con.close()

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


def get_suppliers_kpi_summary():
    con = connect()
    sup_count = con.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
    total_pur, total_paid, pending_dues = con.execute("""
        SELECT 
            COALESCE(SUM(total), 0.0),
            COALESCE(SUM(CASE WHEN paid = 1 THEN total ELSE 0.0 END), 0.0),
            COALESCE(SUM(CASE WHEN paid = 0 THEN total ELSE 0.0 END), 0.0)
        FROM invoices
    """).fetchone()
    con.close()
    return {
        "count": sup_count,
        "total_purchases": float(total_pur or 0.0),
        "total_paid": float(total_paid or 0.0),
        "pending_payables": float(pending_dues or 0.0)
    }


# ══════════════════════════════════════════════════════════════════
#  👥 CUSTOMERS (CLIENTS / KHATA / RECEIVABLES) PORTAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def add_customer(name, phone="", email="", address="", credit_limit=10000.0):
    name = str(name).strip()
    if not name:
        return False, "Customer name cannot be empty."
    con = connect()
    try:
        con.execute(
            """INSERT INTO customers (name, phone, email, address, credit_limit, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, str(phone).strip(), str(email).strip(), str(address).strip(), float(credit_limit or 0), datetime.date.today().isoformat())
        )
        con.commit()
        return True, f"Customer '{name}' registered successfully."
    except sqlite3.IntegrityError:
        return False, f"Customer '{name}' already exists."
    except Exception as e:
        return False, str(e)
    finally:
        con.close()


def delete_customer(name):
    con = connect()
    con.execute("DELETE FROM customer_transactions WHERE LOWER(TRIM(customer_name)) = LOWER(TRIM(?))", (str(name),))
    con.execute("DELETE FROM customers WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (str(name),))
    con.commit()
    con.close()


def add_customer_transaction(customer_name, date, trans_type, amount, notes="", payment_mode="Cash"):
    """
    trans_type: 'SALE' (Debit / Udhar Diya) or 'PAYMENT' (Credit / Jama Kiya)
    """
    amount = float(amount or 0)
    if amount <= 0:
        return False, "Transaction amount must be greater than zero."
    cust_name = str(customer_name).strip()
    if not cust_name:
        return False, "Customer name is required."

    con = connect()
    try:
        # Verify customer exists, if not, create automatically
        row = con.execute("SELECT 1 FROM customers WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (cust_name,)).fetchone()
        if not row:
            con.execute(
                "INSERT INTO customers (name, created_at) VALUES (?, ?)",
                (cust_name, datetime.date.today().isoformat())
            )

        con.execute(
            """INSERT INTO customer_transactions (customer_name, date, type, amount, notes, payment_mode, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                cust_name,
                str(date) or datetime.date.today().isoformat(),
                trans_type.upper(),
                amount,
                str(notes).strip(),
                str(payment_mode),
                datetime.datetime.now().isoformat()
            )
        )
        con.commit()
        return True, "Transaction recorded successfully."
    except Exception as e:
        return False, str(e)
    finally:
        con.close()


def get_all_customers(search=None):
    con = connect()
    query = """
        SELECT 
            c.id,
            c.name,
            COALESCE(c.phone, '') as phone,
            COALESCE(c.email, '') as email,
            COALESCE(c.address, '') as address,
            COALESCE(c.credit_limit, 10000.0) as credit_limit,
            COALESCE(SUM(CASE WHEN t.type = 'SALE' THEN t.amount ELSE 0.0 END), 0.0) as total_credit_given,
            COALESCE(SUM(CASE WHEN t.type = 'PAYMENT' THEN t.amount ELSE 0.0 END), 0.0) as total_collected,
            (COALESCE(SUM(CASE WHEN t.type = 'SALE' THEN t.amount ELSE 0.0 END), 0.0) - 
             COALESCE(SUM(CASE WHEN t.type = 'PAYMENT' THEN t.amount ELSE 0.0 END), 0.0)) as balance_due,
            COUNT(t.id) as trans_count,
            MAX(t.date) as last_activity
        FROM customers c
        LEFT JOIN customer_transactions t ON LOWER(TRIM(t.customer_name)) = LOWER(TRIM(c.name))
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (c.name LIKE ? OR c.phone LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term])

    query += " GROUP BY c.id, c.name ORDER BY balance_due DESC, c.name ASC"
    rows = con.execute(query, params).fetchall()
    con.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "phone": r[2],
            "email": r[3],
            "address": r[4],
            "credit_limit": float(r[5] or 10000.0),
            "total_credit_given": float(r[6] or 0.0),
            "total_collected": float(r[7] or 0.0),
            "balance_due": float(r[8] or 0.0),
            "trans_count": int(r[9] or 0),
            "last_activity": r[10] or "No transactions"
        })
    return result


def get_customer_ledger(customer_name):
    con = connect()
    rows = con.execute(
        """SELECT id, date, type, amount, notes, payment_mode, created_at
           FROM customer_transactions
           WHERE LOWER(TRIM(customer_name)) = LOWER(TRIM(?))
           ORDER BY date ASC, id ASC""",
        (str(customer_name),)
    ).fetchall()
    con.close()

    ledger = []
    running_balance = 0.0
    for r in rows:
        t_type = r[2]
        amt = float(r[3] or 0.0)
        if t_type == "SALE":
            running_balance += amt
        else:
            running_balance -= amt

        ledger.append({
            "id": r[0],
            "date": r[1],
            "type": t_type,
            "amount": amt,
            "notes": r[4],
            "payment_mode": r[5],
            "balance_after": running_balance,
            "created_at": r[6]
        })
    return ledger


def get_customers_kpi_summary():
    con = connect()
    cust_count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_sales, total_payments = con.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'SALE' THEN amount ELSE 0.0 END), 0.0),
            COALESCE(SUM(CASE WHEN type = 'PAYMENT' THEN amount ELSE 0.0 END), 0.0)
        FROM customer_transactions
    """).fetchone()
    con.close()

    total_sales = float(total_sales or 0.0)
    total_payments = float(total_payments or 0.0)
    balance_due = total_sales - total_payments

    return {
        "count": cust_count,
        "total_credit_given": total_sales,
        "total_collected": total_payments,
        "total_receivables": balance_due
    }


# ══════════════════════════════════════════════════════════════════
#  💸 EXPENSES TRACKING FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def add_expense(category, amount, date, notes="", payment_mode="Cash"):
    amount = float(amount or 0)
    if amount <= 0:
        return False, "Amount must be greater than zero."
    con = connect()
    try:
        con.execute(
            """INSERT INTO expenses (category, amount, date, notes, payment_mode)
               VALUES (?, ?, ?, ?, ?)""",
            (category.strip(), amount, str(date), str(notes).strip(), str(payment_mode))
        )
        con.commit()
        return True, "Expense recorded successfully."
    except Exception as e:
        return False, str(e)
    finally:
        con.close()


def get_all_expenses():
    con = connect()
    rows = con.execute(
        """SELECT id, category, amount, date, notes, payment_mode
           FROM expenses ORDER BY date DESC, id DESC"""
    ).fetchall()
    con.close()
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "category": r[1],
            "amount": float(r[2] or 0.0),
            "date": r[3],
            "notes": r[4],
            "payment_mode": r[5]
        })
    return result


def get_expense_summary():
    con = connect()
    total_exp = con.execute("SELECT COALESCE(SUM(amount), 0.0) FROM expenses").fetchone()[0]
    by_cat = con.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY 2 DESC").fetchall()
    con.close()
    return float(total_exp or 0.0), by_cat


# Ensure all tables exist on startup
setup()
