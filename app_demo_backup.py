
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Karobar Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: #F6F7F2;
    color: #26352D;
    font-family: 'Arial', sans-serif;
}

/* Main content */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main headings */
h1, h2, h3, h4 {
    color: #183D32 !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown, .stCaption {
    color: #34443B !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #183D32 !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}

/* Sidebar radio options */
[data-testid="stSidebar"] [role="radiogroup"] label {
    background-color: transparent;
    border-radius: 8px;
    padding: 8px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E3E9E1;
    padding: 18px;
    border-radius: 14px;
}

[data-testid="stMetricLabel"] {
    color: #66766C !important;
}

[data-testid="stMetricValue"] {
    color: #183D32 !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background-color: #267B5A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #183D32 !important;
    color: #FFFFFF !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #26352D !important;
    border: 1px solid #D6DED5 !important;
    border-radius: 8px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #87938A !important;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #26352D !important;
    border-color: #D6DED5 !important;
}

/* Dropdown text */
[data-baseweb="popover"] * {
    color: #26352D !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border-radius: 10px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #E3E9E1;
    border-radius: 10px;
}

/* Insight panel */
.insight-box {
    background-color: #E9F2E9;
    border-left: 5px solid #267B5A;
    border-radius: 10px;
    padding: 18px;
    color: #183D32 !important;
    margin: 12px 0;
}

.insight-box p {
    color: #183D32 !important;
}

/* Small labels */
.small-muted {
    color: #718076 !important;
    font-size: 13px;
}

/* Divider */
hr {
    border-color: #E1E7DF !important;
}

/* Form submit buttons */
.stFormSubmitButton > button {
    background-color: #267B5A !important;
    color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"Date": "2026-11-14", "Description": "Daily sales", "Type": "Sale", "Amount": 12500, "Payment": "UPI"},
        {"Date": "2026-11-13", "Description": "Supplier payment", "Type": "Expense", "Amount": 4500, "Payment": "Bank"},
        {"Date": "2026-11-12", "Description": "Customer purchase", "Type": "Sale", "Amount": 8200, "Payment": "Cash"},
        {"Date": "2026-11-11", "Description": "Electricity bill", "Type": "Expense", "Amount": 1800, "Payment": "UPI"},
    ]

if "products" not in st.session_state:
    st.session_state.products = [
        {"Product": "Atta 5kg", "Category": "Grocery", "Stock": 8, "Reorder Level": 10, "Price": 260},
        {"Product": "Cooking Oil 1L", "Category": "Grocery", "Stock": 24, "Reorder Level": 10, "Price": 145},
        {"Product": "Milk 500ml", "Category": "Dairy", "Stock": 6, "Reorder Level": 15, "Price": 30},
        {"Product": "Parle-G", "Category": "Snacks", "Stock": 40, "Reorder Level": 20, "Price": 10},
        {"Product": "Rice 5kg", "Category": "Grocery", "Stock": 5, "Reorder Level": 8, "Price": 340},
    ]

if "customers" not in st.session_state:
    st.session_state.customers = [
        {"Name": "Amit Sharma", "Mobile": "98XXXXXX21", "Total Purchases": 12500},
        {"Name": "Neha Verma", "Mobile": "97XXXXXX45", "Total Purchases": 8200},
        {"Name": "Rahul Gupta", "Mobile": "99XXXXXX12", "Total Purchases": 5600},
    ]

if "suppliers" not in st.session_state:
    st.session_state.suppliers = [
        {"Name": "Shree Traders", "Mobile": "98XXXXXX31", "GSTIN": "07XXXXX1234X1Z5"},
        {"Name": "City Wholesale", "Mobile": "97XXXXXX62", "GSTIN": "07XXXXX5678X1Z2"},
    ]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def money(amount):
    return f"₹{amount:,.0f}"


df = pd.DataFrame(st.session_state.transactions)

total_sales = df[df["Type"] == "Sale"]["Amount"].sum()
total_expenses = df[df["Type"] == "Expense"]["Amount"].sum()
net_difference = total_sales - total_expenses

