import re, hashlib, math, os, csv
from datetime import datetime, timedelta
import streamlit as st

FOOD_CATEGORIES = ["Cooked Food", "Packaged Food", "Fresh Produce", "Bakery Items", "Dairy Products", "Beverages", "Canned Goods"]
FOOD_UNITS = ["kg", "g", "pieces", "packets", "liters", "servings"]

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def validate_phone(phone):
    return len(re.sub(r'\D', '', phone)) >= 10

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def parse_datetime(dt_str):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try: return datetime.strptime(dt_str, fmt)
        except ValueError: pass
    return None

def haversine_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2): return float('inf')
    r1, o1, r2, o2 = map(math.radians, [lat1, lon1, lat2, lon2])
    a = math.sin((r2-r1)/2)**2 + math.cos(r1)*math.cos(r2)*math.sin((o2-o1)/2)**2
    return 6371.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def extract_coords_from_text(text):
    m = re.search(r'\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)', text or "")
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)

def predict_expiry_risk(cat, exp_str):
    exp = parse_datetime(exp_str)
    if not exp: return "Unknown"
    rem = (exp - datetime.now()).total_seconds() / 3600.0
    if rem <= 0: return "Expired"
    h_lim, m_lim = (8, 18) if cat in ["Cooked Food", "Dairy Products", "Bakery Items"] else ((12, 30) if cat in ["Fresh Produce", "Beverages"] else (24, 72))
    return "High" if rem < h_lim else ("Medium" if rem < m_lim else "Low")

def get_food_waste_insights():
    dons, reqs = st.session_state.donations, st.session_state.requests
    if not dons: return ["Not enough donations listed to generate waste insights yet."]
    exp_c = sum(1 for d in dons if d["status"] == "Expired")
    exp_p = (exp_c / len(dons)) * 100
    cls, exps = {}, {}
    for d in dons:
        cat = d["category"]
        if d["status"] == "Expired": exps[cat] = exps.get(cat, 0) + 1
        cr = [r for r in reqs if r["donation_id"] == d["id"]]
        if cr: cls[cat] = cls.get(cat, 0) + len(cr)
    tc, te = (max(cls, key=cls.get) if cls else None), (max(exps, key=exps.get) if exps else None)
    res = [f"📊 Plate Rescue Rate: {round(100 - exp_p, 1)}% redistributed.",
           f"⚠️ High Expiry Risk: {round(exp_p, 1)}% expired." if exp_p > 20 else f"🌱 High Success: Low waste rate of {round(exp_p, 1)}%!"]
    if tc: res.append(f"🔥 Highest Demand: '{tc}' is most active.")
    if te: res.append(f"💡 Action: '{te}' has high unclaimed rate.")
    return res

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILES = {
    "users": (os.path.join(DATA_DIR, "users.csv"), ["id", "full_name", "email", "password", "phone", "address", "role", "created_at"]),
    "ngos": (os.path.join(DATA_DIR, "ngos.csv"), ["id", "user_id", "organization_name", "registration_number", "location", "phone", "email"]),
    "donations": (os.path.join(DATA_DIR, "donations.csv"), ["id", "donor_id", "food_name", "category", "quantity", "unit", "cooked_or_packaged", "expiry_time", "pickup_address", "latitude", "longitude", "status", "image", "created_at"]),
    "requests": (os.path.join(DATA_DIR, "requests.csv"), ["id", "donation_id", "ngo_id", "request_date", "status", "pickup_time"]),
    "notifications": (os.path.join(DATA_DIR, "notifications.csv"), ["id", "user_id", "title", "message", "status", "created_at"])
}

def parse_record(row, tbl):
    for k in ["id", "user_id", "donation_id", "ngo_id"]:
        if k in row: row[k] = int(row[k])
    for k in ["latitude", "longitude", "quantity"]:
        if k in row:
            try: row[k] = float(row[k]) if row[k] not in (None, "", "None") else None
            except ValueError: row[k] = None
    if tbl == "requests" and row.get("pickup_time") == "": row["pickup_time"] = None
    return row

def load_csv(name, default_data):
    path, fields = CSV_FILES[name]
    if not os.path.exists(path):
        save_csv(name, default_data)
        return [dict(r) for r in default_data]
    records = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try: records.append(parse_record(dict(r), name))
            except Exception: pass
    return records

def save_csv(name, data=None):
    path, fields = CSV_FILES[name]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if data is None: data = st.session_state[name]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in data:
            cr = {k: ("" if r.get(k) is None else r[k]) for k in fields if k in r}
            w.writerow(cr)

def save_users_to_csv(): save_csv("users")
def save_ngos_to_csv(): save_csv("ngos")
def save_donations_to_csv(): save_csv("donations")
def save_requests_to_csv(): save_csv("requests")
def save_notifications_to_csv(): save_csv("notifications")

