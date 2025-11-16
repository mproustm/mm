Python Desktop App for a Seafood Restaurant (DiBono)
================================================

Actors
------
- **Admin**: Owns end-to-end restaurant operations, manages stock, menu, staff, and reviews analytical reports.
- **Employee**: Front-of-house or cashier role. Needs a high-speed POS, limited to selling, ticket printing, and logging out.

Shared Experience Principles
----------------------------
- Elevated, animated visuals (floating bubbles, moving seaweed silhouettes) but never at the expense of snappy navigation.
- Warm blue/teal palette with coral accents, custom typography matching DiBono branding.
- Consistent iconography and high-contrast typography for readability in dimly lit dining rooms.
- Hardware support: all transactional flows end with optional kitchen receipt print + auto-triggered cash drawer pulse.

Data Layer Architecture
-----------------------
- SQLite database file `dibono.db` sits next to the application; SQLAlchemy manages tables and sessions.
- Tables: `users`, `inventory_items`, `menu_categories`, `menu_items`, `menu_item_ingredients`, `purchase_orders`, `purchase_order_items`, `waste_logs`, `sales_snapshots`, `report_points`, `orders`, `order_items`, `sessions`, `suppliers`, `physical_counts`, `held_orders`.
- Seeding runs automatically on first launch, inserting seafood-focused fixtures plus a **hard-configured admin** (`admin / CatchTheWave!`) and two employees.
- Menu definitions map to inventory SKUs via junction tables so ingredient depletion, COGS, and reporting stay accurate.
- Reporting tables store time-series snapshots, ensuring the dashboard and charts stay responsive even with large order volumes.

Transaction Schema & Order Lifecycle
------------------------------------
- **orders table**: id, employee_id, order_number (daily sequential), timestamp, subtotal, tax_amount, service_charge, discount_amount, total, payment_method (cash/card/split), status (active/completed/voided), voided_by, void_reason.
- **order_items table**: id, order_id, menu_item_id, item_name (snapshot), quantity, weight_kg, unit_price, modifiers_json, line_total.
- **Order lifecycle**: Orders start as 'active' in POS memory (not DB), commit to DB only on payment completion as 'completed', or save as 'voided' with admin approval.
- **Order numbers**: Reset daily, format YYYYMMDD-001, YYYYMMDD-002, etc.
- **Split payment**: Single order can have payment_method='split' with additional `cash_amount` and `card_amount` columns.

Inventory Depletion Logic
-------------------------
- **On order completion**: For each order_item, subtract (quantity × recipe_ingredient_qty) or (weight_kg × recipe_per_kg_qty) from inventory_items.on_hand.
- **Negative stock rule**: Sales are BLOCKED if any ingredient would go below zero; POS shows "Insufficient stock: [ingredient]" error.
- **Void restoration**: When order status changes to 'voided', add ingredients back to inventory using same calculation in reverse.
- **Physical count adjustments**: Variance screen allows admin to set inventory_items.on_hand to actual counted value; difference logged to report_points as 'variance' type.

Session & Cash Reconciliation
-----------------------------
- **sessions table**: id, user_id, login_time, logout_time, orders_count, cash_sales, card_sales, total_sales, expected_cash, actual_cash, variance.
- **Session start**: Login creates session record with login_time, opens with zero totals.
- **During shift**: Every completed order increments session totals (orders_count, cash_sales or card_sales, total_sales).
- **Session end**: Logout button triggers cash count modal (for employees with cash transactions), admin enters actual_cash, variance = actual_cash - expected_cash, prints shift report, sets logout_time.
- **Expected cash**: Sum of all cash payments in this session (excludes card transactions).

Business Rules & Constants
--------------------------
- **Tax rate**: 0% (Libya VAT exempt for food; field reserved for future).
- **Service charge**: 0% default (can be toggled per order by admin override).
- **Weight rounding**: Display and calculate to 0.01 kg precision (two decimals).
- **Currency**: All monetary values stored as INTEGER (fils/cents: 1 LYD = 1000 fils) to avoid floating-point errors; display divides by 1000.
- **Admin PIN**: Hard-configured as '1234' for override actions (Discount, Void, Open Drawer); validates against users table where role='admin'.
- **Price formula for weight items**: `ROUND((base_price_per_kg × weight_kg), 2)` yields line_total in LYD.
- **Discount**: Percentage (5%, 10%, 15%) or fixed amount; stored as positive integer in fils, subtracted from subtotal before tax.
- **Held orders**: Stored in held_orders table with items_json; auto-expire after 4 hours; max 5 holds per employee.

