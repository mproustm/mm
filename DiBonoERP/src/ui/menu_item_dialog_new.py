"""
Enhanced Menu Item Dialog with Recipe Management and Customization Groups
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox,
                              QCheckBox, QDialogButtonBox, QMessageBox, QGridLayout,
                              QGroupBox, QScrollArea, QWidget, QFrame, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from models.database import (get_session, MenuItem, MenuCategory, InventoryItem,
                            MenuItemIngredient, MenuCustomizationGroup, MenuCustomizationOption)
from utils.helpers import CurrencyFormatter
from utils.unit_converter import UnitConverter


class IngredientRow(QWidget):
    """Single ingredient row with remove button"""
    
    remove_requested = pyqtSignal(object)  # Signal when remove button clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Ingredient selector
        self.ingredient_combo = QComboBox()
        self.ingredient_combo.setMinimumWidth(200)
        self.load_ingredients()
        layout.addWidget(self.ingredient_combo)
        
        # Quantity input
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.001)
        self.quantity_input.setMaximum(10000.0)
        self.quantity_input.setDecimals(3)
        self.quantity_input.setValue(1.0)
        self.quantity_input.setMinimumWidth(100)
        layout.addWidget(self.quantity_input)
        
        # Unit selector
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["g", "kg", "ml", "l", "غرام", "كجم", "ملل", "لتر", "قطعة", "حزمة"])
        self.unit_combo.setMinimumWidth(80)
        layout.addWidget(self.unit_combo)
        
        # Remove button
        remove_btn = QPushButton("🗑️")
        remove_btn.setMaximumWidth(40)
        remove_btn.setObjectName("danger")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def load_ingredients(self):
        """Load inventory items (ingredients only)"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_ar).all()
            for item in items:
                self.ingredient_combo.addItem(
                    f"{item.name_ar} ({item.sku}) - {item.unit}",
                    item.id
                )
        finally:
            db.close()
    
    def get_data(self):
        """Get ingredient data"""
        return {
            'inventory_item_id': self.ingredient_combo.currentData(),
            'quantity': self.quantity_input.value(),
            'unit': self.unit_combo.currentText()
        }
    
    def set_data(self, inventory_item_id, quantity, unit):
        """Set ingredient data"""
        # Find and set inventory item
        for i in range(self.ingredient_combo.count()):
            if self.ingredient_combo.itemData(i) == inventory_item_id:
                self.ingredient_combo.setCurrentIndex(i)
                break
        
        self.quantity_input.setValue(quantity)
        
        # Find and set unit
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)


