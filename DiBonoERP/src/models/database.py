"""
DiBono ERP - Database Models
SQLAlchemy 2.x models for seafood restaurant management system
All monetary values stored as INTEGER (fils: 1 LYD = 1000 fils)
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from typing import Optional
import os

Base = declarative_base()


class User(Base):
    """User accounts - Admin and Employee roles"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' or 'employee'
    salary = Column(Integer, default=0)  # Monthly salary in fils
    shift = Column(String(50))  # e.g., "Morning 8AM-4PM"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user")
    orders = relationship("Order", back_populates="employee", foreign_keys="Order.employee_id")
    held_orders = relationship("HeldOrder", back_populates="employee")


class Session(Base):
    """Employee work sessions for cash reconciliation"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    login_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    logout_time = Column(DateTime)
    orders_count = Column(Integer, default=0)
    cash_sales = Column(Integer, default=0)  # In fils
    card_sales = Column(Integer, default=0)  # In fils
    total_sales = Column(Integer, default=0)  # In fils
    expected_cash = Column(Integer, default=0)  # In fils
    actual_cash = Column(Integer)  # In fils, set on logout
    variance = Column(Integer, default=0)  # In fils
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class Supplier(Base):
    """Supplier information for purchase orders"""
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    payment_terms = Column(String(100))  # e.g., "Net 30"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class InventoryCategory(Base):
    """Inventory categories for organizing ingredients"""
    __tablename__ = 'inventory_categories'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    icon = Column(String(50))  # Emoji or icon identifier
    color = Column(String(7), default='#0088AA')  # Hex color
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="category_rel")


class InventoryItem(Base):
    """Inventory items/ingredients with stock tracking"""
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)  # kg, pc, L, etc.
    category = Column(String(50))  # Legacy field - kept for backward compatibility
    category_id = Column(Integer, ForeignKey('inventory_categories.id'))  # New foreign key
    on_hand = Column(Float, default=0.0)  # Current quantity
    min_threshold = Column(Float, default=0.0)
    max_threshold = Column(Float, default=0.0)
    cost_per_unit = Column(Integer, default=0)  # In fils
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category_rel = relationship("InventoryCategory", back_populates="inventory_items")
    menu_item_ingredients = relationship("MenuItemIngredient", back_populates="inventory_item")
    waste_logs = relationship("WasteLog", back_populates="inventory_item")
    physical_counts = relationship("PhysicalCount", back_populates="inventory_item")


class MenuCategory(Base):
    """Menu categories (Breakfast, Seafood, Pasta, etc.)"""
    __tablename__ = 'menu_categories'
    
    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    icon = Column(String(50))  # Icon identifier or emoji
    color = Column(String(7), default='#0088AA')  # Hex color
    display_order = Column(Integer, default=0)
    availability_start = Column(String(5))  # e.g., "08:00"
    availability_end = Column(String(5))  # e.g., "23:00"
    active = Column(Boolean, default=True)
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    """Menu items available for sale"""
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('menu_categories.id'), nullable=False)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    description_en = Column(Text)
    description_ar = Column(Text)
    base_price = Column(Integer, nullable=False)  # In fils (selling price)
    recipe_cost = Column(Integer, default=0)  # In fils (calculated from ingredients)
    price_per_kg = Column(Integer)  # In fils, for weight-based items
    is_weight_based = Column(Boolean, default=False)
    item_type = Column(String(20), default='dish')  # 'dish' (recipe-based) or 'beverage' (inventory-based)
    linked_inventory_id = Column(Integer, ForeignKey('inventory_items.id'))  # For beverages only
    image_path = Column(String(255))
    active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("MenuCategory", back_populates="menu_items")
    ingredients = relationship("MenuItemIngredient", back_populates="menu_item", cascade="all, delete-orphan")
    customization_groups = relationship("MenuCustomizationGroup", back_populates="menu_item", cascade="all, delete-orphan")
    alternatives = relationship("MenuItemAlternative", back_populates="menu_item", cascade="all, delete-orphan")
    addons = relationship("MenuItemAddon", back_populates="menu_item", cascade="all, delete-orphan")
    linked_inventory = relationship("InventoryItem", foreign_keys=[linked_inventory_id])
    order_items = relationship("OrderItem", back_populates="menu_item")


class MenuItemIngredient(Base):
    """Junction table mapping menu items to inventory ingredients (Recipe)"""
    __tablename__ = 'menu_item_ingredients'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)  # Amount needed per serving
    unit = Column(String(20), nullable=False)  # kg, g, liter, ml, piece
    display_order = Column(Integer, default=0)
    
    # Relationships
    menu_item = relationship("MenuItem", back_populates="ingredients")
    inventory_item = relationship("InventoryItem", back_populates="menu_item_ingredients")


class MenuItemAlternative(Base):
    """Alternative ingredients for menu items (e.g., Penne instead of Spaghetti)"""
    __tablename__ = 'menu_item_alternatives'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    replaces_ingredient_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)  # Base ingredient
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)  # Alternative ingredient
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)  # Amount to use instead
    unit = Column(String(20), nullable=False)  # kg, g, liter, ml, piece
    price_modifier = Column(Integer, default=0)  # In fils (can be positive or negative)
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    # Relationships
    menu_item = relationship("MenuItem", back_populates="alternatives")
    replaces_ingredient = relationship("InventoryItem", foreign_keys=[replaces_ingredient_id])
    inventory_item = relationship("InventoryItem", foreign_keys=[inventory_item_id])


class MenuItemAddon(Base):
    """Add-ons available for menu items (e.g., Extra Sauce, Grilled Vegetables)"""
    __tablename__ = 'menu_item_addons'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)  # Amount deducted when selected
    unit = Column(String(20), nullable=False)  # kg, g, liter, ml, piece
    price = Column(Integer, nullable=False)  # In fils
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    # Relationships
    menu_item = relationship("MenuItem", back_populates="addons")
    inventory_item = relationship("InventoryItem")


class MenuCustomizationGroup(Base):
    """Customization option groups for menu items (e.g., 'Cooking Style', 'Toppings')"""
    __tablename__ = 'menu_customization_groups'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    selection_type = Column(String(20), nullable=False)  # 'single' or 'multiple'
    required = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    # Relationships
    menu_item = relationship("MenuItem", back_populates="customization_groups")
    options = relationship("MenuCustomizationOption", back_populates="group", cascade="all, delete-orphan")


class MenuCustomizationOption(Base):
    """Individual options within a customization group"""
    __tablename__ = 'menu_customization_options'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('menu_customization_groups.id'), nullable=False)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    price_modifier = Column(Integer, default=0)  # In fils, can be positive or negative
    is_default = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    # Relationships
    group = relationship("MenuCustomizationGroup", back_populates="options")


class Order(Base):
    """Completed/voided customer orders"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, nullable=False)  # YYYYMMDD-001
    employee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    table_id = Column(Integer, ForeignKey('restaurant_tables.id'))  # NULL for takeaway
    order_type = Column(String(20), nullable=False, default='dine-in')  # dine-in, takeaway
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    subtotal = Column(Integer, nullable=False)  # In fils
    tax_amount = Column(Integer, default=0)  # In fils
    service_charge = Column(Integer, default=0)  # In fils
    discount_amount = Column(Integer, default=0)  # In fils
    total = Column(Integer, nullable=False)  # In fils
    payment_method = Column(String(20), nullable=False)  # cash, card, split
    cash_amount = Column(Integer, default=0)  # For split payments, in fils
    card_amount = Column(Integer, default=0)  # For split payments, in fils
    status = Column(String(20), nullable=False)  # completed, voided
    voided_by = Column(Integer, ForeignKey('users.id'))
    void_reason = Column(Text)
    voided_at = Column(DateTime)
    
    # Relationships
    employee = relationship("User", back_populates="orders", foreign_keys=[employee_id])
    table = relationship("RestaurantTable", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Individual items within an order"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    item_name = Column(String(100), nullable=False)  # Snapshot for historical data
    quantity = Column(Integer, nullable=False, default=1)
    weight_kg = Column(Float)  # For weight-based items
    unit_price = Column(Integer, nullable=False)  # In fils
    modifiers_json = Column(JSON)  # Add-ons, special requests
    line_total = Column(Integer, nullable=False)  # In fils
    selected_alternative_id = Column(Integer, ForeignKey('menu_item_alternatives.id'))  # NULL if standard
    calculated_cost = Column(Integer, default=0)  # In fils (recipe + addons cost)
    net_profit = Column(Integer, default=0)  # In fils (line_total - calculated_cost)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    modifiers = relationship("OrderItemModifier", back_populates="order_item", cascade="all, delete-orphan")
    addons = relationship("OrderItemAddon", back_populates="order_item", cascade="all, delete-orphan")
    selected_alternative = relationship("MenuItemAlternative", foreign_keys=[selected_alternative_id])


class OrderItemAddon(Base):
    """Junction table for add-ons selected on an order item"""
    __tablename__ = 'order_item_addons'
    
    id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey('order_items.id'), nullable=False)
    addon_id = Column(Integer, ForeignKey('menu_item_addons.id'), nullable=False)
    addon_name = Column(String(100), nullable=False)  # Snapshot
    quantity = Column(Float, nullable=False)  # Snapshot
    unit = Column(String(20), nullable=False)  # Snapshot
    price = Column(Integer, nullable=False)  # Snapshot in fils
    
    # Relationships
    order_item = relationship("OrderItem", back_populates="addons")
    addon = relationship("MenuItemAddon")


