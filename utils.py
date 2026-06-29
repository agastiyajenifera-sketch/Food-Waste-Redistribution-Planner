import re
from datetime import datetime
import math
from database import get_connection

def validate_email(email):
    """Validates email format using regex."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validates phone number format (basic digits checker)."""
    return len(re.sub(r'\D', '', phone)) >= 10

def parse_datetime(dt_str):
    """Parses a datetime string in YYYY-MM-DD HH:MM:SS format."""
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points on the Earth
    in kilometers using the Haversine formula.
    """
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
        
    R = 6371.0  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def extract_coords_from_text(text):
    """
    Helper to extract coordinates like (12.9715, 77.5946) from an address string.
    Returns (lat, lon) or (None, None) if not found.
    """
    if not text:
        return None, None
    match = re.search(r'\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)', text)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

# --- AI & Analytics Functions ---

def predict_expiry_risk(category, expiry_time_str):
    """
    AI Predictor: Predicts food expiration risk (High, Medium, Low)
    based on the time remaining and the vulnerability of the food category.
    """
    expiry_time = parse_datetime(expiry_time_str)
    if not expiry_time:
        return "Unknown"
        
    now = datetime.now()
    remaining_hours = (expiry_time - now).total_seconds() / 3600.0

    if remaining_hours <= 0:
        return "Expired"

    # Category vulnerability classification
    # High vulnerability: Cooked Food, Dairy Products, Bakery Items (expire fast)
    # Medium vulnerability: Fresh Produce, Beverages
    # Low vulnerability: Packaged Food, Canned Goods
    
    if category in ["Cooked Food", "Dairy Products", "Bakery Items"]:
        if remaining_hours < 8:
            return "High"
        elif remaining_hours < 18:
            return "Medium"
        else:
            return "Low"
    elif category in ["Fresh Produce", "Beverages"]:
        if remaining_hours < 12:
            return "High"
        elif remaining_hours < 30:
            return "Medium"
        else:
            return "Low"
    else:  # Packaged Food, Canned Goods, etc.
        if remaining_hours < 24:
            return "High"
        elif remaining_hours < 72:
            return "Medium"
        else:
            return "Low"

def recommend_nearest_ngos(donation_latitude, donation_longitude, limit=3):
    """
    AI Recommender: Computes distances to all registered NGOs using the Haversine
    formula and returns the top recommended (nearest) NGOs.
    """
    if donation_latitude is None or donation_longitude is None:
        return []

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ngo_id, organization_name, location, phone, email FROM ngos")
    ngos = cursor.fetchall()
    conn.close()

    recommendations = []
    for ngo in ngos:
        # Parse coordinates from location string if latitude/longitude are not separate fields
        loc_str = ngo["location"]
        ngo_lat, ngo_lon = extract_coords_from_text(loc_str)
        
        # If coordinates couldn't be parsed, assign default mock coordinates
        if ngo_lat is None or ngo_lon is None:
            # Assign fallback coordinates based on ID
            ngo_lat = 12.97 + (ngo["ngo_id"] * 0.01)
            ngo_lon = 77.59 + (ngo["ngo_id"] * 0.01)

        dist = haversine_distance(donation_latitude, donation_longitude, ngo_lat, ngo_lon)
        recommendations.append({
            "ngo_id": ngo["ngo_id"],
            "organization_name": ngo["organization_name"],
            "distance_km": round(dist, 2),
            "phone": ngo["phone"],
            "email": ngo["email"],
            "location": ngo["location"]
        })

    # Sort by distance ascending
    recommendations.sort(key=lambda x: x["distance_km"])
    return recommendations[:limit]

def get_food_waste_insights():
    """
    AI Analytics: Analyzes historical database records to generate text-based
    food waste predictions, recommendations, and insights.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get percentage of donations that expired without being claimed
    cursor.execute("SELECT COUNT(*) FROM donations WHERE status = 'Expired'")
    expired_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM donations")
    total_count = cursor.fetchone()[0]
    
    # NGO Demand by category
    cursor.execute("""
        SELECT d.category, COUNT(r.request_id) as req_count 
        FROM requests r
        JOIN donations d ON r.donation_id = d.donation_id
        GROUP BY d.category
        ORDER BY req_count DESC
        LIMIT 1
    """)
    top_demanded_category_row = cursor.fetchone()
    
    # Donation categories most likely to expire
    cursor.execute("""
        SELECT category, COUNT(*) as exp_count
        FROM donations
        WHERE status = 'Expired'
        GROUP BY category
        ORDER BY exp_count DESC
        LIMIT 1
    """)
    top_expired_category_row = cursor.fetchone()

    conn.close()

    if total_count == 0:
        return ["Not enough data in the database to generate waste insights yet."]

    expired_percent = (expired_count / total_count) * 100

    insights = []
    insights.append(f"📊 Plate Rescue Rate: {round(100 - expired_percent, 1)}% of all registered donations successfully claimed.")
    
    if expired_percent > 20:
        insights.append(f"⚠️ High Expiry Risk: {round(expired_percent, 1)}% of donations expired unclaimed. Recommendation: Donors should register items at least 12 hours prior to expiration.")
    else:
        insights.append(f"🌱 Excellent Redistribution: Low waste rate of {round(expired_percent, 1)}% across the board!")

    if top_demanded_category_row:
        insights.append(f"🔥 Highest NGO Demand: '{top_demanded_category_row['category']}' represents the most requested category. Direct surplus listings here first.")

    if top_expired_category_row and top_expired_category_row['exp_count'] > 0:
        insights.append(f"💡 Action Plan: '{top_expired_category_row['category']}' has the highest expiry frequency. Suggest donor kitchens portion these items into smaller packets for faster NGO pickups.")
        
    return insights
