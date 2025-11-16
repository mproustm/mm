"""
DiBono ERP - Inventory Management Screen
Modern card-based UI with complete inventory tracking, receiving, waste logging, and variance management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
                              QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox,
                              QDialogButtonBox, QFileDialog, QMessageBox, QFrame, QGridLayout,
                              QTabWidget, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from datetime import datetime
from models.database import (get_session, InventoryItem, InventoryCategory, Supplier, PurchaseOrder,
                             PurchaseOrderItem, WasteLog, PhysicalCount, User)
from utils.helpers import CurrencyFormatter, AuthManager
from sqlalchemy import func


class InventoryCardWidget(QFrame):
    """Individual inventory item card with progress bar"""
    
    def __init__(self, item: InventoryItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.parent_widget = parent
        self.init_ui()
        
    def init_ui(self):
        """Initialize card UI"""
        self.setObjectName("inventoryCard")
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Header: Name and Stock
        header = QHBoxLayout()
        
        name_label = QLabel(self.item.name_ar)
        name_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #4ECDC4;")
        name_label.setWordWrap(True)
        header.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        header.addStretch()
        
        # Calculate percentage
        if self.item.max_threshold > 0:
            percentage = (self.item.on_hand / self.item.max_threshold) * 100
        else:
            percentage = (self.item.on_hand / (self.item.min_threshold * 5)) * 100 if self.item.min_threshold > 0 else 0
        
        is_low = self.item.on_hand <= self.item.min_threshold
        
        stock_label = QLabel(f"{self.item.on_hand:.1f} {self.item.unit}")
        stock_label.setStyleSheet(f"""
            font-size: 11pt;
            font-weight: bold;
            color: {'#FF6B6B' if is_low else '#51CF66'};
        """)
        header.addWidget(stock_label, alignment=Qt.AlignmentFlag.AlignLeft)
        
        layout.addLayout(header)
        
        # Progress Bar Container
        progress_container = QFrame()
        progress_container.setFixedHeight(8)
        progress_container.setStyleSheet("""
            QFrame {
                background-color: #0E1A2F;
                border-radius: 4px;
            }
        """)
        
        # Progress Bar
        self.progress_bar = QFrame(progress_container)
        progress_width = min(int((progress_container.width() * percentage) / 100), progress_container.width())
        self.progress_bar.setGeometry(0, 0, 0, 8)
        self.progress_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {'#FF6B6B' if is_low else '#51CF66'};
                border-radius: 4px;
            }}
        """)
        
        layout.addWidget(progress_container)
        
        # Low Stock Warning
        if is_low:
            warning = QHBoxLayout()
            warning_icon = QLabel("⚠️")
            warning_icon.setStyleSheet("font-size: 10pt;")
            warning.addWidget(warning_icon, alignment=Qt.AlignmentFlag.AlignRight)
            
            warning_text = QLabel(f"مخزون منخفض! الحد الأدنى: {self.item.min_threshold:.1f} {self.item.unit}")
            warning_text.setStyleSheet("font-size: 9pt; color: #FF6B6B;")
            warning.addWidget(warning_text, alignment=Qt.AlignmentFlag.AlignRight)
            warning.addStretch()
            
            layout.addLayout(warning)
        
        # Details: SKU, Cost, Value
        details = QHBoxLayout()
        
        sku_label = QLabel(f"SKU: {self.item.sku}")
        sku_label.setStyleSheet("font-size: 9pt; color: #ADB5BD;")
        details.addWidget(sku_label)
        
        details.addStretch()
        
        cost = CurrencyFormatter.fils_to_lyd(self.item.cost_per_unit)
        value = cost * self.item.on_hand
        
        value_label = QLabel(f"القيمة: {value:.2f} د.ل")
        value_label.setStyleSheet("font-size: 9pt; color: #51CF66; font-weight: bold;")
        details.addWidget(value_label)
        
        layout.addLayout(details)
        
        # Apply card styling with Ocean theme
        self.setStyleSheet("""
            QFrame#inventoryCard {
                background-color: #1B263B;
                border: 2px solid #415A77;
                border-radius: 12px;
            }
            QFrame#inventoryCard:hover {
                border: 2px solid #1282A2;
                background-color: #0F4C75;
            }
        """)
        
    def showEvent(self, event):
        """Animate progress bar when shown"""
        super().showEvent(event)
        if hasattr(self, 'progress_bar'):
            try:
                # Calculate target width based on percentage
                percentage = 0
                if self.item.max_threshold > 0:
                    percentage = (self.item.on_hand / self.item.max_threshold) * 100
                else:
                    percentage = (self.item.on_hand / (self.item.min_threshold * 5)) * 100 if self.item.min_threshold > 0 else 0
                
                # Get container width
                container = self.progress_bar.parent()
                if container:
                    target_width = int((container.width() * min(percentage, 100)) / 100)
                    
                    # Animate
                    animation = QPropertyAnimation(self.progress_bar, b"geometry")
                    animation.setDuration(500)
                    animation.setStartValue(self.progress_bar.geometry())
                    end_geom = self.progress_bar.geometry()
                    end_geom.setWidth(target_width)
                    animation.setEndValue(end_geom)
                    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                    animation.start()
                    self._animation = animation  # Keep reference
            except:
                pass


