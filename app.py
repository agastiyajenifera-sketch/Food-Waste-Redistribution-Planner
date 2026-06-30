import os, base64
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils import (
    FOOD_CATEGORIES, FOOD_UNITS, validate_email, validate_phone, hash_password,
    haversine_distance, extract_coords_from_text, predict_expiry_risk, get_food_waste_insights,
    initialize_session_state, save_users_to_csv, save_ngos_to_csv, save_donations_to_csv,
    save_requests_to_csv, save_notifications_to_csv, CSV_FILES
)

st.set_page_config(page_title="Food Waste Redistribution Planner", layout="wide", initial_sidebar_state="expanded")

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        .metric-card { padding: 1.5rem; border-radius: 12px; text-align: center; border-width: 2px; border-style: solid; margin-bottom: 1rem; }
        .metric-value { font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 0.4rem; }
        .metric-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 700; line-height: 1; text-align: center; border-radius: 50px; }
        .badge-high { background-color: #fee2e2; color: #ef4444; }
        .badge-medium { background-color: #fef3c7; color: #d97706; }
        .badge-low { background-color: #d1fae5; color: #059669; }
        .badge-expired { background-color: #e5e7eb; color: #4b5563; }
        .badge-pending { background-color: #fef3c7; color: #d97706; }
        .badge-approved { background-color: #d1fae5; color: #059669; }
        .badge-rejected { background-color: #fee2e2; color: #ef4444; }
        .badge-requested { background-color: #dbeafe; color: #1e40af; }
        .badge-collected { background-color: #f3e8ff; color: #7e22ce; }
        h1, h2, h3 { font-weight: 700; text-transform: uppercase; }
        .dir-card-hover { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
        .dir-card-hover:hover { transform: translateY(-4px); box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.4); border-color: #ff6b6b !important; }
        </style>
    """, unsafe_allow_html=True)

initialize_session_state()
apply_custom_css()

IMAGES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def apply_login_background_css():
    banner_path = os.path.join(IMAGES_DIR, "indian_food_bg.jpg")
    b64_str = get_base64_image(banner_path)
    css_content = f"""
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(10, 15, 30, 0.82), rgba(10, 15, 30, 0.9)), url("data:image/jpeg;base64,{b64_str}");
        background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
    }}""" if b64_str else ""
    st.markdown(f"""
        <style>
        {css_content}
        div[data-testid="stVerticalBlockBorder"] {{
            background: rgba(17, 24, 39, 0.75) !important; backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 20px !important;
            padding: 2.5rem !important; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
        }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: rgba(31, 41, 55, 0.8) !important; border: 1px solid rgba(75, 85, 99, 0.5) !important; color: #ffffff !important;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(17, 24, 39, 0.95) !important; border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }}
        </style>
    """, unsafe_allow_html=True)

if st.session_state.current_user is None:
    sidebar_mode = st.sidebar.selectbox("PORTAL ACTIONS", ["Sign In", "Sign Up"])
else:
    user = st.session_state.current_user
    st.sidebar.markdown(f"### 👤 {user['full_name'].upper()}\n**Role**: `{user['role']}`")
    unread_c = sum(1 for n in st.session_state.notifications if n["user_id"] == user["id"] and n["status"] == "Unread")
    notif_label = f"Notifications ({unread_c})" if unread_c > 0 else "Notifications"
    if user["role"] == "Admin":
        sidebar_mode = st.sidebar.radio("ADMIN NAVIGATION", ["Overview", "Donation Audit", "User Manager", "Visual Analytics", "Generate Reports"])
    elif user["role"] == "Donor":
        sidebar_mode = st.sidebar.radio("DONOR NAVIGATION", ["My Donations", "Donate Food", notif_label])
    elif user["role"] == "NGO":
        sidebar_mode = st.sidebar.radio("NGO NAVIGATION", ["Browse Catalog", "My Collection Claims", notif_label])
    st.sidebar.markdown("---")
    if st.sidebar.button("LOG OUT", type="secondary", use_container_width=True):
        st.session_state.current_user = None
        st.rerun()

def show_login_view():
    apply_login_background_css()
    _, col_c, _ = st.columns([1, 1.2, 1])
    with col_c:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #ff6b6b; margin-bottom: 0.2rem; font-size: 2.2rem;'>🥗 FOOD SHARE</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.85rem; font-style: italic; margin-bottom: 1.5rem;'>Connecting Surplus Food with Local Communities</p>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #ffffff; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.2rem;'>SIGN IN</h3>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email")
            show_pass = st.checkbox("Show password", key="login_show_pass")
            password = st.text_input("Password", type="default" if show_pass else "password", key="login_password")
            if st.button("SIGN IN 🔑", type="primary", use_container_width=True):
                email_clean, pass_clean = email.strip(), password.strip()
                if not email_clean or not pass_clean:
                    st.error("Please fill in all input fields.")
                    return
                hashed = hash_password(pass_clean)
                matched = next((u for u in st.session_state.users if u["email"].lower() == email_clean.lower() and u["password"] == hashed), None)
                if matched:
                    st.session_state.current_user = matched
                    st.success(f"Welcome back, {matched['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password credentials.")

def show_register_view():
    apply_login_background_css()
    _, col_c, _ = st.columns([1, 1.4, 1])
    with col_c:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #ff6b6b; margin-bottom: 0.2rem; font-size: 2.2rem;'>🥗 FOODSHARE</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #ffffff; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.2rem;'>JOIN FOODSHARE</h3>", unsafe_allow_html=True)
            full_name = st.text_input("Full Name / Authorized Person")
            email = st.text_input("Email Address")
            show_pass = st.checkbox("Show password", key="reg_show_pass")
            password = st.text_input("Password", type="default" if show_pass else "password")
            phone = st.text_input("Contact Phone Number")
            address = st.text_input("Address (include coordinates: e.g. downtown (12.97, 77.59))")
            role = st.selectbox("Account Role", ["Donor", "NGO", "Admin"])
            ngo_org_name, ngo_reg_num = "", ""
            if role == "NGO":
                st.markdown("### NGO Details")
                ngo_org_name = st.text_input("Organization Official Name")
                ngo_reg_num = st.text_input("Government Registration Number")
            if st.button("CREATE ACCOUNT 🚀", type="primary", use_container_width=True):
                fn, em, pas, ph, addr = full_name.strip(), email.strip(), password.strip(), phone.strip(), address.strip()
                if not all([fn, em, pas, ph, addr]) or (role == "NGO" and not all([ngo_org_name.strip(), ngo_reg_num.strip()])):
                    st.error("Please fill all required fields.")
                    return
                if not validate_email(em) or len(pas) < 6 or not validate_phone(ph):
                    st.error("Validation failed. Check details.")
                    return
                if any(u["email"].lower() == em.lower() for u in st.session_state.users):
                    st.error("Email address already registered.")
                    return
                new_id = max(u["id"] for u in st.session_state.users) + 1
                new_user = {"id": new_id, "full_name": fn, "email": em, "password": hash_password(pas), "phone": ph, "address": addr, "role": role, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                st.session_state.users.append(new_user)
                save_users_to_csv()
                if role == "NGO":
                    st.session_state.ngos.append({"id": max(n["id"] for n in st.session_state.ngos) + 1, "user_id": new_id, "organization_name": ngo_org_name.strip(), "registration_number": ngo_reg_num.strip(), "location": addr, "phone": ph, "email": em})
                    save_ngos_to_csv()
                st.session_state.current_user = new_user
                st.success("Account successfully created!")
                st.rerun()

def show_donation_thumbnail(d):
    img_path = os.path.join(IMAGES_DIR, d.get("image") or "")
    if d.get("image") and os.path.isfile(img_path): st.image(img_path, use_container_width=True)
    else: st.markdown("<div style='background-color:#374151;height:120px;border-radius:8px;display:flex;align-items:center;justify-content:center;color:gray;'>🖼️ No Image</div>", unsafe_allow_html=True)

def show_admin_overview():
    st.markdown("<h2>Welcome Back, Admin Console</h2>", unsafe_allow_html=True)
    stats = [
        ("👥 Total Donors", sum(1 for u in st.session_state.users if u["role"] == "Donor"), "#0284c7", "#e0f2fe"),
        ("🤝 NGO Partners", sum(1 for u in st.session_state.users if u["role"] == "NGO"), "#7c3aed", "#f3e8ff"),
        ("🍎 Active Listed", sum(1 for d in st.session_state.donations if d["status"] == "Approved"), "#059669", "#d1fae5"),
        ("📦 Rescued Food", sum(1 for r in st.session_state.requests if r["status"] == "Completed"), "#db2777", "#fce7f3")
    ]
    cols = st.columns(4)
    for col, (title, val, border, bg) in zip(cols, stats):
        with col: st.markdown(f"<div class='metric-card' style='border-color:{border}; background-color:{bg}; color:#1e293b;'><div class='metric-value'>{val}</div><div class='metric-title'>{title}</div></div>", unsafe_allow_html=True)

def show_admin_audit():
    st.markdown("<h2>Donation Approval Audit</h2>", unsafe_allow_html=True)
    pending = [d for d in st.session_state.donations if d["status"] == "Pending"]
    if not pending:
        st.info("All listings have been audited. No pending donations.")
        return
    for d in pending:
        with st.container(border=True):
            col1, col2 = st.columns([1.5, 3.5])
            with col1: show_donation_thumbnail(d)
            with col2:
                st.markdown(f"### **{d['food_name'].upper()}**")
                st.write(f"Category: {d['category']} | Qty: {d['quantity']} {d['unit']} | Type: {d['cooked_or_packaged']} | Expires: {d['expiry_time']}")
                c1, c2 = st.columns(2)
                if c1.button("APPROVE ✅", key=f"app_{d['id']}", type="primary", use_container_width=True):
                    d["status"] = "Approved"
                    save_donations_to_csv()
                    st.success("Donation approved.")
                    st.rerun()
                if c2.button("REJECT ❌", key=f"rej_{d['id']}", type="secondary", use_container_width=True):
                    d["status"] = "Rejected"
                    st.session_state.notifications.append({"id": max(n["id"] for n in st.session_state.notifications) + 1, "user_id": d["donor_id"], "title": "Donation Rejected", "message": f"Your donation posting for '{d['food_name']}' was rejected during audit.", "status": "Unread", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    save_donations_to_csv()
                    save_notifications_to_csv()
                    st.warning("Donation rejected.")
                    st.rerun()

def show_admin_users():
    st.markdown("<h2>Platform User Directory</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🍎 FOOD DONORS", "🤝 NGO PARTNERS"])
    with tab1:
        search_donor = st.text_input("🔍 Search Food Donors...", key="search_donor").strip().lower()
        donors = [u for u in st.session_state.users if u["role"] == "Donor" and u["id"] != st.session_state.current_user["id"]]
        if search_donor: donors = [u for u in donors if search_donor in u["full_name"].lower() or search_donor in u["email"].lower() or search_donor in u["address"].lower()]
        for idx in range(0, len(donors), 2):
            cols = st.columns(2)
            for col_idx in range(2):
                if idx + col_idx < len(donors):
                    u = donors[idx + col_idx]
                    with cols[col_idx]:
                        donor_dons = [d for d in st.session_state.donations if d["donor_id"] == u["id"]]
                        total_l, active_l, rescued_l = len(donor_dons), sum(1 for d in donor_dons if d["status"] == "Approved"), sum(1 for d in donor_dons if d["status"] == "Collected")
                        n_l = u["full_name"].lower()
                        av_emoji = "🏨" if "hotel" in n_l or "restaurant" in n_l or "kitchen" in n_l else ("🛒" if "market" in n_l or "store" in n_l or "fresh" in n_l else "🍎")
                        av_grad = "linear-gradient(135deg, #ff6b6b, #ee5253)" if av_emoji == "🏨" else ("linear-gradient(135deg, #f59e0b, #d97706)" if av_emoji == "🛒" else "linear-gradient(135deg, #ec4899, #db2777)")
                        card_html = f"<div class='dir-card-hover' style='background:linear-gradient(135deg,#111827,#1f2937);border:2px solid #374151;border-radius:16px;padding:1.5rem;color:#f3f4f6;margin-bottom:1rem;box-shadow:0 4px 6px rgba(0,0,0,0.1);'><div style='display:flex;align-items:center;gap:1rem;margin-bottom:1rem;'><div style='width:55px;height:55px;border-radius:50%;background:{av_grad};display:flex;align-items:center;justify-content:center;font-size:1.8rem;'>{av_emoji}</div><div><h4 style='margin:0;font-size:1.2rem;font-weight:700;'>{u['full_name'].upper()}</h4><span style='font-size:0.7rem;background-color:#3b82f6;color:white;padding:0.1rem 0.4rem;border-radius:50px;font-weight:bold;'>DONOR</span></div></div><div style='display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin:1rem 0;text-align:center;'><div style='background-color:#111827;border:1px solid #374151;border-radius:8px;padding:0.4rem;'><div style='font-size:1.2rem;font-weight:bold;color:#ff6b6b;'>{total_l}</div><div style='font-size:0.6rem;color:#9ca3af;'>Listings</div></div><div style='background-color:#111827;border:1px solid #374151;border-radius:8px;padding:0.4rem;'><div style='font-size:1.2rem;font-weight:bold;color:#3b82f6;'>{active_l}</div><div style='font-size:0.6rem;color:#9ca3af;'>Active</div></div><div style='background-color:#111827;border:1px solid #374151;border-radius:8px;padding:0.4rem;'><div style='font-size:1.2rem;font-weight:bold;color:#10b981;'>{rescued_l}</div><div style='font-size:0.6rem;color:#9ca3af;'>Rescued</div></div></div><div style='font-size:0.8rem;color:#d1d5db;line-height:1.5;margin-bottom:1rem;'><div>📧 <strong>Email:</strong> {u['email']}</div><div>📞 <strong>Phone:</strong> {u['phone']}</div><div>📍 <strong>Address:</strong> {u['address']}</div></div></div>"
                        with st.container(border=True):
                            st.markdown(card_html, unsafe_allow_html=True)
                            if st.button("DELETE DONOR 🗑️", key=f"del_d_{u['id']}", type="secondary", use_container_width=True):
                                st.session_state.users.remove(u)
                                st.session_state.donations = [d for d in st.session_state.donations if d["donor_id"] != u["id"]]
                                save_users_to_csv(); save_donations_to_csv()
                                st.success(f"Donor {u['full_name']} deleted.")
                                st.rerun()
    with tab2:
        search_ngo = st.text_input("🔍 Search NGO Partners...", key="search_ngo").strip().lower()
        ngos = [u for u in st.session_state.users if u["role"] == "NGO" and u["id"] != st.session_state.current_user["id"]]
        if search_ngo:
            ngo_ids = [n["user_id"] for n in st.session_state.ngos if search_ngo in n["organization_name"].lower() or search_ngo in n["registration_number"].lower()]
            ngos = [u for u in ngos if search_ngo in u["full_name"].lower() or search_ngo in u["email"].lower() or u["id"] in ngo_ids]
        for idx in range(0, len(ngos), 2):
            cols = st.columns(2)
            for col_idx in range(2):
                if idx + col_idx < len(ngos):
                    u = ngos[idx + col_idx]
                    with cols[col_idx]:
                        ngo_p = next((n for n in st.session_state.ngos if n["user_id"] == u["id"]), None)
                        org_name = ngo_p["organization_name"] if ngo_p else "Unknown NGO"
                        reg_num = ngo_p["registration_number"] if ngo_p else "N/A"
                        ngo_id = ngo_p["id"] if ngo_p else 0
                        ngo_reqs = [r for r in st.session_state.requests if r["ngo_id"] == ngo_id]
                        total_c, active_c, rescued_c = len(ngo_reqs), sum(1 for r in ngo_reqs if r["status"] == "Approved"), sum(1 for r in ngo_reqs if r["status"] == "Completed")
                        card_html = f"<div class='dir-card-hover' style='background:linear-gradient(135deg,#111827,#1f2937);border:2px solid #374151;border-radius:16px;padding:1.5rem;color:#f3f4f6;margin-bottom:1rem;box-shadow:0 4px 6px rgba(0,0,0,0.1);'><div style='display:flex;align-items:center;gap:1rem;margin-bottom:1rem;'><div style='width:55px;height:55px;border-radius:50%;background:linear-gradient(135deg,#10b981,#059669);display:flex;align-items:center;justify-content:center;font-size:1.8rem;'>🤝</div><div><h4 style='margin:0;font-size:1.2rem;font-weight:700;'>{org_name.upper()}</h4><span style='font-size:0.7rem;background-color:#10b981;color:white;padding:0.1rem 0.4rem;border-radius:50px;font-weight:bold;'>NGO PARTNER</span></div></div><div style='display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin:1rem 0;text-align:center;'><div style='background-color:#111827;border:1px solid #374151;border-radius:8px;padding:0.4rem;'><div style='font-size:1.2rem;font-weight:bold;color:#ff6b6b;'>{total_c}</div><div style='font-size:0.6rem;color:#9ca3af;'>Claims</div></div><div style='background-color:#111827;border:1px solid #374151;border-radius:8px;padding:0.4rem;'><div style='font-size:1.2rem;font-weight:bold;color:#3b82f6;'>{active_c}</div><div style='font-size:0.6rem;color:#9ca3af;'>Active</div></div><div style='background-color:#111827;border:1px solid #374151;border-radius:8px;padding:0.4rem;'><div style='font-size:1.2rem;font-weight:bold;color:#10b981;'>{rescued_c}</div><div style='font-size:0.6rem;color:#9ca3af;'>Rescued</div></div></div><div style='font-size:0.8rem;color:#d1d5db;line-height:1.5;margin-bottom:1rem;'><div>📜 <strong>Reg:</strong> <code>{reg_num}</code></div><div>👤 <strong>Representative:</strong> {u['full_name']}</div><div>📧 <strong>Email:</strong> {u['email']}</div><div>📞 <strong>Phone:</strong> {u['phone']}</div><div>📍 <strong>Address:</strong> {u['address']}</div></div></div>"
                        with st.container(border=True):
                            st.markdown(card_html, unsafe_allow_html=True)
                            if st.button("DELETE NGO 🗑️", key=f"del_n_{u['id']}", type="secondary", use_container_width=True):
                                st.session_state.users.remove(u)
                                st.session_state.ngos = [n for n in st.session_state.ngos if n["user_id"] != u["id"]]
                                save_users_to_csv(); save_ngos_to_csv()
                                st.success(f"NGO {org_name} deleted.")
                                st.rerun()

def show_admin_analytics():
    st.markdown("<h2>Visual Analytics Dashboard</h2>", unsafe_allow_html=True)
    dons = st.session_state.donations
    if not dons:
        st.info("No donation data to display analytics.")
        return
    df = pd.DataFrame(dons)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Category Share")
        fig, ax = plt.subplots(figsize=(4, 3))
        df["category"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax, colors=["#ff6b6b", "#4db8ff", "#10b981", "#f59e0b", "#8b5cf6"])
        ax.set_ylabel("")
        plt.tight_layout(); st.pyplot(fig)
    with col2:
        st.markdown("### Status Tracking")
        fig, ax = plt.subplots(figsize=(4, 3))
        df["status"].value_counts().plot(kind="bar", ax=ax, color="#3b82f6")
        ax.set_ylabel("Count")
        plt.tight_layout(); st.pyplot(fig)
    st.markdown("### Artificial Intelligence Insights")
    for insight in get_food_waste_insights():
        st.info(insight)

def show_admin_reports():
    st.markdown("<h2>Generate System Reports</h2>", unsafe_allow_html=True)
    st.write("Download summaries of all system tables.")
    for name in CSV_FILES:
        path, _ = CSV_FILES[name]
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(f"📥 Download {name.upper()} CSV", f.read(), file_name=f"{name}_export.csv", mime="text/csv", use_container_width=True)

def show_donor_my_donations():
    st.markdown("<h2>My Food Donations</h2>", unsafe_allow_html=True)
    my_dons = [d for d in st.session_state.donations if d["donor_id"] == st.session_state.current_user["id"]]
    if not my_dons:
        st.info("You haven't listed any food donations yet.")
        return
    for d in my_dons:
        with st.container(border=True):
            col1, col2 = st.columns([1.5, 3.5])
            with col1: show_donation_thumbnail(d)
            with col2:
                risk = predict_expiry_risk(d["category"], d["expiry_time"])
                st.write(f"🍏 **{d['food_name'].upper()}** ({d['category']}) | Risk: `{risk}`")
                st.write(f"Qty: {d['quantity']} {d['unit']} | Status: `{d['status']}` | Expires: {d['expiry_time']}")
                if d["status"] in ["Pending", "Approved"] and st.button("Cancel Donation ❌", key=f"can_{d['id']}"):
                    d["status"] = "Cancelled"
                    save_donations_to_csv()
                    st.success("Donation cancelled.")
                    st.rerun()

def show_donor_donate_food():
    st.markdown("<h2>Register Surplus Food Donation</h2>", unsafe_allow_html=True)
    with st.form("donate_form", clear_on_submit=True):
        name = st.text_input("Food Item Name")
        cat = st.selectbox("Category", FOOD_CATEGORIES)
        col1, col2 = st.columns(2)
        qty = col1.number_input("Quantity", min_value=0.1, step=0.1)
        unit = col2.selectbox("Unit", FOOD_UNITS)
        col3, col4 = st.columns(2)
        type_food = col3.selectbox("Type", ["Cooked", "Packaged", "Fresh"])
        exp_hours = col4.slider("Hours Until Expiry", 1, 168, 24)
        addr = st.text_input("Pickup Address", value=st.session_state.current_user["address"])
        if st.form_submit_button("POST DONATION"):
            if not name.strip():
                st.error("Please specify a food name.")
                return
            lat, lon = extract_coords_from_text(addr)
            new_id = max((d["id"] for d in st.session_state.donations), default=0) + 1
            exp_time = (datetime.now() + timedelta(hours=exp_hours)).strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.donations.append({
                "id": new_id, "donor_id": st.session_state.current_user["id"], "food_name": name.strip(),
                "category": cat, "quantity": qty, "unit": unit, "cooked_or_packaged": type_food,
                "expiry_time": exp_time, "pickup_address": addr, "latitude": lat, "longitude": lon,
                "status": "Pending", "image": "", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            for u in st.session_state.users:
                if u["role"] == "Admin":
                    st.session_state.notifications.append({"id": max(n["id"] for n in st.session_state.notifications) + 1, "user_id": u["id"], "title": "Donation Pending Audit", "message": f"'{name.strip()}' requires approval.", "status": "Unread", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_donations_to_csv(); save_notifications_to_csv()
            st.success("Donation submitted for audit approval.")

def show_ngo_browse():
    st.markdown("<h2>Surplus Food Catalog</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    search_query = col1.text_input("🔍 Search food postings...").strip().lower()
    category_filter = col2.selectbox("Category Filter", ["All Categories"] + FOOD_CATEGORIES)
    sort_method = col3.selectbox("Sort Order", ["Soonest Expiry First", "Largest Quantity First", "Closest Distance First"])
    ngo_p = next((n for n in st.session_state.ngos if n["user_id"] == st.session_state.current_user["id"]), None)
    ngo_lat, ngo_lon = extract_coords_from_text(ngo_p["location"] if ngo_p else "")
    ngo_lat, ngo_lon = ngo_lat or 12.9715, ngo_lon or 77.5946
    approved = []
    for d in st.session_state.donations:
        if d["status"] != "Approved" or (search_query and search_query not in d["food_name"].lower()) or (category_filter != "All Categories" and d["category"] != category_filter):
            continue
        dist = haversine_distance(ngo_lat, ngo_lon, d["latitude"], d["longitude"])
        d["distance_km"] = dist if dist != float("inf") else 999.0
        d["expiry_risk"] = predict_expiry_risk(d["category"], d["expiry_time"])
        approved.append(d)
    if sort_method == "Soonest Expiry First": approved.sort(key=lambda x: x["expiry_time"])
    elif sort_method == "Largest Quantity First": approved.sort(key=lambda x: x["quantity"], reverse=True)
    elif sort_method == "Closest Distance First": approved.sort(key=lambda x: x["distance_km"])
    if not approved:
        st.info("No active surplus food postings found.")
        return
    for i in range(0, len(approved), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j < len(approved):
                item = approved[i + j]
                with row_cols[j]:
                    with st.container(border=True):
                        col1, col2 = st.columns([1.5, 3.5])
                        with col1: show_donation_thumbnail(item)
                        with col2:
                            st.markdown(f"### **{item['food_name'].upper()}**")
                            st.write(f"Category: {item['category']} | Qty: {item['quantity']} {item['unit']}")
                            st.write(f"📍 {round(item['distance_km'], 1)} km away | Risk: `{item['expiry_risk']}`")
                            if st.button("CLAIM COLLECTION 🍲", key=f"claim_btn_{item['id']}", type="primary", use_container_width=True):
                                item["status"] = "Requested"
                                ngo_id = ngo_p["id"] if ngo_p else 1
                                org_name = ngo_p["organization_name"] if ngo_p else "Hope Food"
                                st.session_state.requests.append({"id": max(r["id"] for r in st.session_state.requests) + 1, "donation_id": item["id"], "ngo_id": ngo_id, "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "Approved", "pickup_time": None})
                                st.session_state.notifications.append({"id": max(n["id"] for n in st.session_state.notifications) + 1, "user_id": item["donor_id"], "title": "Donation Claimed by NGO", "message": f"NGO '{org_name}' requested '{item['food_name']}'.", "status": "Unread", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                                save_donations_to_csv(); save_requests_to_csv(); save_notifications_to_csv()
                                st.success("Claimed successfully!")
                                st.rerun()

def show_ngo_claims():
    st.markdown("<h2>My Claims Directory</h2>", unsafe_allow_html=True)
    ngo_p = next((n for n in st.session_state.ngos if n["user_id"] == st.session_state.current_user["id"]), None)
    ngo_id = ngo_p["id"] if ngo_p else 1
    my_reqs = [r for r in st.session_state.requests if r["ngo_id"] == ngo_id]
    if not my_reqs:
        st.write("You have not claimed any collections yet.")
        return
    for r in my_reqs:
        d = next((item for item in st.session_state.donations if item["id"] == r["donation_id"]), None)
        if not d: continue
        donor = next((u for u in st.session_state.users if u["id"] == d["donor_id"]), None)
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### **{d['food_name'].upper()}**")
                st.write(f"Donor: {donor['full_name'] if donor else 'Unknown'} | Contact: {donor['phone'] if donor else 'N/A'}")
                st.write(f"Address: {d['pickup_address']} | Claim Status: `{r['status']}`")
            with col2:
                if r["status"] == "Approved":
                    if st.button("Mark Picked Up ✔", key=f"comp_{r['id']}", type="primary", use_container_width=True):
                        r["status"], d["status"], r["pickup_time"] = "Completed", "Collected", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.notifications.append({"id": max(n["id"] for n in st.session_state.notifications) + 1, "user_id": d["donor_id"], "title": "Donation Collected", "message": f"NGO confirmed collection of '{d['food_name']}'.", "status": "Unread", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        save_donations_to_csv(); save_requests_to_csv(); save_notifications_to_csv()
                        st.success("Redistribution complete!")
                        st.rerun()
                else: st.write(f"*Completed on: {r['pickup_time']}*")

def show_notifications_view():
    st.markdown("<h2>My Notifications Console</h2>", unsafe_allow_html=True)
    my_notifs = [n for n in st.session_state.notifications if n["user_id"] == st.session_state.current_user["id"]]
    if st.button("MARK ALL READ"):
        for n in my_notifs: n["status"] = "Read"
        save_notifications_to_csv(); st.success("All marked read."); st.rerun()
    if not my_notifs:
        st.write("No notifications listed.")
        return
    for n in sorted(my_notifs, key=lambda x: x["id"], reverse=True):
        with st.container(border=True):
            st.markdown(f"#### **{n['title'].upper()}**")
            st.write(f"{n['message']}\n\n*Received: {n['created_at']}*")
            if n["status"] == "Unread":
                n["status"] = "Read"
                save_notifications_to_csv()

if st.session_state.current_user is None:
    if sidebar_mode == "Sign In": show_login_view()
    else: show_register_view()
else:
    if sidebar_mode == "Overview": show_admin_overview()
    elif sidebar_mode == "Donation Audit": show_admin_audit()
    elif sidebar_mode == "User Manager": show_admin_users()
    elif sidebar_mode == "Visual Analytics": show_admin_analytics()
    elif sidebar_mode == "Generate Reports": show_admin_reports()
    elif sidebar_mode == "My Donations" or sidebar_mode == "Donate Food":
        if sidebar_mode == "Donate Food": show_donor_donate_food()
        else: show_donor_my_donations()
    elif sidebar_mode == "Browse Catalog": show_ngo_browse()
    elif sidebar_mode == "My Collection Claims": show_ngo_claims()
    elif "Notifications" in sidebar_mode: show_notifications_view()