Login Page
----------
- Highly animated marine background (e.g., layered parallax fish shoals) with DiBono logo centered.
- Required inputs: username, password, a large "Login" CTA. Optional "Remember me" toggle for Admin workstations only.
- Security: credentials sent via encrypted channel, three failed attempts trigger subtle shake animation + alert copy.

```
.-------------------------------------------------------------.
|  Animated ocean backdrop (looping waves + light caustics)    |
|                                                             |
|            ________            DiBono Seafood               |
|           /  LOGO  \                                          |
|                                                             |
|  [ Username ____________________________ ]                   |
|  [ Password ____________________________ ]                   |
|  ( ) Remember me        [ Login ▶ ]                          |
|                                                             |
|        "Serving the freshest catch in Tripoli" tagline       |
'-------------------------------------------------------------'
```

Admin Workspace (Sidebar Navigation)
------------------------------------
- Fixed left rail with bilingual labels (Arabic primary, English secondary) for: لوحة التحكم, إدارة المخزن, إدارة قائمة الطعام, إدارة الموظفين, إدارة التقارير.
- Right content canvas scrolls; cards and tables respond to window resizing.

Dashboard (لوحة التحكم)
-----------------------
- Nine KPI cards arranged 3x3, grouped by payment medium (cash, card, total revenue) and timeframe (day/week/month).
- Each card displays value (LYD), delta vs previous period, and micro-sparkline.
- "Payment Mix" chart: QtCharts bar chart summarizing day totals for cash vs card vs overall revenue, giving instant visual context.

```
.---------------- Admin Dashboard -----------------------------.
| Sidebar | [Cash Day] [Cash Week] [Cash Month]                |
|         | [Card Day] [Card Week] [Card Month]                |
|         | [Revenue Day] [Revenue Week] [Revenue Month]       |
|         |----------------------------------------------------|
|         |  Bottom area holds mini bar chart by hour +        |
|         |  toggle between LYD and % growth.                  |
'---------'----------------------------------------------------'
```

Inventory Management (إدارة المخزن)
-----------------------------------
- Visual aesthetic: illustrated warehouse mural behind semi-transparent tables, animated ingredient icons drifting subtly.
- Functional blocks:
	- **Inventory Tracking**: master table with SKU, unit, min/max thresholds, cost, on-hand qty. Real-time updates from POS deductions.
	- **Supplier & Purchases**: form to log supplier, PO number, expected delivery. Confirmed deliveries feed Inventory table with batch metadata.
	- **Sales & Usage Sync**: listener on POS events subtracts recipe ingredients per dish, creating theoretical stock level.
	- **Waste & Spoilage**: modal to log discarded quantity + reason + photo. Entries affect variance calculations.
	- **Variance & COGS Analytics**: comparison widget showing theoretical vs physical count, highlighting discrepancies and COGS trendline.

```
.---------------- Inventory Canvas -----------------------------.
| Sidebar |  Warehouse Sketch Background (faded)               |
|         |  ┌Inventory Grid────────────────────────────┐     |
|         |  | Item | Unit | On-hand | Min | Cost | ⚠︎ |     |
|         |  └──────────────────────────────────────────┘     |
|         |  [Receive Stock ▶]  [Log Waste ▶]                 |
|         |  Supplier Timeline: ─■───■── delivery markers     |
|         |  Variance Dial: [ |||  | ]                        |
'---------'----------------------------------------------------'
```

Menu Management (إدارة قائمة الطعام)
------------------------------------
- Uses inventory ingredients as building blocks; categories (e.g., Breakfast, Pasta, Seafood Platters) appear as draggable chips.
- Feature set:
	- Create/Edit categories with icon, color, availability windows.
	- Define menu items with multilingual names, description, base price, ingredient matrix (qty per serving), optional add-ons tied to inventory.
	- Preview POS tile appearance before publishing.

```
.---------------- Menu Builder --------------------------------.
| Sidebar |  Category Chips: [Breakfast] [Pasta] [Seafood]     |
|         |  Selected Item Card:                               |
|         |  ---------------------------------------------     |
|         |  |Name: Lobster Pasta     | Price: 65 LYD |        |
|         |  |Add-ons: +Extra Sauce   | +Garlic Bread|        |
|         |  |Ingredients Matrix:                        |    |
|         |  | Flour 0.2kg | Tomato 0.1kg | Lobster 0.3kg |    |
|         |  ---------------------------------------------     |
'---------'----------------------------------------------------'
```

