import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from extract import read_invoice
import database

database.setup()

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Karobar Copilot",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ──────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


def nav_to(page):
    st.session_state.page = page


# ══════════════════════════════════════════════════════════════════
#  GLOBAL CSS — Premium SaaS Theme
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* ── Import Google Font ───────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Main area ────────────────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"] {
    background: #f0f2f5 !important;
}
[data-testid="stMain"] {
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

/* ── Sidebar — Dark Navy ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(195deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
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
    transition: all 0.2s ease !important;
    display: flex;
    align-items: center;
    gap: 10px;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    transform: translateX(4px);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    transform: translateX(4px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.4) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 0.8rem 0 !important;
}

/* ── Metric Cards ─────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.04);
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
[data-testid="stMetric"] label {
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
}

/* ── Cards / Containers ───────────────────────────────── */
[data-testid="stExpander"],
.stDataFrame {
    background: #ffffff;
    border-radius: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04) !important;
}

/* ── Buttons in main area ─────────────────────────────── */
.stMainBlockContainer .stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.25s ease !important;
    font-size: 0.88rem !important;
}
.stMainBlockContainer .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* ── Data Editor / Inputs ─────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDataFrame {
    border-radius: 10px !important;
}

/* ── Custom Heading Styles ────────────────────────────── */
h1, h2, h3 { color: #0f172a !important; }

/* ── Custom card class ────────────────────────────────── */
.card-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.04);
    transition: all 0.3s ease;
    margin-bottom: 1rem;
}
.card-container:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

/* ── AI Insights card ─────────────────────────────────── */
.ai-card {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%);
    border-radius: 20px;
    padding: 2rem 2rem;
    color: #ffffff !important;
    box-shadow: 0 8px 30px rgba(124, 58, 237, 0.25);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.ai-card::before {
    content: '';
    position: absolute;
    top: -50%; right: -50%;
    width: 100%; height: 100%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.ai-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(124, 58, 237, 0.35);
}
.ai-card h3, .ai-card p, .ai-card span {
    color: #ffffff !important;
    position: relative;
}
.ai-card h3 { font-size: 1.3rem; margin-bottom: 0.5rem; }
.ai-card p { font-size: 0.95rem; opacity: 0.92; line-height: 1.6; }

/* ── Quick Action Buttons ─────────────────────────────── */
.quick-action {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
    transition: all 0.3s ease;
    cursor: pointer;
}
.quick-action:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.quick-action .qa-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.quick-action .qa-label {
    font-weight: 600;
    font-size: 0.92rem;
    color: #0f172a;
}

/* ── Top header bar ───────────────────────────────────── */
.top-header {
    background: #ffffff;
    border-radius: 16px;
    padding: 1rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
}
.top-header .welcome h2 {
    margin: 0; font-size: 1.4rem; font-weight: 700; color: #0f172a;
}
.top-header .welcome p {
    margin: 0; font-size: 0.88rem; color: #64748b; margin-top: 2px;
}
.top-header .header-right {
    display: flex; align-items: center; gap: 16px;
}
.header-icon {
    width: 40px; height: 40px;
    border-radius: 12px;
    background: #f1f5f9;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.2s ease;
}
.header-icon:hover {
    background: #e2e8f0;
    transform: scale(1.05);
}
.profile-badge {
    width: 40px; height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 1rem;
    cursor: pointer;
}

/* ── Status badges ────────────────────────────────────── */
.badge-paid {
    background: #dcfce7; color: #15803d;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600;
    display: inline-block;
}
.badge-pending {
    background: #fef3c7; color: #92400e;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600;
    display: inline-block;
}
.badge-overdue {
    background: #fee2e2; color: #b91c1c;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600;
    display: inline-block;
}

/* ── Section headers ──────────────────────────────────── */
.section-header {
    font-size: 1.15rem; font-weight: 700;
    color: #0f172a; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 8px;
}

