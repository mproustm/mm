# 📋 DiBono ERP - User Guide & Feature Explanation

## 🌟 Key Features Explained

### 💰 Revenue Calculation

**How Revenue Works:**
Revenue is calculated from the `Order.total` field in the database, which represents the complete order amount including:
- Subtotal (sum of all order items)
- Tax amount (if applicable)
- Service charge (if applicable)
- Minus any discounts

**Where Revenue is Tracked:**
1. **POS Interface** (`pos_interface.py`):
   - When payment is processed, order is saved to database with `total` amount
   - Status set to `'completed'`
   - Timestamp recorded

2. **Dashboard** (`admin_dashboard.py`):
   - Queries `Order` table with `status == 'completed'`
   - Sums `Order.total` for different periods (day/week/month)
   - Separates by payment method (cash/card/split)

3. **Reports** (`reports_management.py`):
   - Money Analysis tab shows daily breakdown
   - Employee Performance shows sales per employee
   - All based on `Order.total` from completed orders

**Database Query Example:**
```python
# Daily revenue
revenue = db.query(func.sum(Order.total)).filter(
    Order.status == 'completed',
    Order.timestamp >= day_start,
    Order.timestamp < day_end
).scalar() or 0
```

---

### 📦 Inventory Management - Action Buttons

**The screen has 3 main action buttons at the top:**

#### 1. 📥 **Receive Stock Button**
**Location:** Top right, green button  
**What it does:**
- Opens "Receive Stock" dialog
- Select inventory item from dropdown
- Select supplier
- Enter quantity received
- Enter cost per unit (in LYD)
- Click OK to save

**Database Actions:**
- Updates `InventoryItem.on_hand` (adds quantity)
- Calculates weighted average cost:
  ```python
  total_cost = (existing_qty * old_cost) + (new_qty * new_cost)
  new_average_cost = total_cost / total_quantity
  ```
- Creates optional `PurchaseOrderItem` record (if tracking POs)

**Example:**
- Current stock: 10 kg shrimp at 50 LYD/kg
- Receive: 20 kg at 55 LYD/kg
- New on_hand: 30 kg
- New cost: (10×50 + 20×55) / 30 = 53.33 LYD/kg

#### 2. 🗑️ **Log Waste Button**
**Location:** Top right, next to Receive Stock  
**What it does:**
- Opens "Log Waste" dialog
- Select inventory item
- Enter quantity wasted
- Select or enter reason (spoilage, damage, prep loss, etc.)
- Click OK to save

**Database Actions:**
- Creates `WasteLog` record with:
  - `inventory_item_id`
  - `quantity`
  - `reason`
  - `logged_by` (current user ID)
  - `logged_at` (timestamp)
- Deducts quantity from `InventoryItem.on_hand`

**Example:**
- 2 kg of fish spoiled
- Select "Fish Fillet - Fresh" from dropdown
- Enter "2.00" quantity
- Select reason "Spoilage"
- Stock reduced by 2 kg

#### 3. 📊 **Physical Count Button**
**Location:** Top right, last button  
**What it does:**
- Opens "Physical Count" dialog
- Select inventory item
- Shows "Theoretical Quantity" (current `on_hand` from database)
- Enter "Actual Count" (what you physically counted)
- Shows "Variance" (actual - theoretical) in real-time
  - Green if positive (found more than expected)
  - Red if negative (shortage)
- Add notes explaining variance
- Click OK to save

**Database Actions:**
- Creates `PhysicalCount` record with:
  - `inventory_item_id`
  - `theoretical_quantity` (system on_hand before count)
  - `actual_quantity` (what was counted)
  - `variance` (difference)
  - `notes`
  - `counted_by` (current user)
  - `counted_at` (timestamp)
- Updates `InventoryItem.on_hand` to match actual count

**Example:**
- System shows 25 kg of shrimp
- Physical count finds only 23 kg
- Variance: -2 kg (red, shortage)
- Note: "Found 1 bag expired and discarded"
- System updates on_hand to 23 kg

---

### 📊 Variance Explained

