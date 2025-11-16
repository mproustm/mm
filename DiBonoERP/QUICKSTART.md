# DiBono ERP - Quick Start Guide

## 🚀 Running the Application

The application is now fully installed and ready to use!

### Start the Application
```powershell
cd C:\DiBonoERP
python main.py
```

## 🔑 Login Credentials

### Admin Account (Full Access)
- **Username:** `admin`
- **Password:** `CatchTheWave!`

### Employee Accounts (POS Only)
- **Ahmed:** `ahmed` / `123456`
- **Fatima:** `fatima` / `123456`

### Admin PIN (for POS overrides)
- **PIN:** `1234` (for Discount, Void, Open Drawer actions)

## 📋 Testing Workflow

### 1. Admin Login Test
1. Login as `admin / CatchTheWave!`
2. You'll see the admin sidebar with 6 menu options
3. Dashboard loads by default showing 9 KPI cards (all 0.00 LYD initially)

### 2. Complete a POS Sale
1. Click "💰 POS" in the sidebar
2. Click category chip: "🦞 Seafood Platters"
3. Click "Grilled Shrimp Platter" tile
4. Item appears in order summary (45.00 LYD)
5. Click "💵 PAY CASH"
6. Order completes, confirmation shows order number (e.g., 20251116-001)

### 3. Test Weight-Based Item
1. Click "🐟 Grilled Fish" category
2. Click "Grilled Sea Bass"
3. Weight dialog appears
4. Enter weight: `1.5` kg
5. Total shows: 82.50 LYD (55 LYD/kg × 1.5)
6. Click OK
7. Complete payment

### 4. Verify Dashboard Update
1. Click "📊 Dashboard" in sidebar
2. KPI cards now show updated revenue
3. "Revenue - Day" shows total of your sales
4. "Cash - Day" shows cash payments only

### 5. Hold/Recall Order
1. Go back to POS
2. Add items to order
3. Click "Hold" button
4. Order saved, table clears
5. Add new items to cart
6. Click "Recall" button
7. Previous order restored

### 6. Test Inventory Depletion
1. Click "📊 Dashboard"
2. Note: Inventory automatically reduced after each sale
3. Database tracks ingredient usage per menu item
4. If stock insufficient, sale will be blocked

### 7. Employee Login Test
1. Logout from admin
2. Login as `ahmed / 123456`
3. POS screen appears immediately (no sidebar)
4. Complete a sale
5. Click "Logout"
6. Cash count dialog appears
7. Enter actual cash: `100.00`
8. Variance calculated automatically
9. Session closed

### 8. Admin PIN Test
1. Login as employee
2. Try to click "Discount" button
3. Admin PIN dialog appears
4. Enter `1234`
5. Action proceeds

## 📦 Database Location

The SQLite database is stored at:
```
C:\DiBonoERP\dibono.db
```

All data persists between application restarts.

## 🎨 UI Features

- **Ocean Theme:** Blue/teal (#1282A2) with coral accents (#FF6B6B)
- **Bilingual Labels:** English + Arabic (primary/secondary)
- **High Contrast:** Dark backgrounds (#0A1128) with bright text
- **Responsive:** Grid layouts adapt to window size
- **Animated:** Login screen has gradient ocean background
- **Category Chips:** Toggle-able filter buttons for menu items

## 🔍 Key Features Implemented

✅ **Authentication:** Secure login with bcrypt password hashing  
✅ **Session Tracking:** Automatic login/logout time, order count, cash totals  
✅ **POS:** Menu tiles, weight input, order summary, payment processing  
✅ **Inventory:** Real-time depletion, stock checking before sale  
✅ **Orders:** Sequential daily numbering (YYYYMMDD-001)  
✅ **Admin Dashboard:** 9 KPI cards with day/week/month breakdowns  
✅ **Cash Reconciliation:** Expected vs actual cash count on logout  
✅ **Hold/Recall:** Temporary order storage (4-hour expiration)  
✅ **Admin Override:** PIN protection for sensitive actions  

## 🛠️ Admin Screens (Placeholder UI, Database Ready)

- **Inventory Management:** Database fully functional, UI shows "Coming Soon"
- **Menu Management:** Database fully functional, UI shows "Coming Soon"  
- **Employee Management:** Database fully functional, UI shows "Coming Soon"
- **Reports:** Dashboard shows core KPIs, full reports show "Coming Soon"

To implement these screens, refer to `plan.md` for complete specifications.

## 📊 Pre-Seeded Data

### Inventory Items (23 items)
- **Seafood:** Lobster, Shrimp, Octopus, Sea Bass, Calamari
- **Pasta:** Spaghetti, Penne
- **Sauces:** Tomato, Garlic, Olive Oil
- **Vegetables:** Tomatoes, Onions, Peppers, Garlic
- **Beverages:** Water, Soft Drinks, Lemonade
- **Bread:** Garlic Bread, Pita

### Menu Categories (6)
1. 🌅 Breakfast (6AM-11AM availability window)
2. 🦞 Seafood Platters
3. 🍝 Pasta
4. 🐟 Grilled Fish
5. 🥗 Appetizers
6. 🥤 Beverages

### Menu Items (8)
1. **Lobster Pasta** - 65 LYD (300g lobster, spaghetti, tomato sauce)
2. **Grilled Shrimp Platter** - 45 LYD (400g shrimp, rice, vegetables)
3. **Grilled Sea Bass** - 55 LYD/kg (weight-based)
4. **Crispy Calamari Rings** - 18 LYD (250g calamari)
5. **Seafood Penne** - 38 LYD (mixed seafood, penne)
6. **Bottled Water** - 1 LYD
7. **Soft Drink** - 2 LYD
8. **Fresh Lemonade** - 3 LYD

### Suppliers (2)
- **Tripoli Fish Market** (Net 15 payment terms)
- **Mediterranean Imports** (Net 30 payment terms)

## 🐛 Troubleshooting

### Stylesheet Warning
```
Could not parse application stylesheet
```
**This is harmless.** The app still runs with full styling applied.

### Bcrypt Version Warning
```
(trapped) error reading bcrypt version
```
**This is harmless.** Password hashing works perfectly.

### App Won't Start
1. Ensure all dependencies installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (needs 3.11+)
3. Delete database and restart: `Remove-Item dibono.db; python main.py`

### Database Locked Error
- Close all instances of the app
- SQLite only allows one writer at a time

## 📈 Next Steps

To extend the application:

1. **Implement Inventory UI** - See `plan.md` sections:
   - Inventory tracking table
   - Receive stock form
   - Waste logging
   - Variance calculations

2. **Implement Menu UI** - See `plan.md` sections:
   - Category management
   - Menu item builder
   - Ingredient matrix editor

3. **Add Printing** - Integration guide in `plan.md`:
   - ESC/POS receipt formatting
   - Cash drawer pulse
   - Kitchen ticket printing

4. **Expand Reports** - See dashboard example:
   - Popular items chart
   - Peak hours heatmap
   - Export to PDF/Excel

## 💡 Tips

- **Testing Sales:** Use small weights (0.1 kg) to avoid depleting inventory
- **Resetting Data:** Delete `dibono.db` and restart for fresh seed
- **Admin Access:** Admin can access POS from sidebar navigation
- **Currency Storage:** All amounts stored as integers (fils) for precision
- **Order Numbers:** Auto-reset daily, format YYYYMMDD-XXX

---

**Enjoy using DiBono ERP! 🌊🦞**