/* ── Empty state ──────────────────────────────────────── */
.empty-state {
    text-align: center; padding: 3rem 2rem;
    color: #94a3b8;
}
.empty-state .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h3 { color: #475569; margin-bottom: 0.5rem; }
.empty-state p { font-size: 0.92rem; }

/* ── Coming Soon pages ────────────────────────────────── */
.coming-soon {
    text-align: center;
    padding: 5rem 2rem;
    background: #ffffff;
    border-radius: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.coming-soon .cs-icon { font-size: 4rem; margin-bottom: 1.5rem; }
.coming-soon h2 { color: #0f172a; margin-bottom: 0.5rem; }
.coming-soon p { color: #64748b; font-size: 1rem; max-width: 450px; margin: 0 auto; }

/* ── Plotly chart container ───────────────────────────── */
.js-plotly-plot {
    border-radius: 16px !important;
}

/* ── Tab styles (for invoice sub-tabs) ────────────────── */
button[data-baseweb="tab"] {
    transition: all 0.25s ease;
    border-radius: 8px !important;
}
button[data-baseweb="tab"]:hover {
    transform: scale(1.05);
    background: rgba(99,102,241,0.08) !important;
}

/* ── Scrollbar styling ────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Animations ───────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── Brand ──────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 1.2rem 0 0.8rem 0;">
        <div style="font-size:2.2rem; margin-bottom:4px;">🧾</div>
        <div style="font-size:1.25rem; font-weight:800; color:#ffffff !important;
                    letter-spacing:-0.5px;">Karobar Copilot</div>
        <div style="font-size:0.75rem; color:#64748b !important;
                    margin-top:2px;">Business Management Suite</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Navigation Items ──────────────────────────────────
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
        "⚙️  Settings",
        key="nav_Settings",
        on_click=nav_to,
        args=("Settings",),
        type="primary" if st.session_state.page == "Settings" else "secondary",
        use_container_width=True,
    )

    # ── Sidebar footer ────────────────────────────────────
    st.markdown("""
    <div style="position:fixed; bottom:20px; padding:0 1rem;
                font-size:0.72rem; color:#475569 !important;">
        <div style="background:rgba(255,255,255,0.05); border-radius:12px;
                    padding:0.8rem 1rem;">
            <div style="font-weight:600; color:#94a3b8 !important;
                        margin-bottom:4px;">Karobar Copilot v1.0</div>
            <div style="color:#64748b !important;">Made with ❤️ for Indian SMBs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TOP HEADER BAR
# ══════════════════════════════════════════════════════════════════

hour = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

st.markdown(f"""
<div class="top-header">
    <div class="welcome">
        <h2>{greeting}, Bhoomika 👋</h2>
        <p>Here's what's happening with your business today</p>
    </div>
    <div class="header-right">
        <div class="header-icon">🔔</div>
        <div class="header-icon">📧</div>
        <div class="profile-badge">B</div>
    </div>
</div>
""", unsafe_allow_html=True)

page = st.session_state.page


# ══════════════════════════════════════════════════════════════════
#  HELPER: render a white card wrapper
# ══════════════════════════════════════════════════════════════════

def card_start():
    return '<div class="card-container">'

def card_end():
    return '</div>'


# ══════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════

if page == "Dashboard":

    inv_count = database.get_invoice_count()
    sub, gst_total, total_spend = database.get_gst_totals()
    payment = database.get_payment_summary()
    net_profit = sub  # taxable value (revenue proxy for now)

    # ── Summary Cards ─────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""<div class="card-container" style="border-left:4px solid #6366f1;">
            <div style="color:#64748b;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;">Total Revenue</div>
            <div style="font-size:1.8rem;font-weight:800;color:#0f172a;margin:6px 0;">₹{:,.0f}</div>
            <div style="font-size:0.82rem;color:#6366f1;font-weight:600;">📈 From {} invoice{}</div>
        </div>""".format(total_spend, inv_count, "s" if inv_count != 1 else ""), unsafe_allow_html=True)
    with k2:
        st.markdown("""<div class="card-container" style="border-left:4px solid #f43f5e;">
            <div style="color:#64748b;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;">Total Expenses</div>
            <div style="font-size:1.8rem;font-weight:800;color:#0f172a;margin:6px 0;">₹{:,.0f}</div>
            <div style="font-size:0.82rem;color:#f43f5e;font-weight:600;">💸 GST: ₹{:,.0f}</div>
        </div>""".format(gst_total, gst_total), unsafe_allow_html=True)
    with k3:
        st.markdown("""<div class="card-container" style="border-left:4px solid #0ea5e9;">
            <div style="color:#64748b;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;">Total Invoices</div>
            <div style="font-size:1.8rem;font-weight:800;color:#0f172a;margin:6px 0;">{}</div>
            <div style="font-size:0.82rem;color:#0ea5e9;font-weight:600;">🔴 {} overdue</div>
        </div>""".format(inv_count, payment["overdue_count"]), unsafe_allow_html=True)
    with k4:
        st.markdown("""<div class="card-container" style="border-left:4px solid #10b981;">
            <div style="color:#64748b;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;">Net Profit</div>
            <div style="font-size:1.8rem;font-weight:800;color:#0f172a;margin:6px 0;">₹{:,.0f}</div>
            <div style="font-size:0.82rem;color:#10b981;font-weight:600;">✅ {} paid</div>
        </div>""".format(net_profit, payment["paid_count"]), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Chart + Payment Donut ──────────────────────
    col_chart, col_pie = st.columns([3, 2])

    with col_chart:
        st.markdown('<div class="section-header">📈 Revenue & Expense Analytics</div>',
                    unsafe_allow_html=True)
        monthly = database.get_monthly_spend()
        if monthly:
            df_m = pd.DataFrame(monthly, columns=["Month", "Subtotal", "GST", "Total"])
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_m["Month"], y=df_m["Subtotal"],
                name="Revenue", marker_color="#6366f1",
                marker=dict(cornerradius=6),
            ))
            fig.add_trace(go.Bar(
                x=df_m["Month"], y=df_m["GST"],
                name="GST Expense", marker_color="#f43f5e",
                marker=dict(cornerradius=6),
            ))
            fig.update_layout(
                barmode="group",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="", gridcolor="rgba(0,0,0,0.04)"),
                yaxis=dict(title="Amount (₹)", gridcolor="rgba(0,0,0,0.04)"),
                height=370, margin=dict(t=20, b=40, l=60, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            font=dict(size=12)),
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""<div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>No Analytics Yet</h3>
                <p>Upload your first invoice to see beautiful charts here</p>
            </div>""", unsafe_allow_html=True)

    with col_pie:
        st.markdown('<div class="section-header">💳 Payment Status</div>',
                    unsafe_allow_html=True)
        labels = ["Paid", "Pending", "Overdue"]
        values = [payment["paid_count"], payment["pending_count"], payment["overdue_count"]]
        colors = ["#10b981", "#f59e0b", "#ef4444"]
        if sum(values) > 0:
            fig_pie = go.Figure(go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors),
                hole=0.55,
                textinfo="value+percent",
                textfont=dict(size=13, family="Inter"),
            ))
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=370, margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1,
                            font=dict(size=12)),
                font=dict(family="Inter"),
                annotations=[dict(
                    text=f"<b>{inv_count}</b><br><span style='font-size:11px'>Total</span>",
                    x=0.5, y=0.5, font_size=22, showarrow=False,
                    font=dict(family="Inter"),
                )],
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown("""<div class="empty-state">
                <div class="empty-icon">💳</div>
                <h3>No Payments Yet</h3>
                <p>Payment status will appear here once you add invoices</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── AI Insights Card ──────────────────────────────────
    overdue_text = ""
    if payment["overdue_count"] > 0:
        overdue_text = f"⚠️ You have <b>{payment['overdue_count']}</b> overdue invoice(s) worth <b>₹{payment['overdue_amount']:,.0f}</b>. Consider following up today."
    elif inv_count > 0:
        overdue_text = "✅ All invoices are on track. Great cash-flow management!"
    else:
        overdue_text = "💡 Start by uploading your first invoice. I'll analyze your business trends and give you smart insights."

    gst_tip = ""
    if gst_total > 0:
        gst_tip = f"<br><br>🏛️ Your total GST liability is <b>₹{gst_total:,.0f}</b> — CGST ₹{gst_total/2:,.0f} + SGST ₹{gst_total/2:,.0f}. Make sure to file on time!"

    st.markdown(f"""
    <div class="ai-card">
        <h3>✨ AI Insights</h3>
        <p>{overdue_text}{gst_tip}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Quick Actions + Recent Invoices ───────────────────
    col_qa, col_recent = st.columns([2, 3])

    with col_qa:
        st.markdown('<div class="section-header">⚡ Quick Actions</div>',
                    unsafe_allow_html=True)
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
        st.markdown('<div class="section-header">🕐 Recent Invoices</div>',
                    unsafe_allow_html=True)
        recent = database.get_recent_invoices()
        if recent:
            df_recent = pd.DataFrame(
                recent, columns=["Invoice #", "Vendor", "Date", "Total", "Paid"]
            )
            df_recent["Status"] = df_recent["Paid"].map({1: "✅ Paid", 0: "⏳ Unpaid"})
            df_recent["Total"] = df_recent["Total"].map(lambda x: f"₹{x:,.2f}")
            st.dataframe(
                df_recent[["Invoice #", "Vendor", "Date", "Total", "Status"]],
                use_container_width=True, hide_index=True, height=220,
            )
        else:
            st.markdown("""<div class="empty-state" style="padding:2rem;">
                <div class="empty-icon">🧾</div>
                <h3>No Invoices Yet</h3>
                <p>Your recent invoices will show up here</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Vendor Spend + Inventory ──────────────────────────
    col_v, col_i = st.columns(2)

    with col_v:
        st.markdown('<div class="section-header">🏢 Vendor-wise Spend</div>',
                    unsafe_allow_html=True)
        vendor_data = database.get_vendor_spend()
        if vendor_data:
            df_v = pd.DataFrame(vendor_data, columns=["Vendor", "Spend"])
            fig_v = px.bar(
                df_v, x="Spend", y="Vendor", orientation="h",
                color="Spend", color_continuous_scale=["#c7d2fe", "#6366f1"],
                text_auto=",.0f",
            )
            fig_v.update_layout(
                height=max(220, len(df_v) * 50),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                font=dict(family="Inter"),
            )
            fig_v.update_traces(textposition="outside")
            st.plotly_chart(fig_v, use_container_width=True)
        else:
            st.markdown("""<div class="empty-state" style="padding:2rem;">
                <div class="empty-icon">🏢</div>
                <h3>No Vendors Yet</h3>
                <p>Vendor breakdown will appear here</p>
            </div>""", unsafe_allow_html=True)

    with col_i:
        st.markdown('<div class="section-header">📦 Top Inventory Items</div>',
                    unsafe_allow_html=True)
        inv_data = database.get_top_inventory()
        if inv_data:
            df_inv = pd.DataFrame(inv_data, columns=["Item", "Qty"])
            fig_i = px.bar(
                df_inv, x="Qty", y="Item", orientation="h",
                color="Qty", color_continuous_scale=["#bbf7d0", "#10b981"],
                text_auto=",.0f",
            )
            fig_i.update_layout(
                height=max(220, len(df_inv) * 50),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                font=dict(family="Inter"),
            )
            fig_i.update_traces(textposition="outside")
            st.plotly_chart(fig_i, use_container_width=True)
        else:
            st.markdown("""<div class="empty-state" style="padding:2rem;">
                <div class="empty-icon">📦</div>
                <h3>No Inventory Yet</h3>
                <p>Stock levels will appear here</p>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: INVOICES (preserves all original invoice logic)
# ══════════════════════════════════════════════════════════════════

elif page == "Invoices":
    st.markdown('<div class="section-header" style="font-size:1.5rem;">🧾 Invoice Management</div>',
                unsafe_allow_html=True)

    inv_tab1, inv_tab2, inv_tab3 = st.tabs(["➕ Add Invoice", "💰 Payments", "🏛️ GST Summary"])

    # ── Add Invoice ───────────────────────────────────────
    with inv_tab1:
        st.write("Upload an invoice, check the details, then approve to save.")
        file = st.file_uploader(
            "Upload invoice (photo or PDF)", type=["png", "jpg", "jpeg", "pdf"]
        )
        if file is not None:
            data = read_invoice(file.getvalue())

            st.subheader("Review before saving")
            r1, r2 = st.columns(2)
            with r1:
                vendor = st.text_input("Vendor", data["vendor"])
                invoice_no = st.text_input("Invoice number", data["invoice_no"])
            with r2:
                date = st.text_input("Invoice date", data["date"])
                due_date = st.text_input("Due date", data.get("due_date", ""))

            table = st.data_editor(pd.DataFrame(data["items"]))

            amount = table["qty"] * table["rate"]
            subtotal = float(amount.sum())
            gst = float((amount * table["gst_percent"] / 100).sum())

            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Subtotal", f"₹{subtotal:,.2f}")
            sc2.metric("GST", f"₹{gst:,.2f}")
            sc3.metric("Total", f"₹{subtotal + gst:,.2f}")

            if database.invoice_exists(invoice_no):
                st.error("⚠️ Duplicate invoice: this invoice number is already saved.")
            elif st.button("✅ Approve and Save", type="primary"):
                database.save_invoice(
                    invoice_no, vendor, date, due_date, subtotal, gst,
                    table.to_dict("records"),
                )
                st.success("🎉 Saved! Inventory and payments updated.")
                st.balloons()

    # ── Payments ──────────────────────────────────────────
    with inv_tab2:
        st.markdown('<div class="section-header">💰 Payment Tracker</div>',
                    unsafe_allow_html=True)
        today = datetime.date.today().isoformat()
        rows = database.get_invoices()
        if not rows:
            st.markdown("""<div class="empty-state">
                <div class="empty-icon">💰</div>
                <h3>No Invoices Yet</h3>
                <p>Approve an invoice to start tracking payments</p>
            </div>""", unsafe_allow_html=True)
        for inv_no, ven, d, due, total, paid in rows:
            if paid:
                status = "Paid"
                badge = "badge-paid"
            elif due < today:
                status = "Overdue"
                badge = "badge-overdue"
            else:
                status = "Pending"
                badge = "badge-pending"

            c1, c2, c3, c4 = st.columns([3, 2, 3, 2])
            c1.write(f"**{ven}** (`{inv_no}`)")
            c2.write(f"Due {due}")
            c3.markdown(f"₹{total:,.2f} · <span class='{badge}'>{status}</span>",
                        unsafe_allow_html=True)
            if not paid and c4.button("Mark paid", key=f"pay_{inv_no}"):
                database.mark_paid(inv_no)
                st.rerun()
            if status == "Overdue":
                st.warning(f"⚠️ Reminder: pay {ven} ₹{total:,.2f} for {inv_no}. It was due on {due}.")

    # ── GST Summary ───────────────────────────────────────
    with inv_tab3:
        st.markdown('<div class="section-header">🏛️ GST Summary</div>',
                    unsafe_allow_html=True)
        sub, g, tot = database.get_gst_totals()
        if tot == 0:
            st.markdown("""<div class="empty-state">
                <div class="empty-icon">🏛️</div>
                <h3>No GST Data Yet</h3>
                <p>Approve an invoice to see your GST breakdown</p>
            </div>""", unsafe_allow_html=True)
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Taxable Value", f"₹{sub:,.2f}")
            c2.metric("Total GST", f"₹{g:,.2f}")
            c3.metric("Invoice Total", f"₹{tot:,.2f}")
            c4, c5 = st.columns(2)
            c4.metric("CGST (50%)", f"₹{g / 2:,.2f}")
            c5.metric("SGST (50%)", f"₹{g / 2:,.2f}")
            st.caption("CGST and SGST shown as 50% each, assuming intra-state purchases.")


# ══════════════════════════════════════════════════════════════════
#  PAGE: INVENTORY (preserves existing logic)
# ══════════════════════════════════════════════════════════════════

elif page == "Inventory":
    st.markdown('<div class="section-header" style="font-size:1.5rem;">📦 Inventory Management</div>',
                unsafe_allow_html=True)

    rows = database.get_inventory()
    if rows:
        inv_data = database.get_top_inventory(limit=50)
        df_inv = pd.DataFrame(rows, columns=["Item", "In Stock"])

        # Summary cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Items", len(df_inv))
        m2.metric("Total Units", f"{df_inv['In Stock'].sum():,.0f}")
        m3.metric("Avg Stock/Item", f"{df_inv['In Stock'].mean():,.1f}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        col_table, col_chart = st.columns([3, 2])
        with col_table:
            st.markdown('<div class="section-header">📋 Stock Levels</div>',
                        unsafe_allow_html=True)
            st.dataframe(df_inv, use_container_width=True, hide_index=True, height=400)
        with col_chart:
            st.markdown('<div class="section-header">📊 Stock Distribution</div>',
                        unsafe_allow_html=True)
            fig_i = px.bar(
                df_inv, x="In Stock", y="Item", orientation="h",
                color="In Stock", color_continuous_scale=["#bbf7d0", "#10b981"],
                text_auto=",.0f",
            )
            fig_i.update_layout(
                height=max(300, len(df_inv) * 45),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10), showlegend=False, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                font=dict(family="Inter"),
            )
            fig_i.update_traces(textposition="outside")
            st.plotly_chart(fig_i, use_container_width=True)
    else:
        st.markdown("""<div class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>No Inventory Yet</h3>
            <p>Approve an invoice in the Invoices section to start tracking stock</p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════

elif page == "Analytics":
    st.markdown('<div class="section-header" style="font-size:1.5rem;">📈 Business Analytics</div>',
                unsafe_allow_html=True)

    inv_count = database.get_invoice_count()
    if inv_count == 0:
        st.markdown("""<div class="empty-state">
            <div class="empty-icon">📈</div>
            <h3>No Data for Analytics</h3>
            <p>Add invoices to unlock powerful business insights</p>
        </div>""", unsafe_allow_html=True)
    else:
        sub, gst_total, total_spend = database.get_gst_totals()
        payment = database.get_payment_summary()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Revenue", f"₹{total_spend:,.0f}")
        m2.metric("Total GST", f"₹{gst_total:,.0f}")
        m3.metric("Paid Amount", f"₹{payment['paid_amount']:,.0f}")
        m4.metric("Overdue Amount", f"₹{payment['overdue_amount']:,.0f}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # Monthly trend — line chart
        monthly = database.get_monthly_spend()
        if monthly:
            st.markdown('<div class="section-header">📉 Monthly Trends</div>',
                        unsafe_allow_html=True)
            df_m = pd.DataFrame(monthly, columns=["Month", "Subtotal", "GST", "Total"])
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df_m["Month"], y=df_m["Total"], name="Total",
                line=dict(color="#6366f1", width=3), fill="tozeroy",
                fillcolor="rgba(99,102,241,0.1)",
            ))
            fig_line.add_trace(go.Scatter(
                x=df_m["Month"], y=df_m["GST"], name="GST",
                line=dict(color="#f43f5e", width=2, dash="dot"),
            ))
            fig_line.update_layout(
                height=350,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(0,0,0,0.04)"),
                yaxis=dict(gridcolor="rgba(0,0,0,0.04)", title="₹"),
                margin=dict(t=20, b=40), font=dict(family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # Vendor + Payment split
        col_v, col_p = st.columns(2)
        with col_v:
            st.markdown('<div class="section-header">🏢 Spend by Vendor</div>',
                        unsafe_allow_html=True)
            vendor_data = database.get_vendor_spend()
            if vendor_data:
                df_v = pd.DataFrame(vendor_data, columns=["Vendor", "Spend"])
                fig_vp = px.pie(df_v, names="Vendor", values="Spend",
                                color_discrete_sequence=px.colors.qualitative.Pastel,
                                hole=0.4)
                fig_vp.update_layout(
                    height=320, margin=dict(t=10, b=10),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig_vp, use_container_width=True)

        with col_p:
            st.markdown('<div class="section-header">💳 Payment Breakdown</div>',
                        unsafe_allow_html=True)
            fig_bar = go.Figure(go.Bar(
                x=["Paid", "Pending", "Overdue"],
                y=[payment["paid_amount"], payment["pending_amount"], payment["overdue_amount"]],
                marker_color=["#10b981", "#f59e0b", "#ef4444"],
                text=[f"₹{payment['paid_amount']:,.0f}",
                      f"₹{payment['pending_amount']:,.0f}",
                      f"₹{payment['overdue_amount']:,.0f}"],
                textposition="outside",
            ))
            fig_bar.update_layout(
                height=320, margin=dict(t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="rgba(0,0,0,0.04)", title="₹"),
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: EXPENSES (coming soon)
# ══════════════════════════════════════════════════════════════════

elif page == "Expenses":
    st.markdown("""<div class="coming-soon">
        <div class="cs-icon">💸</div>
        <h2>Expense Tracking</h2>
        <p>Smart expense categorization, receipt scanning, and budget management coming soon.</p>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: CUSTOMERS (coming soon)
# ══════════════════════════════════════════════════════════════════

elif page == "Customers":
    st.markdown("""<div class="coming-soon">
        <div class="cs-icon">👥</div>
        <h2>Customer Management</h2>
        <p>Track customer relationships, purchase history, and outstanding balances — coming soon.</p>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: AI ASSISTANT
# ══════════════════════════════════════════════════════════════════

elif page == "AI Assistant":
    st.markdown('<div class="section-header" style="font-size:1.5rem;">✨ AI Assistant</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-card" style="margin-bottom:1.5rem;">
        <h3>✨ Your Business AI Copilot</h3>
        <p>Ask me anything about your invoices, payments, inventory, or GST.
           I can help you find insights, spot trends, and make smarter decisions.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick data summary for context
    inv_count = database.get_invoice_count()
    sub, gst_total, total_spend = database.get_gst_totals()
    payment = database.get_payment_summary()

    st.markdown('<div class="section-header">📊 Business Snapshot</div>',
                unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Invoices", inv_count)
    m2.metric("Revenue", f"₹{total_spend:,.0f}")
    m3.metric("GST Owed", f"₹{gst_total:,.0f}")
    m4.metric("Overdue", f"₹{payment['overdue_amount']:,.0f}")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Upcoming dues as action items
    st.markdown('<div class="section-header">📅 Action Items</div>',
                unsafe_allow_html=True)
    dues = database.get_upcoming_dues()
    if dues:
        today = datetime.date.today().isoformat()
        for inv_no, vendor, due, total in dues:
            is_overdue = due < today
            icon = "🔴" if is_overdue else "🟡"
            try:
                due_dt = datetime.date.fromisoformat(due)
                delta = (due_dt - datetime.date.today()).days
                if delta < 0:
                    days_text = f"**{abs(delta)}d overdue**"
                elif delta == 0:
                    days_text = "**Due today!**"
                else:
                    days_text = f"{delta}d left"
            except ValueError:
                days_text = ""
            st.markdown(f"{icon} **{vendor}** — ₹{total:,.2f} — `{inv_no}` — {days_text}")
    else:
        st.success("🎉 All clear! No pending action items.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.info("💡 **Tip:** Full AI chat with Claude integration is coming soon! "
            "For now, use the dashboard and analytics to explore your data.")


# ══════════════════════════════════════════════════════════════════
#  PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════

elif page == "Settings":
    st.markdown('<div class="section-header" style="font-size:1.5rem;">⚙️ Settings</div>',
                unsafe_allow_html=True)

    st.markdown("""<div class="coming-soon">
        <div class="cs-icon">⚙️</div>
        <h2>Settings & Preferences</h2>
        <p>Business profile, notification preferences, integrations, and customization options — coming soon.</p>
    </div>""", unsafe_allow_html=True)
