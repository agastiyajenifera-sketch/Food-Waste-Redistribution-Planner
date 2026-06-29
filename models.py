import sqlite3
from database import get_connection, hash_password
from datetime import datetime

class User:
    def __init__(self, user_id, full_name, email, password, phone, address, role, created_at):
        self.user_id = user_id
        self.full_name = full_name
        self.email = email
        self.password = password
        self.phone = phone
        self.address = address
        self.role = role  # 'Admin', 'Donor', 'NGO'
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return User(
            user_id=row['user_id'],
            full_name=row['full_name'],
            email=row['email'],
            password=row['password'],
            phone=row['phone'],
            address=row['address'],
            role=row['role'],
            created_at=row['created_at']
        )

    @classmethod
    def get_by_id(cls, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row)

    @classmethod
    def get_by_email(cls, email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row)

    @classmethod
    def authenticate(cls, email, password):
        user = cls.get_by_email(email)
        if user and user.password == hash_password(password):
            return user
        return None

    @classmethod
    def create(cls, full_name, email, password, phone, address, role):
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute("""
            INSERT INTO users (full_name, email, password, phone, address, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (full_name, email, hash_password(password), phone, address, role, now_str))
            user_id = cursor.lastrowid
            conn.commit()
            return cls.get_by_id(user_id)
        except sqlite3.IntegrityError:
            return None  # Email already exists
        finally:
            conn.close()

    @classmethod
    def delete(cls, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_all_by_role(cls, role):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = ? ORDER BY full_name ASC", (role,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]


class NGO:
    def __init__(self, ngo_id, user_id, organization_name, registration_number, location, phone, email):
        self.ngo_id = ngo_id
        self.user_id = user_id
        self.organization_name = organization_name
        self.registration_number = registration_number
        self.location = location
        self.phone = phone
        self.email = email

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return NGO(
            ngo_id=row['ngo_id'],
            user_id=row['user_id'],
            organization_name=row['organization_name'],
            registration_number=row['registration_number'],
            location=row['location'],
            phone=row['phone'],
            email=row['email']
        )

    @classmethod
    def get_by_id(cls, ngo_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ngos WHERE ngo_id = ?", (ngo_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row)

    @classmethod
    def get_by_user_id(cls, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ngos WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row)

    @classmethod
    def create(cls, user_id, organization_name, registration_number, location, phone, email):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO ngos (user_id, organization_name, registration_number, location, phone, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, organization_name, registration_number, location, phone, email))
            ngo_id = cursor.lastrowid
            conn.commit()
            return cls.get_by_id(ngo_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()


class Donation:
    def __init__(self, donation_id, donor_id, food_name, category, quantity, unit, cooked_or_packaged, 
                 expiry_time, pickup_address, latitude, longitude, status, image, created_at):
        self.donation_id = donation_id
        self.donor_id = donor_id
        self.food_name = food_name
        self.category = category
        self.quantity = quantity
        self.unit = unit
        self.cooked_or_packaged = cooked_or_packaged
        self.expiry_time = expiry_time
        self.pickup_address = pickup_address
        self.latitude = latitude
        self.longitude = longitude
        self.status = status  # 'Pending', 'Approved', 'Rejected', 'Requested', 'Collected', 'Expired'
        self.image = image
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Donation(
            donation_id=row['donation_id'],
            donor_id=row['donor_id'],
            food_name=row['food_name'],
            category=row['category'],
            quantity=row['quantity'],
            unit=row['unit'],
            cooked_or_packaged=row['cooked_or_packaged'],
            expiry_time=row['expiry_time'],
            pickup_address=row['pickup_address'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            status=row['status'],
            image=row['image'],
            created_at=row['created_at']
        )

    @classmethod
    def get_by_id(cls, donation_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donations WHERE donation_id = ?", (donation_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row)

    @classmethod
    def get_all(cls):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def get_by_donor_id(cls, donor_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donations WHERE donor_id = ? ORDER BY created_at DESC", (donor_id,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def get_available(cls):
        """Gets all approved and non-expired donations that aren't collected or requested yet."""
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        SELECT * FROM donations 
        WHERE status = 'Approved' AND expiry_time > ? 
        ORDER BY expiry_time ASC
        """, (now_str,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def create(cls, donor_id, food_name, category, quantity, unit, cooked_or_packaged, 
               expiry_time, pickup_address, latitude=None, longitude=None, status='Pending', image=None):
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO donations (donor_id, food_name, category, quantity, unit, cooked_or_packaged, 
                               expiry_time, pickup_address, latitude, longitude, status, image, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (donor_id, food_name, category, quantity, unit, cooked_or_packaged, 
              expiry_time, pickup_address, latitude, longitude, status, image, now_str))
        donation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cls.get_by_id(donation_id)

    @classmethod
    def update(cls, donation_id, food_name, category, quantity, unit, cooked_or_packaged, 
               expiry_time, pickup_address, latitude=None, longitude=None, status=None, image=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build query dynamically based on supplied fields
        updates = []
        params = []
        fields = [("food_name", food_name), ("category", category), ("quantity", quantity), 
                  ("unit", unit), ("cooked_or_packaged", cooked_or_packaged), ("expiry_time", expiry_time), 
                  ("pickup_address", pickup_address), ("latitude", latitude), ("longitude", longitude),
                  ("status", status), ("image", image)]
        
        for field, value in fields:
            if value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        params.append(donation_id)
        query = f"UPDATE donations SET {', '.join(updates)} WHERE donation_id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return cls.get_by_id(donation_id)

    @classmethod
    def delete(cls, donation_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM donations WHERE donation_id = ?", (donation_id,))
        conn.commit()
        conn.close()


class Request:
    def __init__(self, request_id, donation_id, ngo_id, request_date, status, pickup_time):
        self.request_id = request_id
        self.donation_id = donation_id
        self.ngo_id = ngo_id
        self.request_date = request_date
        self.status = status  # 'Pending', 'Approved', 'Rejected', 'Completed'
        self.pickup_time = pickup_time

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Request(
            request_id=row['request_id'],
            donation_id=row['donation_id'],
            ngo_id=row['ngo_id'],
            request_date=row['request_date'],
            status=row['status'],
            pickup_time=row['pickup_time']
        )

    @classmethod
    def get_by_id(cls, request_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests WHERE request_id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        return cls.from_row(row)

    @classmethod
    def get_by_ngo_id(cls, ngo_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests WHERE ngo_id = ? ORDER BY request_date DESC", (ngo_id,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def get_all(cls):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests ORDER BY request_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def create(cls, donation_id, ngo_id):
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert request
        cursor.execute("""
        INSERT INTO requests (donation_id, ngo_id, request_date, status)
        VALUES (?, ?, ?, 'Pending')
        """, (donation_id, ngo_id))
        request_id = cursor.lastrowid
        
        # Update donation status to "Requested" to prevent other NGOs from claiming it simultaneously
        cursor.execute("UPDATE donations SET status = 'Requested' WHERE donation_id = ?", (donation_id,))
        
        conn.commit()
        conn.close()
        return cls.get_by_id(request_id)

    @classmethod
    def update_status(cls, request_id, status, pickup_time=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Fetch request details first
        cursor.execute("SELECT donation_id, ngo_id FROM requests WHERE request_id = ?", (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close()
            return None
        
        donation_id = req["donation_id"]
        
        # Update the request
        if pickup_time:
            cursor.execute("UPDATE requests SET status = ?, pickup_time = ? WHERE request_id = ?", (status, pickup_time, request_id))
        else:
            cursor.execute("UPDATE requests SET status = ? WHERE request_id = ?", (status, request_id))
            
        # Update the linked donation status based on request status
        if status == 'Approved':
            cursor.execute("UPDATE donations SET status = 'Requested' WHERE donation_id = ?", (donation_id,))
        elif status == 'Completed':
            cursor.execute("UPDATE donations SET status = 'Collected' WHERE donation_id = ?", (donation_id,))
        elif status == 'Rejected':
            # Revert donation to "Approved" so other NGOs can see/request it
            cursor.execute("UPDATE donations SET status = 'Approved' WHERE donation_id = ?", (donation_id,))
            
        conn.commit()
        conn.close()
        return cls.get_by_id(request_id)


class Notification:
    def __init__(self, notification_id, user_id, title, message, status, created_at):
        self.notification_id = notification_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.status = status  # 'Unread', 'Read'
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Notification(
            notification_id=row['notification_id'],
            user_id=row['user_id'],
            title=row['title'],
            message=row['message'],
            status=row['status'],
            created_at=row['created_at']
        )

    @classmethod
    def get_by_user_id(cls, user_id, unread_only=False):
        conn = get_connection()
        cursor = conn.cursor()
        if unread_only:
            cursor.execute("SELECT * FROM notifications WHERE user_id = ? AND status = 'Unread' ORDER BY created_at DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_row(r) for r in rows]

    @classmethod
    def create(cls, user_id, title, message):
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, status, created_at)
        VALUES (?, ?, ?, 'Unread', ?)
        """, (user_id, title, message, now_str))
        notif_id = cursor.lastrowid
        conn.commit()
        conn.close()
        # Return none or simple trigger
        return notif_id

    @classmethod
    def mark_as_read(cls, notif_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET status = 'Read' WHERE notification_id = ?", (notif_id,))
        conn.commit()
        conn.close()
        
    @classmethod
    def mark_all_read(cls, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET status = 'Read' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