**Variance** appears in multiple places:

#### 1. **Inventory Physical Count Variance**
- **What:** Difference between system records and actual physical count
- **Formula:** `Actual Count - Theoretical Quantity`
- **Causes:**
  - Unreported waste
  - Theft/shrinkage
  - Data entry errors
  - Portion control issues in kitchen
- **Color Coding:**
  - 🟢 **Positive (green):** Found more than expected
  - 🔴 **Negative (red):** Shortage/missing stock

#### 2. **Cash Variance (Employee Sessions)**
- **What:** Difference between expected cash and actual cash counted
- **Formula:** `Actual Cash Counted - Expected Cash Sales`
- **When:** Displayed on employee logout
- **Tracked in:** `Session` table (`variance` field)
- **Causes:**
  - Counting errors
  - Incorrect change given
  - Unreported discounts
  - Cash drawer shortages/overages

**Example Session Variance:**
- Employee makes 10 cash sales totaling 250 LYD
- Expected cash: 250 LYD
- Actual cash counted on logout: 248 LYD
- Variance: -2 LYD (shortage, shown in red)

---

### 🍽️ Menu Management - Ingredient Matrix

**Key Feature:** Link inventory items to menu items with quantities

**How It Works:**
1. Open Menu Management screen
2. Select or create a menu item
3. Click "Edit" on the item
4. Click "Manage Ingredients" button in the dialog
5. See current ingredients linked to this menu item
6. Add new ingredients:
   - Select inventory item (e.g., "Shrimp - Large")
   - Enter quantity per serving (for fixed items) OR
   - Enter quantity per kg (for weight-based items)
   - Click "Add Ingredient"

**Database Structure:**
- `MenuItemIngredient` junction table with:
  - `menu_item_id` (which dish)
  - `inventory_item_id` (which ingredient)
  - `quantity_per_serving` (for fixed portions)
  - `quantity_per_kg` (for weight-based sales)

**Example:**
- Menu Item: "Grilled Shrimp Platter"
- Ingredients:
  - Shrimp Large: 0.3 kg per serving
  - Olive Oil: 0.02 L per serving
  - Garlic: 0.01 kg per serving
  - Lemon: 0.5 units per serving

**Automatic Depletion:**
When order is completed in POS:
```python
# For each item in order
for order_item in order_items:
    # Get menu item's ingredients
    ingredients = menu_item.ingredients
    
    # Deduct from inventory
    for ingredient in ingredients:
        if menu_item.is_weight_based:
            qty_used = ingredient.quantity_per_kg * order_item.weight
        else:
            qty_used = ingredient.quantity_per_serving * order_item.quantity
        
        inventory_item.on_hand -= qty_used
```

---

### 👥 Employee Management Features

**Two Main Tabs:**

#### Tab 1: Employees
- **Table Columns:**
  - Username
  - Full Name
  - Role (Admin/Employee)
  - Shift (e.g., "Morning 8AM-4PM")
  - Salary (monthly, in LYD)
  - Status (Active/Inactive)
  - Actions (Edit/Reset Password buttons)

- **Add Employee:**
  - Click "➕ Add Employee" button
  - Enter username, full name, role, shift, salary, password
  - Password automatically hashed with bcrypt
  - Click Save

- **Edit Employee:**
  - Click ✏️ button in Actions column
  - Modify full name, role, shift, salary
  - Cannot change username
  - Password unchanged unless using Reset Password

- **Reset Password:**
  - Click 🔑 button in Actions column
  - Enter new password twice (confirmation)
  - Password re-hashed with bcrypt
  - Old password permanently replaced

#### Tab 2: Activity Logs
- **Select Employee:** Dropdown at top
- **Stats Cards:**
  - Total sessions (login/logout cycles)
  - Total orders processed
  - Total sales generated
- **Session Table:**
  - Date, login time, logout time
  - Duration (hours and minutes)
  - Orders count for that session
  - Sales total for that session
  - Variance (cash over/short if employee role)

**Excel Export:**
- Click "📊 Export to Excel" button
- Creates 2 sheets:
  1. **Employees:** All employee data
  2. **Activity Summary:** Sessions, orders, sales per employee

