"""
DiBono ERP - Utility Functions
Helper functions for authentication, formatting, and business logic
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict

from utils.passlib_compat import ensure_bcrypt_about

ensure_bcrypt_about()
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from models.database import User, Session as SessionModel, Order, OrderItem, InventoryItem, MenuItemIngredient


class AuthManager:
    """Handle authentication and session management"""
    
    current_user: Optional[User] = None
    current_session: Optional[SessionModel] = None
    failed_attempts: int = 0
    
    @classmethod
    def login(cls, db: Session, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user and create session
        Returns: (success, message)
        """
        user = db.query(User).filter_by(username=username, active=True).first()
        
        if not user:
            cls.failed_attempts += 1
            return False, "بيانات الدخول غير صحيحة"
        
        if not bcrypt.verify(password, user.password_hash):
            cls.failed_attempts += 1
            return False, "بيانات الدخول غير صحيحة"
        
        # Create new session
        session = SessionModel(
            user_id=user.id,
            login_time=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        
        cls.current_user = user
        cls.current_session = session
        cls.failed_attempts = 0
        
        return True, f"مرحباً {user.full_name}"
    
    @classmethod
    def logout(cls, db: Session, actual_cash: Optional[int] = None) -> bool:
        """Close current session and calculate variance"""
        if not cls.current_session:
            return False
        
        cls.current_session.logout_time = datetime.utcnow()
        
        if actual_cash is not None:
            cls.current_session.actual_cash = actual_cash
            cls.current_session.variance = actual_cash - cls.current_session.expected_cash
        
        db.commit()
        
        cls.current_user = None
        cls.current_session = None
        
        return True
    
    @classmethod
    def verify_admin_pin(cls, db: Session, pin: str) -> bool:
        """Verify admin PIN for override actions"""
        # Hard-coded PIN: 1234
        if pin != '1234':
            return False
        
        # Verify current user is admin or check if any admin exists
        admin = db.query(User).filter_by(role='admin', active=True).first()
        return admin is not None
    
    @classmethod
    def is_admin(cls) -> bool:
        """Check if current user is admin"""
        return cls.current_user and cls.current_user.role == 'admin'


class CurrencyFormatter:
    """Handle currency formatting (fils ↔ LYD)"""
    
    @staticmethod
    def fils_to_lyd(fils: int) -> float:
        """Convert fils to LYD (1 LYD = 1000 fils)"""
        return fils / 1000.0
    
    @staticmethod
    def lyd_to_fils(lyd: float) -> int:
        """Convert LYD to fils"""
        return int(round(lyd * 1000))
    
    @staticmethod
    def format_lyd(fils: int) -> str:
        """Format fils as LYD string"""
        return f"{fils / 1000.0:.2f} د.ل"
    
    @staticmethod
    def format_weight(kg: float) -> str:
        """Format weight in kg"""
        return f"{kg:.2f} كجم"


class OrderNumberGenerator:
    """Generate daily sequential order numbers"""
    
    @staticmethod
    def generate(db: Session) -> str:
        """Generate next order number for today (YYYYMMDD-XXX)"""
        today = datetime.now().strftime('%Y%m%d')
        
        # Find highest order number for today
        last_order = db.query(Order).filter(
            Order.order_number.like(f'{today}-%')
        ).order_by(Order.order_number.desc()).first()
        
        if last_order:
            last_num = int(last_order.order_number.split('-')[1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        return f"{today}-{next_num:03d}"


class InventoryManager:
    """Handle inventory depletion and validation"""
    
    @staticmethod
    def check_availability(db: Session, menu_item_id: int, quantity: int = 1, 
                          weight_kg: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if sufficient ingredients available for menu item
        Returns: (available, error_message)
        """
        from models.database import MenuItem
        from utils.unit_converter import UnitConverter
        
        menu_item = db.query(MenuItem).get(menu_item_id)
        if not menu_item:
            return False, "الصنف غير موجود"
        
        # Get all ingredients for this menu item
        for ingredient_link in menu_item.ingredients:
            inventory_item = ingredient_link.inventory_item
            
            # Calculate required quantity
            if menu_item.is_weight_based and weight_kg:
                required = ingredient_link.quantity * weight_kg * quantity
            else:
                required = ingredient_link.quantity * quantity
            
            # Convert units if necessary
            try:
                if ingredient_link.unit.lower() != inventory_item.unit.lower():
                    required = UnitConverter.convert(
                        required,
                        ingredient_link.unit,
                        inventory_item.unit
                    )
            except ValueError:
                # Incompatible units - skip this ingredient check
                continue
            
            available = inventory_item.on_hand
            
            if available < required:
                return False, f"المخزون غير كافٍ: {inventory_item.name_ar}"
        
        return True, None
    
    @staticmethod
    def check_low_stock_warnings(db: Session, menu_item_id: int) -> list:
        """
        Check if any ingredients are below minimum threshold
        Returns: List of (ingredient_name, current_stock, min_threshold, unit)
        """
        from models.database import MenuItem
        
        menu_item = db.query(MenuItem).get(menu_item_id)
        if not menu_item:
            return []
        
        warnings = []
        
        # Check main recipe ingredients
        for ingredient_link in menu_item.ingredients:
            inventory_item = ingredient_link.inventory_item
            
            if inventory_item.on_hand <= inventory_item.min_threshold:
                warnings.append((
                    inventory_item.name_ar,
                    inventory_item.on_hand,
                    inventory_item.min_threshold,
                    inventory_item.unit
                ))
        
        # Check alternative ingredients
        for alternative in menu_item.alternatives:
            inventory_item = alternative.inventory_item
            
            if inventory_item.on_hand <= inventory_item.min_threshold:
                warnings.append((
                    f"{inventory_item.name_ar} (بديل)",
                    inventory_item.on_hand,
                    inventory_item.min_threshold,
                    inventory_item.unit
                ))
        
        # Check add-on ingredients
        for addon in menu_item.addons:
            inventory_item = addon.inventory_item
            
            if inventory_item.on_hand <= inventory_item.min_threshold:
                warnings.append((
                    f"{inventory_item.name_ar} (إضافة)",
                    inventory_item.on_hand,
                    inventory_item.min_threshold,
                    inventory_item.unit
                ))
        
        return warnings
    
    @staticmethod
    def deduct_inventory(db: Session, order_id: int) -> bool:
        """
        Deduct inventory for completed order based on recipe ingredients,
        handling alternatives and add-ons
        """
        from utils.unit_converter import UnitConverter
        from models.database import MenuItemAlternative
        
        order = db.query(Order).get(order_id)
        if not order or order.status != 'completed':
            return False
        
        warnings = []  # Track low stock warnings
        
        for order_item in order.items:
            if not order_item.menu_item:
                continue
            
            # Build list of ingredients to deduct, considering alternatives
            ingredients_to_deduct = []
            
            # Check if alternative was selected
            alternative = None
            if order_item.selected_alternative_id:
                alternative = db.query(MenuItemAlternative).get(order_item.selected_alternative_id)
            
            # Process recipe ingredients
            for ingredient_link in order_item.menu_item.ingredients:
                # Check if this ingredient is replaced by an alternative
                if alternative and ingredient_link.inventory_item_id == alternative.replaces_ingredient_id:
                    # Skip base ingredient, use alternative instead
                    ingredients_to_deduct.append({
                        'inventory_item': alternative.inventory_item,
                        'quantity': alternative.quantity,
                        'unit': alternative.unit
                    })
                else:
                    # Use base ingredient
                    ingredients_to_deduct.append({
                        'inventory_item': ingredient_link.inventory_item,
                        'quantity': ingredient_link.quantity,
                        'unit': ingredient_link.unit
                    })
            
            # Add add-ons to deduction list
            for addon_link in order_item.addons:
                if addon_link.addon and addon_link.addon.inventory_item:
                    ingredients_to_deduct.append({
                        'inventory_item': addon_link.addon.inventory_item,
                        'quantity': addon_link.quantity,
                        'unit': addon_link.unit
                    })
            
            # Deduct all ingredients
            for ingredient_data in ingredients_to_deduct:
                inventory_item = ingredient_data['inventory_item']
                base_quantity = ingredient_data['quantity']
                unit = ingredient_data['unit']
                
                # Calculate required quantity for this order item
                if order_item.menu_item.is_weight_based and order_item.weight_kg:
                    # For weight-based items (e.g., seafood by kg)
                    # Scale the recipe proportionally
                    required_quantity = base_quantity * order_item.weight_kg * order_item.quantity
                else:
                    # For standard items
                    required_quantity = base_quantity * order_item.quantity
                
                # Convert units if necessary
                try:
                    if unit.lower() != inventory_item.unit.lower():
                        required_quantity = UnitConverter.convert(
                            required_quantity,
                            unit,
                            inventory_item.unit
                        )
                except ValueError as e:
                    # Incompatible units - log warning but continue
                    warnings.append(
                        f"تحذير: لا يمكن تحويل الوحدات للمكون {inventory_item.name_ar}: {str(e)}"
                    )
                    continue
                
                # Check if sufficient stock available
                if inventory_item.on_hand < required_quantity:
                    warnings.append(
                        f"تحذير: مخزون منخفض - {inventory_item.name_ar} "
                        f"(متوفر: {inventory_item.on_hand:.2f} {inventory_item.unit}, "
                        f"مطلوب: {required_quantity:.2f} {inventory_item.unit})"
                    )
                    # Allow order to proceed even with low stock
                
                # Deduct from inventory
                inventory_item.on_hand -= required_quantity
                
                # Check if inventory is now critically low (below reorder point if set)
                if hasattr(inventory_item, 'reorder_point') and inventory_item.reorder_point:
                    if inventory_item.on_hand <= inventory_item.reorder_point:
                        warnings.append(
                            f"تنبيه: {inventory_item.name_ar} وصل لحد إعادة الطلب "
                            f"({inventory_item.on_hand:.2f} {inventory_item.unit})"
                        )
        
        # Log warnings if any (could be stored in Order notes or logged separately)
        if warnings:
            print("تحذيرات المخزون:", "\n".join(warnings))
        
        # No commit here - let caller handle the transaction
        return True
    
    @staticmethod
    def restore_inventory(db: Session, order_id: int) -> bool:
        """
        Restore inventory for voided order, considering alternatives and add-ons
        """
        from utils.unit_converter import UnitConverter
        from models.database import MenuItemAlternative
        
        order = db.query(Order).get(order_id)
        if not order:
            return False
        
        for order_item in order.items:
            if not order_item.menu_item:
                continue
            
            # Build list of ingredients to restore, considering alternatives
            ingredients_to_restore = []
            
            # Check if alternative was selected
            alternative = None
            if order_item.selected_alternative_id:
                alternative = db.query(MenuItemAlternative).get(order_item.selected_alternative_id)
            
            # Process recipe ingredients
            for ingredient_link in order_item.menu_item.ingredients:
                # Check if this ingredient was replaced by an alternative
                if alternative and ingredient_link.inventory_item_id == alternative.replaces_ingredient_id:
                    # Restore alternative ingredient
                    ingredients_to_restore.append({
                        'inventory_item': alternative.inventory_item,
                        'quantity': alternative.quantity,
                        'unit': alternative.unit
                    })
                else:
                    # Restore base ingredient
                    ingredients_to_restore.append({
                        'inventory_item': ingredient_link.inventory_item,
                        'quantity': ingredient_link.quantity,
                        'unit': ingredient_link.unit
                    })
            
            # Add add-ons to restoration list
            for addon_link in order_item.addons:
                if addon_link.addon and addon_link.addon.inventory_item:
                    ingredients_to_restore.append({
                        'inventory_item': addon_link.addon.inventory_item,
                        'quantity': addon_link.quantity,
                        'unit': addon_link.unit
                    })
            
            # Restore all ingredients
            for ingredient_data in ingredients_to_restore:
                inventory_item = ingredient_data['inventory_item']
                base_quantity = ingredient_data['quantity']
                unit = ingredient_data['unit']
                
                # Calculate quantity to restore
                if order_item.menu_item.is_weight_based and order_item.weight_kg:
                    amount = base_quantity * order_item.weight_kg * order_item.quantity
                else:
                    amount = base_quantity * order_item.quantity
                
                # Convert units if necessary
                try:
                    if unit.lower() != inventory_item.unit.lower():
                        amount = UnitConverter.convert(
                            amount,
                            unit,
                            inventory_item.unit
                        )
                except ValueError:
                    # Incompatible units - skip
                    continue
                
                inventory_item.on_hand += amount
        
        # No commit here - let caller handle the transaction
        return True


class SessionTracker:
    """Track session statistics"""
    
    @staticmethod
    def update_session_stats(db: Session, session_id: int, order: Order):
        """Update session totals after order completion"""
        session = db.query(SessionModel).get(session_id)
        if not session:
            return
        
        session.orders_count += 1
        session.total_sales += order.total
        
        if order.payment_method == 'cash':
            session.cash_sales += order.total
            session.expected_cash += order.total
        elif order.payment_method == 'card':
            session.card_sales += order.total
        elif order.payment_method == 'split':
            session.cash_sales += order.cash_amount
            session.card_sales += order.card_amount
            session.expected_cash += order.cash_amount
        
        # No commit here - let caller handle the transaction


class PriceCalculator:
    """Calculate prices for orders"""
    
    @staticmethod
    def calculate_line_total(base_price: int, quantity: int = 1, 
                            weight_kg: Optional[float] = None, 
                            price_per_kg: Optional[int] = None) -> int:
        """Calculate line total for order item"""
        if weight_kg and price_per_kg:
            return int(round(price_per_kg * weight_kg * quantity))
        return base_price * quantity
    
    @staticmethod
    def calculate_order_total(subtotal: int, tax_rate: float = 0.0, 
                             service_charge_rate: float = 0.0, 
                             discount_amount: int = 0) -> Dict[str, int]:
        """
        Calculate order totals with tax, service charge, and discount
        Returns dict with tax_amount, service_charge, total
        """
        # Apply discount first
        discounted_subtotal = max(0, subtotal - discount_amount)
        
        # Calculate service charge on discounted subtotal
        service_charge = int(round(discounted_subtotal * service_charge_rate))
        
        # Calculate tax on (subtotal - discount + service_charge)
        taxable_amount = discounted_subtotal + service_charge
        tax_amount = int(round(taxable_amount * tax_rate))
        
        # Final total
        total = discounted_subtotal + service_charge + tax_amount
        
        return {
            'tax_amount': tax_amount,
            'service_charge': service_charge,
            'total': total
        }


class DateRangeCalculator:
    """Calculate date ranges for reporting"""
    
    @staticmethod
    def get_day_range() -> Tuple[datetime, datetime]:
        """Get start and end of today"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return today, today + timedelta(days=1)
    
    @staticmethod
    def get_week_range() -> Tuple[datetime, datetime]:
        """Get start and end of current week"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=7)
        return start, end
    
    @staticmethod
    def get_month_range() -> Tuple[datetime, datetime]:
        """Get start and end of current month"""
        today = datetime.now()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 12:
            end = start.replace(year=today.year + 1, month=1)
        else:
            end = start.replace(month=today.month + 1)
        return start, end
    
    @staticmethod
    def get_previous_period(start: datetime, end: datetime) -> Tuple[datetime, datetime]:
        """Get the previous period of same length"""
        delta = end - start
        prev_end = start
        prev_start = start - delta
        return prev_start, prev_end
    
    @staticmethod
    def get_week_start() -> datetime:
        """Get start of current week"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return today - timedelta(days=today.weekday())
    
    @staticmethod
    def get_month_start() -> datetime:
        """Get start of current month"""
        today = datetime.now()
        return today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
