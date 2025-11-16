"""
POS Item Customization Dialog
Allows customer to select alternatives and add-ons when adding item to cart
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QDoubleSpinBox, QRadioButton, QCheckBox, QButtonGroup,
                              QScrollArea, QWidget, QGroupBox, QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from models.database import get_session, MenuItem, MenuItemAlternative, MenuItemAddon
from utils.helpers import CurrencyFormatter


class POSItemCustomizeDialog(QDialog):
    """Dialog for customizing a menu item before adding to cart"""
    
    def __init__(self, menu_item_id, parent=None):
        super().__init__(parent)
        self.menu_item_id = menu_item_id
        self.menu_item = None
        self.selected_alternative = None
        self.selected_addons = []
        
        self.setWindowTitle("تخصيص الطلب")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.init_ui()
        self.load_item()
        self.calculate_price()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel()
        header_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #4ECDC4;")
        layout.addWidget(header_label)
        self.header_label = header_label
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        
        # Quantity/Weight Section
        self.quantity_card = QGroupBox("📏 الكمية")
        quantity_layout = QHBoxLayout()
        
        self.quantity_label = QLabel("الكمية:")
        quantity_layout.addWidget(self.quantity_label)
        
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.001)
        self.quantity_spin.setMaximum(100.0)
        self.quantity_spin.setDecimals(3)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setMinimumHeight(40)
        self.quantity_spin.setStyleSheet("font-size: 12pt;")
        self.quantity_spin.valueChanged.connect(self.calculate_price)
        quantity_layout.addWidget(self.quantity_spin)
        
        self.unit_label = QLabel("كغ")
        self.unit_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        quantity_layout.addWidget(self.unit_label)
        
        quantity_layout.addStretch()
        self.quantity_card.setLayout(quantity_layout)
        content_layout.addWidget(self.quantity_card)
        
        # Alternatives Section
        self.alternatives_card = QGroupBox("🔄 اختر البديل")
        self.alternatives_card.setStyleSheet("QGroupBox { font-size: 12pt; font-weight: bold; }")
        self.alternatives_layout = QVBoxLayout()
        
        self.alternatives_button_group = QButtonGroup()
        self.alternatives_button_group.buttonClicked.connect(self.on_alternative_selected)
        
        # Standard option (no alternative)
        standard_radio = QRadioButton("عادي (بدون تعديل)")
        standard_radio.setChecked(True)
        standard_radio.setStyleSheet("font-size: 11pt; padding: 8px;")
        standard_radio.setProperty("alternative_id", None)
        standard_radio.setProperty("price_modifier", 0)
        self.alternatives_button_group.addButton(standard_radio)
        self.alternatives_layout.addWidget(standard_radio)
        
        self.alternatives_card.setLayout(self.alternatives_layout)
        self.alternatives_card.setVisible(False)
        content_layout.addWidget(self.alternatives_card)
        
        # Add-ons Section
        self.addons_card = QGroupBox("➕ الإضافات")
        self.addons_card.setStyleSheet("QGroupBox { font-size: 12pt; font-weight: bold; }")
        self.addons_layout = QVBoxLayout()
        
        self.addon_checkboxes = []
        
        self.addons_card.setLayout(self.addons_layout)
        self.addons_card.setVisible(False)
        content_layout.addWidget(self.addons_card)
        
        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Price Summary
        price_frame = QFrame()
        price_frame.setFrameStyle(QFrame.Shape.Box)
        price_frame.setStyleSheet("background: #F8F9FA; border: 2px solid #4ECDC4; border-radius: 8px; padding: 15px;")
        price_layout = QGridLayout()
        
        price_layout.addWidget(QLabel("💵 السعر الأساسي:"), 0, 0)
        self.base_price_label = QLabel("0.000 د.ل")
        self.base_price_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        price_layout.addWidget(self.base_price_label, 0, 1)
        
        price_layout.addWidget(QLabel("🔄 تعديل البديل:"), 1, 0)
        self.alt_modifier_label = QLabel("0.000 د.ل")
        self.alt_modifier_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        price_layout.addWidget(self.alt_modifier_label, 1, 1)
        
        price_layout.addWidget(QLabel("➕ الإضافات:"), 2, 0)
        self.addons_total_label = QLabel("0.000 د.ل")
        self.addons_total_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        price_layout.addWidget(self.addons_total_label, 2, 1)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background: #DEE2E6;")
        price_layout.addWidget(separator, 3, 0, 1, 2)
        
        price_layout.addWidget(QLabel("💰 الإجمالي:"), 4, 0)
        self.total_price_label = QLabel("0.000 د.ل")
        self.total_price_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #51CF66;")
        price_layout.addWidget(self.total_price_label, 4, 1)
        
        price_frame.setLayout(price_layout)
        layout.addWidget(price_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setStyleSheet("font-size: 12pt;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("✅ إضافة للطلب")
        add_btn.setObjectName("success")
        add_btn.setMinimumHeight(45)
        add_btn.setMinimumWidth(150)
        add_btn.setStyleSheet("font-size: 12pt; font-weight: bold;")
        add_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(add_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_item(self):
        """Load menu item and its alternatives/add-ons"""
        db = get_session()
        try:
            self.menu_item = db.query(MenuItem).get(self.menu_item_id)
            if not self.menu_item:
                return
            
            # Set header
            self.header_label.setText(f"🍽️ {self.menu_item.name_ar}")
            
            # Configure quantity section
            if self.menu_item.is_weight_based:
                self.quantity_label.setText("الوزن:")
                self.unit_label.setText("كغ")
            else:
                self.quantity_label.setText("العدد:")
                self.unit_label.setText("قطعة")
                self.quantity_spin.setDecimals(0)
                self.quantity_spin.setMinimum(1)
            
            # Load alternatives
            alternatives = db.query(MenuItemAlternative).filter_by(
                menu_item_id=self.menu_item_id,
                active=True
            ).order_by(MenuItemAlternative.display_order).all()
            
            if alternatives:
                self.alternatives_card.setVisible(True)
                for alt in alternatives:
                    radio = QRadioButton()
                    price_mod = CurrencyFormatter.fils_to_lyd(alt.price_modifier)
                    if alt.price_modifier >= 0:
                        radio.setText(f"{alt.name_ar} (+{price_mod:.3f} د.ل)")
                    else:
                        radio.setText(f"{alt.name_ar} ({price_mod:.3f} د.ل)")
                    
                    radio.setStyleSheet("font-size: 11pt; padding: 8px;")
                    radio.setProperty("alternative_id", alt.id)
                    radio.setProperty("price_modifier", alt.price_modifier)
                    self.alternatives_button_group.addButton(radio)
                    self.alternatives_layout.addWidget(radio)
            
            # Load add-ons
            addons = db.query(MenuItemAddon).filter_by(
                menu_item_id=self.menu_item_id,
                active=True
            ).order_by(MenuItemAddon.display_order).all()
            
            if addons:
                self.addons_card.setVisible(True)
                for addon in addons:
                    checkbox = QCheckBox()
                    price_lyd = CurrencyFormatter.fils_to_lyd(addon.price)
                    checkbox.setText(f"{addon.name_ar} (+{price_lyd:.3f} د.ل)")
                    checkbox.setStyleSheet("font-size: 11pt; padding: 8px;")
                    checkbox.setProperty("addon_id", addon.id)
                    checkbox.setProperty("addon_price", addon.price)
                    checkbox.stateChanged.connect(self.calculate_price)
                    self.addon_checkboxes.append(checkbox)
                    self.addons_layout.addWidget(checkbox)
        
        finally:
            db.close()
    
    def on_alternative_selected(self, button):
        """Handle alternative selection"""
        self.selected_alternative = button.property("alternative_id")
        self.calculate_price()
    
    def calculate_price(self):
        """Calculate total price"""
        if not self.menu_item:
            return
        
        quantity = self.quantity_spin.value()
        
        # Base price
        if self.menu_item.is_weight_based:
            base_price_fils = self.menu_item.base_price * quantity
        else:
            base_price_fils = self.menu_item.base_price * int(quantity)
        
        # Alternative modifier
        alt_modifier_fils = 0
        selected_btn = self.alternatives_button_group.checkedButton()
        if selected_btn:
            alt_modifier_fils = selected_btn.property("price_modifier") or 0
            if self.menu_item.is_weight_based:
                alt_modifier_fils = alt_modifier_fils * quantity
        
        # Add-ons total
        addons_total_fils = 0
        for checkbox in self.addon_checkboxes:
            if checkbox.isChecked():
                addons_total_fils += checkbox.property("addon_price") or 0
        
        # Total
        total_fils = base_price_fils + alt_modifier_fils + addons_total_fils
        
        # Update labels
        self.base_price_label.setText(CurrencyFormatter.format_lyd(int(base_price_fils)))
        self.alt_modifier_label.setText(CurrencyFormatter.format_lyd(int(alt_modifier_fils)))
        self.addons_total_label.setText(CurrencyFormatter.format_lyd(int(addons_total_fils)))
        self.total_price_label.setText(CurrencyFormatter.format_lyd(int(total_fils)))
    
    def get_customization_data(self):
        """Get selected customization data"""
        # Get selected alternative
        selected_alternative_id = None
        selected_btn = self.alternatives_button_group.checkedButton()
        if selected_btn:
            selected_alternative_id = selected_btn.property("alternative_id")
        
        # Get selected add-ons
        selected_addon_ids = []
        for checkbox in self.addon_checkboxes:
            if checkbox.isChecked():
                selected_addon_ids.append(checkbox.property("addon_id"))
        
        # Get quantity/weight
        quantity = self.quantity_spin.value()
        if not self.menu_item.is_weight_based:
            quantity = int(quantity)
        
        # Calculate final price
        if self.menu_item.is_weight_based:
            base_price_fils = self.menu_item.base_price * quantity
        else:
            base_price_fils = self.menu_item.base_price * quantity
        
        alt_modifier_fils = 0
        if selected_btn:
            alt_modifier_fils = selected_btn.property("price_modifier") or 0
            if self.menu_item.is_weight_based:
                alt_modifier_fils = alt_modifier_fils * quantity
        
        addons_total_fils = 0
        for checkbox in self.addon_checkboxes:
            if checkbox.isChecked():
                addons_total_fils += checkbox.property("addon_price") or 0
        
        total_fils = base_price_fils + alt_modifier_fils + addons_total_fils
        
        return {
            'quantity': 1 if not self.menu_item.is_weight_based else 1,
            'weight_kg': quantity if self.menu_item.is_weight_based else None,
            'selected_alternative_id': selected_alternative_id,
            'selected_addon_ids': selected_addon_ids,
            'unit_price': int(total_fils / (quantity if self.menu_item.is_weight_based else max(1, quantity))),
            'line_total': int(total_fils)
        }