class CustomizationOptionRow(QWidget):
    """Single customization option row"""
    
    remove_requested = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Option name (English)
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Name (English)")
        self.name_en_input.setMinimumWidth(120)
        layout.addWidget(self.name_en_input)
        
        # Option name (Arabic)
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("الاسم (عربي)")
        self.name_ar_input.setMinimumWidth(120)
        layout.addWidget(self.name_ar_input)
        
        # Price modifier
        layout.addWidget(QLabel("تعديل السعر (د.ل):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(-100.0)
        self.price_input.setMaximum(100.0)
        self.price_input.setDecimals(2)
        self.price_input.setValue(0.0)
        self.price_input.setMinimumWidth(80)
        layout.addWidget(self.price_input)
        
        # Is default
        self.default_checkbox = QCheckBox("افتراضي")
        layout.addWidget(self.default_checkbox)
        
        # Remove button
        remove_btn = QPushButton("🗑️")
        remove_btn.setMaximumWidth(40)
        remove_btn.setObjectName("danger")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_data(self):
        """Get option data"""
        return {
            'name_en': self.name_en_input.text().strip(),
            'name_ar': self.name_ar_input.text().strip(),
            'price_modifier': CurrencyFormatter.lyd_to_fils(self.price_input.value()),
            'is_default': self.default_checkbox.isChecked()
        }
    
    def set_data(self, name_en, name_ar, price_modifier, is_default):
        """Set option data"""
        self.name_en_input.setText(name_en)
        self.name_ar_input.setText(name_ar)
        self.price_input.setValue(CurrencyFormatter.fils_to_lyd(price_modifier))
        self.default_checkbox.setChecked(is_default)


class CustomizationGroupWidget(QGroupBox):
    """Widget for managing a single customization group"""
    
    remove_requested = pyqtSignal(object)
    
    def __init__(self, title="مجموعة خيارات جديدة", parent=None):
        super().__init__(title, parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.option_rows = []
        
        layout = QVBoxLayout()
        
        # Group settings
        settings_layout = QGridLayout()
        
        settings_layout.addWidget(QLabel("اسم المجموعة (إنجليزي):"), 0, 0)
        self.group_name_en = QLineEdit()
        self.group_name_en.setPlaceholderText("e.g., Cooking Style")
        settings_layout.addWidget(self.group_name_en, 0, 1)
        
        settings_layout.addWidget(QLabel("اسم المجموعة (عربي):"), 1, 0)
        self.group_name_ar = QLineEdit()
        self.group_name_ar.setPlaceholderText("مثال: طريقة الطهي")
        settings_layout.addWidget(self.group_name_ar, 1, 1)
        
        settings_layout.addWidget(QLabel("نوع الاختيار:"), 2, 0)
        selection_layout = QHBoxLayout()
        self.selection_type_group = QButtonGroup()
        self.single_radio = QRadioButton("اختيار واحد فقط")
        self.single_radio.setChecked(True)
        self.multiple_radio = QRadioButton("اختيارات متعددة")
        self.selection_type_group.addButton(self.single_radio)
        self.selection_type_group.addButton(self.multiple_radio)
        selection_layout.addWidget(self.single_radio)
        selection_layout.addWidget(self.multiple_radio)
        selection_layout.addStretch()
        settings_layout.addLayout(selection_layout, 2, 1)
        
        self.required_checkbox = QCheckBox("إلزامي (يجب الاختيار)")
        settings_layout.addWidget(self.required_checkbox, 3, 1)
        
        layout.addLayout(settings_layout)
        
        # Options list
        layout.addWidget(QLabel("الخيارات المتاحة:"))
        
        # Scrollable options area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout()
        self.options_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.options_container.setLayout(self.options_layout)
        scroll.setWidget(self.options_container)
        layout.addWidget(scroll)
        
        # Add option button
        add_option_btn = QPushButton("➕ إضافة خيار")
        add_option_btn.setObjectName("info")
        add_option_btn.clicked.connect(self.add_option_row)
        layout.addWidget(add_option_btn)
        
        # Remove group button
        remove_group_btn = QPushButton("🗑️ حذف هذه المجموعة")
        remove_group_btn.setObjectName("danger")
        remove_group_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_group_btn)
        
        self.setLayout(layout)
        
        # Add one default option row
        self.add_option_row()
    
    def add_option_row(self):
        """Add a new option row"""
        row = CustomizationOptionRow()
        row.remove_requested.connect(self.remove_option_row)
        self.option_rows.append(row)
        self.options_layout.addWidget(row)
    
    def remove_option_row(self, row):
        """Remove an option row"""
        if len(self.option_rows) > 1:  # Keep at least one option
            self.option_rows.remove(row)
            self.options_layout.removeWidget(row)
            row.deleteLater()
        else:
            QMessageBox.warning(self, "تحذير", "يجب أن تحتوي المجموعة على خيار واحد على الأقل")
    
    def get_data(self):
        """Get group and options data"""
        options = []
        for row in self.option_rows:
            data = row.get_data()
            if data['name_en'] and data['name_ar']:  # Only include complete options
                options.append(data)
        
        return {
            'name_en': self.group_name_en.text().strip(),
            'name_ar': self.group_name_ar.text().strip(),
            'selection_type': 'single' if self.single_radio.isChecked() else 'multiple',
            'required': self.required_checkbox.isChecked(),
            'options': options
        }
    
    def set_data(self, group_data, options_data):
        """Set group and options data"""
        self.group_name_en.setText(group_data.get('name_en', ''))
        self.group_name_ar.setText(group_data.get('name_ar', ''))
        
        if group_data.get('selection_type') == 'single':
            self.single_radio.setChecked(True)
        else:
            self.multiple_radio.setChecked(True)
        
        self.required_checkbox.setChecked(group_data.get('required', False))
        
        # Clear existing option rows
        for row in self.option_rows[:]:
            self.option_rows.remove(row)
            self.options_layout.removeWidget(row)
            row.deleteLater()
        
        # Add option rows
        for option_data in options_data:
            row = CustomizationOptionRow()
            row.remove_requested.connect(self.remove_option_row)
            row.set_data(
                option_data.get('name_en', ''),
                option_data.get('name_ar', ''),
                option_data.get('price_modifier', 0),
                option_data.get('is_default', False)
            )
            self.option_rows.append(row)
            self.options_layout.addWidget(row)


class EnhancedMenuItemDialog(QDialog):
    """Enhanced dialog for menu item with recipe and customization management"""
    
    def __init__(self, parent=None, item_id=None):
        super().__init__(parent)
        self.item_id = item_id
        self.ingredient_rows = []
        self.customization_groups = []
        
        self.setWindowTitle("تعديل صنف" if item_id else "إضافة صنف جديد")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Main layout with scroll
        main_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout()
        content_widget.setLayout(layout)
        scroll.setWidget(content_widget)
        
        # === BASIC INFORMATION SECTION ===
        basic_group = QGroupBox("📋 المعلومات الأساسية")
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("التصنيف:"), 0, 0)
        self.category_combo = QComboBox()
        self.load_categories()
        basic_layout.addWidget(self.category_combo, 0, 1)
        
        basic_layout.addWidget(QLabel("الاسم (إنجليزي):"), 1, 0)
        self.name_en_input = QLineEdit()
        basic_layout.addWidget(self.name_en_input, 1, 1)
        
        basic_layout.addWidget(QLabel("الاسم (عربي):"), 2, 0)
        self.name_ar_input = QLineEdit()
        basic_layout.addWidget(self.name_ar_input, 2, 1)
        
        basic_layout.addWidget(QLabel("الوصف (إنجليزي):"), 3, 0)
        self.desc_en_input = QTextEdit()
        self.desc_en_input.setMaximumHeight(60)
        basic_layout.addWidget(self.desc_en_input, 3, 1)
        
        basic_layout.addWidget(QLabel("الوصف (عربي):"), 4, 0)
        self.desc_ar_input = QTextEdit()
        self.desc_ar_input.setMaximumHeight(60)
        basic_layout.addWidget(self.desc_ar_input, 4, 1)
        
        self.weight_based_checkbox = QCheckBox("صنف يباع بالوزن (سعر بالكيلو)")
        self.weight_based_checkbox.stateChanged.connect(self.toggle_price_fields)
        basic_layout.addWidget(self.weight_based_checkbox, 5, 1)
        
        basic_layout.addWidget(QLabel("السعر (د.ل):"), 6, 0)
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.0)
        self.base_price_input.setMaximum(1000000.0)
        self.base_price_input.setDecimals(2)
        basic_layout.addWidget(self.base_price_input, 6, 1)
        
        basic_layout.addWidget(QLabel("السعر/كغ (د.ل):"), 7, 0)
        self.price_per_kg_input = QDoubleSpinBox()
        self.price_per_kg_input.setMinimum(0.0)
        self.price_per_kg_input.setMaximum(1000000.0)
        self.price_per_kg_input.setDecimals(2)
        self.price_per_kg_input.setEnabled(False)
        basic_layout.addWidget(self.price_per_kg_input, 7, 1)
        
        basic_layout.addWidget(QLabel("ترتيب العرض:"), 8, 0)
        self.order_input = QSpinBox()
        self.order_input.setMinimum(0)
        self.order_input.setMaximum(1000)
        basic_layout.addWidget(self.order_input, 8, 1)
        
        self.active_checkbox = QCheckBox("نشط")
        self.active_checkbox.setChecked(True)
        basic_layout.addWidget(self.active_checkbox, 9, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # === RECIPE SECTION ===
        recipe_group = QGroupBox("🍳 المكونات (الوصفة)")
        recipe_layout = QVBoxLayout()
        
        info_label = QLabel("💡 حدد المكونات اللازمة لتحضير هذا الصنف. سيتم احتساب التكلفة تلقائياً من أسعار المكونات.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #868E96; font-style: italic;")
        recipe_layout.addWidget(info_label)
        
        # Ingredients list
        ingredients_scroll = QScrollArea()
        ingredients_scroll.setWidgetResizable(True)
        ingredients_scroll.setMaximumHeight(250)
        
        self.ingredients_container = QWidget()
        self.ingredients_layout = QVBoxLayout()
        self.ingredients_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ingredients_container.setLayout(self.ingredients_layout)
        ingredients_scroll.setWidget(self.ingredients_container)
        recipe_layout.addWidget(ingredients_scroll)
        
        # Add ingredient button
        add_ingredient_btn = QPushButton("➕ إضافة مكون")
        add_ingredient_btn.setObjectName("success")
        add_ingredient_btn.clicked.connect(self.add_ingredient_row)
        recipe_layout.addWidget(add_ingredient_btn)
        
        # Cost summary
        cost_frame = QFrame()
        cost_frame.setFrameStyle(QFrame.Shape.Box)
        cost_frame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #DEE2E6; border-radius: 5px; padding: 10px;")
        cost_layout = QGridLayout()
        
        cost_layout.addWidget(QLabel("💰 تكلفة المكونات (تلقائي):"), 0, 0)
        self.recipe_cost_label = QLabel("0.000 د.ل")
        self.recipe_cost_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FD7E14;")
        cost_layout.addWidget(self.recipe_cost_label, 0, 1)
        
        cost_layout.addWidget(QLabel("💵 سعر البيع:"), 1, 0)
        self.selling_price_label = QLabel("0.000 د.ل")
        self.selling_price_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4ECDC4;")
        cost_layout.addWidget(self.selling_price_label, 1, 1)
        
        cost_layout.addWidget(QLabel("✅ صافي الربح:"), 2, 0)
        self.profit_label = QLabel("0.000 د.ل")
        self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #51CF66;")
        cost_layout.addWidget(self.profit_label, 2, 1)
        
        cost_layout.addWidget(QLabel("📊 نسبة الربح:"), 3, 0)
        self.margin_label = QLabel("0.0%")
        self.margin_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #868E96;")
        cost_layout.addWidget(self.margin_label, 3, 1)
        
        calc_btn = QPushButton("🔄 إعادة حساب التكلفة والربح")
        calc_btn.setObjectName("info")
        calc_btn.clicked.connect(self.calculate_costs)
        cost_layout.addWidget(calc_btn, 4, 0, 1, 2)
        
        cost_frame.setLayout(cost_layout)
        recipe_layout.addWidget(cost_frame)
        
        recipe_group.setLayout(recipe_layout)
        layout.addWidget(recipe_group)
        
        # === CUSTOMIZATION GROUPS SECTION ===
        custom_group = QGroupBox("⚙️ خيارات التخصيص (اختياري)")
        custom_layout = QVBoxLayout()
        
        info_label2 = QLabel("💡 أضف خيارات تخصيص للصنف (مثل: درجة الحرارة، الإضافات، الصلصات، إلخ)")
        info_label2.setWordWrap(True)
        info_label2.setStyleSheet("color: #868E96; font-style: italic;")
        custom_layout.addWidget(info_label2)
        
        # Customization groups list
        custom_scroll = QScrollArea()
        custom_scroll.setWidgetResizable(True)
        custom_scroll.setMaximumHeight(300)
        
        self.custom_container = QWidget()
        self.custom_layout = QVBoxLayout()
        self.custom_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.custom_container.setLayout(self.custom_layout)
        custom_scroll.setWidget(self.custom_container)
        custom_layout.addWidget(custom_scroll)
        
        # Add group button
        add_group_btn = QPushButton("➕ إضافة مجموعة خيارات")
        add_group_btn.setObjectName("success")
        add_group_btn.clicked.connect(self.add_customization_group)
        custom_layout.addWidget(add_group_btn)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # Add to main layout
        main_layout.addWidget(scroll)
        
        # === BUTTONS ===
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_item)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("💾 حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("❌ إلغاء")
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
        # Connect price change signals
        self.base_price_input.valueChanged.connect(self.update_profit_display)
        self.price_per_kg_input.valueChanged.connect(self.update_profit_display)
        
        # Load existing data if editing
        if item_id:
            self.load_item()
        else:
            # Add one default ingredient row
            self.add_ingredient_row()
    
    def load_categories(self):
        """Load categories"""
        db = get_session()
        try:
            categories = db.query(MenuCategory).filter_by(active=True).order_by(MenuCategory.display_order).all()
            for category in categories:
                self.category_combo.addItem(f"{category.icon} {category.name_ar}", category.id)
        finally:
            db.close()
    
    def toggle_price_fields(self):
        """Toggle price fields"""
        is_weight = self.weight_based_checkbox.isChecked()
        self.base_price_input.setEnabled(not is_weight)
        self.price_per_kg_input.setEnabled(is_weight)
        self.update_profit_display()
    
    def add_ingredient_row(self):
        """Add ingredient row"""
        row = IngredientRow()
        row.remove_requested.connect(self.remove_ingredient_row)
        row.ingredient_combo.currentIndexChanged.connect(self.calculate_costs)
        row.quantity_input.valueChanged.connect(self.calculate_costs)
        row.unit_combo.currentTextChanged.connect(self.calculate_costs)
        self.ingredient_rows.append(row)
        self.ingredients_layout.addWidget(row)
    
    def remove_ingredient_row(self, row):
        """Remove ingredient row"""
        self.ingredient_rows.remove(row)
        self.ingredients_layout.removeWidget(row)
        row.deleteLater()
        self.calculate_costs()
    
    def add_customization_group(self):
        """Add customization group"""
        group = CustomizationGroupWidget()
        group.remove_requested.connect(self.remove_customization_group)
        self.customization_groups.append(group)
        self.custom_layout.addWidget(group)
    
    def remove_customization_group(self, group):
        """Remove customization group"""
        reply = QMessageBox.question(self, "تأكيد الحذف",
            "هل تريد حذف مجموعة الخيارات هذه؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.customization_groups.remove(group)
            self.custom_layout.removeWidget(group)
            group.deleteLater()
    
    def calculate_costs(self):
        """Calculate recipe cost and profit"""
        total_cost_fils = 0
        db = get_session()
        
        try:
            for row in self.ingredient_rows:
                data = row.get_data()
                if not data['inventory_item_id']:
                    continue
                
                # Get inventory item
                inv_item = db.query(InventoryItem).get(data['inventory_item_id'])
                if not inv_item:
                    continue
                
                # Convert quantity to inventory item's unit
                try:
                    quantity_in_item_unit = UnitConverter.convert(
                        data['quantity'],
                        data['unit'],
                        inv_item.unit
                    )
                except ValueError:
                    # Can't convert - skip this ingredient
                    continue
                
                # Calculate cost
                ingredient_cost = quantity_in_item_unit * inv_item.cost_per_unit
                total_cost_fils += ingredient_cost
        
        finally:
            db.close()
        
        # Update displays
        self.recipe_cost_label.setText(CurrencyFormatter.format_lyd(int(total_cost_fils)))
        self.update_profit_display()
    
    def update_profit_display(self):
        """Update profit and margin display"""
        # Get selling price
        if self.weight_based_checkbox.isChecked():
            selling_price_fils = CurrencyFormatter.lyd_to_fils(self.price_per_kg_input.value())
        else:
            selling_price_fils = CurrencyFormatter.lyd_to_fils(self.base_price_input.value())
        
        self.selling_price_label.setText(CurrencyFormatter.format_lyd(selling_price_fils))
        
        # Get recipe cost
        cost_text = self.recipe_cost_label.text().replace(" د.ل", "").replace(",", "")
        try:
            recipe_cost_lyd = float(cost_text)
            recipe_cost_fils = CurrencyFormatter.lyd_to_fils(recipe_cost_lyd)
        except:
            recipe_cost_fils = 0
        
        # Calculate profit
        profit_fils = selling_price_fils - recipe_cost_fils
        self.profit_label.setText(CurrencyFormatter.format_lyd(profit_fils))
        
        # Update color based on profit
        if profit_fils > 0:
            self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #51CF66;")
        elif profit_fils < 0:
            self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FF6B6B;")
        else:
            self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #868E96;")
        
        # Calculate margin
        if selling_price_fils > 0:
            margin = (profit_fils / selling_price_fils) * 100
            self.margin_label.setText(f"{margin:.1f}%")
        else:
            self.margin_label.setText("0.0%")
    
    def load_item(self):
        """Load existing item data"""
        db = get_session()
        try:
            item = db.query(MenuItem).get(self.item_id)
            if not item:
                return
            
            # Basic info
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == item.category_id:
                    self.category_combo.setCurrentIndex(i)
                    break
            
            self.name_en_input.setText(item.name_en)
            self.name_ar_input.setText(item.name_ar)
            self.desc_en_input.setText(item.description_en or "")
            self.desc_ar_input.setText(item.description_ar or "")
            self.weight_based_checkbox.setChecked(item.is_weight_based)
            self.base_price_input.setValue(CurrencyFormatter.fils_to_lyd(item.base_price))
            self.price_per_kg_input.setValue(CurrencyFormatter.fils_to_lyd(item.price_per_kg or 0))
            self.order_input.setValue(item.display_order)
            self.active_checkbox.setChecked(item.active)
            self.toggle_price_fields()
            
            # Load ingredients
            for ingredient in item.ingredients:
                row = IngredientRow()
                row.remove_requested.connect(self.remove_ingredient_row)
                row.ingredient_combo.currentIndexChanged.connect(self.calculate_costs)
                row.quantity_input.valueChanged.connect(self.calculate_costs)
                row.unit_combo.currentTextChanged.connect(self.calculate_costs)
                row.set_data(ingredient.inventory_item_id, ingredient.quantity, ingredient.unit)
                self.ingredient_rows.append(row)
                self.ingredients_layout.addWidget(row)
            
            # Load customization groups
            for group in item.customization_groups:
                if not group.active:
                    continue
                
                group_widget = CustomizationGroupWidget(f"{group.name_ar}")
                group_widget.remove_requested.connect(self.remove_customization_group)
                
                # Set group data
                group_data = {
                    'name_en': group.name_en,
                    'name_ar': group.name_ar,
                    'selection_type': group.selection_type,
                    'required': group.required
                }
                
                # Get options
                options_data = []
                for option in group.options:
                    if option.active:
                        options_data.append({
                            'name_en': option.name_en,
                            'name_ar': option.name_ar,
                            'price_modifier': option.price_modifier,
                            'is_default': option.is_default
                        })
                
                group_widget.set_data(group_data, options_data)
                self.customization_groups.append(group_widget)
                self.custom_layout.addWidget(group_widget)
            
            # Calculate costs
            self.calculate_costs()
        
        finally:
            db.close()
    
    def save_item(self):
        """Save menu item with ingredients and customizations"""
        # Validate basic info
        name_en = self.name_en_input.text().strip()
        name_ar = self.name_ar_input.text().strip()
        category_id = self.category_combo.currentData()
        
        if not name_en or not name_ar or not category_id:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال الاسم والتصنيف")
            return
        
        # Get recipe cost
        cost_text = self.recipe_cost_label.text().replace(" د.ل", "").replace(",", "")
        try:
            recipe_cost_lyd = float(cost_text)
            recipe_cost_fils = CurrencyFormatter.lyd_to_fils(recipe_cost_lyd)
        except:
            recipe_cost_fils = 0
        
        db = get_session()
        try:
            # Create or update menu item
            if self.item_id:
                item = db.query(MenuItem).get(self.item_id)
            else:
                item = MenuItem()
                db.add(item)
            
            item.category_id = category_id
            item.name_en = name_en
            item.name_ar = name_ar
            item.description_en = self.desc_en_input.toPlainText()
            item.description_ar = self.desc_ar_input.toPlainText()
            item.is_weight_based = self.weight_based_checkbox.isChecked()
            item.base_price = CurrencyFormatter.lyd_to_fils(self.base_price_input.value())
            item.price_per_kg = CurrencyFormatter.lyd_to_fils(self.price_per_kg_input.value()) if item.is_weight_based else None
            item.recipe_cost = recipe_cost_fils
            item.display_order = self.order_input.value()
            item.active = self.active_checkbox.isChecked()
            
            db.flush()  # Get item.id
            
            # Delete old ingredients and customization groups
            if self.item_id:
                db.query(MenuItemIngredient).filter_by(menu_item_id=self.item_id).delete()
                db.query(MenuCustomizationGroup).filter_by(menu_item_id=self.item_id).delete()
            
            # Save ingredients
            for idx, row in enumerate(self.ingredient_rows):
                data = row.get_data()
                if data['inventory_item_id']:
                    ingredient = MenuItemIngredient(
                        menu_item_id=item.id,
                        inventory_item_id=data['inventory_item_id'],
                        quantity=data['quantity'],
                        unit=data['unit'],
                        display_order=idx
                    )
                    db.add(ingredient)
            
            # Save customization groups
            for idx, group_widget in enumerate(self.customization_groups):
                group_data = group_widget.get_data()
                
                if not group_data['name_en'] or not group_data['name_ar']:
                    continue  # Skip incomplete groups
                
                if not group_data['options']:
                    continue  # Skip groups with no options
                
                group = MenuCustomizationGroup(
                    menu_item_id=item.id,
                    name_en=group_data['name_en'],
                    name_ar=group_data['name_ar'],
                    selection_type=group_data['selection_type'],
                    required=group_data['required'],
                    display_order=idx,
                    active=True
                )
                db.add(group)
                db.flush()  # Get group.id
                
                # Save options
                for opt_idx, option_data in enumerate(group_data['options']):
                    option = MenuCustomizationOption(
                        group_id=group.id,
                        name_en=option_data['name_en'],
                        name_ar=option_data['name_ar'],
                        price_modifier=option_data['price_modifier'],
                        is_default=option_data['is_default'],
                        display_order=opt_idx,
                        active=True
                    )
                    db.add(option)
            
            db.commit()
            
            profit_fils = CurrencyFormatter.lyd_to_fils(self.base_price_input.value()) - recipe_cost_fils
            
            QMessageBox.information(self, "✅ تم بنجاح",
                f"تم حفظ الصنف '{name_ar}' بنجاح\n\n"
                f"💰 تكلفة المكونات: {CurrencyFormatter.format_lyd(recipe_cost_fils)}\n"
                f"💵 سعر البيع: {CurrencyFormatter.format_lyd(CurrencyFormatter.lyd_to_fils(self.base_price_input.value()))}\n"
                f"✅ صافي الربح: {CurrencyFormatter.format_lyd(profit_fils)}")
            
            self.accept()
        
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "❌ خطأ", f"تعذر حفظ الصنف:\n{str(e)}")
        
        finally:
            db.close()
