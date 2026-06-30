import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
from config import DB_PATH

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_tables():
    """Creates the SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'Donor', 'NGO')),
        created_at TEXT NOT NULL
    );
    """)

    # NGOs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ngos (
        ngo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        organization_name TEXT NOT NULL,
        registration_number TEXT UNIQUE NOT NULL,
        location TEXT,
        phone TEXT,
        email TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
    );
    """)

    # Donations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        cooked_or_packaged TEXT NOT NULL,
        expiry_time TEXT NOT NULL,
        pickup_address TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        status TEXT NOT NULL DEFAULT 'Pending',
        image TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (donor_id) REFERENCES users (user_id) ON DELETE CASCADE
    );
    """)

    # Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        donation_id INTEGER NOT NULL,
        ngo_id INTEGER NOT NULL,
        request_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        pickup_time TEXT,
        FOREIGN KEY (donation_id) REFERENCES donations (donation_id) ON DELETE CASCADE,
        FOREIGN KEY (ngo_id) REFERENCES ngos (ngo_id) ON DELETE CASCADE
    );
    """)

    # Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Unread',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def seed_database():
    """Seeds the database with test accounts and sample data if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # 1. Seed Users
    users_data = [
        ("System Admin", "admin@foodwaste.org", hash_password("AdminPass123!"), "1234567890", "Admin HQ Main City", "Admin", now_str),
        ("Grand Plaza Hotel", "donor.hotel@foodwaste.org", hash_password("DonorPass123!"), "9876543210", "123 Luxury Avenue, downtown (12.9715, 77.5946)", "Donor", now_str),
        ("FreshFoods Supermarket", "donor.market@foodwaste.org", hash_password("DonorPass123!"), "5551234567", "456 Market Road, suburbs (12.9345, 77.6201)", "Donor", now_str),
        ("Hope NGO Director", "ngo.hope@foodwaste.org", hash_password("NgoPass123!"), "2223334444", "789 Care Street, downtown (12.9782, 77.5855)", "NGO", now_str),
        ("Rescue NGO Coordinator", "ngo.rescue@foodwaste.org", hash_password("NgoPass123!"), "8889990000", "321 Helping Lane, tech hub (12.9562, 77.7011)", "NGO", now_str)
    ]

    for user in users_data:
        cursor.execute("""
        INSERT INTO users (full_name, email, password, phone, address, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, user)

    # 2. Seed NGOs
    # Hope NGO - link to user_id=4
    # Rescue NGO - link to user_id=5
    ngos_data = [
        (4, "Hope Food Distribution", "REG-839210", "789 Care Street, downtown", "2223334444", "ngo.hope@foodwaste.org"),
        (5, "Rescue Kitchen Community", "REG-445892", "321 Helping Lane, tech hub", "8889990000", "ngo.rescue@foodwaste.org")
    ]

    for ngo in ngos_data:
        cursor.execute("""
        INSERT INTO ngos (user_id, organization_name, registration_number, location, phone, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ngo)

    # Get user IDs for reference
    cursor.execute("SELECT user_id, email FROM users")
    user_ids = {row["email"]: row["user_id"] for row in cursor.fetchall()}

    # Get NGO IDs for reference
    cursor.execute("SELECT ngo_id, organization_name FROM ngos")
    ngo_ids = {row["organization_name"]: row["ngo_id"] for row in cursor.fetchall()}

    # 3. Seed Donations
    # Grand Plaza Hotel (user_id=2)
    # FreshFoods Supermarket (user_id=3)
    donations_data = [
        # Approved & Available Cooked Food
        (user_ids["donor.hotel@foodwaste.org"], "Veg Rice & Curry", "Cooked Food", 15.0, "servings", "Cooked", 
         (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), "123 Luxury Avenue, downtown", 12.9715, 77.5946, "Approved", "veg_rice_curry.jpg", now_str),
        
        # Pending Packaged Food
        (user_ids["donor.market@foodwaste.org"], "Wheat Bread Loaves", "Bakery Items", 20.0, "pieces", "Packaged", 
         (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "456 Market Road, suburbs", 12.9345, 77.6201, "Pending", "wheat_bread.jpg", now_str),
        
        # Expired (Low Risk at first, but set back in time)
        (user_ids["donor.hotel@foodwaste.org"], "Fruit Salad Cups", "Fresh Produce", 10.0, "pieces", "Fresh", 
         (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"), "123 Luxury Avenue, downtown", 12.9715, 77.5946, "Approved", "fruit_salad.jpg", now_str),
        
        # Approved and already requested
        (user_ids["donor.market@foodwaste.org"], "Fresh Apples", "Fresh Produce", 5.0, "kg", "Fresh", 
         (now + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), "456 Market Road, suburbs", 12.9345, 77.6201, "Approved", "fresh_apples.jpg", now_str),

        # Completed/Collected donation
        (user_ids["donor.hotel@foodwaste.org"], "Pasta Marinara", "Cooked Food", 25.0, "servings", "Cooked", 
         (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "123 Luxury Avenue, downtown", 12.9715, 77.5946, "Collected", "pasta_marinara.jpg", now_str),
    ]

    for donation in donations_data:
        cursor.execute("""
        INSERT INTO donations (donor_id, food_name, category, quantity, unit, cooked_or_packaged, expiry_time, pickup_address, latitude, longitude, status, image, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, donation)

    # Get donation IDs for reference
    cursor.execute("SELECT donation_id, food_name FROM donations")
    donation_ids = {row["food_name"]: row["donation_id"] for row in cursor.fetchall()}

    # 4. Seed Requests
    # Request for Fresh Apples by Hope NGO
    # Request for Pasta Marinara by Rescue NGO (Completed)
    requests_data = [
        (donation_ids["Fresh Apples"], ngo_ids["Hope Food Distribution"], (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "Pending", None),
        (donation_ids["Pasta Marinara"], ngo_ids["Rescue Kitchen Community"], (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "Completed", (now - timedelta(days=1, hours=22)).strftime("%Y-%m-%d %H:%M:%S"))
    ]

    for req in requests_data:
        cursor.execute("""
        INSERT INTO requests (donation_id, ngo_id, request_date, status, pickup_time)
        VALUES (?, ?, ?, ?, ?)
        """, req)

    # 5. Seed Notifications
    notifications_data = [
        (user_ids["donor.hotel@foodwaste.org"], "Welcome to FoodShare!", "Thank you for registering. You can now post your surplus food donations.", "Unread", now_str),
        (user_ids["ngo.hope@foodwaste.org"], "New Donation Alert", "Grand Plaza Hotel posted Veg Rice & Curry. Expiry risk is high, collect soon!", "Unread", now_str),
        (user_ids["admin@foodwaste.org"], "New User Registered", "Rescue Kitchen Community registered as a new NGO.", "Read", now_str)
    ]

    for notif in notifications_data:
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, status, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, notif)

    conn.commit()
    conn.close()

def initialize():
    """Initializes database tables and seeds them."""
    create_tables()
    seed_database()

if __name__ == "__main__":
    initialize()
    print("Database initialized and seeded successfully.")