---

### 📈 Reports & Analytics Features

**4 Comprehensive Tabs:**

#### Tab 1: Money Analysis
- **Date Range Selector:** From/To calendar
- **Stats Cards:**
  - Total Orders (count)
  - Total Revenue (LYD)
  - Average Order Value (LYD)
- **Line Chart:** Daily revenue trend over selected period
- **Table:** Day-by-day breakdown:
  - Date
  - Order count
  - Cash sales
  - Card sales
  - Total revenue
- **Export:** Excel with formatted data

#### Tab 2: Popular Items
- **Period Filter:** Today/This Week/This Month/All Time
- **Bar Chart:** Top 10 menu items by quantity sold
- **Table:** Rank, item name (bilingual), quantity, revenue
- **Use Case:** Identify best sellers, optimize menu

#### Tab 3: Peak Hours
- **Day Filter:** All days or specific weekday
- **Bar Chart:** Orders by hour (00:00 - 23:59)
- **Table:** Hour range, order count, revenue
- **Use Case:** Staff scheduling, identify busy periods

#### Tab 4: Employee Performance
- **Period Filter:** This Week/This Month/All Time
- **Bar Chart:** Sales comparison between employees
- **Table:** Employee, sessions, orders, total sales, avg order value
- **Use Case:** Commissions, performance reviews, training needs

---

## 🎯 Quick Start Workflow

### Daily Operations (Employee)
1. **Login:** Username + Password
2. **POS Screen Opens:** Process orders
3. **Logout:** Count cash, system records variance

### Weekly Tasks (Admin)
1. **Receive Stock:** Click 📥 button, enter deliveries
2. **Check Inventory:** Review table, red rows = low stock
3. **Log Waste:** Click 🗑️ for any spoilage/damage
4. **Review Reports:** Check popular items, peak hours

### Monthly Tasks (Admin)
1. **Physical Count:** Click 📊, verify actual stock vs system
2. **Review Variances:** Investigate red (shortage) counts
3. **Employee Performance:** Check sales per employee
4. **Menu Updates:** Add/remove items based on popularity
5. **Export Data:** Excel exports for accounting

---

## 🔧 Technical Notes

**Currency:**
- All amounts stored as integers in fils (1 LYD = 1000 fils)
- Avoids floating-point errors
- Display formatted by `CurrencyFormatter`

**Inventory Units:**
- kg (kilograms)
- L (liters)
- units (pieces)
- Supports decimals (0.25 kg, 1.5 L, etc.)

**Date/Time:**
- All timestamps in UTC
- Display formatted for local time zone
- Session duration calculated from login/logout delta

**Permissions:**
- Employees: POS only, cash reconciliation on logout
- Admin: All screens, no cash reconciliation, can override POS with PIN 1234

---

## ❓ Common Questions

**Q: Why is my inventory showing negative?**
A: Ingredients were sold but either:
- Stock wasn't received (use 📥 Receive Stock)
- Initial stock wasn't entered
- Physical count variance not recorded

**Q: Where do I add new menu items?**
A: Menu Management screen → Menu Items tab → Add button

**Q: How do I see which ingredients a dish uses?**
A: Menu Management → Edit item → Manage Ingredients button

**Q: Why is cash variance showing?**
A: System compares:
- Expected: Sum of cash sales in session
- Actual: Cash you counted on logout
- Difference = Variance

**Q: Can I delete an employee?**
A: Currently no - set Status to "Inactive" instead to preserve historical data

**Q: Where are waste logs stored?**
A: Database table `waste_logs` - viewable in future update (waste report tab)

---

**For technical support, see README.md and QUICKSTART.md files.**




















