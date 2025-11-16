"""
DiBono ERP - Point of Sale Interface
High-speed POS for employee order processing
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QGridLayout, QScrollArea, QFrame, QTableWidget, 
                              QTableWidgetItem, QDialog, QLineEdit, QDialogButtonBox,
                              QMessageBox, QDoubleSpinBox, QComboBox, QButtonGroup,
                              QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models.database import get_session, MenuItem, MenuCategory, Order, OrderItem, HeldOrder, RestaurantTable
from utils.helpers import (AuthManager, CurrencyFormatter, OrderNumberGenerator, 
                          InventoryManager, SessionTracker, PriceCalculator)
from utils.styles import POS_MENU_TILE_STYLE, CATEGORY_CHIP_STYLE
from ui.table_selection import TableSelectionScreen
import json


class POSInterface(QWidget):
    """Point of Sale interface for employees"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_order_items = []  # List of {menu_item, quantity, weight_kg, line_total}
        self.current_category_id = None
        self.current_table_id = None  # Track selected table
        self.current_order_type = 'dine-in'  # 'dine-in' or 'takeaway'
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize POS UI with stacked layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Stacked widget for table selection vs ordering
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Page 0: Table selection
        self.table_selection = TableSelectionScreen()
        self.table_selection.table_selected.connect(self.on_table_selected)
        self.table_selection.takeaway_selected.connect(self.on_takeaway_selected)
        self.stack.addWidget(self.table_selection)
        
        # Page 1: Main POS ordering screen
        self.ordering_screen = self.create_ordering_screen()
        self.stack.addWidget(self.ordering_screen)
        
        # Start with table selection
        self.stack.setCurrentIndex(0)
        
    def create_ordering_screen(self):
        """Create the main POS ordering screen"""
        widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(main_layout)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Left side - Menu tiles
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 10, 20)
        left_panel.setLayout(left_layout)
        
        # Top bar with user info and logout
        top_bar = QHBoxLayout()
        self.user_label = QLabel(f"👤 {AuthManager.current_user.full_name}")
        self.user_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4ECDC4;")
        top_bar.addWidget(self.user_label)
        
        top_bar.addStretch()
        
        back_btn = QPushButton("🔙 العودة للطاولات")
        back_btn.setStyleSheet("font-size: 11pt; padding: 8px 15px; background-color: #1282A2; color: white;")
        back_btn.clicked.connect(self.go_back_to_tables)
        top_bar.addWidget(back_btn)
        
        logout_btn = QPushButton("تسجيل الخروج")
        logout_btn.setObjectName("danger")
        logout_btn.clicked.connect(self.handle_logout)
        top_bar.addWidget(logout_btn)
        
        left_layout.addLayout(top_bar)
        
        # Category chips
        self.category_scroll = QScrollArea()
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setMaximumHeight(80)
        self.category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.category_container = QWidget()
        self.category_layout = QHBoxLayout()
        self.category_layout.setSpacing(10)
        self.category_container.setLayout(self.category_layout)
        self.category_scroll.setWidget(self.category_container)
        
        self.category_button_group = QButtonGroup()
        self.category_button_group.setExclusive(True)
        
        left_layout.addWidget(self.category_scroll)
        
        # Menu items grid
        self.menu_scroll = QScrollArea()
        self.menu_scroll.setWidgetResizable(True)
        
        self.menu_container = QWidget()
        self.menu_grid = QGridLayout()
        self.menu_grid.setSpacing(15)
        self.menu_container.setLayout(self.menu_grid)
        self.menu_scroll.setWidget(self.menu_container)
        
        left_layout.addWidget(self.menu_scroll)
        
        main_layout.addWidget(left_panel, 2)
        
        # Right side - Order summary
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #0E1A2F; border-left: 3px solid #1282A2;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_panel.setLayout(right_layout)
        right_panel.setFixedWidth(420)
        
        # Order summary title
        order_title = QLabel("الطلب الحالي")
        order_title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #4ECDC4;")
        right_layout.addWidget(order_title)
        
        # Order table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["الصنف", "الكمية/الوزن", "السعر", "الإجمالي"])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        self.order_table.setColumnWidth(0, 150)
        self.order_table.setColumnWidth(1, 70)
        self.order_table.setColumnWidth(2, 70)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_layout.addWidget(self.order_table)
        
        # Totals section
        totals_frame = QFrame()
        totals_frame.setObjectName("card")
        totals_layout = QVBoxLayout()
        totals_frame.setLayout(totals_layout)
        
        self.subtotal_label = QLabel("المجموع الفرعي: 0.00 د.ل")
        self.subtotal_label.setStyleSheet("font-size: 13pt; color: #E8F1F2;")
        totals_layout.addWidget(self.subtotal_label)
        
        self.tax_label = QLabel("الضريبة: 0.00 د.ل")
        self.tax_label.setStyleSheet("font-size: 11pt; color: #ADB5BD;")
        totals_layout.addWidget(self.tax_label)
        
        self.service_label = QLabel("الخدمة: 0.00 د.ل")
        self.service_label.setStyleSheet("font-size: 11pt; color: #ADB5BD;")
        totals_layout.addWidget(self.service_label)
        
        self.discount_label = QLabel("الخصم: 0.00 د.ل")
        self.discount_label.setStyleSheet("font-size: 11pt; color: #FF6B6B;")
        totals_layout.addWidget(self.discount_label)
        
        self.total_label = QLabel("الإجمالي: 0.00 د.ل")
        self.total_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #51CF66;")
        totals_layout.addWidget(self.total_label)
        
        right_layout.addWidget(totals_frame)
        
        # Action buttons
        actions_grid = QGridLayout()
        actions_grid.setSpacing(10)
        
        hold_btn = QPushButton("تعليق")
        hold_btn.clicked.connect(self.hold_order)
        actions_grid.addWidget(hold_btn, 0, 0)
        
        recall_btn = QPushButton("استرجاع")
        recall_btn.clicked.connect(self.recall_order)
        actions_grid.addWidget(recall_btn, 0, 1)
        
        void_btn = QPushButton("حذف صنف")
        void_btn.setObjectName("danger")
        void_btn.clicked.connect(self.void_item)
        actions_grid.addWidget(void_btn, 1, 0)
        
        discount_btn = QPushButton("خصم")
        discount_btn.clicked.connect(self.apply_discount)
        actions_grid.addWidget(discount_btn, 1, 1)
        
        right_layout.addLayout(actions_grid)
        
        # Payment buttons
        payment_layout = QVBoxLayout()
        payment_layout.setSpacing(12)
        
        cash_btn = QPushButton("💵 دفع نقدي")
        cash_btn.setObjectName("success")
        cash_btn.setMinimumHeight(55)
        cash_btn.clicked.connect(lambda: self.process_payment('cash'))
        payment_layout.addWidget(cash_btn)
        
        card_btn = QPushButton("💳 دفع بالبطاقة")
        card_btn.setObjectName("success")
        card_btn.setMinimumHeight(55)
        card_btn.clicked.connect(lambda: self.process_payment('card'))
        payment_layout.addWidget(card_btn)
        
        split_btn = QPushButton("💰 دفع مشترك")
        split_btn.setMinimumHeight(50)
        split_btn.clicked.connect(lambda: self.process_payment('split'))
        payment_layout.addWidget(split_btn)
        
        right_layout.addLayout(payment_layout)
        
        main_layout.addWidget(right_panel)
        
        # Load categories and apply styles after UI is created
        self.load_categories()
        self.apply_styles()
        
        return widget
    
    def on_table_selected(self, table_id):
        """Handle table selection"""
        self.current_table_id = table_id
        self.current_order_type = 'dine-in'
        
        # Check if this table has a held order
        db = get_session()
        try:
            held_order = db.query(HeldOrder).filter_by(
                table_id=table_id
            ).filter(HeldOrder.expires_at > datetime.utcnow()).first()
            
            if held_order:
                # Restore the order automatically (no confirmation)
                self.current_order_items.clear()
                for item_data in held_order.items_json:
                    menu_item = db.query(MenuItem).get(item_data['menu_item_id'])
                    if menu_item:
                        self.current_order_items.append({
                            'menu_item': menu_item,
                            'quantity': item_data['quantity'],
                            'weight_kg': item_data.get('weight_kg'),
                            'line_total': item_data['line_total']
                        })
                
                # Delete the held order since we're restoring it
                db.delete(held_order)
                db.commit()
                
                # Update display
                self.update_order_display()
            else:
                # New order - mark table as occupied
                table = db.query(RestaurantTable).get(table_id)
                if table:
                    table.status = 'occupied'
                    db.commit()
        except Exception as e:
            db.rollback()
            QMessageBox.warning(self, "تحذير", f"حدث خطأ: {e}")
        finally:
            db.close()
        
        self.stack.setCurrentIndex(1)  # Switch to ordering screen
        self.update_order_header()
    
    def on_takeaway_selected(self):
        """Handle takeaway selection"""
        self.current_table_id = None
        self.current_order_type = 'takeaway'
        self.stack.setCurrentIndex(1)  # Switch to ordering screen
        self.update_order_header()
    
    def update_order_header(self):
        """Update order header with table/takeaway info"""
        if self.current_order_type == 'takeaway':
            self.user_label.setText(f"👤 {AuthManager.current_user.full_name} | 🥡 طلب توصيل")
        else:
            db = get_session()
            try:
                table = db.query(RestaurantTable).get(self.current_table_id)
                if table:
                    self.user_label.setText(f"👤 {AuthManager.current_user.full_name} | 🍽️ طاولة {table.table_number}")
            finally:
                db.close()
    
    def go_back_to_tables(self):
        """Go back to table selection screen"""
        # Auto-save order if there are items (don't ask)
        if self.current_order_items:
            db = get_session()
            try:
                subtotal = sum(item['line_total'] for item in self.current_order_items)
                
                # Serialize items
                items_data = []
                for item in self.current_order_items:
                    items_data.append({
                        'menu_item_id': item['menu_item'].id,
                        'quantity': item['quantity'],
                        'weight_kg': item.get('weight_kg'),
                        'line_total': item['line_total']
                    })
                
                # Check if there's already a held order for this table
                existing_held = db.query(HeldOrder).filter_by(
                    table_id=self.current_table_id
                ).filter(HeldOrder.expires_at > datetime.utcnow()).first()
                
                if existing_held:
                    # Update existing held order
                    existing_held.items_json = items_data
                    existing_held.subtotal = subtotal
                    existing_held.held_at = datetime.utcnow()
                    existing_held.expires_at = datetime.utcnow() + timedelta(hours=4)
                else:
                    # Create new held order
                    held_order = HeldOrder(
                        employee_id=AuthManager.current_user.id,
                        table_id=self.current_table_id,
                        order_type=self.current_order_type,
                        items_json=items_data,
                        subtotal=subtotal,
                        expires_at=datetime.utcnow() + timedelta(hours=4)
                    )
                    db.add(held_order)
                
                db.commit()
            except Exception as e:
                db.rollback()
                QMessageBox.warning(self, "تحذير", f"تعذر حفظ الطلب: {e}")
            finally:
                db.close()
        else:
            # No items - release table if it was occupied
            if self.current_order_type == 'dine-in' and self.current_table_id:
                db = get_session()
                try:
                    table = db.query(RestaurantTable).get(self.current_table_id)
                    if table:
                        table.status = 'available'
                        db.commit()
                except Exception as e:
                    db.rollback()
                finally:
                    db.close()
        
        # Clear order items from memory (but they're saved in database)
        self.current_order_items.clear()
        self.update_order_display()
        
        # Reset state
        self.current_table_id = None
        self.current_order_type = 'dine-in'
        
        # Refresh tables and go back
        self.table_selection.refresh_tables()
        self.stack.setCurrentIndex(0)
        
    def apply_styles(self):
        """Apply POS specific styles"""
        self.setStyleSheet(POS_MENU_TILE_STYLE + CATEGORY_CHIP_STYLE)
        
    def load_categories(self):
        """Load menu categories"""
        db = get_session()
        try:
            categories = db.query(MenuCategory).filter_by(active=True).order_by(MenuCategory.display_order).all()
            
            for category in categories:
                btn = QPushButton(f"{category.icon} {category.name_ar}")
                btn.setObjectName("categoryChip")
                btn.setCheckable(True)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked, c=category: self.load_menu_items(c.id))
                
                self.category_button_group.addButton(btn)
                self.category_layout.addWidget(btn)
                
                # Select first category by default
                if not self.current_category_id:
                    self.current_category_id = category.id
                    btn.setChecked(True)
                    self.load_menu_items(category.id)
                    
        finally:
            db.close()
            
    def load_menu_items(self, category_id: int):
        """Load menu items for selected category"""
        self.current_category_id = category_id
        
        # Clear existing items
        for i in reversed(range(self.menu_grid.count())):
            self.menu_grid.itemAt(i).widget().deleteLater()
        
        db = get_session()
        try:
            items = db.query(MenuItem).filter_by(
                category_id=category_id, 
                active=True
            ).order_by(MenuItem.display_order).all()
            
            row, col = 0, 0
            max_cols = 3
            
            for item in items:
                btn = QPushButton()
                btn.setObjectName("menuTile")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Item display text
                price_text = CurrencyFormatter.format_lyd(item.base_price)
                if item.is_weight_based:
                    price_text = f"{CurrencyFormatter.format_lyd(item.price_per_kg)} لكل كجم"
                
                btn.setText(f"{item.name_ar}\n\n{price_text}")
                btn.clicked.connect(lambda checked, m=item: self.add_item_to_order(m))
                
                self.menu_grid.addWidget(btn, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        finally:
            db.close()
            
    def add_item_to_order(self, menu_item: MenuItem):
        """Add menu item to current order with alternatives and add-ons"""
        # Check for low stock warnings FIRST
        db = get_session()
        try:
            warnings = InventoryManager.check_low_stock_warnings(db, menu_item.id)
            if warnings:
                # Build warning message
                warning_lines = ["⚠️ تحذير: المكونات التالية قاربت على النفاد:\n"]
                for name, current, min_thresh, unit in warnings:
                    warning_lines.append(f"• {name}: {current:.1f} {unit} (الحد الأدنى: {min_thresh:.1f})")
                
                warning_msg = "\n".join(warning_lines)
                warning_msg += "\n\nهل تريد الاستمرار في إضافة هذا الصنف؟"
                
                reply = QMessageBox.warning(
                    self, 
                    "تحذير مخزون منخفض",
                    warning_msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return  # User cancelled
        finally:
            db.close()
        
        # Show customization dialog (handles weight, alternatives, add-ons)
        from ui.pos_item_customize_dialog import POSItemCustomizeDialog
        
        dialog = POSItemCustomizeDialog(menu_item.id, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return  # User cancelled
        
        # Get customization data
        custom_data = dialog.get_customization_data()
        
        # Check inventory availability
        db = get_session()
        try:
            available, error = InventoryManager.check_availability(
                db, menu_item.id, custom_data['quantity'], custom_data.get('weight_kg')
            )
            if not available:
                QMessageBox.warning(self, "مخزون غير كافٍ", error)
                return
        finally:
            db.close()
        
        # Add to order
        self.current_order_items.append({
            'menu_item': menu_item,
            'quantity': custom_data['quantity'],
            'weight_kg': custom_data.get('weight_kg'),
            'line_total': custom_data['line_total'],
            'unit_price': custom_data['unit_price'],
            'selected_alternative_id': custom_data.get('selected_alternative_id'),
            'selected_addon_ids': custom_data.get('selected_addon_ids', []),
            'modifiers': []  # Keep for compatibility
        })
        
        # Legacy code for old customization system - can be removed later
        # Check if item has customization groups
        has_customizations = False
        db = get_session()
        try:
            # Get fresh instance with relationships loaded
            fresh_item = db.query(MenuItem).get(menu_item.id)
            if fresh_item:
                has_customizations = len(fresh_item.customization_groups) > 0
        finally:
            db.close()
        
        modifiers = []
        final_price = menu_item.base_price
        
        # Show old customization dialog if needed (backward compatibility)
        if has_customizations and not menu_item.is_weight_based:
            from ui.pos_customization_dialog import MenuItemCustomizationDialog
            try:
                custom_dialog = MenuItemCustomizationDialog(menu_item.id, self)
                if custom_dialog.exec() == QDialog.DialogCode.Accepted:
                    modifiers = custom_dialog.get_modifiers()
                    final_price = custom_dialog.get_final_price()
                    
                    # Update the last added item with these modifiers
                    if self.current_order_items:
                        self.current_order_items[-1]['modifiers'] = modifiers
                        self.current_order_items[-1]['line_total'] = final_price
            except:
                pass  # Old dialog may not exist anymore
        
        # OLD CODE BELOW - KEPT FOR REFERENCE BUT NOT EXECUTED
        return
        
        # Check if weight-based
        if menu_item.is_weight_based:
            dialog = WeightInputDialog(menu_item, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                weight_kg = dialog.get_weight()
                line_total = PriceCalculator.calculate_line_total(
                    0, 1, weight_kg, menu_item.price_per_kg
                )
                
                # Check inventory
                db = get_session()
                try:
                    available, error = InventoryManager.check_availability(
                        db, menu_item.id, 1, weight_kg
                    )
                    if not available:
                        QMessageBox.warning(self, "مخزون غير كافٍ", error)
                        return
                finally:
                    db.close()
                
                self.current_order_items.append({
                    'menu_item': menu_item,
                    'quantity': 1,
                    'weight_kg': weight_kg,
                    'line_total': line_total,
                    'modifiers': modifiers
                })
        else:
            # Fixed price item
            line_total = final_price
            
            # Check inventory
            db = get_session()
            try:
                available, error = InventoryManager.check_availability(db, menu_item.id, 1)
                if not available:
                    QMessageBox.warning(self, "مخزون غير كافٍ", error)
                    return
            finally:
                db.close()
            
            # Check if identical item already in order (same item + same modifiers)
            existing = None
            if not modifiers:  # Only merge if no customizations
                existing = next((item for item in self.current_order_items 
                               if item['menu_item'].id == menu_item.id and 
                                  item.get('weight_kg') is None and 
                                  not item.get('modifiers')), None)
            
            if existing:
                existing['quantity'] += 1
                existing['line_total'] += final_price
            else:
                self.current_order_items.append({
                    'menu_item': menu_item,
                    'quantity': 1,
                    'weight_kg': None,
                    'line_total': line_total,
                    'modifiers': modifiers
                })
        
        self.update_order_display()
        
    def update_order_display(self):
        """Update order table and totals"""
        self.order_table.setRowCount(len(self.current_order_items))
        
        subtotal = 0
        
        for idx, item in enumerate(self.current_order_items):
            menu_item = item['menu_item']
            
            # Item name
            self.order_table.setItem(idx, 0, QTableWidgetItem(menu_item.name_ar))
            
            # Quantity or weight
            if item.get('weight_kg'):
                qty_text = f"{item['weight_kg']:.2f} كجم"
            else:
                qty_text = str(item['quantity'])
            self.order_table.setItem(idx, 1, QTableWidgetItem(qty_text))
            
            # Unit price
            if item.get('weight_kg'):
                price_text = CurrencyFormatter.format_lyd(menu_item.price_per_kg)
            else:
                price_text = CurrencyFormatter.format_lyd(menu_item.base_price)
            self.order_table.setItem(idx, 2, QTableWidgetItem(price_text))
            
            # Line total
            self.order_table.setItem(idx, 3, QTableWidgetItem(
                CurrencyFormatter.format_lyd(item['line_total'])
            ))
            
            subtotal += item['line_total']
        
        # Calculate totals
        totals = PriceCalculator.calculate_order_total(subtotal, 0, 0, 0)
        
        self.subtotal_label.setText(f"المجموع الفرعي: {CurrencyFormatter.format_lyd(subtotal)}")
        self.tax_label.setText(f"الضريبة: {CurrencyFormatter.format_lyd(totals['tax_amount'])}")
        self.service_label.setText(f"الخدمة: {CurrencyFormatter.format_lyd(totals['service_charge'])}")
        self.discount_label.setText("الخصم: 0.00 د.ل")
        self.total_label.setText(f"الإجمالي: {CurrencyFormatter.format_lyd(totals['total'])}")
        
    def void_item(self):
        """Remove selected item from order"""
        current_row = self.order_table.currentRow()
        if current_row >= 0:
            del self.current_order_items[current_row]
            self.update_order_display()
            
    def hold_order(self):
        """Hold current order"""
        if not self.current_order_items:
            QMessageBox.information(self, "طلب فارغ", "لا توجد أصناف للتعليق")
            return
        
        db = get_session()
        try:
            # Check hold limit
            held_count = db.query(HeldOrder).filter_by(employee_id=AuthManager.current_user.id).count()
            if held_count >= 5:
                QMessageBox.warning(self, "حد التعليق", "تم بلوغ الحد الأعلى (5 طلبات)")
                return
            
            subtotal = sum(item['line_total'] for item in self.current_order_items)
            
            # Serialize items
            items_data = []
            for item in self.current_order_items:
                items_data.append({
                    'menu_item_id': item['menu_item'].id,
                    'quantity': item['quantity'],
                    'weight_kg': item.get('weight_kg'),
                    'line_total': item['line_total']
                })
            
            held_order = HeldOrder(
                employee_id=AuthManager.current_user.id,
                table_id=self.current_table_id,
                order_type=self.current_order_type,
                items_json=items_data,
                subtotal=subtotal,
                expires_at=datetime.utcnow() + timedelta(hours=4)
            )
            
            db.add(held_order)
            db.commit()
            
            self.current_order_items.clear()
            self.update_order_display()
            
            QMessageBox.information(self, "تم التعليق", "تم حفظ الطلب بنجاح")
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حفظ الطلب: {e}")
        finally:
            db.close()
            
    def recall_order(self):
        """Recall a held order"""
        db = get_session()
        try:
            held_orders = db.query(HeldOrder).filter_by(
                employee_id=AuthManager.current_user.id
            ).filter(HeldOrder.expires_at > datetime.utcnow()).all()
            
            if not held_orders:
                QMessageBox.information(self, "لا توجد طلبات معلقة", "لا توجد طلبات محفوظة حالياً")
                return
            
            # Show selection dialog (simplified - just use first one for now)
            held_order = held_orders[0]
            
            # Restore items
            self.current_order_items.clear()
            for item_data in held_order.items_json:
                menu_item = db.query(MenuItem).get(item_data['menu_item_id'])
                if menu_item:
                    self.current_order_items.append({
                        'menu_item': menu_item,
                        'quantity': item_data['quantity'],
                        'weight_kg': item_data.get('weight_kg'),
                        'line_total': item_data['line_total']
                    })
            
            # Restore table and order type
            self.current_table_id = held_order.table_id
            self.current_order_type = held_order.order_type
            self.update_order_header()
            
            # Delete held order
            db.delete(held_order)
            db.commit()
            
            self.update_order_display()
            QMessageBox.information(self, "استرجاع الطلب", "تم استرجاع الطلب بنجاح")
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر استرجاع الطلب: {e}")
        finally:
            db.close()
            
    def apply_discount(self):
        """Apply discount to order (requires admin PIN)"""
        dialog = AdminPINDialog("أدخل رقم PIN للمدير لتطبيق الخصم", self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Simplified - just show message for now
            QMessageBox.information(self, "الخصومات", "سيتم إضافة خاصية الخصم لاحقاً")
    
    def calculate_item_cost(self, db, item):
        """Calculate the actual cost of an order item including recipe, alternatives, and add-ons"""
        from models.database import MenuItemAlternative, MenuItemAddon
        from utils.unit_converter import UnitConverter
        
        menu_item = item['menu_item']
        quantity = item['quantity']
        weight_kg = item.get('weight_kg', 1.0 if menu_item.is_weight_based else None)
        
        total_cost = 0
        
        # Get alternative if selected
        alternative = None
        if item.get('selected_alternative_id'):
            alternative = db.query(MenuItemAlternative).get(item['selected_alternative_id'])
        
        # Calculate recipe cost
        for ingredient_link in menu_item.ingredients:
            inventory_item = ingredient_link.inventory_item
            
            # Check if this ingredient is replaced by alternative
            if alternative and ingredient_link.inventory_item_id == alternative.replaces_ingredient_id:
                # Use alternative cost
                ing_quantity = alternative.quantity
                ing_unit = alternative.unit
                cost_inventory_item = alternative.inventory_item
            else:
                # Use base ingredient cost
                ing_quantity = ingredient_link.quantity
                ing_unit = ingredient_link.unit
                cost_inventory_item = inventory_item
            
            # Scale by weight or quantity
            if menu_item.is_weight_based and weight_kg:
                scaled_quantity = ing_quantity * weight_kg * quantity
            else:
                scaled_quantity = ing_quantity * quantity
            
            # Convert units if needed
            try:
                if ing_unit.lower() != cost_inventory_item.unit.lower():
                    scaled_quantity = UnitConverter.convert(
                        scaled_quantity,
                        ing_unit,
                        cost_inventory_item.unit
                    )
            except:
                pass  # Skip if conversion fails
            
            # Add to cost
            total_cost += scaled_quantity * cost_inventory_item.cost_per_unit
        
        # Add add-on costs
        for addon_id in item.get('selected_addon_ids', []):
            addon = db.query(MenuItemAddon).get(addon_id)
            if addon and addon.inventory_item:
                addon_quantity = addon.quantity
                
                # Convert units if needed
                try:
                    if addon.unit.lower() != addon.inventory_item.unit.lower():
                        addon_quantity = UnitConverter.convert(
                            addon_quantity,
                            addon.unit,
                            addon.inventory_item.unit
                        )
                except:
                    pass
                
                total_cost += addon_quantity * addon.inventory_item.cost_per_unit
        
        return int(total_cost)
            
    def process_payment(self, payment_method: str):
        """Process payment and complete order"""
        if not self.current_order_items:
            QMessageBox.information(self, "طلب فارغ", "لا توجد أصناف لمعالجتها")
            return
        
        db = get_session()
        try:
            # Calculate totals
            subtotal = sum(item['line_total'] for item in self.current_order_items)
            totals = PriceCalculator.calculate_order_total(subtotal, 0, 0, 0)
            
            # Generate order number
            order_number = OrderNumberGenerator.generate(db)
            
            # Create order
            order = Order(
                order_number=order_number,
                employee_id=AuthManager.current_user.id,
                session_id=AuthManager.current_session.id if AuthManager.current_session else None,
                table_id=self.current_table_id,
                order_type=self.current_order_type,
                timestamp=datetime.utcnow(),
                subtotal=subtotal,
                tax_amount=totals['tax_amount'],
                service_charge=totals['service_charge'],
                discount_amount=0,
                total=totals['total'],
                payment_method=payment_method,
                status='completed'
            )
            
            db.add(order)
            db.flush()
            
            # Create order items
            for item in self.current_order_items:
                menu_item = item['menu_item']
                
                # Calculate cost and profit
                calculated_cost = self.calculate_item_cost(db, item)
                net_profit = item['line_total'] - calculated_cost
                
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    item_name=menu_item.name_ar,
                    quantity=item['quantity'],
                    weight_kg=item.get('weight_kg'),
                    unit_price=item.get('unit_price', menu_item.base_price),
                    line_total=item['line_total'],
                    selected_alternative_id=item.get('selected_alternative_id'),
                    calculated_cost=calculated_cost,
                    net_profit=net_profit
                )
                db.add(order_item)
                db.flush()  # Get order_item.id
                
                # Create order item modifiers if any (old system)
                for modifier in item.get('modifiers', []):
                    from models.database import OrderItemModifier
                    order_modifier = OrderItemModifier(
                        order_item_id=order_item.id,
                        modifier_name_en=modifier['name_en'],
                        modifier_name_ar=modifier['name_ar'],
                        price_modifier=modifier['price_modifier']
                    )
                    db.add(order_modifier)
                
                # Create order item add-ons (new system)
                from models.database import OrderItemAddon, MenuItemAddon
                for addon_id in item.get('selected_addon_ids', []):
                    addon = db.query(MenuItemAddon).get(addon_id)
                    if addon:
                        order_addon = OrderItemAddon(
                            order_item_id=order_item.id,
                            addon_id=addon.id,
                            addon_name=addon.name_ar,
                            quantity=addon.quantity,
                            unit=addon.unit,
                            price=addon.price
                        )
                        db.add(order_addon)
            
            db.flush()
            
            # Refresh order to ensure relationships are loaded
            db.refresh(order)
            
            # Deduct inventory (modifies inventory items)
            InventoryManager.deduct_inventory(db, order.id)
            
            # Update session stats (modifies session)
            if AuthManager.current_session:
                SessionTracker.update_session_stats(db, AuthManager.current_session.id, order)
            
            # Commit everything in one transaction
            db.commit()
            
            # Release table if dine-in
            if self.current_order_type == 'dine-in' and self.current_table_id:
                table = db.query(RestaurantTable).get(self.current_table_id)
                if table:
                    table.status = 'available'
                    db.commit()
            
            # Clear order
            self.current_order_items.clear()
            self.update_order_display()
            
            QMessageBox.information(
                self,
                "تم الدفع",
                f"تم إنهاء الطلب {order_number}!\nالإجمالي: {CurrencyFormatter.format_lyd(order.total)}"
            )
            
            # Return to table selection
            self.current_table_id = None
            self.current_order_type = 'dine-in'
            self.table_selection.refresh_tables()
            self.stack.setCurrentIndex(0)
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر إتمام الدفع: {e}")
        finally:
            db.close()
            
    def handle_logout(self):
        """Handle logout request"""
        self.logout_requested.emit()


class WeightInputDialog(QDialog):
    """Dialog for entering weight for weight-based items"""
    
    def __init__(self, menu_item: MenuItem, parent=None):
        super().__init__(parent)
        self.menu_item = menu_item
        self.setWindowTitle(f"أدخل الوزن - {menu_item.name_ar}")
        self.setModal(True)
        self.setFixedWidth(350)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        label = QLabel(
            f"أدخل الوزن بالكيلوغرام:\nالسعر: {CurrencyFormatter.format_lyd(menu_item.price_per_kg)} لكل كجم"
        )
        label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(label)
        
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setMinimum(0.01)
        self.weight_input.setMaximum(100.0)
        self.weight_input.setDecimals(2)
        self.weight_input.setSingleStep(0.1)
        self.weight_input.setValue(0.5)
        self.weight_input.setSuffix(" كجم")
        self.weight_input.setFixedHeight(45)
        layout.addWidget(self.weight_input)
        
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #51CF66;")
        layout.addWidget(self.total_label)
        
        self.weight_input.valueChanged.connect(self.update_total)
        self.update_total()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn:
            ok_btn.setText("تأكيد")
        if cancel_btn:
            cancel_btn.setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def update_total(self):
        """Update total price display"""
        weight = self.weight_input.value()
        total = PriceCalculator.calculate_line_total(0, 1, weight, self.menu_item.price_per_kg)
        self.total_label.setText(f"الإجمالي: {CurrencyFormatter.format_lyd(total)}")
        
    def get_weight(self) -> float:
        """Get entered weight"""
        return self.weight_input.value()


class AdminPINDialog(QDialog):
    """Dialog for admin PIN verification"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        label = QLabel("أدخل رمز PIN للمدير:")
        label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(label)
        
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setFixedHeight(45)
        layout.addWidget(self.pin_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.verify_pin)
        buttons.rejected.connect(self.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn:
            ok_btn.setText("تأكيد")
        if cancel_btn:
            cancel_btn.setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def verify_pin(self):
        """Verify entered PIN"""
        db = get_session()
        try:
            if AuthManager.verify_admin_pin(db, self.pin_input.text()):
                self.accept()
            else:
                QMessageBox.warning(self, "رمز PIN غير صحيح", "يرجى المحاولة مرة أخرى")
                self.pin_input.clear()
        finally:
            db.close()