class CategoryHeaderWidget(QFrame):
    """Category header with icon and count"""
    
    def __init__(self, category: InventoryCategory, item_count: int, parent=None):
        super().__init__(parent)
        self.category = category
        self.item_count = item_count
        self.init_ui()
        
    def init_ui(self):
        """Initialize header UI"""
        self.setFixedHeight(60)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0E1A2F;
                border: 1px solid #415A77;
                border-left: 4px solid {self.category.color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        self.setLayout(layout)
        
        # Icon
        icon_label = QLabel(self.category.icon or "📦")
        icon_label.setStyleSheet("font-size: 24pt;")
        layout.addWidget(icon_label)
        
        # Category name
        name_label = QLabel(self.category.name_ar)
        name_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #4ECDC4;
        """)
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Item count
        count_label = QLabel(f"{self.item_count} صنف")
        count_label.setStyleSheet("""
            font-size: 11pt;
            color: #E8F1F2;
            background-color: #1282A2;
            padding: 6px 12px;
            border-radius: 12px;
        """)
        layout.addWidget(count_label)
        
    def _lighten_color(self, hex_color: str) -> str:
        """Lighten a hex color for gradient"""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = min(255, int(r + (255 - r) * 0.3))
            g = min(255, int(g + (255 - g) * 0.3))
            b = min(255, int(b + (255 - b) * 0.3))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#0099BB"


class InventoryManagement(QWidget):
    """Modern card-based inventory management interface"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_inventory()
        
    def init_ui(self):
        """Initialize modern inventory UI"""
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main content widget that will be scrolled
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll_area)
        
        # Apply Ocean theme background
        self.setStyleSheet("""
            QWidget {
                background-color: #0A1128;
                color: #E8F1F2;
            }
            QPushButton {
                background-color: #1282A2;
                color: #E8F1F2;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0E6687;
            }
            QPushButton#successBtn {
                background-color: #51CF66;
            }
            QPushButton#successBtn:hover {
                background-color: #40B356;
            }
        """)
        
        # Header Card
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_card.setStyleSheet("""
            QFrame#headerCard {
                background-color: #1B263B;
                border: 1px solid #415A77;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        header_layout = QVBoxLayout()
        header_card.setLayout(header_layout)
        
        # Title row
        title_row = QHBoxLayout()
        
        title_icon = QLabel("🍴")
        title_icon.setStyleSheet("font-size: 32pt;")
        title_row.addWidget(title_icon)
        
        title_label = QLabel("نظام إدارة المخزون الديناميكي")
        title_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #4ECDC4;
        """)
        title_row.addWidget(title_label)
        
        title_row.addStretch()
        
        # Action buttons
        add_btn = QPushButton("📥 إضافة مخزون")
        add_btn.setObjectName("successBtn")
        add_btn.clicked.connect(self.show_add_stock_dialog)
        title_row.addWidget(add_btn)
        
        waste_btn = QPushButton("🗑️ تسجيل هدر")
        waste_btn.clicked.connect(self.show_waste_dialog)
        title_row.addWidget(waste_btn)
        
        count_btn = QPushButton("📊 جرد فعلي")
        count_btn.clicked.connect(self.show_physical_count_dialog)
        title_row.addWidget(count_btn)
        
        view_waste_btn = QPushButton("📋 عرض الهدر")
        view_waste_btn.clicked.connect(self.show_waste_log_dialog)
        title_row.addWidget(view_waste_btn)
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.load_inventory)
        title_row.addWidget(refresh_btn)
        
        header_layout.addLayout(title_row)
        
        # Subtitle
        subtitle = QLabel("تتبع المخزون بدقة < 0.1% باستخدام نظام الوصفات الديناميكي")
        subtitle.setStyleSheet("font-size: 11pt; color: #7f8c8d; margin-top: 8px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(subtitle)
        
        content_layout.addWidget(header_card)
        
        # Filter and Category Management row
        filter_row = QHBoxLayout()
        
        filter_label = QLabel("تصفية حسب التصنيف:")
        filter_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #E8F1F2;")
        filter_row.addWidget(filter_label)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("جميع التصنيفات", None)
        self.category_filter.currentIndexChanged.connect(self.filter_by_category)
        self.category_filter.setStyleSheet("""
            QComboBox {
                background-color: #1B263B;
                color: #E8F1F2;
                border: 1px solid #415A77;
                padding: 8px;
                border-radius: 6px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1B263B;
                color: #E8F1F2;
                selection-background-color: #1282A2;
            }
        """)
        filter_row.addWidget(self.category_filter)
        
        # Add Category button
        add_category_btn = QPushButton("➕ إضافة تصنيف")
        add_category_btn.clicked.connect(self.show_add_category_dialog)
        filter_row.addWidget(add_category_btn)
        
        filter_row.addStretch()
        
        # Stats
        self.stats_label = QLabel("إجمالي الأصناف: 0 | مخزون منخفض: 0")
        self.stats_label.setStyleSheet("font-size: 11pt; color: #ADB5BD;")
        filter_row.addWidget(self.stats_label)
        
        content_layout.addLayout(filter_row)
        
        # This is where the cards will be added, inside the scrollable area
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(24)
        content_layout.addLayout(self.scroll_layout)
        
        content_layout.addStretch()

    def load_inventory(self):
        """Load inventory data grouped by category"""
        db = get_session()
        try:
            # Load categories for filter
            categories = db.query(InventoryCategory).order_by(InventoryCategory.sort_order).all()
            
            self.category_filter.clear()
            self.category_filter.addItem("جميع التصنيفات", None)
            for cat in categories:
                self.category_filter.addItem(f"{cat.icon} {cat.name_ar}", cat.id)
            
            # Display inventory by category
            self.display_inventory(db)
            
        finally:
            db.close()
    
    def display_inventory(self, db):
        """Display inventory cards grouped by category"""
        # Clear existing widgets
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get filter
        selected_cat_id = self.category_filter.currentData()
        
        # Get categories
        if selected_cat_id:
            categories = db.query(InventoryCategory).filter(
                InventoryCategory.id == selected_cat_id
            ).all()
        else:
            categories = db.query(InventoryCategory).order_by(InventoryCategory.sort_order).all()
        
        total_items = 0
        low_stock_count = 0
        displayed_item_ids = set()  # Track which items we've displayed
        
        for category in categories:
            # Get items in this category
            items = db.query(InventoryItem).filter(
                InventoryItem.category_id == category.id
            ).order_by(InventoryItem.name_ar).all()
            
            for item in items:
                displayed_item_ids.add(item.id)
            
            if not items:
                continue
            
            # Category header
            header = CategoryHeaderWidget(category, len(items))
            self.scroll_layout.addWidget(header)
            
            # Items grid
            grid = QGridLayout()
            grid.setSpacing(16)
            grid.setContentsMargins(0, 0, 0, 0)
            
            row = 0
            col = 0
            max_cols = 3  # 3 cards per row
            
            for item in items:
                card = InventoryCardWidget(item, self)
                grid.addWidget(card, row, col)
                
                total_items += 1
                if item.on_hand <= item.min_threshold:
                    low_stock_count += 1
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            grid_widget = QWidget()
            grid_widget.setLayout(grid)
            self.scroll_layout.addWidget(grid_widget)
        
        # Display uncategorized items (fallback for items without category_id)
        uncategorized_items = db.query(InventoryItem).filter(
            InventoryItem.category_id.is_(None)
        ).order_by(InventoryItem.name_ar).all()
        
        if uncategorized_items:
            # Create a temporary "Uncategorized" header
            temp_category = InventoryCategory(
                id=0,
                name_ar="غير مصنف",
                name_en="Uncategorized",
                icon="❓",
                color="#FF6B6B",
                sort_order=999
            )
            
            header = CategoryHeaderWidget(temp_category, len(uncategorized_items))
            self.scroll_layout.addWidget(header)
            
            # Items grid
            grid = QGridLayout()
            grid.setSpacing(16)
            grid.setContentsMargins(0, 0, 0, 0)
            
            row = 0
            col = 0
            max_cols = 3
            
            for item in uncategorized_items:
                if item.id not in displayed_item_ids:
                    card = InventoryCardWidget(item, self)
                    grid.addWidget(card, row, col)
                    
                    total_items += 1
                    if item.on_hand <= item.min_threshold:
                        low_stock_count += 1
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            
            grid_widget = QWidget()
            grid_widget.setLayout(grid)
            self.scroll_layout.addWidget(grid_widget)
        
        # Update stats
        self.stats_label.setText(f"إجمالي الأصناف: {total_items} | ⚠️ مخزون منخفض: {low_stock_count}")
        
        self.scroll_layout.addStretch()
    
    def filter_by_category(self):
        """Filter inventory by selected category"""
        db = get_session()
        try:
            self.display_inventory(db)
        finally:
            db.close()
    
    def show_add_category_dialog(self):
        """Show add category dialog"""
        dialog = AddCategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()
            
    def show_add_stock_dialog(self):
        """Show add stock dialog"""
        dialog = AddStockDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()
    
    def show_receive_stock_dialog(self):
        """Show receive stock dialog - DEPRECATED, use show_add_stock_dialog"""
        self.show_add_stock_dialog()
    
    def show_waste_log_dialog(self):
        """Show waste log view dialog"""
        dialog = WasteLogViewDialog(self)
        dialog.exec()
            
    def show_waste_dialog(self):
        """Show waste logging dialog"""
        dialog = WasteLogDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()
            
    def show_physical_count_dialog(self):
        """Show physical count dialog"""
        dialog = PhysicalCountDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()


class ReceiveStockDialog(QDialog):
    """Dialog for receiving stock/deliveries"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("استلام المخزون")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Item selection
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("الصنف:"), 0, 0)
        self.item_combo = QComboBox()
        self.load_items()
        form_layout.addWidget(self.item_combo, 0, 1)
        
        form_layout.addWidget(QLabel("الكمية المستلمة:"), 1, 0)
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(10000.0)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setValue(1.0)
        form_layout.addWidget(self.quantity_input, 1, 1)
        
        form_layout.addWidget(QLabel("المورد:"), 2, 0)
        self.supplier_combo = QComboBox()
        self.load_suppliers()
        form_layout.addWidget(self.supplier_combo, 2, 1)
        
        form_layout.addWidget(QLabel("التكلفة لكل وحدة (د.ل):"), 3, 0)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMinimum(0.01)
        self.cost_input.setMaximum(1000000.0)
        self.cost_input.setDecimals(2)
        self.cost_input.setValue(1.0)
        form_layout.addWidget(self.cost_input, 3, 1)
        
        form_layout.addWidget(QLabel("ملاحظات:"), 4, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form_layout.addWidget(self.notes_input, 4, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.receive_stock)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_items(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_en).all()
            for item in items:
                self.item_combo.addItem(f"{item.sku} - {item.name_ar}", item.id)
        finally:
            db.close()
            
    def load_suppliers(self):
        """Load suppliers"""
        db = get_session()
        try:
            suppliers = db.query(Supplier).filter_by(active=True).order_by(Supplier.name).all()
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier.name, supplier.id)
        finally:
            db.close()
            
    def receive_stock(self):
        """Process stock receipt"""
        item_id = self.item_combo.currentData()
        quantity = self.quantity_input.value()
        cost_lyd = self.cost_input.value()
        cost_fils = CurrencyFormatter.lyd_to_fils(cost_lyd)
        
        db = get_session()
        try:
            item = db.query(InventoryItem).get(item_id)
            if item:
                # Update quantity
                item.on_hand += quantity
                
                # Update cost (weighted average)
                total_cost = (item.on_hand - quantity) * item.cost_per_unit + quantity * cost_fils
                item.cost_per_unit = int(total_cost / item.on_hand) if item.on_hand > 0 else cost_fils
                
                db.commit()
                
                QMessageBox.information(self, "تم بنجاح", 
                    f"تم استلام {quantity:.2f} {item.unit} من {item.name_ar}\n"
                    f"المخزون الجديد: {item.on_hand:.2f} {item.unit}")
                self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر تسجيل الاستلام: {e}")
        finally:
            db.close()


class WasteLogDialog(QDialog):
    """Dialog for logging waste/spoilage"""
    
    def __init__(self, parent=None, prefill_item_id=None, prefill_quantity=None):
        super().__init__(parent)
        self.setWindowTitle("تسجيل الهدر")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("الصنف:"), 0, 0)
        self.item_combo = QComboBox()
        self.load_items()
        
        # Pre-fill item if provided
        if prefill_item_id:
            for i in range(self.item_combo.count()):
                if self.item_combo.itemData(i) == prefill_item_id:
                    self.item_combo.setCurrentIndex(i)
                    self.item_combo.setEnabled(False)  # Lock selection
                    break
        
        form_layout.addWidget(self.item_combo, 0, 1)
        
        form_layout.addWidget(QLabel("الكمية المهدرة:"), 1, 0)
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(10000.0)
        self.quantity_input.setDecimals(2)
        
        # Pre-fill quantity if provided
        if prefill_quantity:
            self.quantity_input.setValue(prefill_quantity)
        else:
            self.quantity_input.setValue(1.0)
        
        form_layout.addWidget(self.quantity_input, 1, 1)
        
        form_layout.addWidget(QLabel("السبب:"), 2, 0)
        self.reason_combo = QComboBox()
        self.reason_combo.addItems(["تلف", "تكسر", "زيادة الحصة", "منتهي الصلاحية", "ملوث", "أخرى"])
        form_layout.addWidget(self.reason_combo, 2, 1)
        
        form_layout.addWidget(QLabel("ملاحظات:"), 3, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form_layout.addWidget(self.notes_input, 3, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.log_waste)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_items(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_en).all()
            for item in items:
                self.item_combo.addItem(f"{item.sku} - {item.name_ar}", item.id)
        finally:
            db.close()
            
    def log_waste(self):
        """Log waste entry"""
        item_id = self.item_combo.currentData()
        quantity = self.quantity_input.value()
        reason = self.reason_combo.currentText()
        notes = self.notes_input.toPlainText()
        
        db = get_session()
        try:
            item = db.query(InventoryItem).get(item_id)
            if item:
                if item.on_hand < quantity:
                    QMessageBox.warning(self, "مخزون غير كاف",
                        f"لا يمكن تسجيل {quantity:.2f} {item.unit} كهدر.\n"
                        f"المخزون الحالي: {item.on_hand:.2f} {item.unit}")
                    return
                
                # Deduct from inventory
                item.on_hand -= quantity
                
                # Create waste log
                waste_log = WasteLog(
                    inventory_item_id=item_id,
                    quantity=quantity,
                    reason=reason,
                    notes=notes,
                    logged_by=AuthManager.current_user.id,
                    approved=True
                )
                db.add(waste_log)
                
                db.commit()
                
                QMessageBox.information(self, "تم بنجاح",
                    f"تم تسجيل {quantity:.2f} {item.unit} كهدر للصنف {item.name_ar}\n"
                    f"السبب: {reason}\n"
                    f"المخزون الجديد: {item.on_hand:.2f} {item.unit}")
                self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر تسجيل الهدر: {e}")
        finally:
            db.close()


class AddStockDialog(QDialog):
    """Simplified dialog for adding stock to inventory"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مخزون")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("الاسم (بالإنجليزية):"), 0, 0)
        self.name_en_input = QLineEdit()
        form_layout.addWidget(self.name_en_input, 0, 1)
        
        form_layout.addWidget(QLabel("الاسم (بالعربية):"), 1, 0)
        self.name_ar_input = QLineEdit()
        form_layout.addWidget(self.name_ar_input, 1, 1)
        
        form_layout.addWidget(QLabel("الوحدة:"), 2, 0)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["كجم", "قطعة", "لتر", "غرام", "حزمة"])
        form_layout.addWidget(self.unit_combo, 2, 1)
        
        form_layout.addWidget(QLabel("التصنيف:"), 3, 0)
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addWidget(self.category_combo, 3, 1)
        
        form_layout.addWidget(QLabel("الكمية المستلمة:"), 4, 0)
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(10000.0)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setValue(1.0)
        form_layout.addWidget(self.quantity_input, 4, 1)
        
        form_layout.addWidget(QLabel("التكلفة لكل وحدة (د.ل):"), 5, 0)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMinimum(0.01)
        self.cost_input.setMaximum(1000000.0)
        self.cost_input.setDecimals(2)
        self.cost_input.setValue(1.0)
        form_layout.addWidget(self.cost_input, 5, 1)
        
        form_layout.addWidget(QLabel("الحد الأدنى:"), 6, 0)
        self.min_input = QDoubleSpinBox()
        self.min_input.setMinimum(0.0)
        self.min_input.setMaximum(10000.0)
        self.min_input.setDecimals(2)
        self.min_input.setValue(5.0)
        form_layout.addWidget(self.min_input, 6, 1)
        
        form_layout.addWidget(QLabel("الحد الأقصى:"), 7, 0)
        self.max_input = QDoubleSpinBox()
        self.max_input.setMinimum(0.0)
        self.max_input.setMaximum(10000.0)
        self.max_input.setDecimals(2)
        self.max_input.setValue(50.0)
        form_layout.addWidget(self.max_input, 7, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.add_stock)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("إضافة")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_categories(self):
        """Load inventory categories"""
        db = get_session()
        try:
            categories = db.query(InventoryCategory).order_by(InventoryCategory.sort_order).all()
            for cat in categories:
                self.category_combo.addItem(f"{cat.icon} {cat.name_ar}", cat.id)
            
            # Default to "Other" if exists
            for i in range(self.category_combo.count()):
                if "أخرى" in self.category_combo.itemText(i):
                    self.category_combo.setCurrentIndex(i)
                    break
        finally:
            db.close()
        
    def add_stock(self):
        """Add new inventory item"""
        name_en = self.name_en_input.text().strip()
        name_ar = self.name_ar_input.text().strip()
        
        if not name_en or not name_ar:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال الاسم باللغتين")
            return
        
        db = get_session()
        try:
            # Get selected category
            category_id = self.category_combo.currentData()
            category = db.query(InventoryCategory).get(category_id)
            
            if not category:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار تصنيف")
                return
            
            # Auto-generate SKU
            # Format: CAT-YYYYMMDD-XXX
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')
            category_prefix = category.name_en[:3].upper()
            
            # Find highest SKU for this category today
            last_item = db.query(InventoryItem).filter(
                InventoryItem.sku.like(f'{category_prefix}-{today}-%')
            ).order_by(InventoryItem.sku.desc()).first()
            
            if last_item:
                last_num = int(last_item.sku.split('-')[2])
                next_num = last_num + 1
            else:
                next_num = 1
            
            sku = f"{category_prefix}-{today}-{next_num:03d}"
            
            # Check if SKU already exists (shouldn't happen, but just in case)
            existing = db.query(InventoryItem).filter_by(sku=sku).first()
            if existing:
                QMessageBox.warning(self, "خطأ", "SKU موجود مسبقًا")
                return
            
            # Create new inventory item
            item = InventoryItem(
                sku=sku,
                name_en=name_en,
                name_ar=name_ar,
                unit=self.unit_combo.currentText(),
                category=category.name_en,  # Keep legacy field for compatibility
                category_id=category_id,  # Use new foreign key
                on_hand=self.quantity_input.value(),
                min_threshold=self.min_input.value(),
                max_threshold=self.max_input.value(),
                cost_per_unit=CurrencyFormatter.lyd_to_fils(self.cost_input.value())
            )
            
            db.add(item)
            db.commit()
            
            QMessageBox.information(
                self, 
                "تم بنجاح",
                f"تم إضافة الصنف '{name_ar}'\nSKU: {sku}\nالكمية: {self.quantity_input.value()} {self.unit_combo.currentText()}"
            )
            self.accept()
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر إضافة المخزون: {e}")
        finally:
            db.close()