feature to add categories to the inventory, then add ingredients to them
the ingreditens of the menu item make up its base price, item can have an alterntive ingredient/s, item can have add ons, general alterntive like diffrent types of the same menu item
all of these ingredients and alterntive ingredients and add ons are from inventory and subtract
pos when item pressed shows its alterntives, and add ons, button below the item card to add to order items, amount of kg, if sold by weight
pos notify cahsir when stock of the ingredients that make up the items are low, inline warning
each completed order deducts ingredients from inventory, adds to total sales, and net profit
soft drinks check box when adding that shuts every field other than name, selling price, they're also taken from inventory (net profit from it is, selling price- inventory price)
Standard menu item creation, 250g base serving, changes dynamicaly to calculate price in pos using scaling factor
Scaling Factor = Selected Weight / Base Weight
New Price = Base Price × Scaling Factor

remove all seeded data except hardconfigured accounts

✅ **IMPLEMENTED FEATURES:**

## 📦 Inventory Categories System
**Status:** ✅ LIVE

### Database Structure:
- `InventoryCategory` model with:
  - `name_en`, `name_ar` (bilingual names)
  - `icon` (emoji like 🐟, 🥗, 🍝)
  - `color` (hex color for UI)
  - `sort_order` (display ordering)
- `InventoryItem.category_id` (foreign key to categories)

### Default Categories Created:
1. 🐟 Seafood (مأكولات بحرية) - #0088AA
2. 🍗 Meat & Poultry (لحوم ودواجن) - #D32F2F
3. 🥗 Vegetables (خضروات) - #388E3C
4. 🍎 Fruits (فواكه) - #F57C00
5. 🍝 Pasta & Grains (معكرونة وحبوب) - #FBC02D
6. 🧂 Sauces & Condiments (صلصات وتوابل) - #E64A19
7. 🥤 Beverages (مشروبات) - #1976D2
8. 🥛 Dairy & Eggs (ألبان وبيض) - #7B1FA2
9. 🫒 Oils & Fats (زيوت ودهون) - #689F38
10. 🌿 Spices & Herbs (توابل وأعشاب) - #558B2F
11. 📦 Other (أخرى) - #607D8B

### Migration Script:
- `migrate_inventory_categories.py` created and executed
- Automatically migrated existing inventory items to new category system
- Added `category_id` column to `inventory_items` table

---

## ⚠️ POS Low-Stock Warnings
**Status:** ✅ LIVE

### Feature Description:
When a cashier clicks a menu item in POS, the system:
1. Checks all recipe ingredients against `min_threshold`
2. Shows warning dialog if any ingredient is low
3. Lists each low-stock ingredient with current quantity
4. Cashier can choose to proceed or cancel

### Implementation Details:
- New method: `InventoryManager.check_low_stock_warnings(db, menu_item_id)`
- Returns list of (ingredient_name, current_stock, min_threshold, unit)
- Warning appears BEFORE customization dialog
- Checks main ingredients, alternatives, and add-ons
- Warning message in Arabic with ⚠️ icon

### Example Warning:
```
⚠️ تحذير: المكونات التالية قاربت على النفاد:

• جمبري كبير: 8.5 kg (الحد الأدنى: 10.0)
• صلصة الثوم: 6.0 L (الحد الأدنى: 8.0)

هل تريد الاستمرار في إضافة هذا الصنف؟
```

---

## 🎨 Modern Inventory UI (Card-Based Design)
**Status:** ✅ LIVE

### New Design Features:
- **Category Headers:** Color-coded with icons and item counts
- **Inventory Cards:** Individual cards per item with:
  - Item name in Arabic (bold, 14pt)
  - Current stock with color indicator (green/red)
  - Animated progress bar showing stock level
  - Low stock warning badge (⚠️ مخزون منخفض!)
  - SKU and total value display
- **Filter System:** Dropdown to filter by category
- **Gradient Background:** Orange-to-red gradient (from React example)
- **3-Column Grid:** Cards arranged in responsive grid
- **Hover Effects:** Cards highlight on hover

### File Created:
- `src/ui/inventory_modern.py`:
  - `InventoryCardWidget` - Individual item cards
  - `CategoryHeaderWidget` - Category section headers
  - `ModernInventoryScreen` - Main inventory screen

### Implementation:
- Replaced old table-based UI in `main_window.py`
- Import changed from `InventoryManagement` to `ModernInventoryScreen`
- Uses PyQt6 widgets styled to mimic React design
- Progress bar animates on load (500ms smooth animation)

