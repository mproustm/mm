"""
Full-Screen Menu Item Management with Fixed Layout Issues
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QLineEdit, QDoubleSpinBox, QTextEdit, QComboBox,
                              QCheckBox, QMessageBox, QGridLayout, QGroupBox, QScrollArea,
                              QFrame, QRadioButton, QButtonGroup, QTabWidget, QStackedWidget,
                              QSizePolicy, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from models.database import (get_session, MenuItem, MenuCategory, InventoryItem,
                            MenuItemIngredient, MenuCustomizationGroup, MenuCustomizationOption,
                            MenuItemAlternative, MenuItemAddon)
from utils.helpers import CurrencyFormatter
from utils.unit_converter import (UnitConverter, calculate_ingredient_cost, 
                                  calculate_alternative_cost_modifier,
                                  convert_recipe_to_inventory_units)
from ui.menu_item_widgets import AlternativeRow, AddonRow


class SimpleIngredientRow(QWidget):
    """Simple ingredient row with large, clear controls and auto cost calculation"""
    
    remove_requested = pyqtSignal(object)
    cost_changed = pyqtSignal()  # Signal when cost changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumHeight(60)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Ingredient selector - wider
        ingredient_label = QLabel("المكون:")
        ingredient_label.setMinimumWidth(80)
        layout.addWidget(ingredient_label)
        
        self.ingredient_combo = QComboBox()
        self.ingredient_combo.setMinimumWidth(300)
        self.ingredient_combo.setStyleSheet("QComboBox { padding: 8px; font-size: 11pt; }")
        self.ingredient_combo.currentIndexChanged.connect(self._on_ingredient_changed)
        self.load_ingredients()
        layout.addWidget(self.ingredient_combo)
        
        # Quantity input - larger
        qty_label = QLabel("الكمية:")
        qty_label.setMinimumWidth(60)
        layout.addWidget(qty_label)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.001)
        self.quantity_input.setMaximum(10000.0)
        self.quantity_input.setDecimals(3)
        self.quantity_input.setValue(1.0)
        self.quantity_input.setMinimumWidth(120)
        self.quantity_input.setStyleSheet("QDoubleSpinBox { padding: 8px; font-size: 11pt; }")
        self.quantity_input.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.quantity_input)
        
        # Unit selector - larger
        unit_label = QLabel("الوحدة:")
        unit_label.setMinimumWidth(60)
        layout.addWidget(unit_label)
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["g", "kg", "ml", "l", "غرام", "كجم", "ملل", "لتر", "قطعة", "حزمة", "pc", "slice"])
        self.unit_combo.setMinimumWidth(100)
        self.unit_combo.setStyleSheet("QComboBox { padding: 8px; font-size: 11pt; }")
        self.unit_combo.currentIndexChanged.connect(self._on_value_changed)
        layout.addWidget(self.unit_combo)
        
        # Cost display - read-only
        cost_label = QLabel("التكلفة:")
        cost_label.setMinimumWidth(60)
        layout.addWidget(cost_label)
        
        self.cost_display = QLabel("0.000 د.ل")
        self.cost_display.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #51CF66;
                padding: 8px;
                background-color: #F8FFF4;
                border-radius: 5px;
            }
        """)
        self.cost_display.setMinimumWidth(120)
        layout.addWidget(self.cost_display)
        
        layout.addStretch()
        
        # Remove button - larger and clearer
        remove_btn = QPushButton("🗑️ حذف")
        remove_btn.setMinimumWidth(100)
        remove_btn.setMinimumHeight(40)
        remove_btn.setObjectName("danger")
        remove_btn.setStyleSheet("QPushButton { font-size: 11pt; }")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
        
        # Add separator line
        self.setStyleSheet("QWidget { border-bottom: 1px solid #E9ECEF; }")
        
    def load_ingredients(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_ar).all()
            for item in items:
                self.ingredient_combo.addItem(
                    f"{item.name_ar} ({item.sku}) - {item.cost_per_unit/1000:.3f} د.ل/{item.unit}",
                    item.id
                )
        finally:
            db.close()
    
    def _on_ingredient_changed(self):
        """Recalculate cost when ingredient changes"""
        self._update_cost()
        self.cost_changed.emit()
    
    def _on_value_changed(self):
        """Recalculate cost when quantity or unit changes"""
        self._update_cost()
        self.cost_changed.emit()
    
    def _update_cost(self):
        """Calculate and display ingredient cost"""
        ingredient_id = self.ingredient_combo.currentData()
        if not ingredient_id:
            self.cost_display.setText("0.000 د.ل")
            return
        
        db = get_session()
        try:
            ingredient = db.query(InventoryItem).get(ingredient_id)
            if ingredient:
                quantity = self.quantity_input.value()
                unit = self.unit_combo.currentText()
                
                cost_fils = calculate_ingredient_cost(ingredient, quantity, unit)
                cost_lyd = cost_fils / 1000
                
                self.cost_display.setText(f"{cost_lyd:.3f} د.ل")
        except Exception as e:
            self.cost_display.setText("خطأ")
            print(f"Error calculating cost: {e}")
        finally:
            db.close()
    
    def get_cost_fils(self) -> int:
        """Get the calculated cost in fils"""
        ingredient_id = self.ingredient_combo.currentData()
        if not ingredient_id:
            return 0
        
        db = get_session()
        try:
            ingredient = db.query(InventoryItem).get(ingredient_id)
            if ingredient:
                quantity = self.quantity_input.value()
                unit = self.unit_combo.currentText()
                return calculate_ingredient_cost(ingredient, quantity, unit)
        except:
            return 0
        finally:
            db.close()
        
        return 0
    
    def get_data(self):
        return {
            'inventory_item_id': self.ingredient_combo.currentData(),
            'quantity': self.quantity_input.value(),
            'unit': self.unit_combo.currentText()
        }
    
    def set_data(self, inventory_item_id, quantity, unit):
        for i in range(self.ingredient_combo.count()):
            if self.ingredient_combo.itemData(i) == inventory_item_id:
                self.ingredient_combo.setCurrentIndex(i)
                break
        self.quantity_input.setValue(quantity)
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        self._update_cost()


