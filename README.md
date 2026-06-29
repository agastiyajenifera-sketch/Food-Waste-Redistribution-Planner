# Food Waste Redistribution Planner (FoodShare Desktop App)

A modern, AI-powered desktop application built using Python and **CustomTkinter** to combat food waste. It connects food donors (restaurants, hotels, supermarkets) with local non-governmental organizations (NGOs) to coordinate immediate collection and distribution of surplus food.

---

## 🌟 Key Features

### 1. Unified Authentication & Role-Based Dashboards
- **System Administrator Console**:
  - Audit and approve/reject food postings.
  - Search platform members and delete records.
  - Interactive visual analytics (Pie & Bar charts).
  - Export system metrics and activity reports to CSV or plain text.
- **Donor Portal**:
  - Post surplus food donations.
  - Track expiry dates and automatically predict expiration risk using AI.
  - Upload food item photos.
  - Edit or delete pending postings.
  - Receive real-time system notifications.
- **NGO Portal**:
  - Browse available food in a modern catalog card layout.
  - Filter food by categories, search by item names, and sort.
  - Proximity calculation: Auto-calculates distances to food pickup locations using the Haversine formula.
  - Request collection claims and track log history.
  - Receive notifications when new donations are approved.

### 2. Intelligent AI Features
- **Expiry Risk Predictor**: Evaluates time remaining and food vulnerability (e.g. Cooked Food vs. Packaged Food) to classify risk levels (High, Medium, Low) dynamically.
- **Nearest NGO Recommender**: Computes coordinates and distance proximity to recommend matching distribution partners.
- **Food Waste Analytics Engine**: Evaluates database histories to print smart recommendations and insights on reducing waste on the admin dashboard.

---

## 🛠️ Technology Stack
- **User Interface**: CustomTkinter (Python GUI framework)
- **Data Plotting**: Matplotlib & Pandas (embedded into Tkinter canvas)
- **Database**: SQLite (direct database connection via standard `sqlite3` library)
- **Security**: SHA-256 password hashing

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher installed on your system.

### Step 1: Set Up Virtual Environment (Recommended)
Open a terminal in the project directory:
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate
```

### Step 2: Install Dependencies
Install all required libraries listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Launch the desktop application directly using Python:
```bash
python app.py
```
On first launch, the SQLite database (`database.db`) will be automatically created and populated with demo seed data.

---

## 🔑 Demonstration Credentials (Seeded Automatically)

The database is seeded with the following pre-configured accounts (Password for all accounts follows the pattern shown below):

| Role | Email Address | Password | Details |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@foodwaste.org` | `AdminPass123!` | Access to the entire platform audit deck, analytics, and user lists. |
| **Food Donor** | `donor.hotel@foodwaste.org` | `DonorPass123!` | Registered as *Grand Plaza Hotel* (Cooked food donor). |
| **Food Donor** | `donor.market@foodwaste.org` | `DonorPass123!` | Registered as *FreshFoods Supermarket* (Bakery/Produce donor). |
| **NGO Organization** | `ngo.hope@foodwaste.org` | `NgoPass123!` | Registered as *Hope Food Distribution*. |
| **NGO Organization** | `ngo.rescue@foodwaste.org` | `NgoPass123!` | Registered as *Rescue Kitchen Community*. |