low_stock_count = sum(
    1 for item in st.session_state.products
    if item["Stock"] <= item["Reorder Level"]
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("# KAROBAR")
    st.markdown("### COPILOT")
    st.caption("Business intelligence for everyday businesses")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "AI Assistant",
            "Sales & Expenses",
            "Inventory",
            "Customers",
            "Suppliers",
            "Reports"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.markdown("**YOUR BUSINESS**")
    st.markdown("Retail Store")
    st.caption("Demo workspace")

    st.divider()
    st.caption("KAROBAR COPILOT • 2026")


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.title("Good day! 👋")
    st.write("Here is what's happening with your business today.")

    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sales", money(total_sales), "+12.5%")

    with col2:
        st.metric("Total Expenses", money(total_expenses), "-4.2%")

    with col3:
        st.metric("Net Difference", money(net_difference))

    with col4:
        st.metric("Low Stock Items", low_stock_count)

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Sales Overview")

        chart_df = df[df["Type"] == "Sale"].copy()

        if not chart_df.empty:
            chart_df["Date"] = pd.to_datetime(chart_df["Date"])

            fig = px.bar(
                chart_df,
                x="Date",
                y="Amount",
                title="Recorded sales",
                color_discrete_sequence=["#299B76"]
            )

            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_color="#26352D",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add sales transactions to see your chart.")

    with right:
        st.subheader("Business Snapshot")

        st.markdown(f"""
        <div class="insight-box">
            <h3>Today's numbers</h3>
            <p>Sales recorded: <b>{money(total_sales)}</b></p>
            <p>Expenses recorded: <b>{money(total_expenses)}</b></p>
            <p>Net difference: <b>{money(net_difference)}</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Stock Alerts")

        low_items = [
            p for p in st.session_state.products
            if p["Stock"] <= p["Reorder Level"]
        ]

        if low_items:
            for item in low_items:
                st.warning(
                    f"{item['Product']} — {item['Stock']} units left"
                )
        else:
            st.success("No low-stock alerts.")

    st.markdown("---")
    st.subheader("Recent Transactions")

    st.dataframe(
        df.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# AI ASSISTANT PAGE
# --------------------------------------------------

elif page == "AI Assistant":

    st.title("AI Business Assistant")
    st.write("Ask questions about your business data.")

    st.markdown("""
    <div class="insight-box">
        <b>Your business, explained.</b>
        <p>Understand sales, expenses, inventory and customer activity in simple language.</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "What would you like to know?",
        placeholder="Example: Which products need restocking?"
    )

    st.write("**Try asking:**")

    prompts = [
        "How much have I sold?",
        "Which products need restocking?",
        "Compare my sales and expenses",
        "How is my business performing?"
    ]

    selected_prompt = st.selectbox(
        "Suggested questions",
        prompts
    )

    if st.button("Ask Karobar Copilot"):
        q = question.strip() if question.strip() else selected_prompt

        if "restock" in q.lower() or "stock" in q.lower():
            low_items = [
                p for p in st.session_state.products
                if p["Stock"] <= p["Reorder Level"]
            ]

            if low_items:
                names = ", ".join(p["Product"] for p in low_items)
                st.info(f"These products need attention: {names}")
            else:
                st.success("No products currently need restocking.")

        elif "sales" in q.lower():
            st.success(f"Recorded sales total: {money(total_sales)}")

        elif "expense" in q.lower():
            st.success(f"Recorded expenses total: {money(total_expenses)}")

        elif "perform" in q.lower() or "business" in q.lower():
            st.info(
                f"Your recorded sales are {money(total_sales)} "
                f"and expenses are {money(total_expenses)}. "
                f"The difference is {money(net_difference)}."
            )

        else:
            st.info(
                "This demo assistant currently supports sales, expenses "
                "and stock questions. LLM integration will be added next."
            )

    st.caption("Demo mode: answers use the sample data shown in this application.")


# --------------------------------------------------
# SALES AND EXPENSES PAGE
# --------------------------------------------------

elif page == "Sales & Expenses":

    st.title("Sales & Expenses")
    st.write("Keep track of money coming into and going out of your business.")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sales", money(total_sales))

    with col2:
        st.metric("Expenses", money(total_expenses))

    st.markdown("---")
    st.subheader("Add a transaction")

    with st.form("transaction_form"):

        transaction_type = st.selectbox(
            "Transaction type",
            ["Sale", "Expense"]
        )

        description = st.text_input("Description")

        amount = st.number_input(
            "Amount (₹)",
            min_value=1,
            step=100
        )

        payment_method = st.selectbox(
            "Payment method",
            ["UPI", "Cash", "Bank Transfer", "Card"]
        )

        transaction_date = st.date_input(
            "Date",
            value=date.today()
        )

        submitted = st.form_submit_button("Save Transaction")

        if submitted:
            if not description.strip():
                st.error("Please enter a description.")
            else:
                st.session_state.transactions.append({
                    "Date": str(transaction_date),
                    "Description": description,
                    "Type": transaction_type,
                    "Amount": amount,
                    "Payment": payment_method
                })

                st.success("Transaction added successfully!")
                st.rerun()

    st.markdown("---")
    st.subheader("All Transactions")

    st.dataframe(
        pd.DataFrame(st.session_state.transactions),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# INVENTORY PAGE
# --------------------------------------------------

elif page == "Inventory":

    st.title("Inventory Management")
    st.write("Keep an eye on stock levels and products that need restocking.")

    search = st.text_input(
        "Search products",
        placeholder="Search by product name..."
    )

    products_df = pd.DataFrame(st.session_state.products)

    if search:
        products_df = products_df[
            products_df["Product"].str.contains(
                search, case=False, na=False
            )
        ]

    st.dataframe(
        products_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Restock Alerts")

    low_items = [
        p for p in st.session_state.products
        if p["Stock"] <= p["Reorder Level"]
    ]

    if low_items:
        for item in low_items:
            st.warning(
                f"**{item['Product']}** — "
                f"{item['Stock']} units remaining. "
                f"Reorder level: {item['Reorder Level']}."
            )
    else:
        st.success("All products are above their reorder levels.")

    st.markdown("---")
    st.subheader("Add a Product")

    with st.form("product_form"):

        product_name = st.text_input("Product name")
        category = st.selectbox(
            "Category",
            ["Grocery", "Dairy", "Snacks", "Beverages", "Other"]
        )

        stock = st.number_input("Current stock", min_value=0, step=1)
        reorder = st.number_input("Reorder level", min_value=0, step=1)
        price = st.number_input("Selling price (₹)", min_value=0, step=1)

        add_product = st.form_submit_button("Add Product")

        if add_product:
            if not product_name.strip():
                st.error("Enter a product name.")
            else:
                st.session_state.products.append({
                    "Product": product_name,
                    "Category": category,
                    "Stock": stock,
                    "Reorder Level": reorder,
                    "Price": price
                })

                st.success("Product added!")
                st.rerun()


# --------------------------------------------------
# CUSTOMERS PAGE
# --------------------------------------------------

elif page == "Customers":

    st.title("Customers")
    st.write("View and manage your customer records.")

    customers_df = pd.DataFrame(st.session_state.customers)

    st.metric("Total Customers", len(customers_df))

    st.dataframe(
        customers_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Add Customer")

    with st.form("customer_form"):

        customer_name = st.text_input("Customer name")
        mobile = st.text_input("Mobile number")

        add_customer = st.form_submit_button("Save Customer")

        if add_customer:
            if not customer_name.strip():
                st.error("Enter the customer's name.")
            else:
                st.session_state.customers.append({
                    "Name": customer_name,
                    "Mobile": mobile,
                    "Total Purchases": 0
                })

                st.success("Customer added successfully!")
                st.rerun()


# --------------------------------------------------
# SUPPLIERS PAGE
# --------------------------------------------------

elif page == "Suppliers":

    st.title("Suppliers")
    st.write("Manage your supplier information.")

    suppliers_df = pd.DataFrame(st.session_state.suppliers)

    st.metric("Total Suppliers", len(suppliers_df))

    st.dataframe(
        suppliers_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Add Supplier")

    with st.form("supplier_form"):

        supplier_name = st.text_input("Supplier name")
        supplier_mobile = st.text_input("Mobile number")
        gstin = st.text_input("GSTIN (optional)")

        add_supplier = st.form_submit_button("Save Supplier")

        if add_supplier:
            if not supplier_name.strip():
                st.error("Enter the supplier's name.")
            else:
                st.session_state.suppliers.append({
                    "Name": supplier_name,
                    "Mobile": supplier_mobile,
                    "GSTIN": gstin
                })

                st.success("Supplier added successfully!")
                st.rerun()


# --------------------------------------------------
# REPORTS PAGE
# --------------------------------------------------

elif page == "Reports":

    st.title("Business Reports")
    st.write("A simple view of your recorded business activity.")

    report_type = st.selectbox(
        "Choose report",
        ["Sales vs Expenses", "Payment Methods", "Inventory"]
    )

    if report_type == "Sales vs Expenses":

        report_df = pd.DataFrame({
            "Type": ["Sales", "Expenses"],
            "Amount": [total_sales, total_expenses]
        })

        fig = px.bar(
            report_df,
            x="Type",
            y="Amount",
            color="Type",
            color_discrete_sequence=["#299B76", "#E5A63B"],
            title="Sales and expenses"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_color="#26352D",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    elif report_type == "Payment Methods":

        payment_df = df.groupby("Payment")["Amount"].sum().reset_index()

        fig = px.pie(
            payment_df,
            names="Payment",
            values="Amount",
            title="Transactions by payment method"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif report_type == "Inventory":

        inventory_df = pd.DataFrame(st.session_state.products)

        fig = px.bar(
            inventory_df,
            x="Product",
            y="Stock",
            title="Current stock levels",
            color_discrete_sequence=["#299B76"]
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_color="#26352D"
        )

        st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
st.caption(
    "KAROBAR COPILOT | Business intelligence made simpler."
)