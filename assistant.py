import datetime
import os
import re
import database

# Check for Anthropic API key
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get_business_context_summary():
    """
    Compiles a comprehensive real-time snapshot of the merchant's business data.
    """
    sub, gst_total, total_spend = database.get_gst_totals()
    pay_sum = database.get_payment_summary()
    total_exp, exp_by_cat = database.get_expense_summary()

    cust_kpi = database.get_customers_kpi_summary()
    customers = database.get_all_customers()
    debtors = [c for c in customers if c["balance_due"] > 0]
    debtors.sort(key=lambda x: x["balance_due"], reverse=True)

    sup_kpi = database.get_suppliers_kpi_summary()
    suppliers = database.get_all_suppliers()
    upcoming_dues = database.get_upcoming_dues(limit=5)

    inventory = database.get_inventory()

    context = {
        "total_revenue": total_spend,
        "total_gst": gst_total,
        "total_expenses": total_exp,
        "customer_count": cust_kpi["count"],
        "total_credit_given": cust_kpi["total_credit_given"],
        "total_collected": cust_kpi["total_collected"],
        "total_receivables": cust_kpi["total_receivables"],
        "top_debtors": debtors[:5],
        "supplier_count": sup_kpi["count"],
        "total_purchases": sup_kpi["total_purchases"],
        "total_paid_suppliers": sup_kpi["total_paid"],
        "pending_payables": sup_kpi["pending_payables"],
        "upcoming_dues": upcoming_dues,
        "inventory_count": len(inventory),
        "inventory_items": inventory[:10],
    }
    return context


def ask_ai_assistant(query, custom_api_key=None):
    """
    Processes the shopkeeper's query.
    Uses Anthropic Claude if API key is available; otherwise uses built-in Karobar Domain Engine.
    """
    q_lower = query.lower().strip()
    ctx = get_business_context_summary()

    # 1. Try Claude if API Key is configured
    api_key = custom_api_key or os.getenv("ANTHROPIC_API_KEY")
    if api_key and len(api_key.strip()) > 10:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key.strip())
            
            system_prompt = f"""You are 'Karobar AI Copilot', an expert, practical business advisor for Indian shopkeepers, kirana store owners, and small merchants.
You speak clearly, respectfully, and practically (fluent in English, Hindi, and Hinglish).
Here is the LIVE business data from the merchant's shop right now:
- Total Store Revenue/Purchases: ₹{ctx['total_revenue']:,.2f}
- Total Operating Expenses: ₹{ctx['total_expenses']:,.2f}
- Outstanding Customer Receivables (बाकी लेना): ₹{ctx['total_receivables']:,.2f} across {len(ctx['top_debtors'])} customers with pending dues.
  Top debtors: {', '.join([f"{d['name']} (₹{d['balance_due']:,.2f})" for d in ctx['top_debtors']]) if ctx['top_debtors'] else 'None (all dues cleared)'}
- Pending Supplier Payables (देना है): ₹{ctx['pending_payables']:,.2f} across {ctx['supplier_count']} suppliers.
- Total Inventory Items in Stock: {ctx['inventory_count']} items.
  Sample stock: {', '.join([f"{it[0]} ({it[1]} units)" for it in ctx['inventory_items']]) if ctx['inventory_items'] else 'No stock logged'}

Guidelines:
1. Always use actual numbers from the live data when answering questions about their finances, customers, or stock.
2. Give clear, polite, and actionable recommendations.
3. If drafting a message for a customer or vendor, make it courteous, professional, and ready to send.
"""
            msg = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=800,
                system=system_prompt,
                messages=[{"role": "user", "content": query}]
            )
            return msg.content[0].text
        except Exception:
            pass

    # 2. Built-in Karobar Smart Domain Engine (100% Offline & Reliable)
    return local_smart_engine(q_lower, ctx, query)