class OrderItemModifier(Base):
    """Modifiers/customizations applied to an order item"""
    __tablename__ = 'order_item_modifiers'
    
    id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey('order_items.id'), nullable=False)
    modifier_name_en = Column(String(100), nullable=False)
    modifier_name_ar = Column(String(100), nullable=False)
    price_modifier = Column(Integer, nullable=False)  # In fils
    
    # Relationships
    order_item = relationship("OrderItem", back_populates="modifiers")


class HeldOrder(Base):
    """Temporarily held orders in POS"""
    __tablename__ = 'held_orders'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    table_id = Column(Integer, ForeignKey('restaurant_tables.id'))  # NULL for takeaway
    order_type = Column(String(20), nullable=False, default='dine-in')  # dine-in, takeaway
    items_json = Column(JSON, nullable=False)  # Serialized order items
    subtotal = Column(Integer, nullable=False)  # In fils
    held_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Auto-expire after 4 hours
    
    # Relationships
    employee = relationship("User", back_populates="held_orders")


class PurchaseOrder(Base):
    """Purchase orders for inventory replenishment"""
    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expected_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    status = Column(String(20), nullable=False)  # draft, submitted, received
    total_cost = Column(Integer, default=0)  # In fils
    notes = Column(Text)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    """Line items in purchase orders"""
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity_ordered = Column(Float, nullable=False)
    quantity_received = Column(Float, default=0.0)
    unit_cost = Column(Integer, nullable=False)  # In fils
    line_total = Column(Integer, nullable=False)  # In fils
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")


