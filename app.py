import datetime
import json
import textwrap
import time
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
    st.session_state.auth_mode = "login"

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
    # ── Inject Modern Dark SaaS Theme Styles for Login Page ──
    st.markdown(textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* ── Dark Premium Canvas ── */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #080F1F !important;
        background-image: 
            radial-gradient(circle at 10% 15%, rgba(37, 99, 235, 0.22) 0%, transparent 45%),
            radial-gradient(circle at 90% 85%, rgba(56, 189, 248, 0.16) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(16, 24, 39, 0.92) 0%, transparent 100%) !important;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        color: #FFFFFF !important;
    }

    /* ── Hide Sidebar Completely During Auth ── */
    section[data-testid="stSidebar"], 
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
    }
    [data-testid="stMain"], .main {
        margin-left: 0px !important;
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 !important;
    }
    .block-container {
        max-width: 1240px !important;
        padding-top: 3.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Hide default Streamlit headers & chrome */
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* ── Rising Brand Hero Showcase (Left Section) ── */
    .left-rising-container {
        position: relative;
        min-height: 520px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 2.5rem 2rem 2.5rem 0.5rem;
    }
    .ambient-glow-circle {
        position: absolute;
        width: 420px;
        height: 420px;
        left: -80px;
        bottom: 10px;
        background: radial-gradient(circle, rgba(37, 99, 235, 0.38) 0%, rgba(56, 189, 248, 0.14) 45%, transparent 70%);
        filter: blur(60px);
        pointer-events: none;
        z-index: 0;
    }
    .rising-wrapper {
        position: relative;
        z-index: 1;
        animation: riseFromBottom 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes riseFromBottom {
        0% {
            opacity: 0;
            transform: translateY(90px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .rising-brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(37, 99, 235, 0.16);
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 8px 18px;
        border-radius: 30px;
        margin-bottom: 1.8rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.25);
    }
    .rising-badge-icon {
        font-size: 1.2rem;
    }
    .rising-badge-text {
        color: #38BDF8;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.4px;
        text-transform: uppercase;
    }
    .rising-hero-title {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        font-size: 4.8rem !important;
        font-weight: 900 !important;
        line-height: 1.04 !important;
        color: #FFFFFF !important;
        letter-spacing: -2.5px !important;
        margin: 0 0 1.2rem 0 !important;
        text-shadow: 0 15px 40px rgba(0, 0, 0, 0.7);
    }
    .rising-gradient-text {
        background: linear-gradient(135deg, #38BDF8 0%, #2563EB 55%, #60A5FA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 35px rgba(56, 189, 248, 0.5));
    }
    .rising-hero-subtitle {
        color: #AAB4C5 !important;
        font-size: 1.25rem !important;
        line-height: 1.6 !important;
        max-width: 500px;
        margin: 0 0 2rem 0 !important;
        letter-spacing: -0.3px;
        font-weight: 500 !important;
    }
    .rising-pills-row {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }
    .rising-pill {
        background: rgba(16, 24, 39, 0.8);
        border: 1px solid #263449;
        color: #E2E8F0;
        font-size: 0.88rem;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 20px;
        backdrop-filter: blur(8px);
        transition: all 0.25s ease;
    }
    .rising-pill:hover {
        border-color: #2563EB;
        background: rgba(37, 99, 235, 0.15);
        color: #FFFFFF;
        transform: translateY(-2px);
    }

    /* ── Right Section: Premium Card Container ── */
    [data-testid="stForm"] {
        background-color: #101827 !important;
        border: 1px solid #263449 !important;
        border-radius: 24px !important;
        padding: 2.5rem 2.2rem !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65), 0 0 45px rgba(37, 99, 235, 0.12) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [data-testid="stForm"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2563EB, #38BDF8, #2563EB);
    }

    .secure-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #38BDF8;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.6rem;
    }
    .lock-dot {
        width: 6px;
        height: 6px;
        background: #38BDF8;
        border-radius: 50%;
        box-shadow: 0 0 6px #38BDF8;
    }
    .auth-main-title {
        color: #FFFFFF !important;
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.6px !important;
        margin: 0 0 6px 0 !important;
    }
    .auth-sub-title {
        color: #AAB4C5 !important;
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
        margin: 0 0 1.8rem 0 !important;
    }

    /* ── Form Inputs ── */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #AAB4C5 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #080F1F !important;
        border: 1px solid #263449 !important;
        border-radius: 12px !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
        background-color: #0b1424 !important;
    }
    [data-testid="stTextInput"] input {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.85rem 1rem !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #64748B !important;
    }
    /* Password eye toggle */
    [data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
        color: #AAB4C5 !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }
    [data-testid="stTextInput"] button:hover {
        color: #38BDF8 !important;
    }
    [data-testid="stTextInput"] button svg {
        fill: #AAB4C5 !important;
    }

    /* ── Submit Button (Gradient Electric Blue) ── */
    [data-testid="stFormSubmitButton"] {
        display: block !important;
        width: 100% !important;
        margin-top: 1.2rem !important;
    }
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 50%, #38BDF8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.88rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        cursor: pointer !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.45) !important;
        transition: all 0.25s ease !important;
        pointer-events: auto !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(37, 99, 235, 0.65) !important;
        filter: brightness(1.1) !important;
    }
    [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(0) !important;
    }

    /* ── Secondary Switch Auth Button ── */
    .stButton > button {
        background: rgba(38, 52, 73, 0.45) !important;
        border: 1px solid #263449 !important;
        color: #38BDF8 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.75rem 1.2rem !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background: rgba(37, 99, 235, 0.2) !important;
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }

    /* ── Clear, Beautiful Error / Success Alerts ── */
    div[data-testid="stAlert"] {
        background: rgba(239, 68, 68, 0.12) !important;
        border: 1px solid rgba(239, 68, 68, 0.35) !important;
        border-radius: 12px !important;
        color: #fca5a5 !important;
        margin-bottom: 1.2rem !important;
    }
    div[data-testid="stAlert"] * {
        color: #fecaca !important;
    }

    /* ── Footer Elements ── */
    .auth-footer-notes {
        margin-top: 1.8rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(38, 52, 73, 0.6);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }
    .security-badge-text {
        color: #AAB4C5;
        font-size: 0.78rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .copyright-badge-text {
        color: #64748B;
        font-size: 0.74rem;
    }

    /* ── Responsive Mobile & Tablet Layout ── */
    @media (max-width: 900px) {
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .left-rising-container {
            min-height: auto !important;
            padding: 1rem 0 !important;
        }
        .rising-hero-title {
            font-size: 3rem !important;
        }
        [data-testid="stForm"] {
            padding: 1.8rem 1.4rem !important;
            margin-top: 1.2rem !important;
        }
    }
    </style>
    """).strip(), unsafe_allow_html=True)

    col_left, col_right = st.columns([1.18, 1], gap="large")

    # ══════════════════════════════════════════════════════════
    #  LEFT SECTION: BIG BRAND RISING HERO
    # ══════════════════════════════════════════════════════════
    with col_left:
        st.markdown(textwrap.dedent("""
        <div class="left-rising-container">
            <div class="ambient-glow-circle"></div>
            <div class="rising-wrapper">
                <div class="rising-brand-badge">
                    <span class="rising-badge-icon">🧾</span>
                    <span class="rising-badge-text">AI-POWERED BUSINESS OS</span>
                </div>
                <h1 class="rising-hero-title">
                    Karobar<br>
                    <span class="rising-gradient-text">Copilot</span>
                </h1>
                <p class="rising-hero-subtitle">
                    Your Business, Smarter. Every Day.
                </p>
                <div class="rising-pills-row">
                    <span class="rising-pill">⚡ Smart Invoicing</span>
                    <span class="rising-pill">📊 Real-Time Telemetry</span>
                    <span class="rising-pill">📦 Inventory Sync</span>
                </div>
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  RIGHT SECTION: PREMIUM AUTHENTICATION CARD
    # ══════════════════════════════════════════════════════════
    with col_right:
        # ── 1. LOGIN MODE ──────────────────────────────────────
        if st.session_state.auth_mode == "login":
            with st.form("login_form"):
                st.markdown(textwrap.dedent("""
                <div class="secure-badge">
                    <span class="lock-dot"></span>
                    <span>SECURE MERCHANT ACCESS</span>
                </div>
                <h2 class="auth-main-title">Welcome Back!</h2>
                <p class="auth-sub-title">Sign in to continue to your Karobar Copilot dashboard.</p>
                """).strip(), unsafe_allow_html=True)

                username = st.text_input("👤 Username or ID", placeholder="Enter username (e.g. admin)", key="auth_user_in")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="auth_pass_in")
                submit = st.form_submit_button("Sign In to Dashboard →", use_container_width=True)

                if submit:
                    with st.spinner("Authenticating credentials..."):
                        time.sleep(0.35)
                        if username in st.session_state.users_db and st.session_state.users_db[username]["password"] == password:
                            user_info = st.session_state.users_db[username]
                            st.session_state.logged_in = True
                            st.session_state.profile["full_name"] = user_info["full_name"]
                            st.session_state.profile["email"] = user_info["email"]
                            st.session_state.profile["phone"] = user_info["phone"]
                            st.session_state.profile["user_id"] = f"KC-{abs(hash(username)) % 90000 + 10000}"
                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password. Please verify your credentials.")

            st.markdown(textwrap.dedent("""
            <p style='text-align:center; color:#AAB4C5; font-size:0.88rem; margin:1.5rem 0 0.5rem 0;'>Don't have an account yet?</p>
            """).strip(), unsafe_allow_html=True)
            if st.button("✨ Create New Account", key="btn_goto_signup", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

        # ── 2. SIGN UP / REGISTRATION MODE ─────────────────────
        else:
            with st.form("signup_form"):
                st.markdown(textwrap.dedent("""
                <div class="secure-badge">
                    <span class="lock-dot"></span>
                    <span>NEW MERCHANT REGISTRATION</span>
                </div>
                <h2 class="auth-main-title">Create Account</h2>
                <p class="auth-sub-title">Join Karobar Copilot and streamline your business operations.</p>
                """).strip(), unsafe_allow_html=True)

                new_fullname = st.text_input("👤 Full Name", placeholder="e.g. Rajesh Kumar")
                new_username = st.text_input("🏷️ Choose Username", placeholder="e.g. rajesh99")
                new_email = st.text_input("📧 Business Email Address", placeholder="rajesh@mybusiness.com")
                new_phone = st.text_input("📱 Phone Number", placeholder="+91 98765 43210")
                new_password = st.text_input("🔒 Create Password", type="password", placeholder="••••••••")
                confirm_password = st.text_input("🛡️ Confirm Password", type="password", placeholder="••••••••")
                
                signup_submit = st.form_submit_button("🚀 Register & Open Dashboard →", use_container_width=True)

                if signup_submit:
                    with st.spinner("Setting up your merchant profile..."):
                        time.sleep(0.35)
                        if not new_username or not new_password:
                            st.error("Username and password are required fields.")
                        elif new_username in st.session_state.users_db:
                            st.error("This username already exists. Please choose a different one.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match. Please re-enter carefully.")
                        else:
                            st.session_state.users_db[new_username] = {
                                "password": new_password,
                                "full_name": new_fullname if new_fullname else new_username.capitalize(),
                                "email": new_email if new_email else f"{new_username}@karobarcopilot.in",
                                "phone": new_phone if new_phone else "+91 99999 00000"
                            }
                            st.session_state.logged_in = True
                            st.session_state.profile["full_name"] = st.session_state.users_db[new_username]["full_name"]
                            st.session_state.profile["email"] = st.session_state.users_db[new_username]["email"]
                            st.session_state.profile["phone"] = st.session_state.users_db[new_username]["phone"]
                            st.session_state.profile["user_id"] = f"KC-{abs(hash(new_username)) % 90000 + 10000}"
                            st.session_state.auth_mode = "login"
                            st.success("🎉 Account registered successfully! Welcome aboard.")
                            st.rerun()

            st.markdown(textwrap.dedent("""
            <p style='text-align:center; color:#AAB4C5; font-size:0.88rem; margin:1.5rem 0 0.5rem 0;'>Already have an account?</p>
            """).strip(), unsafe_allow_html=True)
            if st.button("🔙 Back to Login", key="btn_goto_login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

        # Footer notes
        st.markdown(textwrap.dedent("""
        <div class="auth-footer-notes">
            <div class="security-badge-text">🔒 256-bit Bank-grade TLS Encryption</div>
            <div class="copyright-badge-text">© 2026 Karobar Copilot. All rights reserved.</div>
        </div>
        """).strip(), unsafe_allow_html=True)

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
#  GLOBAL CSS — Permanent Locked Sidebar & Clean SaaS Layout
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

/* ── 🚀 FORCE SIDEBAR TO STAY PERMANENTLY VISIBLE & OPEN ── */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    transform: none !important;
    margin-left: 0px !important;
    left: 0px !important;
    width: 19rem !important;
    min-width: 19rem !important;
    max-width: 19rem !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 0 !important;
    bottom: 0 !important;
    z-index: 99 !important;
    transition: none !important;
}

/* Push the main app content so it neatly aligns beside the sidebar */
[data-testid="stMain"],
.main {
    margin-left: 19rem !important;
    width: calc(100% - 19rem) !important;
}

/* Hide the collapse arrow (<) so it can never be accidentally lost again */
[data-testid="stSidebarCollapseButton"],
button[aria-label="Collapse sidebar"],
button[aria-label="Close sidebar"] {
    display: none !important;
}

/* ── NON-BLOCKING STREAMLIT HEADER ────────────────────── */
header[data-testid="stHeader"] {
    background: transparent !important;
    pointer-events: none !important;
    z-index: 50 !important;
}

[data-testid="stToolbar"] {
    display: none !important;
    pointer-events: none !important;
}

/* ── App Background ───────────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #f0f2f5 !important;
}
.block-container {
    padding-top: 1.5rem !important;
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

/* ── 🎯 100% CLICKABLE POPOVER BUTTONS (Alerts & Profile) */
div[data-testid="stPopover"] {
    position: relative !important;
    z-index: 1000 !important;
    width: 100% !important;
}

div[data-testid="stPopover"] > button,
div[data-testid="stPopover"] button,
[data-testid="stPopoverButton"] {
    position: relative !important;
    z-index: 1001 !important;
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    padding: 0.65rem 1rem !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    pointer-events: auto !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stPopover"] > button *,
div[data-testid="stPopover"] button *,
[data-testid="stPopoverButton"] * {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    cursor: pointer !important;
    pointer-events: none !important;
}

div[data-testid="stPopover"] > button:hover,
div[data-testid="stPopover"] button:hover {
    background-color: #f8fafc !important;
    border-color: #6366f1 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
    transform: translateY(-1px) !important;
}

/* ── INSIDE POPOVER DROPDOWN MENU ─────────────────────── */
div[data-baseweb="popover"],
[data-testid="stPopoverBody"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    z-index: 999999 !important;
}
div[data-baseweb="popover"] *,
[data-testid="stPopoverBody"] * {
    color: #0f172a !important;
}

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

/* ── 🔴 RED LOGOUT BUTTON ─────────────────────────────── */
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

/* ── SIDEBAR STYLE ────────────────────────────────────── */
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
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════

if page == "Dashboard":
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
#  PAGE: INVOICES (MERGED: REVIEW CARD + PERMANENT STORAGE + LIFETIME HISTORY)
# ══════════════════════════════════════════════════════════════════

elif page == "Invoices":
    st.markdown('<h2 style="font-size:1.6rem; color:#0f172a; margin-bottom:0.2rem;">🧾 Invoice Management & Storage</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:0.92rem; margin-bottom:1.2rem;">Add new invoices with real-time duplicate checks, review beautifully parsed data, store records permanently, and browse lifetime invoice history anytime.</p>', unsafe_allow_html=True)

    inv_tab1, inv_tab2, inv_tab3 = st.tabs([
        "➕ Add / Upload Invoice",
        "📜 Invoice History (All Time)",
        "💰 Payments Tracker"
    ])

    # ──────────────────────────────────────────────────────────────
    # TAB 1: ADD / UPLOAD INVOICE (Review Card + Duplicate Detection)
    # ──────────────────────────────────────────────────────────────
    with inv_tab1:
        entry_mode = st.radio(
            "Select invoice entry method:",
            ["📁 Upload Invoice Document (PDF / Image)", "✏️ Manual Invoice Entry"],
            horizontal=True,
            key="inv_entry_mode_selector"
        )

        today_val = datetime.date.today()
        default_due_val = today_val + datetime.timedelta(days=30)

        if entry_mode == "📁 Upload Invoice Document (PDF / Image)":
            st.write("Upload an invoice, check the details, then approve to save.")
            file = st.file_uploader("Upload Invoice (photo or PDF)", type=["png", "jpg", "jpeg", "pdf"], key="inv_file_uploader")

            if file is not None:
                data = read_invoice(file.getvalue(), filename=file.name)

                # ── Compute financials from parsed data ─────────────
                items_df = pd.DataFrame(data.get("items", []))
                if items_df.empty:
                    items_df = pd.DataFrame([{"item": "Sample Item", "qty": 1.0, "rate": 100.0, "gst_percent": 18.0}])

                items_df["qty"] = items_df["qty"].astype(float)
                items_df["rate"] = items_df["rate"].astype(float)
                items_df["gst_percent"] = items_df["gst_percent"].astype(float)
                items_df["amount"] = items_df["qty"] * items_df["rate"]
                items_df["gst_amount"] = items_df["amount"] * items_df["gst_percent"] / 100.0
                items_df["line_total"] = items_df["amount"] + items_df["gst_amount"]
                subtotal = float(items_df["amount"].sum())
                gst_total_val = float(items_df["gst_amount"].sum())
                grand_total = subtotal + gst_total_val

                # ── Build line-item table rows ──────────────────────
                table_rows_html = ""
                for idx, row in items_df.iterrows():
                    table_rows_html += f'<tr><td style="padding:14px 16px; border-bottom:1px solid #f1f5f9;"><span style="font-weight:600; color:#0f172a;">{row["item"]}</span></td><td style="padding:14px 16px; border-bottom:1px solid #f1f5f9; text-align:center; color:#334155;">{int(row["qty"])}</td><td style="padding:14px 16px; border-bottom:1px solid #f1f5f9; text-align:center; color:#334155;">₹{row["rate"]:,.2f}</td><td style="padding:14px 16px; border-bottom:1px solid #f1f5f9; text-align:center;"><span style="background:#FEF3C7; color:#92400E; font-size:12px; font-weight:600; padding:3px 10px; border-radius:6px;">{int(row["gst_percent"])}%</span></td><td style="padding:14px 16px; border-bottom:1px solid #f1f5f9; text-align:right; font-weight:600; color:#0f172a;">₹{row["line_total"]:,.2f}</td></tr>'

                # ── Render Styled Invoice Review Card ───────────────
                review_html = f"""<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:28px 32px; margin:20px 0; box-shadow:0 4px 20px rgba(0,0,0,0.06);">
<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:24px; padding-bottom:18px; border-bottom:1px solid #f1f5f9;">
<div style="display:flex; align-items:center; gap:14px;">
<div style="width:46px; height:46px; background:linear-gradient(135deg,#6366f1,#8b5cf6); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:22px; flex-shrink:0;">🧾</div>
<div>
<div style="font-size:20px; font-weight:700; color:#0f172a; margin:0;">Invoice Review</div>
<div style="font-size:13px; color:#64748b; margin-top:2px;">Extracted from uploaded document · Verify details below</div>
</div>
</div>
<div style="display:inline-flex; align-items:center; gap:6px; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600; letter-spacing:0.3px; text-transform:uppercase; background:#FEF3C7; color:#92400E; border:1px solid #FDE68A;">⏳ Pending Review</div>
</div>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(190px,1fr)); gap:14px; margin-bottom:24px;">
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px;">
<div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.7px; margin-bottom:5px;">Vendor</div>
<div style="font-size:16px; font-weight:700; color:#0f172a;">🏢 {data.get('vendor', 'Unknown')}</div>
</div>
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px;">
<div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.7px; margin-bottom:5px;">Invoice Number</div>
<div style="font-size:16px; font-weight:700; color:#0f172a;">📄 {data.get('invoice_no', 'INV-1042')}</div>
</div>
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px;">
<div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.7px; margin-bottom:5px;">Issue Date</div>
<div style="font-size:16px; font-weight:700; color:#0f172a;">📅 {data.get('date', today_val.isoformat())}</div>
</div>
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px;">
<div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.7px; margin-bottom:5px;">Due Date</div>
<div style="font-size:16px; font-weight:700; color:#0f172a;">⏰ {data.get('due_date', default_due_val.isoformat())}</div>
</div>
</div>
<div style="display:flex; align-items:center; gap:8px; margin:20px 0 14px 0;">
<span style="font-size:13px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.8px;">📦 Line Items</span>
<div style="flex:1; height:1px; background:#e2e8f0;"></div>
</div>
<table style="width:100%; border-collapse:separate; border-spacing:0; margin-bottom:24px; border-radius:12px; overflow:hidden; border:1px solid #e2e8f0;">
<thead>
<tr style="background:#f1f5f9;">
<th style="padding:12px 16px; text-align:left; font-size:11px; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.7px; border-bottom:2px solid #e2e8f0;">Item / Description</th>
<th style="padding:12px 16px; text-align:center; font-size:11px; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.7px; border-bottom:2px solid #e2e8f0;">Qty</th>
<th style="padding:12px 16px; text-align:center; font-size:11px; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.7px; border-bottom:2px solid #e2e8f0;">Rate</th>
<th style="padding:12px 16px; text-align:center; font-size:11px; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.7px; border-bottom:2px solid #e2e8f0;">GST</th>
<th style="padding:12px 16px; text-align:right; font-size:11px; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.7px; border-bottom:2px solid #e2e8f0;">Total</th>
</tr>
</thead>
<tbody>
{table_rows_html}
</tbody>
</table>
<div style="display:flex; justify-content:flex-end; margin-bottom:16px;">
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:18px 24px; min-width:280px;">
<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0;">
<span style="font-size:14px; color:#64748b;">Subtotal</span>
<span style="font-size:14px; font-weight:600; color:#334155;">₹{subtotal:,.2f}</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0;">
<span style="font-size:14px; color:#64748b;">GST Amount</span>
<span style="font-size:14px; font-weight:600; color:#334155;">₹{gst_total_val:,.2f}</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0 4px 0; margin-top:8px; border-top:2px dashed #e2e8f0;">
<span style="font-size:16px; font-weight:700; color:#0f172a;">Grand Total</span>
<span style="font-size:22px; font-weight:800; background:linear-gradient(135deg,#6366f1,#8b5cf6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">₹{grand_total:,.2f}</span>
</div>
</div>
</div>
<details style="margin-top:12px;">
<summary style="color:#94a3b8; font-size:13px; cursor:pointer; padding:8px 0; user-select:none;">🔍 View Raw JSON</summary>
<pre style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px; font-size:12px; color:#6366f1; overflow-x:auto; margin-top:8px;">{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
</details>
</div>"""
                st.markdown(review_html, unsafe_allow_html=True)

                # ── Editable Fields (Streamlit native widgets) ──────
                with st.expander("✏️ Edit Invoice Details", expanded=False):
                    st.caption("Make corrections to the extracted data before saving.")

                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        vendor = st.text_input("Vendor", data.get("vendor", "Sharma Traders"), key="edit_vendor")
                        invoice_no = st.text_input("Invoice Number", data.get("invoice_no", "INV-1042"), key="edit_inv_no")
                    with col_e2:
                        date_val = st.text_input("Invoice Date", data.get("date", today_val.isoformat()), key="edit_date")
                        due_date_val = st.text_input("Due Date", data.get("due_date", default_due_val.isoformat()), key="edit_due")

                    st.markdown("**Line Items**")
                    table = st.data_editor(
                        items_df[["item", "qty", "rate", "gst_percent"]],
                        use_container_width=True,
                        num_rows="dynamic",
                        column_config={
                            "item": st.column_config.TextColumn("Item Name", width="large"),
                            "qty": st.column_config.NumberColumn("Quantity", min_value=0, format="%d"),
                            "rate": st.column_config.NumberColumn("Rate (₹)", min_value=0, format="₹%.2f"),
                            "gst_percent": st.column_config.NumberColumn("GST %", min_value=0, max_value=100, format="%d%%"),
                        },
                        key="edit_items_table",
                    )

                    # Recalculate from edited values
                    edited_amount = table["qty"] * table["rate"]
                    subtotal = float(edited_amount.sum())
                    gst_total_val = float((edited_amount * table["gst_percent"] / 100).sum())
                    grand_total = subtotal + gst_total_val

                    rc1, rc2, rc3 = st.columns(3)
                    rc1.metric("Subtotal", f"₹{subtotal:,.2f}")
                    rc2.metric("GST", f"₹{gst_total_val:,.2f}")
                    rc3.metric("Grand Total", f"₹{grand_total:,.2f}")

                # Use edited values if expander was used, otherwise defaults
                if "edit_vendor" not in st.session_state:
                    vendor = data.get("vendor", "Sharma Traders")
                    invoice_no = data.get("invoice_no", "INV-1042")
                    date_val = data.get("date", today_val.isoformat())
                    due_date_val = data.get("due_date", default_due_val.isoformat())
                    final_items = items_df[["item", "qty", "rate", "gst_percent"]].to_dict("records")
                else:
                    vendor = st.session_state.get("edit_vendor", data.get("vendor", "Sharma Traders"))
                    invoice_no = st.session_state.get("edit_inv_no", data.get("invoice_no", "INV-1042"))
                    date_val = st.session_state.get("edit_date", data.get("date", today_val.isoformat()))
                    due_date_val = st.session_state.get("edit_due", data.get("due_date", default_due_val.isoformat()))
                    final_items = table.to_dict("records")

                # ── Live Duplicate Check & Overwrite Option ──────────
                is_duplicate = database.invoice_exists(invoice_no)
                allow_overwrite = False

                if is_duplicate:
                    existing_inv = database.get_invoice(invoice_no)
                    st.markdown(f"""
                    <div style="background:#FEF2F2; border:1.5px solid #f87171; border-radius:12px; padding:14px 18px; margin:14px 0;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:20px;">⚠️</span>
                            <span style="color:#991B1B; font-weight:700; font-size:15px;">Duplicate Invoice Detected:</span>
                        </div>
                        <div style="color:#7F1D1D; font-size:13.5px; margin-top:5px; line-height:1.5;">
                            Invoice <b>#{invoice_no}</b> already exists in permanent storage.<br>
                            <b>Vendor:</b> {existing_inv['vendor']} &nbsp;|&nbsp;
                            <b>Date:</b> {existing_inv['date']} &nbsp;|&nbsp;
                            <b>Amount:</b> ₹{existing_inv['total']:,.2f} &nbsp;|&nbsp;
                            <b>Status:</b> {'✅ Paid' if existing_inv['paid'] else '⏳ Unpaid'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    allow_overwrite = st.checkbox(
                        "⚠️ Allow Overwrite / Update existing invoice in storage",
                        value=False,
                        key="chk_overwrite_upload",
                        help="Check this if you intentionally want to replace the existing invoice record."
                    )
                else:
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px; padding:10px 16px; margin:10px 0;">
                        <span style="color:#166534; font-weight:600; font-size:13.5px;">✅ New Invoice Verified: <code>#{invoice_no}</code> is ready to be saved!</span>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Action Buttons ───────────────────────────────────
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                btn_c1, btn_c2, btn_c3 = st.columns([5, 2, 2.5])

                with btn_c2:
                    discard = st.button(
                        "🗑️ Discard",
                        use_container_width=True,
                        type="secondary",
                        key="btn_discard_inv"
                    )
                with btn_c3:
                    saving = st.session_state.get("_saving_invoice", False)
                    btn_label = "💾 Update Invoice" if (is_duplicate and allow_overwrite) else ("✅ Accept & Save" if not saving else "⏳ Saving…")
                    can_save = (not is_duplicate) or allow_overwrite

                    accept = st.button(
                        btn_label,
                        use_container_width=True,
                        type="primary",
                        disabled=(not can_save) or saving,
                        key="btn_accept_save_inv"
                    )

                if accept and can_save:
                    st.session_state["_saving_invoice"] = True

                    with st.spinner("Saving invoice to database…"):
                        time.sleep(0.4)
                        database.save_invoice(
                            invoice_no=invoice_no,
                            vendor=vendor,
                            date=str(date_val),
                            due_date=str(due_date_val),
                            subtotal=subtotal,
                            gst=gst_total_val,
                            items=final_items,
                            overwrite=allow_overwrite
                        )

                    st.session_state["_saving_invoice"] = False
                    st.toast("✅ Invoice saved successfully!", icon="🎉")
                    st.success(
                        f"**Invoice {invoice_no}** from **{vendor}** has been saved to permanent storage. "
                        "Inventory and payment records updated."
                    )
                    time.sleep(1.0)
                    st.rerun()

                if discard:
                    st.toast("Invoice discarded.", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

            else:
                # ── Empty state when no file is uploaded ─────────────
                st.markdown('<div style="text-align:center; padding:48px 24px; border:2px dashed #cbd5e1; border-radius:16px; background:#f8fafc; margin:24px 0;"><div style="font-size:48px; margin-bottom:16px;">📤</div><div style="font-size:16px; color:#475569; font-weight:500;">Drop an invoice image or PDF above to get started</div><div style="font-size:13px; color:#94a3b8; margin-top:8px;">Supported formats: PNG, JPG, JPEG, PDF</div></div>', unsafe_allow_html=True)

        # ── METHOD B: MANUAL INVOICE ENTRY ─────────────────────────
        else:
            st.write("Directly enter invoice details to record and store in your business ledger.")
            with st.container(border=True):
                man_inv_no = st.text_input("Invoice Number *", placeholder="e.g. INV-2026-001", key="man_inv_no").strip()

                is_man_dup = database.invoice_exists(man_inv_no) if man_inv_no else False
                if is_man_dup:
                    existing_man = database.get_invoice(man_inv_no)
                    st.markdown(f"""
                    <div style="background:#FEF2F2; border:1.5px solid #f87171; border-radius:12px; padding:12px 16px; margin-bottom:1rem;">
                        <b style="color:#991B1B;">⚠️ Duplicate Invoice Alert:</b>
                        <span style="color:#7F1D1D; font-size:0.92rem;">
                            Invoice <b>#{man_inv_no}</b> already exists (Vendor: {existing_man['vendor']}, Total: ₹{existing_man['total']:,.2f}, Date: {existing_man['date']}).
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                elif man_inv_no:
                    st.success(f"✅ Invoice #{man_inv_no} is available to register.")

                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    man_vendor = st.text_input("Vendor / Merchant Name *", placeholder="e.g. Reliance Supplies", key="man_vendor")
                    man_date = st.date_input("Invoice Date", value=today_val, key="man_date")
                with m_col2:
                    man_due = st.date_input("Due Date", value=default_due_val, key="man_due")
                    man_item_name = st.text_input("Primary Item Description", placeholder="e.g. Cotton Fabrics", key="man_item_name")

                m_col3, m_col4, m_col5 = st.columns(3)
                with m_col3:
                    man_qty = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0, key="man_qty")
                with m_col4:
                    man_rate = st.number_input("Unit Rate (₹)", min_value=0.0, value=500.0, step=50.0, key="man_rate")
                with m_col5:
                    man_gst_pct = st.selectbox("GST Rate (%)", [0, 5, 12, 18, 28], index=3, key="man_gst_pct")

                man_subtotal = man_qty * man_rate
                man_gst = man_subtotal * (man_gst_pct / 100.0)
                man_total = man_subtotal + man_gst

                st.markdown("---")
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Subtotal", f"₹{man_subtotal:,.2f}")
                mc2.metric("GST", f"₹{man_gst:,.2f}")
                mc3.metric("Total Payable", f"₹{man_total:,.2f}")

                man_allow_overwrite = False
                if is_man_dup:
                    man_allow_overwrite = st.checkbox("⚠️ Overwrite existing invoice record", value=False, key="man_overwrite")

                man_can_save = (not is_man_dup) or man_allow_overwrite
                if st.button("💾 Save Invoice to Storage", type="primary", disabled=not man_can_save, key="man_save_btn", use_container_width=True):
                    if not man_inv_no:
                        st.error("Please specify an Invoice Number.")
                    elif not man_vendor:
                        st.error("Please enter a Vendor Name.")
                    else:
                        items_payload = [{
                            "item": man_item_name if man_item_name else "Standard Goods",
                            "qty": man_qty,
                            "rate": man_rate,
                            "gst_percent": man_gst_pct,
                            "amount": man_subtotal
                        }]
                        database.save_invoice(
                            invoice_no=man_inv_no,
                            vendor=man_vendor,
                            date=man_date.isoformat(),
                            due_date=man_due.isoformat(),
                            subtotal=man_subtotal,
                            gst=man_gst,
                            items=items_payload,
                            overwrite=man_allow_overwrite
                        )
                        st.toast("✅ Invoice saved successfully!", icon="🎉")
                        st.success(f"🎉 Invoice **#{man_inv_no}** saved successfully!")
                        st.balloons()
                        time.sleep(1.0)
                        st.rerun()

    # ──────────────────────────────────────────────────────────────
    # TAB 2: INVOICE HISTORY (ALL TIME - REGARDLESS OF TIME DURATION)
    # ──────────────────────────────────────────────────────────────
    with inv_tab2:
        st.markdown("#### 📜 Lifetime Invoice Records & History")
        st.caption("All invoices ever recorded are permanently stored. View, search, filter, and inspect your full invoice history anytime without time expiration.")

        all_invoices = database.get_all_invoices_dicts()

        if not all_invoices:
            st.info("No invoices stored in your database yet. Upload or create your first invoice in the 'Add Invoice' tab!")
        else:
            # ── 1. Lifetime Summary KPI Cards ──────────────────────
            total_count = len(all_invoices)
            total_sum = sum(inv["total"] for inv in all_invoices)
            paid_sum = sum(inv["total"] for inv in all_invoices if inv["paid"])
            pending_sum = total_sum - paid_sum
            paid_count = sum(1 for inv in all_invoices if inv["paid"])
            pending_count = total_count - paid_count

            hk1, hk2, hk3, hk4 = st.columns(4)
            with hk1:
                st.markdown(f"""
                <div style="background:#ffffff; border-radius:14px; padding:1.1rem; border-left:4px solid #6366f1; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                    <div style="color:#64748b; font-size:0.78rem; font-weight:700; text-transform:uppercase;">All-Time Invoices</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0f172a; margin:4px 0;">{total_count}</div>
                    <div style="font-size:0.78rem; color:#6366f1; font-weight:600;">📁 Full Lifetime Storage</div>
                </div>
                """, unsafe_allow_html=True)
            with hk2:
                st.markdown(f"""
                <div style="background:#ffffff; border-radius:14px; padding:1.1rem; border-left:4px solid #0ea5e9; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                    <div style="color:#64748b; font-size:0.78rem; font-weight:700; text-transform:uppercase;">Total Invoiced</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0f172a; margin:4px 0;">₹{total_sum:,.2f}</div>
                    <div style="font-size:0.78rem; color:#0ea5e9; font-weight:600;">💳 Lifetime Invoiced Value</div>
                </div>
                """, unsafe_allow_html=True)
            with hk3:
                st.markdown(f"""
                <div style="background:#ffffff; border-radius:14px; padding:1.1rem; border-left:4px solid #10b981; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                    <div style="color:#64748b; font-size:0.78rem; font-weight:700; text-transform:uppercase;">Total Paid</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0f172a; margin:4px 0;">₹{paid_sum:,.2f}</div>
                    <div style="font-size:0.78rem; color:#10b981; font-weight:600;">✅ {paid_count} Invoices Settled</div>
                </div>
                """, unsafe_allow_html=True)
            with hk4:
                st.markdown(f"""
                <div style="background:#ffffff; border-radius:14px; padding:1.1rem; border-left:4px solid #f43f5e; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                    <div style="color:#64748b; font-size:0.78rem; font-weight:700; text-transform:uppercase;">Total Outstanding</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0f172a; margin:4px 0;">₹{pending_sum:,.2f}</div>
                    <div style="font-size:0.78rem; color:#f43f5e; font-weight:600;">⏳ {pending_count} Pending Invoices</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

            # ── 2. Search & Filter Bar ─────────────────────────────
            with st.container(border=True):
                st.markdown("<b style='color:#0f172a; font-size:0.95rem;'>🔍 Filter & Search History</b>", unsafe_allow_html=True)
                f_col1, f_col2, f_col3, f_col4 = st.columns([2.5, 1.5, 1.8, 1.5])

                with f_col1:
                    hist_search = st.text_input("Search Invoices", placeholder="Type Invoice # or Vendor Name...", key="hist_srch_input")
                with f_col2:
                    hist_status = st.selectbox("Payment Status", ["All Invoices", "Paid Only", "Unpaid / Pending Only", "Overdue Only"], key="hist_status_filter")
                with f_col3:
                    hist_time = st.selectbox(
                        "Time Duration",
                        ["All Time (Complete History)", "This Month", "Last 30 Days", "This Year", "Custom Date Range"],
                        index=0,
                        key="hist_time_filter"
                    )
                with f_col4:
                    hist_sort = st.selectbox(
                        "Sort By",
                        ["Date (Newest First)", "Date (Oldest First)", "Amount (High to Low)", "Amount (Low to High)", "Due Date"],
                        key="hist_sort_filter"
                    )

                custom_start = None
                custom_end = None
                if hist_time == "Custom Date Range":
                    c_dr1, c_dr2 = st.columns(2)
                    with c_dr1:
                        custom_start = st.date_input("From Date", value=today_val - datetime.timedelta(days=90), key="cust_start_dt")
                    with c_dr2:
                        custom_end = st.date_input("To Date", value=today_val, key="cust_end_dt")

            # ── 3. Apply Filters ───────────────────────────────────
            today_str = today_val.isoformat()
            filtered = []

            for inv in all_invoices:
                # Text Search
                if hist_search:
                    kw = hist_search.lower()
                    if kw not in inv["invoice_no"].lower() and kw not in inv["vendor"].lower():
                        continue

                # Status Filter
                if hist_status == "Paid Only" and not inv["paid"]:
                    continue
                elif hist_status == "Unpaid / Pending Only" and inv["paid"]:
                    continue
                elif hist_status == "Overdue Only":
                    if inv["paid"] or not (inv["due_date"] and inv["due_date"] < today_str):
                        continue

                # Time Duration Filter
                inv_date_str = inv["date"]
                if hist_time == "This Month":
                    if not inv_date_str.startswith(today_str[:7]):
                        continue
                elif hist_time == "Last 30 Days":
                    limit_30 = (today_val - datetime.timedelta(days=30)).isoformat()
                    if inv_date_str < limit_30 or inv_date_str > today_str:
                        continue
                elif hist_time == "This Year":
                    if not inv_date_str.startswith(today_str[:4]):
                        continue
                elif hist_time == "Custom Date Range" and custom_start and custom_end:
                    if inv_date_str < custom_start.isoformat() or inv_date_str > custom_end.isoformat():
                        continue

                filtered.append(inv)

            # Sorting
            if hist_sort == "Date (Newest First)":
                filtered.sort(key=lambda x: (x["date"], x["invoice_no"]), reverse=True)
            elif hist_sort == "Date (Oldest First)":
                filtered.sort(key=lambda x: (x["date"], x["invoice_no"]))
            elif hist_sort == "Amount (High to Low)":
                filtered.sort(key=lambda x: x["total"], reverse=True)
            elif hist_sort == "Amount (Low to High)":
                filtered.sort(key=lambda x: x["total"])
            elif hist_sort == "Due Date":
                filtered.sort(key=lambda x: x["due_date"])

            st.markdown(f"<p style='color:#475569; font-weight:600; font-size:0.92rem; margin:0.8rem 0 0.5rem 0;'>Showing <b>{len(filtered)}</b> invoice(s) matching your criteria:</p>", unsafe_allow_html=True)

            if not filtered:
                st.warning("No invoices found for the selected filter combination.")
            else:
                # ── 4. Main Overview Table ─────────────────────────
                df_rows = []
                for inv in filtered:
                    is_overdue = (not inv["paid"]) and inv["due_date"] and (inv["due_date"] < today_str)
                    status_badge = "✅ Paid" if inv["paid"] else ("🚨 Overdue" if is_overdue else "⏳ Pending")
                    df_rows.append({
                        "Invoice #": inv["invoice_no"],
                        "Vendor": inv["vendor"],
                        "Date": inv["date"],
                        "Due Date": inv["due_date"],
                        "Subtotal (₹)": f"₹{inv['subtotal']:,.2f}",
                        "GST (₹)": f"₹{inv['gst']:,.2f}",
                        "Total Amount (₹)": f"₹{inv['total']:,.2f}",
                        "Payment Status": status_badge,
                    })

                df_table = pd.DataFrame(df_rows)
                st.dataframe(df_table, use_container_width=True, hide_index=True)

                # Export CSV button
                csv_export = df_table.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Export Invoice History (CSV)",
                    data=csv_export,
                    file_name=f"invoices_history_{today_str}.csv",
                    mime="text/csv",
                    key="btn_export_invoices_csv"
                )

                st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
                st.markdown("#### 🔍 Detailed Invoice Inspector & Actions")

                for inv in filtered:
                    inv_no = inv["invoice_no"]
                    is_overdue = (not inv["paid"]) and inv["due_date"] and (inv["due_date"] < today_str)
                    status_badge = "✅ Paid" if inv["paid"] else ("🚨 Overdue" if is_overdue else "⏳ Pending")

                    with st.expander(f"🧾 #{inv_no} — {inv['vendor']}  |  ₹{inv['total']:,.2f}  |  {status_badge}"):
                        d_col1, d_col2, d_col3 = st.columns([2, 2, 1.8])

                        with d_col1:
                            st.markdown(f"**Invoice Number:** `{inv_no}`")
                            st.markdown(f"**Vendor / Merchant:** {inv['vendor']}")
                            st.markdown(f"**Invoice Date:** {inv['date']}")
                            st.markdown(f"**Payment Due Date:** {inv['due_date']}")

                        with d_col2:
                            st.markdown(f"**Subtotal:** ₹{inv['subtotal']:,.2f}")
                            st.markdown(f"**GST:** ₹{inv['gst']:,.2f}")
                            st.markdown(f"**Grand Total:** ₹{inv['total']:,.2f}")
                            st.markdown(f"**Current Status:** {status_badge}")

                        with d_col3:
                            st.markdown("**Quick Actions:**")
                            if not inv["paid"]:
                                if st.button("✅ Mark as Paid", key=f"hist_pay_{inv_no}", use_container_width=True):
                                    database.mark_paid(inv_no, 1)
                                    st.success(f"Invoice #{inv_no} marked as Paid!")
                                    st.rerun()
                            else:
                                if st.button("↩️ Revert to Unpaid", key=f"hist_unpay_{inv_no}", use_container_width=True):
                                    database.mark_paid(inv_no, 0)
                                    st.info(f"Invoice #{inv_no} reverted to Unpaid.")
                                    st.rerun()

                            if st.button("🗑️ Delete Invoice", key=f"hist_del_{inv_no}", use_container_width=True):
                                database.delete_invoice(inv_no)
                                st.warning(f"Invoice #{inv_no} has been deleted.")
                                st.rerun()

                        # Line items for this invoice
                        line_items = database.get_invoice_items(inv_no)
                        if line_items:
                            st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#334155; margin-top:0.6rem;'>Itemized Breakdown:</p>", unsafe_allow_html=True)
                            item_rows = []
                            for it in line_items:
                                item_rows.append({
                                    "Item": it["item"],
                                    "Qty": it["qty"],
                                    "Rate (₹)": f"₹{it['rate']:,.2f}",
                                    "GST %": f"{it['gst_percent']:.0f}%",
                                    "Total (₹)": f"₹{it['amount']:,.2f}"
                                })
                            st.dataframe(pd.DataFrame(item_rows), use_container_width=True, hide_index=True)
                        else:
                            st.caption("No specific line items recorded for this invoice.")

    # ──────────────────────────────────────────────────────────────
    # TAB 3: PAYMENTS TRACKER (Merged with Teammate's Quick Row View)
    # ──────────────────────────────────────────────────────────────
    with inv_tab3:
        st.markdown("#### 💰 Payment Schedule & Settlement")
        st.write("All payments recorded from database.")

        summary = database.get_payment_summary()
        today_str = datetime.date.today().isoformat()

        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.metric("Total Settled (Paid)", f"₹{summary['paid_amount']:,.2f}", f"{summary['paid_count']} paid invoices")
        with pc2:
            st.metric("Upcoming Pending Dues", f"₹{summary['pending_amount']:,.2f}", f"{summary['pending_count']} pending")
        with pc3:
            st.metric("Overdue Bills", f"₹{summary['overdue_amount']:,.2f}", f"{summary['overdue_count']} overdue", delta_color="inverse")

        st.markdown("---")

        pay_rows = database.get_invoices()
        if not pay_rows:
            st.info("No invoices yet. Save one from the Add Invoice tab first.")
        else:
            for inv_no, ven, d, due, sub_val, gst_val, total, paid in pay_rows:
                if paid:
                    pay_status = "✅ Paid"
                elif due and due < today_str:
                    pay_status = "🔴 Overdue"
                else:
                    pay_status = "🟡 Pending"

                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3.5, 2, 2.5, 2])
                    with c1:
                        st.markdown(f"**{ven}** (`{inv_no}`)")
                    with c2:
                        st.caption(f"Due: {due}")
                    with c3:
                        st.markdown(f"**₹{total:,.2f}** &nbsp; {pay_status}")
                    with c4:
                        if not paid:
                            if st.button("Mark paid ✅", key=f"pay_tab_{inv_no}", use_container_width=True):
                                database.mark_paid(inv_no, 1)
                                st.toast(f"Marked #{inv_no} as paid!", icon="✅")
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            st.caption("Settled")


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
