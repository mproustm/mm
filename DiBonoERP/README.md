# DiBono ERP - Seafood Restaurant Management System

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-Proprietary-red)

## 🌊 Overview

DiBono ERP is a comprehensive desktop application for managing seafood restaurant operations in Tripoli, Libya. Built with Python and PyQt6, it features an ocean-themed UI with full bilingual support (English/Arabic).

## ✨ Key Features

### 🔐 Authentication & Security
- Hard-configured admin account: `admin / CatchTheWave!`
- Employee accounts with role-based access control
- Session tracking with automatic cash reconciliation
- Admin PIN protection (1234) for sensitive POS actions

### 💰 Point of Sale (POS)
- High-speed menu tile interface with category filtering
- Weight-based pricing for fresh seafood (by kg)
- Real-time inventory availability checking
- Hold/Recall orders (max 5 per employee, 4-hour expiration)
- Cash/Card/Split payment methods
- Automatic inventory depletion on order completion
- Order voiding with inventory restoration

### 📦 Inventory Management
- 23 pre-seeded seafood and ingredient items
- SKU-based tracking with min/max thresholds
- Recipe ingredient mapping to menu items
- Real-time stock updates from POS transactions
- Cost tracking in fils (1 LYD = 1000 fils)
- Waste and spoilage logging
- Physical count and variance calculation

### 🍽️ Menu Management
- 6 menu categories (Breakfast, Seafood, Pasta, Grilled Fish, Appetizers, Beverages)
- 8 pre-configured menu items with full ingredient mappings
- Weight-based items (e.g., Grilled Sea Bass at 55 LYD/kg)
- Fixed-price items (e.g., Lobster Pasta at 65 LYD)
- Automatic recipe costing based on ingredient prices

### 📊 Admin Dashboard
- 9 KPI cards (Cash/Card/Revenue by Day/Week/Month)
- Real-time revenue calculations
- Previous period delta comparisons
- Payment mix visualization

### 👥 Session Management
- Employee login/logout with shift duration tracking
- Automatic session statistics (order count, cash sales, card sales)
- Cash count reconciliation on logout with variance calculation
- Expected vs actual cash comparison

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Windows OS (tested on Windows 10/11)

### Setup

1. **Clone or download the project**
```powershell
cd C:\DiBonoERP
```

2. **Create virtual environment (recommended)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Run the application**
```powershell
python main.py
```

The database (`dibono.db`) will be created automatically on first launch with all seed data.

## 🔑 Default Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `CatchTheWave!`
- **Access:** Full system access (Dashboard, Inventory, Menu, Employees, Reports, POS)

### Employee Accounts
- **Ahmed Hassan**
  - Username: `ahmed`
  - Password: `123456`
  - Shift: Morning 8AM-4PM
  
- **Fatima Ali**
  - Username: `fatima`
  - Password: `123456`
  - Shift: Evening 4PM-12AM

### Admin PIN for POS Overrides
- **PIN:** `1234` (for Discount, Void, Open Drawer actions)

## 📁 Project Structure

```
DiBonoERP/
├── main.py                 # Application entry point
├── dibono.db              # SQLite database (auto-generated)
├── requirements.txt       # Python dependencies
├── plan.md               # Complete feature specification
├── src/
│   ├── models/
│   │   ├── database.py        # SQLAlchemy models
│   │   └── seed_data.py       # Initial data population
│   ├── ui/
│   │   ├── login_screen.py    # Authentication interface
│   │   ├── main_window.py     # Main application window
│   │   ├── pos_interface.py   # Point of Sale screen
│   │   └── admin_dashboard.py # Admin KPI dashboard
│   └── utils/
│       ├── helpers.py         # Business logic utilities
│       └── styles.py          # Ocean theme styling
└── assets/
    └── images/               # Application assets

```

## 💾 Database Schema

### Core Tables
- **users** - Admin and employee accounts with bcrypt password hashing
- **sessions** - Employee shift tracking and cash reconciliation
- **inventory_items** - Ingredient and product stock tracking
- **menu_categories** - Menu organization with bilingual names
- **menu_items** - Dishes with pricing and weight-based options
- **menu_item_ingredients** - Recipe ingredient mappings
- **orders** - Completed and voided transactions
- **order_items** - Line items within orders
- **held_orders** - Temporarily held POS orders
- **suppliers** - Vendor information
- **purchase_orders** - Inventory replenishment tracking
- **waste_logs** - Spoilage and waste documentation
- **physical_counts** - Inventory variance tracking
- **sales_snapshots** - Time-series reporting data
- **report_points** - Flexible metrics storage

## 🎨 Design Principles

- **Ocean Theme:** Blue/teal/coral palette with marine animations
- **Bilingual UI:** Arabic primary, English secondary labels
- **High Contrast:** Optimized for dimly lit restaurant environments
- **Performance First:** Synchronous operations, no background jobs
- **Fail Loudly:** Clear error messages, blocked actions when stock insufficient
- **Currency Precision:** All amounts stored as integers (fils) to avoid floating-point errors

## 🔧 Configuration

### Business Rules (in `plan.md`)
- Tax Rate: 0% (Libya VAT exempt)
- Service Charge: 0% default
- Weight Precision: 0.01 kg (2 decimal places)
- Currency: Libyan Dinar (LYD), stored as fils
- Daily Order Numbers: Format YYYYMMDD-001, auto-reset
- Held Order Expiration: 4 hours
- Max Held Orders per Employee: 5

## 🧪 Testing

### Quick Test Workflow
1. Login as `admin / CatchTheWave!`
2. Navigate to Dashboard - verify KPIs show 0.00 LYD (no sales yet)
3. Go to POS screen
4. Select "Seafood Platters" category
5. Add "Grilled Shrimp Platter" to order
6. Click "PAY CASH" to complete transaction
7. Return to Dashboard - verify KPIs updated with sale
8. Test weight-based item: "Grilled Fish" → "Grilled Sea Bass"
9. Enter weight (e.g., 1.5 kg), verify price calculation
10. Logout → Enter actual cash count → Verify variance

### Employee Test
1. Login as `ahmed / 123456`
2. POS screen opens directly (no admin navigation)
3. Complete a sale
4. Try "Discount" button → Admin PIN required (1234)
5. Logout → Cash reconciliation modal appears

## 📦 Production Build

To create a standalone Windows executable:

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name="DiBonoERP" --icon=assets/icon.ico main.py
```

The executable will be in `dist/DiBonoERP.exe`.

## 🐛 Known Limitations

- Inventory Management screen: UI placeholder only (database fully functional)
- Menu Management screen: UI placeholder only (seed data demonstrates structure)
- Employee Management screen: UI placeholder only (session tracking works)
- Reports screen: UI placeholder only (dashboard shows core KPIs)
- Printing: ESC/POS integration defined in plan, not implemented
- Cash Drawer: Hardware pulse logic defined, not implemented
- Split Payment: Database ready, UI simplified to single payment type

## 📝 License

Proprietary software for DiBono Seafood Restaurant, Tripoli, Libya.

## 🤝 Support

For technical support or feature requests, contact the development team.

---

**Built with ❤️ for the freshest catch in Tripoli** 🦞🐟🦐
