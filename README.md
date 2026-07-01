# 🥗 FoodShare: Food Waste Redistribution Planner

## Problem Statement

Every day, a large amount of good and edible food is wasted by restaurants, hotels, supermarkets, and households, while many people do not have enough food to eat. There is no simple and efficient system to connect food donors with NGOs in time. Because of delays and poor coordination, much of the donated food expires before it can reach people in need.

Our **Food Waste Redistribution Planner** solves this problem by providing a platform where donors can donate surplus food, administrators can verify the donations, and NGOs can request and collect the food quickly. This helps reduce food waste and ensures that more food reaches needy people safely.

## Project
A neat, modern, and highly professional web application built using Python and **Streamlit** to coordinate food surplus rescue. The platform connects verified food donors (hotels, restaurants, supermarkets) with local non-governmental organizations (NGOs) to minimize food waste and support communities in need.

![Indian Food Background](assets/images/indian_food_bg.jpg)

---

## 🌟 Core Features

### 1. Unified Authentication & Glassmorphism Portal
- Centered, floating glass card login and registration screens decorated with a blurred Indian food background image.
- Password security powered by SHA-256 hashing.

### 2. Role-Based Dashboards
- **System Administrator Console**:
  - **Overview Dashboard**: Tracks statistics (Donors, NGOs, Active Donations, Rescued Food) with visual cards.
  - **Donation Audit**: Inspects, approves, or rejects pending postings from donors.
  - **User Manager**: Segmented tabs separating verified Food Donors and NGO Partners, containing live performance analytics and coordinates.
  - **Visual Analytics**: Dynamic charts representing category shares and status distributions using Matplotlib.
  - **Generate Reports**: Downloadable CSV spreadsheets for system audits.
- **Donor Portal**:
  - **My Donations**: Real-time listing tracking with expiration risk analysis.
  - **Donate Food**: Simplified registration form to post surplus items, set expiry hours, and auto-parse coordinates.
  - **Inbox**: In-app notifications when claims or approvals change.
- **NGO Portal**:
  - **Browse Catalog**: Proximity catalog displaying approved surplus food items sorted by expiry hours, largest quantities, or nearest distances.
  - **My Claims**: Active collection checklists to mark claims as picked up or completed.
  - **Inbox**: Notification panel when new food posts are listed.

### 3. Intelligent Algorithms
- **AI Expiry Risk Predictor**: Evaluates time decay and food category (Cooked Food, Produce, Dairy, Packaged) to flag items as High, Medium, Low risk dynamically.
- **Proximity Distance Parser**: Auto-extracts map coordinates from address text and computes geographical distances using the **Haversine formula**.
- **AI Waste Insights**: Analyzes database history to output redistribution rates and recommend optimization steps on the admin console.

---

## 📁 Database Schema (CSV Persistence)

Data is saved locally within the `./data/` directory across five structured tables:
1. `users.csv`: Stores user accounts, emails, hashed passwords, contact details, and platform roles.
2. `ngos.csv`: Holds NGO organizational names, registration numbers, locations, and coordinate profiles.
3. `donations.csv`: Tracks surplus listings, donor IDs, quantities, units, statuses (Pending, Approved, Requested, Collected, Expired), and expiry timelines.
4. `requests.csv`: Coordinates claims, request dates, pickup timelines, and completed rescue logs.
5. `notifications.csv`: Tracks notification titles, timestamps, messages, and read/unread statuses.

---

## 🛠️ Technology Stack
- **Framework**: Streamlit (Python Web Application Engine)
- **Data Tables**: Pandas (structured loaders and analytics processing)
- **Visualization**: Matplotlib (custom chart plotting)
- **Database Engine**: File-based CSV persistence with generic validation parsers.
- **Styling**: Custom CSS injecting Outfit typography, glassmorphism containers, and card hover animations.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher installed.

### Step 1: Clone or Open the Directory
Open a terminal in the folder:
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate
```

### Step 2: Install Libraries
```bash
pip install -r requirements.txt
```

### Step 3: Run the Server
```bash
streamlit run app.py
```
On startup, the system will automatically create the `./data/` folder and seed the database tables with default values.

---

## 🔑 Demonstration Credentials

| Role | Email Address | Password | Organization |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@foodwaste.org` | `AdminPass123!` | System Console |
| **Food Donor** | `donor.hotel@foodwaste.org` | `DonorPass123!` | *Grand Plaza Hotel* |
| **Food Donor** | `donor.market@foodwaste.org` | `DonorPass123!` | *FreshFoods Supermarket* |
| **NGO Partner** | `ngo.hope@foodwaste.org` | `NgoPass123!` | *Hope Food Distribution* |
| **NGO Partner** | `ngo.rescue@foodwaste.org` | `NgoPass123!` | *Rescue Kitchen Community* |

