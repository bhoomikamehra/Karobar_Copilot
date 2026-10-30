import streamlit as st
import pandas as pd
from extract import read_invoice

st.set_page_config(page_title="Karobar Copilot", page_icon="🧾")
st.title("Karobar Copilot")
st.write("Upload an invoice, check the details, then approve to save.")

file = st.file_uploader("Upload invoice (photo or PDF)", type=["png", "jpg", "jpeg", "pdf"])

if file is not None:
    data = read_invoice(file.getvalue())

    st.subheader("Review before saving")
    vendor = st.text_input("Vendor", data["vendor"])
    invoice_no = st.text_input("Invoice number", data["invoice_no"])
    date = st.text_input("Invoice date", data["date"])

    table = st.data_editor(pd.DataFrame(data["items"]))

    amount = table["qty"] * table["rate"]
    subtotal = amount.sum()
    gst = (amount * table["gst_percent"] / 100).sum()

    st.write(f"Subtotal: ₹{subtotal:,.2f}")
    st.write(f"GST: ₹{gst:,.2f}")
    st.write(f"**Total: ₹{subtotal + gst:,.2f}**")

    if st.button("Approve and save"):
        st.success("Saved! (the database comes in the next step)")