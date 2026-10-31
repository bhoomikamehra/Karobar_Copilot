import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from extract import read_invoice
import database

# ── Database Initialization ────────────────────────────────────────
database.setup()

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Karobar Copilot",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
# 🔐 AUTHENTICATION & MULTI-USER SYSTEM
# ══════════════════════════════════════════════════════════════════

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # 'login' or 'signup'

# Users database stored in session
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": {
            "password": "12345",
            "full_name": "Admin",
            "email": "admin@karobarcopilot.in",
            "phone": "+91 98765 43210"
        }
    }

if "profile" not in st.session_state:
    st.session_state.profile = {
        "full_name": "Admin",
        "email": "admin@karobarcopilot.in",
        "phone": "+91 98765 43210",
        "user_id": "KC-80942",
        "account_type": "Business Pro Plan",
        "verification_status": "Verified Merchant ✅",
        "language": "English",
        "theme": "Light",
        "login_history": [
            {"Date & Time": "Today, 10:45 AM", "Device / Browser": "Chrome on Windows 11", "IP Address": "192.168.1.14", "Status": "Success ✅"},
            {"Date & Time": "Yesterday, 06:12 PM", "Device / Browser": "Chrome on Windows 11", "IP Address": "192.168.1.14", "Status": "Success ✅"},
            {"Date & Time": "28 Oct 2026, 09:30 AM", "Device / Browser": "Mobile Safari (iOS)", "IP Address": "157.34.89.21", "Status": "Success ✅"},
        ]
    }

if "edit_profile_mode" not in st.session_state:
    st.session_state.edit_profile_mode = False