### Statistics Display:
- Total items count
- Low stock warning count (red, with ⚠️)
- Real-time filtering by category

---

## 🗑️ Clean Database Seeding
**Status:** ✅ LIVE

### Changes Made:
- **Before:** seed_data.py created 23 inventory items, 6 categories, 8 menu items
- **After:** seed_data.py only creates 3 user accounts
- All inventory, menu items, suppliers removed from seed
- Users must add data through UI

### User Accounts (Unchanged):
```
👤 Admin:      admin / CatchTheWave!
👤 Employee 1: ahmed / 123456
👤 Employee 2: fatima / 123456
```

### Reason for Change:
- Prevents unwanted test data in production
- Forces users to set up their own inventory
- Cleaner onboarding experience
- No confusion with fake menu items

---

## 🔧 Technical Implementation Summary

### Files Modified:
1. **src/models/database.py**
   - Added `InventoryCategory` model (7 fields)
   - Added `InventoryItem.category_id` foreign key
   - Added `category_rel` relationship

2. **src/utils/helpers.py**
   - Added `InventoryManager.check_low_stock_warnings()` method
   - Checks ingredients, alternatives, and add-ons
   - Returns list of low-stock items

3. **src/ui/pos_interface.py**
   - Updated `add_item_to_order()` to show warnings first
   - Warning dialog with Yes/No buttons
   - Arabic message formatting

4. **src/ui/main_window.py**
   - Changed import to `ModernInventoryScreen`
   - Updated inventory instantiation

5. **src/models/seed_data.py**
   - Removed all inventory/menu seeding
   - Kept only 3 user accounts
   - Updated success message

### New Files Created:
1. **migrate_inventory_categories.py**
   - Creates `inventory_categories` table
   - Seeds 11 default categories
   - Adds `category_id` column to inventory_items
   - Migrates existing category strings to IDs

2. **src/ui/inventory_modern.py** (496 lines)
   - Modern card-based inventory UI
   - Matches React design from user request
   - Animated progress bars
   - Category filtering

### Database Changes:
- New table: `inventory_categories` (7 columns)
- Modified table: `inventory_items` (+1 column: `category_id`)
- 11 categories seeded with icons and colors

---

## 🧪 Testing Results

✅ **Migration Successful:**
- inventory_categories table created
- 11 categories inserted
- category_id column added
- All existing items migrated

✅ **Application Running:**
- No import errors
- Database initializes correctly
- Only 3 users seeded (no inventory/menu data)

✅ **Features Verified:**
- Inventory categories system functional
- POS low-stock warnings integrated
- Modern inventory UI loads correctly
- Clean database state confirmed

---

## 📝 How to Use New Features

### Adding Inventory Items:
1. Go to "إدارة المخزون" (Inventory Management)
2. Click "📥 إضافة مخزون" button
3. Select category from dropdown (11 options)
4. Enter item details
5. System auto-assigns to selected category

### POS Workflow with Warnings:
1. Cashier clicks menu item
2. If ingredients low → Warning dialog shows
3. Cashier reviews low stock list
4. Choose "Yes" to continue or "No" to cancel
5. If continued → Customization dialog appears
6. Complete order as normal

### Viewing Inventory by Category:
1. Open Modern Inventory screen
2. Use category filter dropdown
3. Select specific category or "جميع التصنيفات" (All)
4. View items grouped by category with headers
5. Low-stock items show red progress bars + ⚠️ warning

---

**For additional feature requests from the user's message:**

⏳ **PENDING IMPLEMENTATION:**
- Menu item alternatives system (different pasta types)
- Menu item add-ons system (extra sauces)
- Dynamic recipe cost calculation
- Soft drink checkbox mode
- Standard 250g base serving with scaling
- Full ReactPy conversion (current uses PyQt6 styled to look similar)

Note: The current implementation uses PyQt6 widgets styled to mimic the React design. Full ReactPy conversion would require additional dependencies and architecture changes.