class WasteLog(Base):
    """Waste and spoilage tracking"""
    __tablename__ = 'waste_logs'
    
    id = Column(Integer, primary_key=True)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    reason = Column(String(100), nullable=False)  # spoilage, breakage, over-portion
    notes = Column(Text)
    photo_path = Column(String(255))
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    logged_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    approved = Column(Boolean, default=True)
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="waste_logs")


class PhysicalCount(Base):
    """Physical inventory count records for variance calculation"""
    __tablename__ = 'physical_counts'
    
    id = Column(Integer, primary_key=True)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    counted_quantity = Column(Float, nullable=False)
    theoretical_quantity = Column(Float, nullable=False)  # System quantity at time of count
    variance = Column(Float, nullable=False)
    variance_value = Column(Integer, nullable=False)  # In fils
    counted_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    counted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="physical_counts")


class SalesSnapshot(Base):
    """Time-series snapshots for reporting performance"""
    __tablename__ = 'sales_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    period_type = Column(String(20), nullable=False)  # hourly, daily
    revenue = Column(Integer, nullable=False)  # In fils
    orders_count = Column(Integer, default=0)
    cash_revenue = Column(Integer, default=0)  # In fils
    card_revenue = Column(Integer, default=0)  # In fils
    avg_ticket = Column(Integer, default=0)  # In fils
    top_item_id = Column(Integer)
    top_item_count = Column(Integer, default=0)


class ReportPoint(Base):
    """Flexible key-value storage for various report metrics"""
    __tablename__ = 'report_points'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metric_type = Column(String(50), nullable=False)  # variance, cogs, popular_item
    metric_key = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    meta_data = Column(JSON)


class RestaurantTable(Base):
    """Restaurant tables for dine-in orders"""
    __tablename__ = 'restaurant_tables'
    
    id = Column(Integer, primary_key=True)
    table_number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)  # Number of seats
    status = Column(String(20), nullable=False, default='available')  # available, occupied, reserved
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="table")


# Database engine and session management
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dibono.db')
        _engine = create_engine(f'sqlite:///{db_path}', echo=False)
        # Enable WAL mode for better concurrency
        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.commit()
    return _engine


def get_session() -> Session:
    """Get a new database session"""
    global _SessionLocal
    if _SessionLocal is None:
        # Keep ORM objects usable after commit to prevent detached errors in UI
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionLocal()


def init_db():
    """Initialize database - create all tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully")