Employee Management (إدارة الموظفين)
-------------------------------------
- Table of employees including username, full name, role, salary, shift blocks.
- Activity logs show session start/end timestamps, orders handled, LYD totals by day/week/month/year.
- Export option for payroll or HR review.

```
.---------------- Employee Console ----------------------------.
| Sidebar |  Employees Table                                   |
|         |  | Username | Name | Shift | Salary | Status |     |
|         |  ------------------------------------------------  |
|         |  Activity Ledger (per employee):                   |
|         |  Day ▒▒▒  Week ▓▓▓  Month ███ trend bars           |
|         |  [Add Employee] [Reset Password] buttons           |
'---------'----------------------------------------------------'
```

Report Management (إدارة التقارير)
-----------------------------------
- Multi-tab analytics (Money, Popular Items, Peak Hours, Most Ordered, etc.).
- Filters for hour/day/week/month/year, export to PDF/Excel.
- Visualizations: QtCharts renders the core line/area trends (revenue by hour) with additional placeholders for stacked bars and heatmaps as datasets expand.

```
.---------------- Reporting Suite -----------------------------.
| Sidebar |  Tabs: [Money] [Popular Items] [Peak Hours] ...    |
|         |  Date Selector: |◀ Week ▶|   | Export |            |
|         |  Chart Area:                                         |
|         |   ┌────────────────────────────────────────┐       |
|         |   | $$$ Revenue Line + markers             |       |
|         |   | Heatmap grid (hours vs days)           |       |
|         |   └────────────────────────────────────────┘       |
|         |  KPI Row: Avg ticket, most ordered dish, etc.      |
'---------'----------------------------------------------------'
```

Employee Screens
----------------

Point of Sale (POS)
~~~~~~~~~~~~~~~~~~~
- Grid of menu tiles grouped by category; selecting item opens modifier drawer for weight/portion adjustments (e.g., whole fish weight input).
- Order summary panel with running total, taxes, service charge if applicable.
- Action buttons: Hold, Void, Discount (permissions tied to Admin), Print Kitchen Ticket, Cash/Card settlement.
- Integrated scale/weight field for seafood sold by weight.

```
.---------------- Employee POS --------------------------------.
| Categories: [Seafood] [Pasta] [Drinks]                       |
| Menu Tiles: [ Lobster 🦞 ] [ Shrimp Tray ] [ Fish Soup ]     |
| Modifier Drawer (right slide):                               |
|  Weight (kg): [ 0.00 ]  -> auto price update                 |
| Order Summary:                                               |
|  #  Item            Qty  Price   Total                      |
|  1  Lobster Pasta   1    65      65                         |
|  Subtotal: 65  Tax: 0  Grand: 65                           |
|  [Cash] [Card] [Print Ticket] [Hold] [Logout]               |
'--------------------------------------------------------------'
```

Logout Confirmation
-------------------
- Triggered from POS top bar; modal overlay ensures accidental taps are avoided.
- Displays active session duration and requires explicit confirmation.

```
.---------------- Logout Modal -------------------------------.
|  You are ending your shift (02:15:43 elapsed).               |
|  Pending orders: 0                                          |
|  [Cancel]        [Confirm Logout + Print Shift Report]      |
'-------------------------------------------------------------'
```

Printing & Cash Drawer Integration
----------------------------------
- Every payment flow calls a hardware service that:
	1. Formats receipt (logo, order items, payment method, employee name, timestamps).
	2. Sends ESC/POS commands to receipt printer.
	3. Pulses cash drawer via printer kick port for cash transactions only.
- POS also supports manual "Reprint" and "Open Drawer" actions with Admin authentication.

```
.------------ Hardware Service Diagram -----------------------.
| POS Action -> Print Queue -> ESC/POS Renderer -> Printer     |
|                                     ↘ Drawer Pulse (Cash)    |
'-------------------------------------------------------------'
```

Seafood Context
---------------
- Inventory and menu emphasize seafood staples (lobster, shrimp, octopus, fish) plus pasta sides. Ingredient depletion, cost calculation, and reporting all assume these SKUs.

Technology Stack
----------------
- **Python 3.11+** with PyQt6 for UI framework, QtCharts for visualizations.
- **SQLAlchemy 2.x** ORM with sqlite3 driver; database in WAL mode for concurrency.
- **passlib with bcrypt** for password hashing.
- **python-escpos** for receipt printing via USB/network printers.
- **Packaging**: PyInstaller for standalone Windows .exe with bundled Python runtime.

All functionality above remains within the requested feature set, expanded for implementation clarity and visual guidance.