def initialize_session_state():
    if "initialized" in st.session_state and st.session_state.initialized: return
    now = datetime.now()
    ns = now.strftime("%Y-%m-%d %H:%M:%S")
    
    u_seed = [
        {"id": 1, "full_name": "System Admin", "email": "admin@foodwaste.org", "password": hash_password("AdminPass123!"), "phone": "1234567890", "address": "Admin HQ Main City", "role": "Admin", "created_at": ns},
        {"id": 2, "full_name": "Grand Plaza Hotel", "email": "donor.hotel@foodwaste.org", "password": hash_password("DonorPass123!"), "phone": "9876543210", "address": "123 Luxury Avenue, downtown (12.9715, 77.5946)", "role": "Donor", "created_at": ns},
        {"id": 3, "full_name": "FreshFoods Supermarket", "email": "donor.market@foodwaste.org", "password": hash_password("DonorPass123!"), "phone": "5551234567", "address": "456 Market Road, suburbs (12.9345, 77.6201)", "role": "Donor", "created_at": ns},
        {"id": 4, "full_name": "Hope NGO Director", "email": "ngo.hope@foodwaste.org", "password": hash_password("NgoPass123!"), "phone": "2223334444", "address": "789 Care Street, downtown (12.9782, 77.5855)", "role": "NGO", "created_at": ns},
        {"id": 5, "full_name": "Rescue NGO Coordinator", "email": "ngo.rescue@foodwaste.org", "password": hash_password("NgoPass123!"), "phone": "8889990000", "address": "321 Helping Lane, tech hub (12.9562, 77.7011)", "role": "NGO", "created_at": ns}
    ]
    n_seed = [
        {"id": 1, "user_id": 4, "organization_name": "Hope Food Distribution", "registration_number": "REG-839210", "location": "789 Care Street, downtown (12.9782, 77.5855)", "phone": "2223334444", "email": "ngo.hope@foodwaste.org"},
        {"id": 2, "user_id": 5, "organization_name": "Rescue Kitchen Community", "registration_number": "REG-445892", "location": "321 Helping Lane, tech hub (12.9562, 77.7011)", "phone": "8889990000", "email": "ngo.rescue@foodwaste.org"}
    ]
    d_seed = [
        {"id": 1, "donor_id": 2, "food_name": "Veg Rice & Curry", "category": "Cooked Food", "quantity": 15.0, "unit": "servings", "cooked_or_packaged": "Cooked", "expiry_time": (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), "pickup_address": "123 Luxury Avenue, downtown (12.9715, 77.5946)", "latitude": 12.9715, "longitude": 77.5946, "status": "Approved", "image": "veg_rice_curry.jpg", "created_at": ns},
        {"id": 2, "donor_id": 3, "food_name": "Wheat Bread Loaves", "category": "Bakery Items", "quantity": 20.0, "unit": "pieces", "cooked_or_packaged": "Packaged", "expiry_time": (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "pickup_address": "456 Market Road, suburbs (12.9345, 77.6201)", "latitude": 12.9345, "longitude": 77.6201, "status": "Pending", "image": "wheat_bread.jpg", "created_at": ns},
        {"id": 3, "donor_id": 2, "food_name": "Fruit Salad Cups", "category": "Fresh Produce", "quantity": 10.0, "unit": "pieces", "cooked_or_packaged": "Fresh", "expiry_time": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"), "pickup_address": "123 Luxury Avenue, downtown (12.9715, 77.5946)", "latitude": 12.9715, "longitude": 77.5946, "status": "Expired", "image": "fruit_salad.jpg", "created_at": ns},
        {"id": 4, "donor_id": 3, "food_name": "Fresh Apples", "category": "Fresh Produce", "quantity": 5.0, "unit": "kg", "cooked_or_packaged": "Fresh", "expiry_time": (now + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), "pickup_address": "456 Market Road, suburbs (12.9345, 77.6201)", "latitude": 12.9345, "longitude": 77.6201, "status": "Requested", "image": "fresh_apples.jpg", "created_at": ns},
        {"id": 5, "donor_id": 2, "food_name": "Pasta Marinara", "category": "Cooked Food", "quantity": 25.0, "unit": "servings", "cooked_or_packaged": "Cooked", "expiry_time": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "pickup_address": "123 Luxury Avenue, downtown (12.9715, 77.5946)", "latitude": 12.9715, "longitude": 77.5946, "status": "Collected", "image": "pasta_marinara.jpg", "created_at": ns}
    ]
    r_seed = [
        {"id": 1, "donation_id": 4, "ngo_id": 1, "request_date": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "status": "Pending", "pickup_time": ""},
        {"id": 2, "donation_id": 5, "ngo_id": 2, "request_date": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "status": "Completed", "pickup_time": (now - timedelta(days=1, hours=22)).strftime("%Y-%m-%d %H:%M:%S")}
    ]
    nt_seed = [
        {"id": 1, "user_id": 2, "title": "Welcome to FoodShare!", "message": "Thank you for registering.", "status": "Unread", "created_at": ns},
        {"id": 2, "user_id": 4, "title": "New Donation Alert", "message": "Grand Plaza Hotel posted Veg Rice & Curry.", "status": "Unread", "created_at": ns},
        {"id": 3, "user_id": 1, "title": "New User Registered", "message": "Rescue Kitchen Community registered.", "status": "Read", "created_at": ns}
    ]
    
    st.session_state.users = load_csv("users", u_seed)
    st.session_state.ngos = load_csv("ngos", n_seed)
    st.session_state.donations = load_csv("donations", d_seed)
    st.session_state.requests = load_csv("requests", r_seed)
    st.session_state.notifications = load_csv("notifications", nt_seed)
    st.session_state.current_user = None
    st.session_state.initialized = True