def show_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
        
        # ── 1. LOGIN MODE ──────────────────────────────────────────
        if st.session_state.auth_mode == "login":
            st.title("🔐 Karobar Copilot Login")
            st.write("Please sign in to access your business dashboard.")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In", use_container_width=True)

                if submit:
                    if username in st.session_state.users_db and st.session_state.users_db[username]["password"] == password:
                        user_info = st.session_state.users_db[username]
                        st.session_state.logged_in = True
                        st.session_state.profile["full_name"] = user_info["full_name"]
                        st.session_state.profile["email"] = user_info["email"]
                        st.session_state.profile["phone"] = user_info["phone"]
                        st.session_state.profile["user_id"] = f"KC-{abs(hash(username)) % 90000 + 10000}"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

            # Option to switch to Sign Up
            st.markdown("<p style='text-align:center; color:#64748b; margin-top:1.5rem; margin-bottom:0.5rem;'>Don't have an account?</p>", unsafe_allow_html=True)
            if st.button("✨ Create New Account", key="btn_goto_signup", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

        # ── 2. SIGN UP / CREATE ACCOUNT MODE ───────────────────────
        else:
            st.title("📝 Create New Account")
            st.write("Set up your details to get started with Karobar Copilot.")
            
            with st.form("signup_form"):
                new_fullname = st.text_input("Full Name (e.g., Rajesh Kumar)")
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email Address")
                new_phone = st.text_input("Phone Number")
                new_password = st.text_input("Create Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                signup_submit = st.form_submit_button("🚀 Register & Start", use_container_width=True)

                if signup_submit:
                    if not new_username or not new_password:
                        st.error("Username and password are required.")
                    elif new_username in st.session_state.users_db:
                        st.error("This username already exists. Please pick another.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match. Please re-type.")
                    else:
                        # Save new account
                        st.session_state.users_db[new_username] = {
                            "password": new_password,
                            "full_name": new_fullname if new_fullname else new_username.capitalize(),
                            "email": new_email if new_email else f"{new_username}@karobarcopilot.in",
                            "phone": new_phone if new_phone else "+91 99999 00000"
                        }
                        
                        # Automatically log in the user
                        st.session_state.logged_in = True
                        st.session_state.profile["full_name"] = st.session_state.users_db[new_username]["full_name"]
                        st.session_state.profile["email"] = st.session_state.users_db[new_username]["email"]
                        st.session_state.profile["phone"] = st.session_state.users_db[new_username]["phone"]
                        st.session_state.profile["user_id"] = f"KC-{abs(hash(new_username)) % 90000 + 10000}"
                        st.session_state.auth_mode = "login"
                        st.success("🎉 Account created successfully! Logging you in...")
                        st.rerun()

            # Option to switch back to Login
            st.markdown("<p style='text-align:center; color:#64748b; margin-top:1.5rem; margin-bottom:0.5rem;'>Already have an account?</p>", unsafe_allow_html=True)
            if st.button("🔙 Back to Login", key="btn_goto_login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

if not st.session_state.logged_in:
    show_auth_page()
    st.stop()


# ══════════════════════════════════════════════════════════════════
# 🧭 SESSION STATE & NAVIGATION
# ══════════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

def nav_to(page):
    st.session_state.page = page


# ══════════════════════════════════════════════════════════════════
#  GLOBAL CSS — Clean Theme, Fixed Clickable Areas & Popovers
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

/* ── App Background ───────────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #f0f2f5 !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 1400px;
}

/* ── Headings & Paragraphs ────────────────────────────── */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {
    color: #0f172a !important;
    font-weight: 700 !important;
}
[data-testid="stMain"] p,
[data-testid="stMain"] span,
[data-testid="stMain"] label {
    color: #1e293b !important;
}

/* ── TOP RIGHT BUTTONS (🔔 Alerts & 👤 Avatar) ───────── */
div[data-testid="stPopover"] > button,
div[data-testid="stPopover"] button {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    padding: 0.55rem 1rem !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}
/* Ensure entire center of the button triggers click and hand icon */
div[data-testid="stPopover"] > button *,
div[data-testid="stPopover"] button * {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    cursor: pointer !important;
    pointer-events: none !important;
}
div[data-testid="stPopover"] > button:hover {
    background-color: #f8fafc !important;
    border-color: #6366f1 !important;
}

/* ── INSIDE POPOVER DROPDOWN MENU ─────────────────────── */
div[data-baseweb="popover"],
[data-testid="stPopoverBody"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}
div[data-baseweb="popover"] *,
[data-testid="stPopoverBody"] * {
    color: #0f172a !important;
}

/* Fix "View Profile & Settings" inside the popup */
div[data-baseweb="popover"] button:not([aria-label*="Log Out"]),
[data-testid="stPopoverBody"] button:not([aria-label*="Log Out"]) {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
div[data-baseweb="popover"] button:not([aria-label*="Log Out"]) *,
[data-testid="stPopoverBody"] button:not([aria-label*="Log Out"]) * {
    color: #0f172a !important;
    font-weight: 600 !important;
}
div[data-baseweb="popover"] button:not([aria-label*="Log Out"]):hover {
    background-color: #e2e8f0 !important;
}

/* ── 🔴 RED LOGOUT BUTTON (Everywhere) ─────────────────── */
button[aria-label*="Log Out"], 
button[aria-label*="Logout"],
button[aria-label*="Log out"] {
    background-color: #ef4444 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}
button[aria-label*="Log Out"] *, 
button[aria-label*="Logout"] *,
button[aria-label*="Log out"] * {
    color: #ffffff !important;
    font-weight: 700 !important;
}
button[aria-label*="Log Out"]:hover, 
button[aria-label*="Logout"]:hover {
    background-color: #dc2626 !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
}

/* ── INVOICE FILE UPLOADER ────────────────────────────── */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploader"] > section {
    background-color: #ffffff !important;
    border: 2px dashed #94a3b8 !important;
    border-radius: 16px !important;
    padding: 1.8rem 1rem !important;
}
[data-testid="stFileUploader"] section *,
[data-testid="stFileUploaderDropzone"] * {
    color: #334155 !important;
}
[data-testid="stFileUploader"] button {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] button * {
    color: #0f172a !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploader"] small {
    color: #64748b !important;
}

/* ── GENERAL BUTTONS ──────────────────────────────────── */
[data-testid="stMain"] button[kind="secondary"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 10px !important;
}
[data-testid="stMain"] button[kind="secondary"] * {
    color: #0f172a !important;
    font-weight: 600 !important;
}
[data-testid="stMain"] button[kind="secondary"]:hover {
    background-color: #f8fafc !important;
    border-color: #94a3b8 !important;
}

/* ── TABS ─────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    background: transparent !important;
}
button[data-baseweb="tab"] * {
    color: #475569 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] * {
    color: #6366f1 !important;
    font-weight: 800 !important;
}

/* ── CONTAINERS / CARDS ───────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
}

.info-row {
    display: flex;
    justify-content: space-between;
    padding: 0.85rem 0;
    border-bottom: 1px solid #f1f5f9;
}
.info-label {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.95rem;
}
.info-value {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 1rem;
}

/* ── SIDEBAR ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(195deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1rem !important;
    margin: 2px 0 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.2rem 0 0.8rem 0;">
        <div style="font-size:2.2rem; margin-bottom:4px;">🧾</div>
        <div style="font-size:1.25rem; font-weight:800; color:#ffffff !important;">Karobar Copilot</div>
        <div style="font-size:0.75rem; color:#94a3b8 !important;">Business Management Suite</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    nav_items = [
        ("📊", "Dashboard"),
        ("🧾", "Invoices"),
        ("💸", "Expenses"),
        ("📦", "Inventory"),
        ("👥", "Customers"),
        ("📈", "Analytics"),
        ("✨", "AI Assistant"),
    ]

    for icon, label in nav_items:
        btn_type = "primary" if st.session_state.page == label else "secondary"
        st.button(
            f"{icon}  {label}",
            key=f"nav_{label}",
            on_click=nav_to,
            args=(label,),
            type=btn_type,
            use_container_width=True,
        )

    st.divider()

    st.button(
        "⚙️  Profile & Settings",
        key="nav_Settings",
        on_click=nav_to,
        args=("Settings",),
        type="primary" if st.session_state.page == "Settings" else "secondary",
        use_container_width=True,
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    if st.button("🚪 Log Out", key="sidebar_logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════
#  TOP HEADER BAR
# ══════════════════════════════════════════════════════════════════

hour = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
current_user = st.session_state.profile["full_name"]
avatar_initial = current_user[0].upper() if current_user else "U"

head_col1, head_col2, head_col3 = st.columns([5, 1.2, 1])

with head_col1:
    st.markdown(f"""
    <div style="background:#ffffff; border-radius:16px; padding:1.1rem 1.8rem; box-shadow:0 1px 3px rgba(0,0,0,0.05); border:1px solid #e2e8f0;">
        <h2 style="margin:0; font-size:1.4rem; font-weight:700; color:#0f172a !important;">{greeting}, {current_user} 👋</h2>
        <p style="margin:0; font-size:0.88rem; color:#475569 !important; margin-top:2px;">Here's what's happening with your business today</p>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    with st.popover("🔔 Alerts", use_container_width=True):
        st.markdown("<h3 style='color:#0f172a; margin-top:0;'>🔔 Notifications</h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.warning("⚠️ **Payment Reminder**: Vendor Apex Supplies is overdue by 2 days (₹12,400).")
        st.info("📦 **Stock Update**: 15 units of Paper Rolls added to inventory.")
        st.success("✅ **GST Filing**: Q3 draft report ready for review.")

with head_col3:
    with st.popover(f"👤 {avatar_initial}", use_container_width=True):
        st.markdown(f"<h3 style='margin:0 0 4px 0; color:#0f172a;'>{st.session_state.profile['full_name']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#64748b; margin-bottom:12px;'>{st.session_state.profile['email']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("👤 View Profile & Settings", key="pop_view_profile", use_container_width=True):
            nav_to("Settings")
            st.rerun()
        if st.button("🚪 Log Out", key="pop_logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

page = st.session_state.page


# ══════════════════════════════════════════════════════════════════
#  PAGE: INVOICES
# ══════════════════════════════════════════════════════════════════

if page == "Invoices":
    st.markdown('<h2 style="font-size:1.5rem; color:#0f172a;">🧾 Invoice Management</h2>', unsafe_allow_html=True)
    inv_tab1, inv_tab2 = st.tabs(["➕ Add Invoice", "💰 Payments"])
    
    with inv_tab1:
        st.write("Upload an invoice, check the details, then approve to save.")
        file = st.file_uploader("Upload invoice (photo or PDF)", type=["png", "jpg", "jpeg", "pdf"])
        if file is not None:
            data = read_invoice(file.getvalue())
            st.json(data)
            
    with inv_tab2:
        st.write("All payments recorded from database.")


# ══════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════

elif page == "Dashboard":
    inv_count = database.get_invoice_count()
    sub, gst_total, total_spend = database.get_gst_totals()
    payment = database.get_payment_summary()
    net_profit = sub

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""<div style="background:#ffffff; border-radius:16px; padding:1.3rem; border-left:4px solid #6366f1; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
            <div style="color:#64748b; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Total Revenue</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin:6px 0;">₹{:,.0f}</div>
            <div style="font-size:0.82rem; color:#6366f1; font-weight:600;">📈 From {} invoice{}</div>
        </div>""".format(total_spend, inv_count, "s" if inv_count != 1 else ""), unsafe_allow_html=True)
    with k2:
        st.markdown("""<div style="background:#ffffff; border-radius:16px; padding:1.3rem; border-left:4px solid #f43f5e; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
            <div style="color:#64748b; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Total Expenses</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin:6px 0;">₹{:,.0f}</div>
            <div style="font-size:0.82rem; color:#f43f5e; font-weight:600;">💸 GST: ₹{:,.0f}</div>
        </div>""".format(gst_total, gst_total), unsafe_allow_html=True)
    with k3:
        st.markdown("""<div style="background:#ffffff; border-radius:16px; padding:1.3rem; border-left:4px solid #0ea5e9; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
            <div style="color:#64748b; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Total Invoices</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin:6px 0;">{}</div>
            <div style="font-size:0.82rem; color:#0ea5e9; font-weight:600;">🔴 {} overdue</div>
        </div>""".format(inv_count, payment["overdue_count"]), unsafe_allow_html=True)
    with k4:
        st.markdown("""<div style="background:#ffffff; border-radius:16px; padding:1.3rem; border-left:4px solid #10b981; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
            <div style="color:#64748b; font-size:0.82rem; font-weight:600; text-transform:uppercase;">Net Profit</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin:6px 0;">₹{:,.0f}</div>
            <div style="font-size:0.82rem; color:#10b981; font-weight:600;">✅ {} paid</div>
        </div>""".format(net_profit, payment["paid_count"]), unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    col_qa, col_recent = st.columns([2, 3])
    with col_qa:
        st.markdown('<h3 style="font-size:1.2rem; color:#0f172a; margin-bottom:0.8rem;">⚡ Quick Actions</h3>', unsafe_allow_html=True)
        qa1, qa2 = st.columns(2)
        with qa1:
            if st.button("🧾\n\nCreate Invoice", key="qa_inv", use_container_width=True):
                nav_to("Invoices")
                st.rerun()
            if st.button("📦\n\nManage Inventory", key="qa_stock", use_container_width=True):
                nav_to("Inventory")
                st.rerun()
        with qa2:
            if st.button("💸\n\nAdd Expense", key="qa_exp", use_container_width=True):
                nav_to("Expenses")
                st.rerun()
            if st.button("✨\n\nAsk AI", key="qa_ai", use_container_width=True):
                nav_to("AI Assistant")
                st.rerun()

    with col_recent:
        st.markdown('<h3 style="font-size:1.2rem; color:#0f172a; margin-bottom:0.8rem;">🕐 Recent Invoices</h3>', unsafe_allow_html=True)
        recent = database.get_recent_invoices()
        if recent:
            df_recent = pd.DataFrame(recent, columns=["Invoice #", "Vendor", "Date", "Total", "Paid"])
            df_recent["Status"] = df_recent["Paid"].map({1: "✅ Paid", 0: "⏳ Unpaid"})
            df_recent["Total"] = df_recent["Total"].map(lambda x: f"₹{x:,.2f}")
            st.dataframe(df_recent[["Invoice #", "Vendor", "Date", "Total", "Status"]], use_container_width=True, hide_index=True, height=220)
        else:
            st.info("No invoices yet. Create your first invoice!")


# ══════════════════════════════════════════════════════════════════
#  PAGE: PROFILE & SETTINGS
# ══════════════════════════════════════════════════════════════════

elif page == "Settings":
    st.markdown('<h2 style="font-size:1.6rem; color:#0f172a; margin-bottom:1rem;">👤 Account, Profile & Settings</h2>', unsafe_allow_html=True)

    set_tab1, set_tab2, set_tab3 = st.tabs([
        "👤 Profile & Account", 
        "⚙️ Preferences & Settings", 
        "❓ Help & Support"
    ])

    # ── TAB 1: PROFILE & ACCOUNT ────────────────────────────────────
    with set_tab1:
        with st.container(border=True):
            head_p1, head_p2 = st.columns([5, 1.5])
            with head_p1:
                st.subheader("1. Personal Information")
            with head_p2:
                if not st.session_state.edit_profile_mode:
                    if st.button("✏️ Edit Profile", key="btn_edit_profile"):
                        st.session_state.edit_profile_mode = True
                        st.rerun()
                else:
                    if st.button("❌ Cancel", key="btn_cancel_edit"):
                        st.session_state.edit_profile_mode = False
                        st.rerun()

            if st.session_state.edit_profile_mode:
                with st.form("edit_profile_form"):
                    new_name = st.text_input("Full Name", st.session_state.profile["full_name"])
                    new_email = st.text_input("Email Address", st.session_state.profile["email"])
                    new_phone = st.text_input("Phone Number", st.session_state.profile["phone"])
                    save_btn = st.form_submit_button("💾 Save Profile Changes", type="primary")

                    if save_btn:
                        st.session_state.profile["full_name"] = new_name
                        st.session_state.profile["email"] = new_email
                        st.session_state.profile["phone"] = new_phone
                        st.session_state.edit_profile_mode = False
                        st.success("✅ Profile details updated successfully!")
                        st.rerun()
            else:
                st.markdown(f"""
                <div class="info-row"><span class="info-label">Full Name:</span><span class="info-value">{st.session_state.profile['full_name']}</span></div>
                <div class="info-row"><span class="info-label">Email Address:</span><span class="info-value">{st.session_state.profile['email']}</span></div>
                <div class="info-row" style="border-bottom:none;"><span class="info-label">Phone Number:</span><span class="info-value">{st.session_state.profile['phone']}</span></div>
                """, unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader("2. Account Information")
            st.markdown(f"""
            <div class="info-row"><span class="info-label">User ID:</span><span class="info-value"><code>{st.session_state.profile['user_id']}</code></span></div>
            <div class="info-row"><span class="info-label">Account Type:</span><span class="info-value">{st.session_state.profile['account_type']}</span></div>
            <div class="info-row" style="border-bottom:none;"><span class="info-label">Verification Status:</span><span class="info-value" style="color:#10b981 !important;">{st.session_state.profile['verification_status']}</span></div>
            """, unsafe_allow_html=True)

            st.markdown("<br><h4 style='color:#0f172a; margin-bottom:8px;'>Recent Login History:</h4>", unsafe_allow_html=True)
            df_login = pd.DataFrame(st.session_state.profile["login_history"])
            st.dataframe(df_login, use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.subheader("Account Session")
            st.write("End your current session across this browser window.")
            if st.button("🚪 Log Out of Karobar Copilot", key="settings_logout_btn"):
                st.session_state.logged_in = False
                st.rerun()

    # ── TAB 2: PREFERENCES & SETTINGS ───────────────────────────────
    with set_tab2:
        with st.container(border=True):
            st.subheader("4. Preferences & Settings")
            languages = ["English", "Hindi (हिन्दी)", "Gujarati (ગુજરાતી)", "Marathi (मराठी)", "Tamil (தமிழ்)"]
            selected_lang = st.selectbox("Language Selection", languages, index=0)
            
            themes = ["Light Mode (Default)", "Dark Mode"]
            selected_theme = st.radio("App Theme", themes, index=0, horizontal=True)

            if st.button("Save Preferences", type="primary"):
                st.session_state.profile["language"] = selected_lang
                st.session_state.profile["theme"] = selected_theme
                st.success("Preferences updated!")

    # ── TAB 3: HELP & SUPPORT ───────────────────────────────────────
    with set_tab3:
        with st.container(border=True):
            st.subheader("5. Help & Support")

            with st.expander("📚 Help Centre & FAQs"):
                st.write("""
                - **How do I upload an invoice?** Go to the Invoices tab and upload a clear PDF or PNG/JPG receipt.
                - **How is GST calculated?** CGST and SGST are split evenly at 50% for intra-state transactions.
                - **Need immediate support?** Contact our support desk at `support@karobarcopilot.in`.
                """)

            with st.expander("🚨 Report a Problem"):
                with st.form("problem_form"):
                    issue_type = st.selectbox("Issue Category", ["Invoice Upload Error", "Calculation Mismatch", "Feature Request", "Other"])
                    issue_desc = st.text_area("Describe the issue in detail")
                    submitted = st.form_submit_button("Submit Report")
                    if submitted:
                        st.success("Thank you! Your issue report has been logged.")

            with st.expander("📄 Terms and Conditions"):
                st.write("""
                By using Karobar Copilot, you agree to keep your credentials confidential. 
                All financial data generated is retained for tax and GST accounting compliance purposes under Indian SME regulatory norms.
                """)

            with st.expander("🔒 Privacy Policy"):
                st.write("""
                Your invoice data and customer contacts are strictly encrypted and never shared with third parties without your explicit permission.
                """)


# ══════════════════════════════════════════════════════════════════
#  OTHER PAGES
# ══════════════════════════════════════════════════════════════════

elif page == "Inventory":
    st.markdown('<h2 style="font-size:1.5rem; color:#0f172a;">📦 Inventory Management</h2>', unsafe_allow_html=True)
    rows = database.get_inventory()
    if rows:
        st.dataframe(pd.DataFrame(rows, columns=["Item", "In Stock"]), use_container_width=True)
    else:
        st.info("No inventory yet.")

elif page == "Analytics":
    st.markdown('<h2 style="font-size:1.5rem; color:#0f172a;">📈 Business Analytics</h2>', unsafe_allow_html=True)
    st.info("Analytics charts active.")

elif page in ["Expenses", "Customers"]:
    st.markdown(f'<div style="background:#ffffff; border-radius:16px; padding:2rem; border:1px solid #e2e8f0;"><h2 style="color:#0f172a;">{page} coming soon!</h2></div>', unsafe_allow_html=True)

elif page == "AI Assistant":
    st.markdown('<h2 style="font-size:1.5rem; color:#0f172a;">✨ AI Assistant</h2>', unsafe_allow_html=True)
    st.info("AI Copilot active.")