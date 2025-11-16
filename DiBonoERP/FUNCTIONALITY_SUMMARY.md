
# DiBono ERP - Functionality Summary

## 1. High-Level Overview

**DiBono ERP** is a comprehensive, bilingual (Arabic/English) desktop application designed for managing a seafood restaurant in Tripoli, Libya. Built with Python and the PyQt6 framework, it provides a complete solution for point-of-sale, inventory control, menu configuration, employee management, and financial reporting. The application features a modern, ocean-themed user interface and is designed for high-speed, reliable operation in a restaurant environment.

---

## 2. Core Modules

### 🔐 Authentication & Session Management
- **Role-Based Access**: The system distinguishes between `Admin` and `Employee` roles.
  - **Admins** have full access to all modules, including configuration and reporting.
  - **Employees** are directed immediately to the POS screen for sales operations.
- **Secure Login**: User passwords are encrypted using `bcrypt`. Default accounts are provided for initial setup (`admin`/`CatchTheWave!`).
- **Session Tracking**:
  - Each employee login/logout is recorded as a `Session`.
  - The system tracks session duration, total orders processed, and total sales value.
  - **Cash Reconciliation**: Upon logout, employees must declare their cash-on-hand. The system compares this to the expected cash from sales and calculates any variance (over/short), which is logged for admin review.
- **Admin PIN**: A hard-coded PIN (`1234`) is required for sensitive POS actions like applying discounts or voiding orders, allowing admins to override standard employee permissions.

### 💰 Point of Sale (POS)
- **Table-First Workflow**: The POS interface starts with a visual `Table Selection` screen, where tables are color-coded by status (Available, Occupied, Reserved).
- **Dine-In & Takeaway**: Employees can select a table for a dine-in order or choose the "Takeaway" option, which bypasses table assignment.
- **Intuitive Order Entry**:
  - Menu items are displayed as large, clickable tiles, filtered by category.
  - **Weight-Based Pricing**: For items like fresh fish, the system prompts for weight (in kg) and calculates the price dynamically based on the pre-configured price-per-kg.
  - **Low-Stock Warnings**: If an ingredient for a selected menu item is below its minimum threshold, a warning is displayed to the cashier before the item is added to the order.
- **Order Management**:
  - **Hold/Recall**: Orders can be temporarily saved ("held") and recalled later, linked to a specific table.
  - **Payment Processing**: Supports Cash, Card, and Split payments.
  - **Automatic Inventory Depletion**: Upon successful payment, the system automatically deducts the corresponding ingredients from the inventory based on the menu item's recipe.

### 🪑 Table Management
- **Admin CRUD Interface**: Admins can create, edit, and deactivate restaurant tables, defining their number and seating capacity.
- **Visual Layout**: Both the admin and POS screens display a grid of custom-drawn, table-shaped buttons that reflect the real-time status of the restaurant floor.
- **Seamless Order Association**: When an occupied table is selected, its in-progress order is automatically loaded. When an order is paid, the associated table is automatically released and marked as "Available".

### 📦 Inventory Management
- **Modern, Card-Based UI**: Inventory items are displayed as visually informative cards, grouped by category. Each card includes:
  - An animated progress bar showing the current stock level relative to its capacity.
  - A low-stock warning badge.
  - Key details like SKU, unit, and total value.
- **Comprehensive Stock Operations**:
  - **Add Stock**: A simplified dialog allows for adding new inventory items or replenishing existing ones. It captures details like name, category, unit, quantity, cost, and thresholds, and auto-generates a unique SKU.
  - **Log Waste**: Enables tracking of spoiled or damaged goods, which deducts from on-hand stock and creates a `WasteLog` for auditing.
  - **Physical Count**: A tool for comparing the theoretical (system) stock count against the actual physical count, logging any variance and updating the stock level accordingly.
- **Cost Tracking**: The system calculates the `weighted average cost` for each item upon receiving new stock, ensuring accurate cost-of-goods-sold (COGS) data.

### 🍽️ Menu Management
- **Full Recipe Control**: Admins have complete control over the menu.
  - **Categories**: Create and manage menu categories with bilingual names, colors, and icons.
  - **Menu Items**: Define dishes with names, descriptions, and pricing. Items can be designated as fixed-price or weight-based.
  - **Ingredient Matrix**: The core of the menu system. Admins can link specific inventory items as ingredients to each menu item, defining the exact quantity used per serving. This linkage is what drives automatic inventory depletion.

### 👥 Employee Management
- **Employee Database**: Admins can manage a full list of employees, including their role, shift, and salary.
- **User Lifecycle**: Admins can add new employees, edit their details, and reset their passwords.
- **Activity Monitoring**: The "Activity Logs" tab provides a detailed view of each employee's performance, including:
  - A list of all their sessions with duration, order counts, and sales totals.
  - Key performance stats (total sessions, total orders, total sales).
  - Cash variance history from their session reconciliations.
- **Excel Export**: Employee data and activity logs can be exported to an Excel file for payroll or HR purposes.

### 📈 Reporting & Analytics
- **Admin Dashboard**: The default admin screen provides an at-a-glance view of the restaurant's financial health with 12 Key Performance Indicator (KPI) cards, including:
  - Revenue (Day, Week, Month) for Cash, Card, and Total.
  - **Net Profit** (Day, Week, Month), calculated after deducting estimated payment processing fees.
- **Comprehensive Reports**: A dedicated module with four tabs for deep-dive analysis:
  - **Money Analysis**: Tracks revenue trends over time with a line chart and a daily breakdown table.
  - **Popular Items**: Identifies best-selling dishes with a bar chart and ranked table.
  - **Peak Hours**: Visualizes customer traffic by hour of the day to optimize staffing.
  - **Employee Performance**: Compares sales figures across employees.
- **Data Export**: All reports can be exported to formatted Excel spreadsheets.

---

## 3. Database & Technology

- **Backend**: Python 3.11+
- **UI Framework**: PyQt6 with QtCharts for data visualization.
- **Database**: SQLite, managed via the SQLAlchemy 2.x ORM. The database file (`dibono.db`) is self-contained in the project directory.
- **Password Security**: `passlib` with `bcrypt` for hashing user passwords.
- **Dependencies**: Key libraries include `openpyxl` for Excel exports and `Pillow` for image handling.

---

## 4. User Guide & Workflows

### Daily Operations (Employee)
1.  **Login**: Use assigned username and password.
2.  **Select Order Type**: From the `Table Selection` screen, either click a green "Available" table or the "Takeaway" button.
3.  **Process Order**: Add items from the menu grid. If prompted for weight, enter it.
4.  **Take Payment**: Click the appropriate payment button to complete the sale.
5.  **Logout**: At the end of a shift, click "Logout", count the physical cash in the drawer, enter the amount in the reconciliation dialog, and confirm.

### Administrative Tasks (Admin)
- **Inventory Management**:
  - **Receiving Goods**: Use the "Add Stock" button in the Inventory screen to log new deliveries.
  - **Auditing**: Regularly use the "Physical Count" feature to ensure data accuracy and track shrinkage.
- **Menu Updates**:
  - Use the "Menu Management" screen to add new dishes or update recipes and prices.
- **Performance Review**:
  - Check the **Dashboard** for a quick overview of daily/weekly performance.
  - Use the **Reports** module to analyze sales trends, item popularity, and employee performance.