def local_smart_engine(q_lower, ctx, original_query):
    """
    Intelligent heuristic engine that understands shopkeeper queries and returns rich, formatted answers with live numbers.
    """
    # ── 1. DRAFT PAYMENT REMINDER / WHATSAPP MESSAGE (Higher priority than general customer) ──
    if any(k in q_lower for k in ["draft", "template", "whatsapp reminder", "remind", "yad dilana", "message for"]):
        return (
            "### ✍️ Draft Payment Reminder Messages\n\n"
            "Here are polite, professional reminder templates ready to send to your customers:\n\n"
            "#### 🇬🇧 English Template:\n"
            "```text\n"
            "Dear [Customer Name],\n"
            "Greetings from Karobar Store! This is a gentle reminder regarding your pending balance of ₹[Amount]. "
            "Kindly settle the amount at your convenience via UPI (GPay/PhonePe) or cash.\n"
            "Thank you for your valued patronage!\n"
            "```\n\n"
            "#### 🇮🇳 Hindi / Hinglish Template:\n"
            "```text\n"
            "नमस्ते [Customer Name] जी,\n"
            "कारोबार स्टोर से सादर प्रणाम। आपके खाते का बकाया ₹[Amount] बाकी है। "
            "कृपया सुविधानुसार UPI (GPay/PhonePe) या नकद द्वारा भुगतान करने की कृपा करें।\n"
            "सहयोग के लिए धन्यवाद!\n"
            "```\n\n"
            "👉 *Tip: In the **👥 Customers Portal → WhatsApp Payment Reminders** tab, you can click one button to open WhatsApp with this pre-filled message!*"
        )

    # ── 2. GST & TAX INQUIRIES ────────────────────────────────────────
    if any(k in q_lower for k in ["gst", "tax", "hsn", "itc", "input tax"]):
        return (
            "### 🧾 GST & Retail Tax Quick Guide\n\n"
            "**1. Standard GST Slabs for Retail & Kirana:**\n"
            "- **0% (Exempt):** Unbranded grains, loose flour, fresh vegetables, milk, eggs, salt.\n"
            "- **5%:** Packaged food items, branded edible oil, tea, spices, sugar, mustard oil.\n"
            "- **12%:** Butter, cheese, ghee, packaged dry fruits, processed food, namkeen.\n"
            "- **18%:** Soaps, detergents, toothpaste, hair oil, branded consumer goods, stationery.\n"
            "- **28%:** Aerated soft drinks, luxury items.\n\n"
            "**2. How Input Tax Credit (ITC) Works in Karobar Copilot:**\n"
            "When you scan a supplier bill with GST, you can claim that amount against your outward sales tax liability, directly reducing your tax outflow!\n\n"
            "**3. Current Shop Input GST Tracked:**\n"
            f"- Total Input GST from Invoices: **₹{ctx['total_gst']:,.2f}**"
        )

    # ── 3. FINANCIAL SUMMARY / PROFIT / HEALTH CHECK ───────────────────
    if any(k in q_lower for k in ["profit", "financial", "health", "revenue", "loss", "how is business", "summary", "overview"]):
        net_receivables = ctx["total_receivables"]
        net_payables = ctx["pending_payables"]
        working_gap = net_receivables - net_payables
        gap_status = "Positive (You are owed more than you owe)" if working_gap >= 0 else "Negative (You owe more than you are owed)"

        return (
            "### 📊 Karobar Financial Health Snapshot\n\n"
            f"| Metric | Amount (₹) | Note |\n"
            f"| :--- | :--- | :--- |\n"
            f"| **Total Purchases (Procurement)** | ₹{ctx['total_revenue']:,.2f} | Billed from suppliers |\n"
            f"| **Customer Receivables (उधार लेना)** | ₹{net_receivables:,.2f} | To collect from clients |\n"
            f"| **Supplier Payables (देना है)** | ₹{net_payables:,.2f} | Owed to vendors |\n"
            f"| **Net Working Gap** | ₹{working_gap:,.2f} | {gap_status} |\n"
            f"| **Shop Operating Expenses** | ₹{ctx['total_expenses']:,.2f} | Rent, power, refreshments |\n\n"
            "💡 **Advice to Improve Cash Flow:**\n"
            "1. Collect pending customer balances before taking new credit from suppliers.\n"
            "2. Offer a small 1-2% discount to customers who pay immediately via UPI instead of taking Udhar."
        )

    # ── 4. INVENTORY / STOCK ──────────────────────────────────────────
    if any(k in q_lower for k in ["inventory", "stock", "items", "mal", "saman", "goods", "quantity"]):
        items = ctx["inventory_items"]
        count = ctx["inventory_count"]

        if not items:
            return (
                "### 📦 Inventory Status\n\n"
                "You currently have no stock tracked in inventory.\n\n"
                "💡 **How to add stock:**\n"
                "1. Go to **🏢 Suppliers Portal → Scan & Upload Supplier Bill**.\n"
                "2. When you scan and approve an invoice, item quantities are automatically added to your stock!"
            )

        resp = [
            f"### 📦 Inventory Stock Overview\n",
            f"You have **{count} distinct products** logged in stock:\n",
            "| Item / Product | Stock In Hand | Status |",
            "| :--- | :--- | :--- |"
        ]
        for it in items:
            qty = it[1]
            status = "🟢 Adequate" if qty > 10 else ("🟡 Low Stock" if qty > 0 else "🔴 Out of Stock")
            resp.append(f"| **{it[0]}** | {qty:g} units | {status} |")

        resp.append("\n💡 *Tip: Keep at least 15–20 units of fast-moving items like Rice, Oil, and Soap to avoid stock-outs.*")
        return "\n".join(resp)

    # ── 5. SUPPLIERS / PAYABLES / BILLS DUE ────────────────────────────
    if any(k in q_lower for k in ["supplier", "vendor", "payable", "dena", "bill due", "upcoming", "due date"]):
        pending_p = ctx["pending_payables"]
        upcoming = ctx["upcoming_dues"]

        if pending_p <= 0:
            return (
                "### 🏢 Supplier Accounts All Clear!\n\n"
                "You currently have **₹0 in pending supplier payables**. All procurement invoices are fully settled.\n\n"
                f"- **Total Purchases Logged:** ₹{ctx['total_purchases']:,.2f}\n"
                f"- **Total Paid to Suppliers:** ₹{ctx['total_paid_suppliers']:,.2f}\n"
                f"- **Registered Suppliers:** {ctx['supplier_count']}\n\n"
                "💡 *Tip: Scan incoming vendor bills in **🏢 Suppliers Portal** to automatically update inventory stock.*"
            )

        resp = [
            f"### 🏢 Supplier Payables Status\n",
            f"You currently owe **₹{pending_p:,.2f}** to your suppliers.\n"
        ]
        if upcoming:
            resp.append("**Upcoming Bills Due:**")
            resp.append("| Invoice No | Vendor | Due Date | Amount (₹) |")
            resp.append("| :--- | :--- | :--- | :--- |")
            for inv in upcoming:
                resp.append(f"| `{inv[0]}` | **{inv[1]}** | {inv[2]} | **₹{inv[3]:,.2f}** |")
        
        resp.append("\n**Action:** Visit **🏢 Suppliers Portal → Purchase Invoices** to view bills or mark them as paid.")
        return "\n".join(resp)

    # ── 6. CUSTOMERS / UDHAR / RECEIVABLES / DEBTORS ──────────────────
    if any(k in q_lower for k in ["udhar", "customer", "debtor", "owe", "receivable", "khata", "lene", "baaki", "pending payment", "collect"]):
        total_rec = ctx["total_receivables"]
        top_d = ctx["top_debtors"]

        if not top_d or total_rec <= 0:
            return (
                "### 🎉 Excellent Khata Status!\n\n"
                "You currently have **₹0 in pending customer receivables**! All your registered customers have cleared their dues.\n\n"
                f"- **Total Credit Extended:** ₹{ctx['total_credit_given']:,.2f}\n"
                f"- **Total Payments Collected:** ₹{ctx['total_collected']:,.2f}\n\n"
                "💡 *Tip: You can use the **👥 Customers Portal** to register new regular customers and set safe credit limits.*"
            )

        response = [
            f"### 👥 Customer Udhar (Receivables) Summary\n",
            f"You have a total of **₹{total_rec:,.2f}** pending to be collected from customers across **{len(top_d)}** accounts:\n"
        ]
        response.append("| Customer Name | Phone | Amount Due (₹) | Action |")
        response.append("| :--- | :--- | :--- | :--- |")
        for d in top_d:
            p = d.get('phone') or 'Not listed'
            response.append(f"| **{d['name']}** | {p} | **₹{d['balance_due']:,.2f}** | Send Reminder |")

        response.append("\n**Recommended Actions:**")
        response.append("1. **Send WhatsApp Reminders:** Go to **👥 Customers Portal → WhatsApp Payment Reminders** to send 1-click reminders.")
        response.append("2. **Set Credit Limits:** Restrict giving more credit to customers who have exceeded 30 days without payment.")
        return "\n".join(response)

    # ── 7. DEFAULT HELPFUL FALLBACK ───────────────────────────────────
    return (
        f"### 👋 Hello! I am your Karobar AI Copilot.\n\n"
        "I am connected to your live shop database and ready to assist you. Here are some things you can ask me:\n\n"
        "- 🔴 **'Who owes me money?'** — View outstanding customer credit (Udhar) and top debtors.\n"
        "- 🏢 **'What supplier bills are due?'** — Check upcoming vendor payables.\n"
        "- 📦 **'Show inventory stock'** — Check current product stock levels.\n"
        "- 📊 **'How is my business doing?'** — Get a comprehensive financial health summary.\n"
        "- ✍️ **'Draft a payment reminder'** — Get polite WhatsApp message templates.\n"
        "- 🧾 **'Explain GST rates'** — Quick tax and ITC reference.\n\n"
        "*Feel free to type your question in English or Hinglish!*"
    )