class MenuItemManagementScreen(QWidget):
    """Multi-step wizard for menu item management"""
    
    back_requested = pyqtSignal()
    
    def __init__(self, item_id=None, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.ingredient_rows = []
        self.alternative_rows = []
        self.addon_rows = []
        self.customization_groups = []
        self.current_step = 0
        
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()
        
        if item_id:
            self.load_item()
    
    def init_ui(self):
        """Initialize wizard UI with steps"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # === HEADER ===
        header = QHBoxLayout()
        
        back_btn = QPushButton("◀ رجوع")
        back_btn.setObjectName("info")
        back_btn.setMinimumHeight(45)
        back_btn.setMinimumWidth(120)
        back_btn.setStyleSheet("QPushButton { font-size: 13pt; font-weight: bold; }")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(back_btn)
        
        self.title_label = QLabel("📝 إدارة صنف القائمة - الخطوة 1 من 3" if not self.item_id else "✏️ تعديل صنف - الخطوة 1 من 3")
        self.title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #4ECDC4;")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        layout.addLayout(header)
        
        # === STEP INDICATOR ===
        step_indicator = QHBoxLayout()
        step_indicator.setSpacing(10)
        
        self.step1_btn = QPushButton("1️⃣ المعلومات الأساسية")
        self.step1_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
        """)
        step_indicator.addWidget(self.step1_btn)
        
        self.step2_btn = QPushButton("2️⃣ الوصفة والمكونات")
        self.step2_btn.setStyleSheet("""
            QPushButton {
                background-color: #CED4DA;
                color: #6C757D;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
        """)
        step_indicator.addWidget(self.step2_btn)
        
        self.step3_btn = QPushButton("3️⃣ البدائل والإضافات")
        self.step3_btn.setStyleSheet("""
            QPushButton {
                background-color: #CED4DA;
                color: #6C757D;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
        """)
        step_indicator.addWidget(self.step3_btn)
        
        step_indicator.addStretch()
        layout.addLayout(step_indicator)
        
        # === STACKED WIDGET FOR STEPS ===
        self.step_stack = QStackedWidget()
        
        # Step 1: Basic Info
        self.step1_widget = self.create_step1()
        self.step_stack.addWidget(self.step1_widget)
        
        # Step 2: Recipe
        self.step2_widget = self.create_step2()
        self.step_stack.addWidget(self.step2_widget)
        
        # Step 3: Alternatives & Add-ons
        self.step3_widget = self.create_step3()
        self.step_stack.addWidget(self.step3_widget)
        
        layout.addWidget(self.step_stack, 1)
        
        # === NAVIGATION BUTTONS ===
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(15)
        
        nav_layout.addStretch()
        
        self.prev_btn = QPushButton("◀ السابق")
        self.prev_btn.setMinimumHeight(50)
        self.prev_btn.setMinimumWidth(150)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover:enabled {
                background-color: #5A6268;
            }
            QPushButton:disabled {
                background-color: #E9ECEF;
                color: #ADB5BD;
            }
        """)
        self.prev_btn.clicked.connect(self.go_previous)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("التالي ▶")
        self.next_btn.setMinimumHeight(50)
        self.next_btn.setMinimumWidth(150)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45B8AF;
            }
            QPushButton:pressed {
                background-color: #3DA39A;
            }
        """)
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.next_btn)
        
        self.save_btn = QPushButton("💾 حفظ الصنف")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setVisible(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #51CF66;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #40C057;
            }
            QPushButton:pressed {
                background-color: #37B24D;
            }
        """)
        self.save_btn.clicked.connect(self.save_item)
        nav_layout.addWidget(self.save_btn)
        
        layout.addLayout(nav_layout)
        
        self.setLayout(layout)
    
    def create_step1(self):
        """Create Step 1: Basic Information"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        step1_hint = QLabel("املأ التصنيف، الاسم العربي، الاسم الإنجليزي، وحدد إن كان الصنف مشروبًا غازيًا أو يباع بالوزن، ثم أدخل السعر قبل الضغط على التالي.")
        step1_hint.setWordWrap(True)
        step1_hint.setStyleSheet("""
            font-size: 12pt;
            color: #495057;
            background-color: #F1F3F5;
            border-radius: 8px;
            border-right: 4px solid #4ECDC4;
            padding: 12px 16px;
        """)
        content_layout.addWidget(step1_hint)
        
        # === BASIC INFO CARD ===
        basic_card = QGroupBox("📋 المعلومات الأساسية")
        basic_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        basic_card.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                border: 2px solid #4ECDC4;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                background-color: #F8FCFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 15px;
            }
        """)
        basic_layout = QGridLayout()
        basic_layout.setVerticalSpacing(20)
        basic_layout.setHorizontalSpacing(20)
        
        # Category
        cat_label = QLabel("التصنيف:")
        cat_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        basic_layout.addWidget(cat_label, 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(45)
        self.category_combo.setStyleSheet("QComboBox { padding: 10px; font-size: 12pt; }")
        self.load_categories()
        basic_layout.addWidget(self.category_combo, 0, 1)
        
        # Arabic Name
        name_ar_label = QLabel("الاسم (عربي):")
        name_ar_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        basic_layout.addWidget(name_ar_label, 1, 0)
        self.name_ar = QLineEdit()
        self.name_ar.setMinimumHeight(45)
        self.name_ar.setStyleSheet("QLineEdit { padding: 10px; font-size: 12pt; }")
        self.name_ar.setPlaceholderText("مثال: بيبسي كولا")
        basic_layout.addWidget(self.name_ar, 1, 1)
        
        # English Name
        name_en_label = QLabel("الاسم (إنجليزي):")
        name_en_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        basic_layout.addWidget(name_en_label, 2, 0)
        self.name_en = QLineEdit()
        self.name_en.setMinimumHeight(45)
        self.name_en.setStyleSheet("QLineEdit { padding: 10px; font-size: 12pt; }")
        self.name_en.setPlaceholderText("Example: Pepsi Cola")
        basic_layout.addWidget(self.name_en, 2, 1)
        
        # Item type checkboxes
        type_layout = QHBoxLayout()
        type_layout.setSpacing(20)
        
        self.is_soft_drink_checkbox = QCheckBox("🥤 مشروب غازي")
        self.is_soft_drink_checkbox.setStyleSheet("QCheckBox { font-size: 12pt; font-weight: bold; }")
        self.is_soft_drink_checkbox.stateChanged.connect(self.toggle_soft_drink_mode)
        type_layout.addWidget(self.is_soft_drink_checkbox)
        
        self.is_weight_based_checkbox = QCheckBox("⚖️ يباع بالوزن")
        self.is_weight_based_checkbox.setStyleSheet("QCheckBox { font-size: 12pt; font-weight: bold; }")
        self.is_weight_based_checkbox.stateChanged.connect(self.toggle_price_fields)
        type_layout.addWidget(self.is_weight_based_checkbox)
        
        self.active_checkbox = QCheckBox("✅ نشط")
        self.active_checkbox.setStyleSheet("QCheckBox { font-size: 12pt; font-weight: bold; }")
        self.active_checkbox.setChecked(True)
        type_layout.addWidget(self.active_checkbox)
        
        type_layout.addStretch()
        basic_layout.addLayout(type_layout, 3, 0, 1, 2)

        # Pricing inputs (base and per kg)
        self.price_section_widget = QWidget()
        price_form = QGridLayout()
        price_form.setContentsMargins(0, 0, 0, 0)
        price_form.setHorizontalSpacing(15)
        price_form.setVerticalSpacing(15)

        self.base_price_label = QLabel("السعر (د.ل):")
        self.base_price_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        price_form.addWidget(self.base_price_label, 0, 0)

        self.base_price = QDoubleSpinBox()
        self.base_price.setMinimum(0.0)
        self.base_price.setMaximum(1000000.0)
        self.base_price.setDecimals(3)
        self.base_price.setMinimumHeight(45)
        self.base_price.setStyleSheet("QDoubleSpinBox { padding: 10px; font-size: 12pt; }")
        self.base_price.valueChanged.connect(self.calculate_costs)
        price_form.addWidget(self.base_price, 0, 1)

        self.price_per_kg_label = QLabel("السعر/كغ (د.ل):")
        self.price_per_kg_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        price_form.addWidget(self.price_per_kg_label, 1, 0)

        self.price_per_kg = QDoubleSpinBox()
        self.price_per_kg.setMinimum(0.0)
        self.price_per_kg.setMaximum(1000000.0)
        self.price_per_kg.setDecimals(3)
        self.price_per_kg.setMinimumHeight(45)
        self.price_per_kg.setStyleSheet("QDoubleSpinBox { padding: 10px; font-size: 12pt; }")
        self.price_per_kg.valueChanged.connect(self.calculate_costs)
        price_form.addWidget(self.price_per_kg, 1, 1)

        self.price_per_kg_label.setVisible(False)
        self.price_per_kg.setVisible(False)

        self.price_section_widget.setLayout(price_form)
        basic_layout.addWidget(self.price_section_widget, 4, 0, 1, 2)
        
        basic_card.setLayout(basic_layout)
        content_layout.addWidget(basic_card)
        
        # === SOFT DRINK SECTION ===
        self.soft_drink_card = QGroupBox("🥤 إعدادات المشروب الغازي")
        self.soft_drink_card.setVisible(False)
        self.soft_drink_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.soft_drink_card.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                border: 2px solid #339AF0;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                background-color: #E7F5FF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 15px;
            }
        """)
        soft_drink_layout = QGridLayout()
        soft_drink_layout.setVerticalSpacing(20)
        soft_drink_layout.setHorizontalSpacing(20)
        
        inv_label = QLabel("اختر من المخزون:")
        inv_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        soft_drink_layout.addWidget(inv_label, 0, 0)
        self.soft_drink_inventory_combo = QComboBox()
        self.soft_drink_inventory_combo.setMinimumHeight(45)
        self.soft_drink_inventory_combo.setStyleSheet("QComboBox { padding: 10px; font-size: 12pt; }")
        self.load_inventory_items()
        self.soft_drink_inventory_combo.currentIndexChanged.connect(self.update_soft_drink_cost)
        soft_drink_layout.addWidget(self.soft_drink_inventory_combo, 0, 1)
        
        cost_label = QLabel("💰 تكلفة الوحدة:")
        cost_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        soft_drink_layout.addWidget(cost_label, 1, 0)
        self.soft_drink_cost_label = QLabel("0.000 د.ل")
        self.soft_drink_cost_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FD7E14;")
        soft_drink_layout.addWidget(self.soft_drink_cost_label, 1, 1)
        
        sell_label = QLabel("💵 سعر البيع (د.ل):")
        sell_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        soft_drink_layout.addWidget(sell_label, 2, 0)
        self.soft_drink_sell_price = QDoubleSpinBox()
        self.soft_drink_sell_price.setMinimum(0.0)
        self.soft_drink_sell_price.setMaximum(1000000.0)
        self.soft_drink_sell_price.setDecimals(3)
        self.soft_drink_sell_price.setMinimumHeight(45)
        self.soft_drink_sell_price.setStyleSheet("QDoubleSpinBox { padding: 10px; font-size: 12pt; }")
        self.soft_drink_sell_price.valueChanged.connect(self.update_soft_drink_profit)
        soft_drink_layout.addWidget(self.soft_drink_sell_price, 2, 1)
        
        profit_label = QLabel("✅ صافي الربح:")
        profit_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        soft_drink_layout.addWidget(profit_label, 3, 0)
        self.soft_drink_profit_label = QLabel("0.000 د.ل")
        self.soft_drink_profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #51CF66;")
        soft_drink_layout.addWidget(self.soft_drink_profit_label, 3, 1)
        
        self.soft_drink_card.setLayout(soft_drink_layout)
        content_layout.addWidget(self.soft_drink_card)
        
        # === DESCRIPTION SECTION ===
        desc_card = QGroupBox("📝 وصف الصنف (اختياري)")
        desc_card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        desc_card.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                border: 2px dashed #ADB5BD;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                background-color: #F8F9FA;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 15px;
            }
        """)
        desc_layout = QGridLayout()
        desc_layout.setHorizontalSpacing(20)
        desc_layout.setVerticalSpacing(15)

        desc_layout.addWidget(QLabel("الوصف (عربي):"), 0, 0)
        self.desc_ar = QTextEdit()
        self.desc_ar.setPlaceholderText("اكتب وصفاً موجزاً للصنف...")
        self.desc_ar.setFixedHeight(90)
        self.desc_ar.setStyleSheet("QTextEdit { font-size: 11pt; padding: 8px; }")
        desc_layout.addWidget(self.desc_ar, 0, 1)

        desc_layout.addWidget(QLabel("Description (English):"), 1, 0)
        self.desc_en = QTextEdit()
        self.desc_en.setPlaceholderText("Write a short description for the item...")
        self.desc_en.setFixedHeight(90)
        self.desc_en.setStyleSheet("QTextEdit { font-size: 11pt; padding: 8px; }")
        desc_layout.addWidget(self.desc_en, 1, 1)

        desc_card.setLayout(desc_layout)
        content_layout.addWidget(desc_card)
        
        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def create_step2(self):
        """Create Step 2: Recipe and Ingredients"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Show item name at top
        self.step2_item_name = QLabel("")
        self.step2_item_name.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #4ECDC4;
            padding: 15px;
            background-color: #E6FCFF;
            border-radius: 8px;
            border-right: 5px solid #4ECDC4;
        """)
        self.step2_item_name.setVisible(False)
        content_layout.addWidget(self.step2_item_name)

        step2_hint = QLabel("راجع الوصفة والمكونات الخاصة بالصنف الحالي قبل المتابعة إلى البدائل والإضافات.")
        step2_hint.setWordWrap(True)
        step2_hint.setStyleSheet("""
            font-size: 12pt;
            color: #495057;
            background-color: #FFF5E6;
            border-radius: 8px;
            border-right: 4px solid #FD7E14;
            padding: 12px 16px;
        """)
        content_layout.addWidget(step2_hint)
        
        # === RECIPE SECTION ===
        self.recipe_card = QGroupBox("🍳 الوصفة والمكونات")
        self.recipe_card.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                border: 2px solid #FD7E14;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                background-color: #FFF5E6;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 15px;
            }
        """)
        recipe_layout = QVBoxLayout()
        recipe_layout.setSpacing(15)
        
        # Ingredients container with scroll
        ingredients_scroll = QScrollArea()
        ingredients_scroll.setWidgetResizable(True)
        ingredients_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        ingredients_scroll.setStyleSheet("QScrollArea { border: 1px solid #DEE2E6; border-radius: 5px; background-color: white; }")
        
        self.ingredients_container = QWidget()
        self.ingredients_layout = QVBoxLayout()
        self.ingredients_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ingredients_layout.setSpacing(0)
        self.ingredients_layout.setContentsMargins(5, 5, 5, 5)
        self.ingredients_container.setLayout(self.ingredients_layout)
        ingredients_scroll.setWidget(self.ingredients_container)
        recipe_layout.addWidget(ingredients_scroll)
        
        add_btn = QPushButton("➕ إضافة مكون")
        add_btn.setMinimumHeight(50)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #51CF66;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #40C057;
            }
        """)
        add_btn.clicked.connect(self.add_ingredient_row)
        recipe_layout.addWidget(add_btn)
        
        # Cost summary
        cost_frame = QFrame()
        cost_frame.setFrameStyle(QFrame.Shape.Box)
        cost_frame.setStyleSheet("background: #F8F9FA; border: 2px solid #DEE2E6; border-radius: 8px; padding: 15px;")
        cost_layout = QGridLayout()
        cost_layout.setVerticalSpacing(15)
        cost_layout.setHorizontalSpacing(20)
        
        cost_lbl = QLabel("💰 تكلفة المكونات:")
        cost_lbl.setStyleSheet("font-size: 13pt; font-weight: bold;")
        cost_layout.addWidget(cost_lbl, 0, 0)
        self.recipe_cost_label = QLabel("0.000 د.ل")
        self.recipe_cost_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FD7E14;")
        cost_layout.addWidget(self.recipe_cost_label, 0, 1)
        
        profit_lbl = QLabel("✅ صافي الربح:")
        profit_lbl.setStyleSheet("font-size: 13pt; font-weight: bold;")
        cost_layout.addWidget(profit_lbl, 1, 0)
        self.profit_label = QLabel("0.000 د.ل")
        self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #51CF66;")
        cost_layout.addWidget(self.profit_label, 1, 1)
        
        calc_btn = QPushButton("🔄 إعادة الحساب")
        calc_btn.setMinimumHeight(45)
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45B8AF;
            }
        """)
        calc_btn.clicked.connect(self.calculate_costs)
        cost_layout.addWidget(calc_btn, 2, 0, 1, 2)
        
        cost_frame.setLayout(cost_layout)
        recipe_layout.addWidget(cost_frame)
        
        self.recipe_card.setLayout(recipe_layout)
        content_layout.addWidget(self.recipe_card)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def create_step3(self):
        """Create Step 3: Alternatives and Add-ons"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)

        step3_hint = QLabel("أضف أو عدّل البدائل والإضافات المتاحة للصنف ثم اضغط حفظ عند الانتهاء.")
        step3_hint.setWordWrap(True)
        step3_hint.setStyleSheet("""
            font-size: 12pt;
            color: #495057;
            background-color: #F8FFF4;
            border-radius: 8px;
            border-right: 4px solid #51CF66;
            padding: 12px 16px;
        """)
        content_layout.addWidget(step3_hint)

        self.step3_item_name = QLabel("")
        self.step3_item_name.setStyleSheet("""
            font-size: 15pt;
            font-weight: bold;
            color: #2E7D32;
            padding: 12px 15px;
            background-color: #E8F5E9;
            border-radius: 8px;
            border-right: 5px solid #51CF66;
        """)
        self.step3_item_name.setVisible(False)
        content_layout.addWidget(self.step3_item_name)
        
        # === ALTERNATIVES SECTION ===
        self.alternatives_card = QGroupBox("🔄 البدائل المتاحة")
        self.alternatives_card.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                color: #1282A2;
                border: 3px solid #1282A2;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 25px;
                background-color: #F8FCFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 15px;
                background-color: #E3F2FD;
                border-radius: 5px;
                color: #1282A2;
                right: 15px;
                top: 10px;
            }
        """)
        alternatives_main_layout = QVBoxLayout()
        alternatives_main_layout.setSpacing(15)
        alternatives_main_layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("💡 أضف بدائل للمكونات (مثال: بيني بدلاً من معكرونة عادية)")
        info_label.setStyleSheet("""
            color: #1282A2;
            font-style: italic;
            font-size: 11pt;
            padding: 10px 15px;
            background-color: #E8F4F8;
            border-radius: 5px;
            border-right: 4px solid #1282A2;
        """)
        alternatives_main_layout.addWidget(info_label)
        
        # Alternatives scroll area
        alternatives_scroll = QScrollArea()
        alternatives_scroll.setWidgetResizable(True)
        alternatives_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        alternatives_scroll.setStyleSheet("""
            QScrollArea { 
                border: 1px solid #B3D9E6; 
                border-radius: 5px; 
                background-color: white;
            }
        """)
        
        alternatives_container = QWidget()
        self.alternatives_layout = QVBoxLayout()
        self.alternatives_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.alternatives_layout.setSpacing(10)
        self.alternatives_layout.setContentsMargins(10, 10, 10, 10)
        alternatives_container.setLayout(self.alternatives_layout)
        alternatives_scroll.setWidget(alternatives_container)
        alternatives_main_layout.addWidget(alternatives_scroll)
        
        add_alt_btn = QPushButton("➕ إضافة بديل")
        add_alt_btn.setStyleSheet("""
            QPushButton {
                background-color: #1282A2;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #0D5F7E;
            }
            QPushButton:pressed {
                background-color: #094A63;
            }
        """)
        add_alt_btn.clicked.connect(self.add_alternative_row)
        alternatives_main_layout.addWidget(add_alt_btn)
        
        self.alternatives_card.setLayout(alternatives_main_layout)
        content_layout.addWidget(self.alternatives_card)
        
        # === ADD-ONS SECTION ===
        self.addons_card = QGroupBox("➕ الإضافات المتاحة")
        self.addons_card.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                color: #2E7D32;
                border: 3px solid #51CF66;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 25px;
                background-color: #F1F8E9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 5px 15px;
                background-color: #C8E6C9;
                border-radius: 5px;
                color: #2E7D32;
                right: 15px;
                top: 10px;
            }
        """)
        addons_main_layout = QVBoxLayout()
        addons_main_layout.setSpacing(15)
        addons_main_layout.setContentsMargins(15, 15, 15, 15)
        
        addon_info = QLabel("💡 أضف إضافات يمكن للزبون طلبها مع الصنف (مثال: صوص إضافي، خضار مشوي)")
        addon_info.setStyleSheet("""
            color: #2E7D32;
            font-style: italic;
            font-size: 11pt;
            padding: 10px 15px;
            background-color: #E8F5E9;
            border-radius: 5px;
            border-right: 4px solid #51CF66;
        """)
        addons_main_layout.addWidget(addon_info)
        
        # Add-ons scroll area
        addons_scroll = QScrollArea()
        addons_scroll.setWidgetResizable(True)
        addons_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        addons_scroll.setStyleSheet("""
            QScrollArea { 
                border: 1px solid #A9D5A9; 
                border-radius: 5px; 
                background-color: white;
            }
        """)
        
        addons_container = QWidget()
        self.addons_layout = QVBoxLayout()
        self.addons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.addons_layout.setSpacing(10)
        self.addons_layout.setContentsMargins(10, 10, 10, 10)
        addons_container.setLayout(self.addons_layout)
        addons_scroll.setWidget(addons_container)
        addons_main_layout.addWidget(addons_scroll)
        
        add_addon_btn = QPushButton("➕ إضافة إضافة")
        add_addon_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #1B5E20;
            }
            QPushButton:pressed {
                background-color: #104D1A;
            }
        """)
        add_addon_btn.clicked.connect(self.add_addon_row)
        addons_main_layout.addWidget(add_addon_btn)
        
        self.addons_card.setLayout(addons_main_layout)
        content_layout.addWidget(self.addons_card)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def go_next(self):
        """Go to next step"""
        if self.current_step == 0:
            # Validate step 1
            category_id = self.category_combo.currentData()
            if not category_id:
                QMessageBox.warning(self, "بيانات ناقصة", "يرجى اختيار التصنيف")
                return

            name_ar = self.name_ar.text().strip()
            if not name_ar:
                QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال الاسم العربي")
                return

            name_en = self.name_en.text().strip()
            if not name_en:
                QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال الاسم الإنجليزي")
                return

            is_soft_drink = self.is_soft_drink_checkbox.isChecked()
            is_weight = self.is_weight_based_checkbox.isChecked()

            if is_soft_drink:
                if not self.soft_drink_inventory_combo.currentData():
                    QMessageBox.warning(self, "بيانات ناقصة", "يرجى اختيار الصنف من المخزون")
                    return
                if self.soft_drink_sell_price.value() <= 0:
                    QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال سعر بيع للمشروب الغازي")
                    return
            else:
                if not is_weight and self.base_price.value() <= 0:
                    QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال سعر بيع للصنف")
                    return
                if is_weight and self.price_per_kg.value() <= 0:
                    QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال سعر الكيلو للصنف الوزن")
                    return
            
            # Update step 2 & 3 headers with the current item name
            item_name = f"📋 الصنف: {name_ar}"
            if name_en:
                item_name += f" ({name_en})"
            self.step2_item_name.setText(item_name)
            self.step2_item_name.setVisible(True)
            self.step3_item_name.setText(item_name)
            self.step3_item_name.setVisible(True)
        
        self.current_step += 1
        self.step_stack.setCurrentIndex(self.current_step)
        self.update_navigation()
    
    def go_previous(self):
        """Go to previous step"""
        self.current_step -= 1
        self.step_stack.setCurrentIndex(self.current_step)
        self.update_navigation()
    
    def update_navigation(self):
        """Update navigation buttons and step indicators"""
        # Update title
        step_num = self.current_step + 1
        prefix = "📝 إدارة صنف القائمة" if not self.item_id else "✏️ تعديل صنف"
        self.title_label.setText(f"{prefix} - الخطوة {step_num} من 3")
        
        # Update step indicators
        active_style = """
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: #CED4DA;
                color: #6C757D;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
        """
        completed_style = """
            QPushButton {
                background-color: #51CF66;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
        """
        
        if self.current_step == 0:
            self.step1_btn.setStyleSheet(active_style)
            self.step2_btn.setStyleSheet(inactive_style)
            self.step3_btn.setStyleSheet(inactive_style)
        elif self.current_step == 1:
            self.step1_btn.setStyleSheet(completed_style)
            self.step2_btn.setStyleSheet(active_style)
            self.step3_btn.setStyleSheet(inactive_style)
        else:
            self.step1_btn.setStyleSheet(completed_style)
            self.step2_btn.setStyleSheet(completed_style)
            self.step3_btn.setStyleSheet(active_style)
        
        # Update navigation buttons
        self.prev_btn.setEnabled(self.current_step > 0)
        
        if self.current_step < 2:
            self.next_btn.setVisible(True)
            self.save_btn.setVisible(False)
        else:
            self.next_btn.setVisible(False)
            self.save_btn.setVisible(True)
    
    def load_categories(self):
        """Load categories"""
        db = get_session()
        try:
            categories = db.query(MenuCategory).filter_by(active=True).order_by(MenuCategory.display_order).all()
            for category in categories:
                self.category_combo.addItem(f"{category.icon} {category.name_ar}", category.id)
        finally:
            db.close()
    
    def load_inventory_items(self):
        """Load inventory items for soft drinks"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_ar).all()
            for item in items:
                self.soft_drink_inventory_combo.addItem(
                    f"{item.name_ar} ({item.sku}) - {CurrencyFormatter.format_lyd(item.cost_per_unit)}",
                    item.id
                )
        finally:
            db.close()
    
    def toggle_soft_drink_mode(self):
        """Toggle soft drink specific fields"""
        is_soft_drink = self.is_soft_drink_checkbox.isChecked()
        self.soft_drink_card.setVisible(is_soft_drink)
        self.price_section_widget.setVisible(not is_soft_drink)
        self.recipe_card.setVisible(not is_soft_drink)
        self.alternatives_card.setVisible(not is_soft_drink)
        
        if is_soft_drink:
            self.is_weight_based_checkbox.setChecked(False)
            self.is_weight_based_checkbox.setEnabled(False)
            self.update_soft_drink_cost()
        else:
            self.is_weight_based_checkbox.setEnabled(True)
    
    def toggle_price_fields(self):
        """Toggle price fields based on weight-based checkbox"""
        is_weight = self.is_weight_based_checkbox.isChecked()
        self.base_price_label.setVisible(not is_weight)
        self.base_price.setVisible(not is_weight)
        self.price_per_kg_label.setVisible(is_weight)
        self.price_per_kg.setVisible(is_weight)
    
    def update_soft_drink_cost(self):
        """Update soft drink cost from inventory"""
        item_id = self.soft_drink_inventory_combo.currentData()
        if not item_id:
            return
        
        db = get_session()
        try:
            item = db.query(InventoryItem).get(item_id)
            if item:
                self.soft_drink_cost_label.setText(CurrencyFormatter.format_lyd(item.cost_per_unit))
                self.update_soft_drink_profit()
        finally:
            db.close()
    
    def update_soft_drink_profit(self):
        """Calculate and display soft drink profit"""
        cost_text = self.soft_drink_cost_label.text().replace(" د.ل", "").replace(",", "")
        try:
            cost_lyd = float(cost_text)
            cost_fils = CurrencyFormatter.lyd_to_fils(cost_lyd)
        except:
            cost_fils = 0
        
        sell_fils = CurrencyFormatter.lyd_to_fils(self.soft_drink_sell_price.value())
        profit_fils = sell_fils - cost_fils
        
        self.soft_drink_profit_label.setText(CurrencyFormatter.format_lyd(profit_fils))
        
        if profit_fils > 0:
            self.soft_drink_profit_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #51CF66;")
        elif profit_fils < 0:
            self.soft_drink_profit_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #FF6B6B;")
        else:
            self.soft_drink_profit_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #868E96;")
    
    def add_ingredient_row(self):
        """Add ingredient row"""
        row = SimpleIngredientRow()
        row.remove_requested.connect(self.remove_ingredient_row)
        row.cost_changed.connect(self.calculate_costs)  # Auto recalculate when cost changes
        self.ingredient_rows.append(row)
        self.ingredients_layout.addWidget(row)
    
    def remove_ingredient_row(self, row):
        """Remove ingredient row"""
        self.ingredient_rows.remove(row)
        self.ingredients_layout.removeWidget(row)
        row.deleteLater()
        self.calculate_costs()
        self.update_alternative_dropdowns()
    
    def add_alternative_row(self):
        """Add alternative row"""
        row = AlternativeRow()
        row.remove_requested.connect(self.remove_alternative_row)
        self.alternative_rows.append(row)
        self.alternatives_layout.addWidget(row)
        self.update_alternative_dropdowns()
    
    def remove_alternative_row(self, row):
        """Remove alternative row"""
        self.alternative_rows.remove(row)
        self.alternatives_layout.removeWidget(row)
        row.deleteLater()
    
    def update_alternative_dropdowns(self):
        """Update the 'replaces' dropdown in all alternative rows with current ingredients"""
        db = get_session()
        try:
            ingredient_list = []
            for row in self.ingredient_rows:
                data = row.get_data()
                if data['inventory_item_id']:
                    inv_item = db.query(InventoryItem).get(data['inventory_item_id'])
                    if inv_item:
                        ingredient_list.append((inv_item.id, inv_item.name_ar))
            
            for alt_row in self.alternative_rows:
                alt_row.set_replaces_items(ingredient_list)
        finally:
            db.close()
    
    def add_addon_row(self):
        """Add addon row"""
        row = AddonRow()
        row.remove_requested.connect(self.remove_addon_row)
        self.addon_rows.append(row)
        self.addons_layout.addWidget(row)
    
    def remove_addon_row(self, row):
        """Remove addon row"""
        self.addon_rows.remove(row)
        self.addons_layout.removeWidget(row)
        row.deleteLater()
    
    def calculate_costs(self):
        """Calculate recipe cost and profit"""
        total_cost_fils = 0
        
        # Sum up all ingredient costs (they auto-calculate)
        for row in self.ingredient_rows:
            total_cost_fils += row.get_cost_fils()
        
        self.recipe_cost_label.setText(CurrencyFormatter.format_lyd(int(total_cost_fils)))
        
        # Get selling price based on item type
        if self.is_weight_based_checkbox.isChecked():
            selling_price_fils = CurrencyFormatter.lyd_to_fils(self.price_per_kg.value())
        else:
            selling_price_fils = CurrencyFormatter.lyd_to_fils(self.base_price.value())
        
        # Calculate profit
        profit_fils = selling_price_fils - total_cost_fils
        self.profit_label.setText(CurrencyFormatter.format_lyd(int(profit_fils)))
        
        # Color-code profit
        if profit_fils > 0:
            self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #51CF66;")
        elif profit_fils < 0:
            self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FF6B6B;")
        else:
            self.profit_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #868E96;")
    
    def load_item(self):
        """Load existing item"""
        db = get_session()
        try:
            item = db.query(MenuItem).get(self.item_id)
            if not item:
                return
            
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == item.category_id:
                    self.category_combo.setCurrentIndex(i)
                    break
            
            self.name_ar.setText(item.name_ar)
            self.name_en.setText(item.name_en)
            self.desc_ar.setText(item.description_ar or "")
            self.desc_en.setText(item.description_en or "")
            self.is_weight_based_checkbox.setChecked(item.is_weight_based)
            self.base_price.setValue(CurrencyFormatter.fils_to_lyd(item.base_price))
            self.price_per_kg.setValue(CurrencyFormatter.fils_to_lyd(item.price_per_kg or 0))
            self.active_checkbox.setChecked(item.active)
            
            is_beverage = item.item_type == 'beverage' or (item.linked_inventory_id is not None)
            
            if is_beverage:
                self.is_soft_drink_checkbox.setChecked(True)
                inv_id = item.linked_inventory_id or (item.ingredients[0].inventory_item_id if item.ingredients else None)
                if inv_id:
                    for i in range(self.soft_drink_inventory_combo.count()):
                        if self.soft_drink_inventory_combo.itemData(i) == inv_id:
                            self.soft_drink_inventory_combo.setCurrentIndex(i)
                            break
                self.soft_drink_sell_price.setValue(CurrencyFormatter.fils_to_lyd(item.base_price))
            else:
                for ingredient in item.ingredients:
                    row = SimpleIngredientRow()
                    row.remove_requested.connect(self.remove_ingredient_row)
                    row.ingredient_combo.currentIndexChanged.connect(self.calculate_costs)
                    row.quantity_input.valueChanged.connect(self.calculate_costs)
                    row.unit_combo.currentTextChanged.connect(self.calculate_costs)
                    row.set_data(ingredient.inventory_item_id, ingredient.quantity, ingredient.unit)
                    self.ingredient_rows.append(row)
                    self.ingredients_layout.addWidget(row)
                
                self.update_alternative_dropdowns()
                
                for alternative in item.alternatives:
                    row = AlternativeRow()
                    row.remove_requested.connect(self.remove_alternative_row)
                    row.set_data({
                        'name_ar': alternative.name_ar,
                        'name_en': alternative.name_en,
                        'replaces_ingredient_id': alternative.replaces_ingredient_id,
                        'inventory_item_id': alternative.inventory_item_id,
                        'quantity': alternative.quantity,
                        'unit': alternative.unit,
                        'price_modifier': alternative.price_modifier
                    })
                    self.alternative_rows.append(row)
                    self.alternatives_layout.addWidget(row)
                    self.update_alternative_dropdowns()
            
            for addon in item.addons:
                row = AddonRow()
                row.remove_requested.connect(self.remove_addon_row)
                row.set_data({
                    'name_ar': addon.name_ar,
                    'name_en': addon.name_en,
                    'inventory_item_id': addon.inventory_item_id,
                    'quantity': addon.quantity,
                    'unit': addon.unit,
                    'price': addon.price
                })
                self.addon_rows.append(row)
                self.addons_layout.addWidget(row)
            
            self.calculate_costs()
            self.toggle_price_fields()
        
        finally:
            db.close()
    
    def save_item(self):
        """Save menu item"""
        name_ar = self.name_ar.text().strip()
        name_en = self.name_en.text().strip()
        category_id = self.category_combo.currentData()
        
        if not name_ar or not name_en or not category_id:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال الاسم والتصنيف")
            return
        
        is_soft_drink = self.is_soft_drink_checkbox.isChecked()
        
        if is_soft_drink:
            if not self.soft_drink_inventory_combo.currentData():
                QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى اختيار الصنف من المخزون")
                return
            if self.soft_drink_sell_price.value() <= 0:
                QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال سعر البيع")
                return
        
        db = get_session()
        try:
            if self.item_id:
                item = db.query(MenuItem).get(self.item_id)
            else:
                item = MenuItem()
                db.add(item)
            
            item.category_id = category_id
            item.name_en = name_en
            item.name_ar = name_ar
            item.description_en = self.desc_en.toPlainText()
            item.description_ar = self.desc_ar.toPlainText()
            item.is_weight_based = self.is_weight_based_checkbox.isChecked()
            item.active = self.active_checkbox.isChecked()
            item.display_order = 0
            item.item_type = 'beverage' if is_soft_drink else 'dish'
            
            if is_soft_drink:
                item.base_price = CurrencyFormatter.lyd_to_fils(self.soft_drink_sell_price.value())
                item.price_per_kg = None
                item.linked_inventory_id = self.soft_drink_inventory_combo.currentData()
                
                inv_item = db.query(InventoryItem).get(self.soft_drink_inventory_combo.currentData())
                item.recipe_cost = inv_item.cost_per_unit if inv_item else 0
            else:
                item.base_price = CurrencyFormatter.lyd_to_fils(self.base_price.value())
                item.price_per_kg = CurrencyFormatter.lyd_to_fils(self.price_per_kg.value()) if item.is_weight_based else None
                item.linked_inventory_id = None
                
                cost_text = self.recipe_cost_label.text().replace(" د.ل", "").replace(",", "")
                try:
                    item.recipe_cost = CurrencyFormatter.lyd_to_fils(float(cost_text))
                except:
                    item.recipe_cost = 0
            
            db.flush()
            
            if self.item_id:
                db.query(MenuItemIngredient).filter_by(menu_item_id=self.item_id).delete()
                db.query(MenuItemAlternative).filter_by(menu_item_id=self.item_id).delete()
                db.query(MenuItemAddon).filter_by(menu_item_id=self.item_id).delete()
            
            if is_soft_drink:
                ingredient = MenuItemIngredient(
                    menu_item_id=item.id,
                    inventory_item_id=self.soft_drink_inventory_combo.currentData(),
                    quantity=1,
                    unit='قطعة',
                    display_order=0
                )
                db.add(ingredient)
            else:
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
                
                for idx, row in enumerate(self.alternative_rows):
                    data = row.get_data()
                    if data['inventory_item_id'] and data['replaces_ingredient_id']:
                        alternative = MenuItemAlternative(
                            menu_item_id=item.id,
                            replaces_ingredient_id=data['replaces_ingredient_id'],
                            inventory_item_id=data['inventory_item_id'],
                            name_en=data['name_en'],
                            name_ar=data['name_ar'],
                            quantity=data['quantity'],
                            unit=data['unit'],
                            price_modifier=data['price_modifier'],
                            display_order=idx,
                            active=True
                        )
                        db.add(alternative)
            
            for idx, row in enumerate(self.addon_rows):
                data = row.get_data()
                if data['inventory_item_id']:
                    addon = MenuItemAddon(
                        menu_item_id=item.id,
                        inventory_item_id=data['inventory_item_id'],
                        name_en=data['name_en'],
                        name_ar=data['name_ar'],
                        quantity=data['quantity'],
                        unit=data['unit'],
                        price=data['price'],
                        display_order=idx,
                        active=True
                    )
                    db.add(addon)
            
            db.commit()
            
            profit_fils = item.base_price - item.recipe_cost
            QMessageBox.information(self, "✅ تم بنجاح",
                f"تم حفظ الصنف '{name_ar}' بنجاح\n\n"
                f"💰 التكلفة: {CurrencyFormatter.format_lyd(item.recipe_cost)}\n"
                f"💵 سعر البيع: {CurrencyFormatter.format_lyd(item.base_price)}\n"
                f"✅ الربح: {CurrencyFormatter.format_lyd(profit_fils)}")
            
            self.back_requested.emit()
        
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "❌ خطأ", f"تعذر حفظ الصنف:\n{str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            db.close()

