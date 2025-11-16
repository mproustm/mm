"""
Widget components for menu item management (alternatives and add-ons)
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QLineEdit, QDoubleSpinBox, QComboBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from models.database import get_session, InventoryItem
from utils.helpers import CurrencyFormatter
from utils.unit_converter import calculate_ingredient_cost, calculate_alternative_cost_modifier


class AlternativeRow(QWidget):
    """Row for configuring an ingredient alternative"""
    
    remove_requested = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumHeight(80)
        self.setStyleSheet("QWidget { border: 1px solid #DEE2E6; border-radius: 5px; background: #F8F9FA; padding: 10px; margin: 5px; }")
        
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Row 1: Names
        layout.addWidget(QLabel("الاسم (عربي):"), 0, 0)
        self.name_ar = QLineEdit()
        self.name_ar.setPlaceholderText("مثال: بيني")
        layout.addWidget(self.name_ar, 0, 1)
        
        layout.addWidget(QLabel("Name (English):"), 0, 2)
        self.name_en = QLineEdit()
        self.name_en.setPlaceholderText("Example: Penne")
        layout.addWidget(self.name_en, 0, 3)
        
        # Row 2: Replaces which ingredient
        layout.addWidget(QLabel("يستبدل:"), 1, 0)
        self.replaces_combo = QComboBox()
        self.replaces_combo.setPlaceholderText("اختر المكون الأساسي")
        layout.addWidget(self.replaces_combo, 1, 1)
        
        # Row 3: Alternative ingredient from inventory
        layout.addWidget(QLabel("البديل من المخزون:"), 2, 0)
        self.inventory_combo = QComboBox()
        self.load_inventory_items()
        layout.addWidget(self.inventory_combo, 2, 1)
        
        layout.addWidget(QLabel("الكمية:"), 2, 2)
        qty_layout = QHBoxLayout()
        self.quantity = QDoubleSpinBox()
        self.quantity.setMinimum(0.001)
        self.quantity.setMaximum(10000.0)
        self.quantity.setDecimals(3)
        self.quantity.setValue(1.0)
        qty_layout.addWidget(self.quantity)
        
        self.unit = QComboBox()
        self.unit.addItems(["g", "kg", "ml", "l", "قطعة"])
        qty_layout.addWidget(self.unit)
        layout.addLayout(qty_layout, 2, 3)
        
        # Row 4: Price modifier
        layout.addWidget(QLabel("تعديل السعر (د.ل):"), 3, 0)
        self.price_modifier = QDoubleSpinBox()
        self.price_modifier.setMinimum(-1000.0)
        self.price_modifier.setMaximum(1000.0)
        self.price_modifier.setDecimals(3)
        self.price_modifier.setValue(0.0)
        self.price_modifier.setPrefix("+ " if self.price_modifier.value() >= 0 else "")
        self.price_modifier.valueChanged.connect(self.update_prefix)
        layout.addWidget(self.price_modifier, 3, 1)
        
        # Remove button
        remove_btn = QPushButton("🗑️ حذف")
        remove_btn.setObjectName("danger")
        remove_btn.setMinimumHeight(35)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn, 3, 3)
        
        self.setLayout(layout)
    
    def update_prefix(self, value):
        self.price_modifier.setPrefix("+ " if value >= 0 else "")
    
    def load_inventory_items(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_ar).all()
            for item in items:
                self.inventory_combo.addItem(
                    f"{item.name_ar} ({item.sku})",
                    item.id
                )
        finally:
            db.close()
    
    def set_replaces_items(self, ingredient_list):
        """Set the list of base ingredients that can be replaced"""
        self.replaces_combo.clear()
        for ing_id, ing_name in ingredient_list:
            self.replaces_combo.addItem(ing_name, ing_id)
    
    def get_data(self):
        return {
            'name_ar': self.name_ar.text(),
            'name_en': self.name_en.text(),
            'replaces_ingredient_id': self.replaces_combo.currentData(),
            'inventory_item_id': self.inventory_combo.currentData(),
            'quantity': self.quantity.value(),
            'unit': self.unit.currentText(),
            'price_modifier': int(self.price_modifier.value() * 1000)  # Convert to fils
        }
    
    def set_data(self, data):
        self.name_ar.setText(data.get('name_ar', ''))
        self.name_en.setText(data.get('name_en', ''))
        
        # Set replaces combo
        replaces_id = data.get('replaces_ingredient_id')
        for i in range(self.replaces_combo.count()):
            if self.replaces_combo.itemData(i) == replaces_id:
                self.replaces_combo.setCurrentIndex(i)
                break
        
        # Set inventory combo
        inv_id = data.get('inventory_item_id')
        for i in range(self.inventory_combo.count()):
            if self.inventory_combo.itemData(i) == inv_id:
                self.inventory_combo.setCurrentIndex(i)
                break
        
        self.quantity.setValue(data.get('quantity', 1.0))
        
        unit = data.get('unit', 'g')
        index = self.unit.findText(unit)
        if index >= 0:
            self.unit.setCurrentIndex(index)
        
        price_fils = data.get('price_modifier', 0)
        self.price_modifier.setValue(price_fils / 1000.0)


class AddonRow(QWidget):
    """Row for configuring a menu item add-on"""
    
    remove_requested = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumHeight(80)
        self.setStyleSheet("QWidget { border: 1px solid #DEE2E6; border-radius: 5px; background: #E3F2FD; padding: 10px; margin: 5px; }")
        
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Row 1: Names
        layout.addWidget(QLabel("الاسم (عربي):"), 0, 0)
        self.name_ar = QLineEdit()
        self.name_ar.setPlaceholderText("مثال: صوص ثوم إضافي")
        layout.addWidget(self.name_ar, 0, 1)
        
        layout.addWidget(QLabel("Name (English):"), 0, 2)
        self.name_en = QLineEdit()
        self.name_en.setPlaceholderText("Example: Extra Garlic Sauce")
        layout.addWidget(self.name_en, 0, 3)
        
        # Row 2: Inventory item
        layout.addWidget(QLabel("المكون من المخزون:"), 1, 0)
        self.inventory_combo = QComboBox()
        self.load_inventory_items()
        layout.addWidget(self.inventory_combo, 1, 1)
        
        # Quantity
        layout.addWidget(QLabel("الكمية:"), 1, 2)
        qty_layout = QHBoxLayout()
        self.quantity = QDoubleSpinBox()
        self.quantity.setMinimum(0.001)
        self.quantity.setMaximum(10000.0)
        self.quantity.setDecimals(3)
        self.quantity.setValue(1.0)
        qty_layout.addWidget(self.quantity)
        
        self.unit = QComboBox()
        self.unit.addItems(["g", "kg", "ml", "l", "قطعة"])
        qty_layout.addWidget(self.unit)
        layout.addLayout(qty_layout, 1, 3)
        
        # Row 3: Price
        layout.addWidget(QLabel("السعر (د.ل):"), 2, 0)
        self.price = QDoubleSpinBox()
        self.price.setMinimum(0.0)
        self.price.setMaximum(1000.0)
        self.price.setDecimals(3)
        self.price.setValue(0.0)
        layout.addWidget(self.price, 2, 1)
        
        # Remove button
        remove_btn = QPushButton("🗑️ حذف")
        remove_btn.setObjectName("danger")
        remove_btn.setMinimumHeight(35)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn, 2, 3)
        
        self.setLayout(layout)
    
    def load_inventory_items(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_ar).all()
            for item in items:
                self.inventory_combo.addItem(
                    f"{item.name_ar} ({item.sku})",
                    item.id
                )
        finally:
            db.close()
    
    def get_data(self):
        return {
            'name_ar': self.name_ar.text(),
            'name_en': self.name_en.text(),
            'inventory_item_id': self.inventory_combo.currentData(),
            'quantity': self.quantity.value(),
            'unit': self.unit.currentText(),
            'price': int(self.price.value() * 1000)  # Convert to fils
        }
    
    def set_data(self, data):
        self.name_ar.setText(data.get('name_ar', ''))
        self.name_en.setText(data.get('name_en', ''))
        
        # Set inventory combo
        inv_id = data.get('inventory_item_id')
        for i in range(self.inventory_combo.count()):
            if self.inventory_combo.itemData(i) == inv_id:
                self.inventory_combo.setCurrentIndex(i)
                break
        
        self.quantity.setValue(data.get('quantity', 1.0))
        
        unit = data.get('unit', 'g')
        index = self.unit.findText(unit)
        if index >= 0:
            self.unit.setCurrentIndex(index)
        
        price_fils = data.get('price', 0)
        self.price.setValue(price_fils / 1000.0)