class WasteLogViewDialog(QDialog):
    """Dialog to view waste log history"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("سجل الهدر")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("فترة:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["اليوم", "هذا الأسبوع", "هذا الشهر", "الكل"])
        self.period_combo.currentIndexChanged.connect(self.load_waste_logs)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.load_waste_logs)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Waste table
        self.waste_table = QTableWidget()
        self.waste_table.setColumnCount(6)
        self.waste_table.setHorizontalHeaderLabels([
            "التاريخ", "الصنف", "الكمية", "السبب", "المسجل بواسطة", "ملاحظات"
        ])
        self.waste_table.horizontalHeader().setStretchLastSection(True)
        self.waste_table.setColumnWidth(0, 150)
        self.waste_table.setColumnWidth(1, 150)
        self.waste_table.setColumnWidth(2, 100)
        self.waste_table.setColumnWidth(3, 120)
        self.waste_table.setColumnWidth(4, 120)
        layout.addWidget(self.waste_table)
        
        # Close button
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        self.load_waste_logs()
        
    def load_waste_logs(self):
        """Load waste logs based on selected period"""
        from models.database import WasteLog, User
        from utils.helpers import DateRangeCalculator
        
        db = get_session()
        try:
            period = self.period_combo.currentText()
            
            query = db.query(WasteLog).order_by(WasteLog.logged_at.desc())
            
            if period == "اليوم":
                start, _ = DateRangeCalculator.get_day_range()
                query = query.filter(WasteLog.logged_at >= start)
            elif period == "هذا الأسبوع":
                start = DateRangeCalculator.get_week_start()
                query = query.filter(WasteLog.logged_at >= start)
            elif period == "هذا الشهر":
                start = DateRangeCalculator.get_month_start()
                query = query.filter(WasteLog.logged_at >= start)
            
            logs = query.all()
            
            self.waste_table.setRowCount(len(logs))
            
            for idx, log in enumerate(logs):
                # Date
                date_str = log.logged_at.strftime("%Y-%m-%d %H:%M")
                self.waste_table.setItem(idx, 0, QTableWidgetItem(date_str))
                
                # Item
                self.waste_table.setItem(idx, 1, QTableWidgetItem(log.inventory_item.name_ar))
                
                # Quantity
                qty_str = f"{log.quantity:.2f} {log.inventory_item.unit}"
                self.waste_table.setItem(idx, 2, QTableWidgetItem(qty_str))
                
                # Reason
                self.waste_table.setItem(idx, 3, QTableWidgetItem(log.reason))
                
                # Logged by
                user = db.query(User).get(log.logged_by)
                logged_by = user.full_name if user else "غير معروف"
                self.waste_table.setItem(idx, 4, QTableWidgetItem(logged_by))
                
                # Notes
                self.waste_table.setItem(idx, 5, QTableWidgetItem(log.notes or "-"))
                
        finally:
            db.close()


class PhysicalCountDialog(QDialog):
    """Dialog for physical inventory count and variance"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الجرد الفعلي")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("الصنف:"), 0, 0)
        self.item_combo = QComboBox()
        form_layout.addWidget(self.item_combo, 0, 1)
        
        form_layout.addWidget(QLabel("الكمية النظرية:"), 1, 0)
        self.theoretical_label = QLabel("0.00")
        self.theoretical_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #ADB5BD;")
        form_layout.addWidget(self.theoretical_label, 1, 1)
        
        form_layout.addWidget(QLabel("الكمية الفعلية:"), 2, 0)
        self.count_input = QDoubleSpinBox()
        self.count_input.setMinimum(0.0)
        self.count_input.setMaximum(10000.0)
        self.count_input.setDecimals(2)
        self.count_input.setValue(0.0)
        self.count_input.valueChanged.connect(self.update_variance)
        form_layout.addWidget(self.count_input, 2, 1)
        
        form_layout.addWidget(QLabel("الانحراف:"), 3, 0)
        self.variance_label = QLabel("0.00")
        self.variance_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        form_layout.addWidget(self.variance_label, 3, 1)
        
        form_layout.addWidget(QLabel("ملاحظات:"), 4, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form_layout.addWidget(self.notes_input, 4, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_count)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Load items and connect signals AFTER all UI elements are created
        self.item_combo.currentIndexChanged.connect(self.update_theoretical)
        self.load_items()
        self.update_theoretical()
        
    def load_items(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_en).all()
            for item in items:
                self.item_combo.addItem(f"{item.sku} - {item.name_ar}", item.id)
        finally:
            db.close()
            
    def update_theoretical(self):
        """Update theoretical quantity display"""
        item_id = self.item_combo.currentData()
        if item_id:
            db = get_session()
            try:
                item = db.query(InventoryItem).get(item_id)
                if item:
                    self.theoretical_label.setText(f"{item.on_hand:.2f} {item.unit}")
                    self.count_input.setValue(item.on_hand)
            finally:
                db.close()
        self.update_variance()
        
    def update_variance(self):
        """Calculate and display variance"""
        item_id = self.item_combo.currentData()
        if item_id:
            db = get_session()
            try:
                item = db.query(InventoryItem).get(item_id)
                if item:
                    variance = self.count_input.value() - item.on_hand
                    color = "#51CF66" if variance >= 0 else "#FF6B6B"
                    sign = "+" if variance >= 0 else ""
                    self.variance_label.setText(f"{sign}{variance:.2f} {item.unit}")
                    self.variance_label.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {color};")
            finally:
                db.close()
                
    def save_count(self):
        """Save physical count and adjust inventory"""
        item_id = self.item_combo.currentData()
        actual_count = self.count_input.value()
        notes = self.notes_input.toPlainText()
        
        db = get_session()
        try:
            item = db.query(InventoryItem).get(item_id)
            if item:
                theoretical = item.on_hand
                variance = actual_count - theoretical
                variance_value = int(variance * item.cost_per_unit)
                
                # Create count record
                count = PhysicalCount(
                    inventory_item_id=item_id,
                    counted_quantity=actual_count,
                    theoretical_quantity=theoretical,
                    variance=variance,
                    variance_value=variance_value,
                    counted_by=AuthManager.current_user.id,
                    notes=notes
                )
                db.add(count)
                
                # Adjust inventory to match physical count
                item.on_hand = actual_count
                
                db.commit()
                
                # If negative variance, automatically open waste log dialog
                if variance < 0:
                    waste_quantity = abs(variance)
                    
                    # Show info message about the shortage
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("نقص في المخزون")
                    msg.setText(f"تم اكتشاف نقص في الصنف {item.name_ar}")
                    msg.setInformativeText(
                        f"النقص: {waste_quantity:.2f} {item.unit}\n"
                        f"يرجى تسجيل سبب الهدر..."
                    )
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
                    msg.button(QMessageBox.StandardButton.Ok).setText("متابعة")
                    msg.exec()
                    
                    # Open waste log dialog with pre-filled data
                    waste_dialog = WasteLogDialog(
                        parent=self,
                        prefill_item_id=item_id,
                        prefill_quantity=waste_quantity
                    )
                    
                    if waste_dialog.exec() == QDialog.DialogCode.Accepted:
                        QMessageBox.information(self, "تم بنجاح",
                            f"تم تسجيل الجرد وتسجيل الهدر للصنف {item.name_ar}\n"
                            f"الكمية النظرية: {theoretical:.2f} {item.unit}\n"
                            f"الكمية الفعلية: {actual_count:.2f} {item.unit}\n"
                            f"الانحراف: {variance:+.2f} {item.unit} ({CurrencyFormatter.format_lyd(variance_value)})")
                    else:
                        QMessageBox.information(self, "تم بنجاح",
                            f"تم تسجيل الجرد للصنف {item.name_ar}\n"
                            f"الكمية النظرية: {theoretical:.2f} {item.unit}\n"
                            f"الكمية الفعلية: {actual_count:.2f} {item.unit}\n"
                            f"الانحراف: {variance:+.2f} {item.unit} ({CurrencyFormatter.format_lyd(variance_value)})\n\n"
                            f"⚠ لم يتم تسجيل سبب الهدر")
                else:
                    # Positive variance - just show success
                    QMessageBox.information(self, "تم بنجاح",
                        f"تم تسجيل الجرد للصنف {item.name_ar}\n"
                        f"الكمية النظرية: {theoretical:.2f} {item.unit}\n"
                        f"الكمية الفعلية: {actual_count:.2f} {item.unit}\n"
                        f"الانحراف: {variance:+.2f} {item.unit} ({CurrencyFormatter.format_lyd(variance_value)})")
                
                self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حفظ الجرد: {e}")
        finally:
            db.close()


class AddCategoryDialog(QDialog):
    """Dialog for adding new inventory category"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة تصنيف جديد")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("الاسم بالعربية:"), 0, 0)
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("مثال: فواكه طازجة")
        form_layout.addWidget(self.name_ar_input, 0, 1)
        
        form_layout.addWidget(QLabel("الاسم بالإنجليزية:"), 1, 0)
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Example: Fresh Fruits")
        form_layout.addWidget(self.name_en_input, 1, 1)
        
        form_layout.addWidget(QLabel("الأيقونة (إيموجي):"), 2, 0)
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("🍎")
        self.icon_input.setMaxLength(2)
        form_layout.addWidget(self.icon_input, 2, 1)
        
        # Common emoji suggestions
        emoji_layout = QHBoxLayout()
        emoji_label = QLabel("اختيارات سريعة:")
        emoji_layout.addWidget(emoji_label)
        
        emojis = ["🐟", "🍗", "🥗", "🍎", "🍝", "🧂", "🥤", "🥛", "🫒", "🌿", "🍰", "🍕", "🍔", "🥖", "🧀"]
        for emoji in emojis:
            btn = QPushButton(emoji)
            btn.setFixedSize(35, 35)
            btn.clicked.connect(lambda checked, e=emoji: self.icon_input.setText(e))
            emoji_layout.addWidget(btn)
        emoji_layout.addStretch()
        form_layout.addLayout(emoji_layout, 3, 0, 1, 2)
        
        form_layout.addWidget(QLabel("اللون (Hex):"), 4, 0)
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#FF6B35")
        self.color_input.setMaxLength(7)
        color_layout.addWidget(self.color_input)
        
        # Color presets
        colors = ["#0088AA", "#D32F2F", "#388E3C", "#F57C00", "#FBC02D", "#E64A19", 
                  "#1976D2", "#7B1FA2", "#689F38", "#558B2F", "#607D8B"]
        for color in colors:
            color_btn = QPushButton()
            color_btn.setFixedSize(30, 30)
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, c=color: self.color_input.setText(c))
            color_layout.addWidget(color_btn)
        
        form_layout.addLayout(color_layout, 4, 1)
        
        form_layout.addWidget(QLabel("ترتيب العرض:"), 5, 0)
        self.sort_order_input = QSpinBox()
        self.sort_order_input.setMinimum(1)
        self.sort_order_input.setMaximum(999)
        self.sort_order_input.setValue(50)
        form_layout.addWidget(self.sort_order_input, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.add_category)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("إضافة")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def add_category(self):
        """Add new inventory category"""
        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        icon = self.icon_input.text().strip()
        color = self.color_input.text().strip()
        
        if not name_ar or not name_en:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال الاسم بالعربية والإنجليزية")
            return
        
        if not icon:
            icon = "📦"
        
        if not color or not color.startswith('#'):
            color = "#607D8B"
        
        db = get_session()
        try:
            category = InventoryCategory(
                name_en=name_en,
                name_ar=name_ar,
                icon=icon,
                color=color,
                sort_order=self.sort_order_input.value()
            )
            
            db.add(category)
            db.commit()
            
            QMessageBox.information(self, "تم بنجاح", f"تم إضافة التصنيف {name_ar} بنجاح")
            self.accept()
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر إضافة التصنيف: {e}")
        finally:
            db.close()
