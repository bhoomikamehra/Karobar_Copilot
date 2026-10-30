import datetime
import streamlit as st
import pandas as pd
from extract import read_invoice
import database

database.setup()

st.set_page_config(page_title="Karobar Copilot", page_icon="🧾")
st.title("Karobar Copilot")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Add invoice", "Inventory", "Payments", "GST summary"]
)

with tab1:
    st.write("Upload an invoice, check the details, then approve to save.")
    file = st.file_uploader(
        "Upload invoice (photo or PDF)", type=["png", "jpg", "jpeg", "pdf"]
    )

    if file is not None:
        data = read_invoice(file.getvalue())

        st.subheader("Review before saving")
        vendor = st.text_input("Vendor", data["vendor"])
        invoice_no = st.text_input("Invoice number", data["invoice_no"])
        date = st.text_input("Invoice date", data["date"])
        due_date = st.text_input("Due date", data["due_date"])

        table = st.data_editor(pd.DataFrame(data["items"]))

        amount = table["qty"] * table["rate"]
        subtotal = float(amount.sum())
        gst = float((amount * table["gst_percent"] / 100).sum())

        st.write(f"Subtotal: ₹{subtotal:,.2f}")
        st.write(f"GST: ₹{gst:,.2f}")
        st.write(f"**Total: ₹{subtotal + gst:,.2f}**")

        if database.invoice_exists(invoice_no):
            st.error("Duplicate invoice: this invoice number is already saved.")
        elif st.button("Approve and save"):
            database.save_invoice(
                invoice_no, vendor, date, due_date, subtotal, gst,
                table.to_dict("records"),
            )
            st.success("Saved. Inventory and payments updated.")

with tab2:
    rows = database.get_inventory()
    if rows:
        st.dataframe(pd.DataFrame(rows, columns=["Item", "In stock"]))
    else:
        st.write("No stock yet. Approve an invoice first.")

with tab3:
    today = datetime.date.today().isoformat()
    rows = database.get_invoices()
    if not rows:
        st.write("No invoices yet. Approve one first.")
    for inv_no, ven, d, due, total, paid in rows:
        if paid:
            status = "Paid"
        elif due < today:
            status = "Overdue"
        else:
            status = "Pending"

        c1, c2, c3, c4 = st.columns([3, 2, 3, 2])
        c1.write(f"{ven} ({inv_no})")
        c2.write(f"Due {due}")
        c3.write(f"₹{total:,.2f} · {status}")
        if not paid and c4.button("Mark paid", key=f"pay_{inv_no}"):
            database.mark_paid(inv_no)
            st.rerun()
        if status == "Overdue":
            st.warning(
                f"Reminder: pay {ven} ₹{total:,.2f} for {inv_no}. It was due on {due}."
            )

with tab4:
    sub, g, tot = database.get_gst_totals()
    if tot == 0:
        st.write("Nothing to show yet. Approve an invoice first.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Taxable value", f"₹{sub:,.2f}")
        c2.metric("Total GST", f"₹{g:,.2f}")
        c3.metric("Invoice total", f"₹{tot:,.2f}")
        c4, c5 = st.columns(2)
        c4.metric("CGST", f"₹{g / 2:,.2f}")
        c5.metric("SGST", f"₹{g / 2:,.2f}")
        st.caption(
            "CGST and SGST are shown as half each, assuming purchases within the same state."
        )