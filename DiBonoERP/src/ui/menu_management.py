"""
DiBono ERP - Menu Management Screen
Complete menu and category management with ingredient mapping
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QTableWidget, QTableWidgetItem, QDialog, QLineEdit,
                              QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox, QCheckBox,
                              QDialogButtonBox, QMessageBox, QFrame, QGridLayout, QListWidget,
                              QListWidgetItem, QTabWidget, QGroupBox, QColorDialog, QStackedWidget,
                              QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.database import (get_session, MenuCategory, MenuItem, MenuItemIngredient, InventoryItem)
from utils.helpers import CurrencyFormatter
from ui.menu_item_screen import MenuItemManagementScreen


class MenuManagement(QWidget):
    """Complete menu management interface"""
    
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.init_ui()
        self.load_categories()
        
    def init_ui(self):
        """Initialize menu UI"""
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Main layout with stack
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main view (list)
        list_widget = QWidget()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(list_widget)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(30, 30, 30, 30)
        list_layout.setSpacing(20)
        
        # Title and actions
        header = QHBoxLayout()
        
        title = QLabel("🍽️ إدارة قائمة الطعام")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(title)
        
        header.addStretch()
        
        add_category_btn = QPushButton("➕ إضافة تصنيف")
        add_category_btn.setObjectName("success")
        add_category_btn.clicked.connect(self.show_add_category_dialog)
        header.addWidget(add_category_btn)
        
        add_item_btn = QPushButton("➕ إضافة صنف")
        add_item_btn.setObjectName("success")
        add_item_btn.clicked.connect(self.show_add_item_screen)
        header.addWidget(add_item_btn)
        
        list_layout.addLayout(header)
        
        # Tab widget for categories and items
        self.tabs = QTabWidget()
        
        # Categories tab
        categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_widget.setLayout(categories_layout)
        
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(7)
        self.categories_table.setHorizontalHeaderLabels([
            "الاسم (إنجليزي)", "الاسم (عربي)", "الأيقونة", "اللون", "ترتيب العرض", "الحالة", "إجراءات"
        ])
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.categories_table.setColumnWidth(0, 150)
        self.categories_table.setColumnWidth(1, 150)
        self.categories_table.setColumnWidth(2, 60)
        self.categories_table.setColumnWidth(3, 80)
        self.categories_table.setColumnWidth(4, 100)
        self.categories_table.setColumnWidth(5, 80)
        categories_layout.addWidget(self.categories_table)
        
        self.tabs.addTab(categories_widget, "📋 التصنيفات")
        
        # Menu Items tab
        items_widget = QWidget()
        items_layout = QVBoxLayout()
        items_widget.setLayout(items_layout)
        
        # Filter by category
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("تصفية حسب التصنيف:"))
        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self.load_menu_items)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addStretch()
        items_layout.addLayout(filter_layout)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels([
            "الاسم (إنجليزي)", "الاسم (عربي)", "التصنيف", "السعر الأساسي", "السعر/كغ", "يباع بالوزن", "الحالة", "إجراءات"
        ])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setColumnWidth(0, 150)
        self.items_table.setColumnWidth(1, 150)
        self.items_table.setColumnWidth(2, 120)
        self.items_table.setColumnWidth(3, 100)
        self.items_table.setColumnWidth(4, 100)
        self.items_table.setColumnWidth(5, 100)
        self.items_table.setColumnWidth(6, 80)
        items_layout.addWidget(self.items_table)
        
        self.tabs.addTab(items_widget, "🍽️ الأصناف")
        
        list_layout.addWidget(self.tabs)
        
        # Add scroll area (containing list_widget) to stack
        self.stack.addWidget(scroll_area)
        main_layout.addWidget(self.stack)
        
    def load_categories(self):
        """Load menu categories"""
        db = get_session()
        try:
            categories = db.query(MenuCategory).order_by(MenuCategory.display_order).all()
            
            self.categories_table.setRowCount(len(categories))
            
            # Also update filter
            self.category_filter.clear()
            self.category_filter.addItem("كل التصنيفات", None)
            
            for idx, category in enumerate(categories):
                # Name EN
                self.categories_table.setItem(idx, 0, QTableWidgetItem(category.name_en))
                
                # Name AR
                self.categories_table.setItem(idx, 1, QTableWidgetItem(category.name_ar))
                
                # Icon
                self.categories_table.setItem(idx, 2, QTableWidgetItem(category.icon))
                
                # Color
                color_item = QTableWidgetItem()
                color_item.setBackground(QColor(category.color))
                color_item.setText(category.color)
                self.categories_table.setItem(idx, 3, color_item)
                
                # Display Order
                self.categories_table.setItem(idx, 4, QTableWidgetItem(str(category.display_order)))
                
                # Active
                active_item = QTableWidgetItem("نشط" if category.active else "متوقف")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.categories_table.setItem(idx, 5, active_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(40)
                edit_btn.clicked.connect(lambda checked, c=category: self.edit_category(c.id))
                actions_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setObjectName("danger")
                delete_btn.setMaximumWidth(40)
                delete_btn.clicked.connect(lambda checked, c=category: self.delete_category(c.id))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.categories_table.setCellWidget(idx, 6, actions_widget)
                
                # Add to filter
                self.category_filter.addItem(f"{category.icon} {category.name_ar}", category.id)
            
            self.load_menu_items()
            
        finally:
            db.close()
            
    def load_menu_items(self):
        """Load menu items"""
        category_id = self.category_filter.currentData()
        
        db = get_session()
        try:
            query = db.query(MenuItem)
            if category_id:
                query = query.filter_by(category_id=category_id)
            
            items = query.order_by(MenuItem.display_order).all()
            
            self.items_table.setRowCount(len(items))
            
            for idx, item in enumerate(items):
                # Name EN
                self.items_table.setItem(idx, 0, QTableWidgetItem(item.name_en))
                
                # Name AR
                self.items_table.setItem(idx, 1, QTableWidgetItem(item.name_ar))
                
                # Category
                self.items_table.setItem(idx, 2, QTableWidgetItem(item.category.name_ar))
                
                # Base Price
                self.items_table.setItem(idx, 3, QTableWidgetItem(
                    CurrencyFormatter.format_lyd(item.base_price) if not item.is_weight_based else "-"
                ))
                
                # Price/kg
                self.items_table.setItem(idx, 4, QTableWidgetItem(
                    CurrencyFormatter.format_lyd(item.price_per_kg) if item.is_weight_based else "-"
                ))
                
                # Weight-Based
                weight_item = QTableWidgetItem("نعم" if item.is_weight_based else "لا")
                weight_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(idx, 5, weight_item)
                
                # Active
                active_item = QTableWidgetItem("نشط" if item.active else "متوقف")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_table.setItem(idx, 6, active_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(40)
                edit_btn.clicked.connect(lambda checked, i=item: self.edit_item(i.id))
                actions_layout.addWidget(edit_btn)
                
                ingredients_btn = QPushButton("🥘")
                ingredients_btn.setMaximumWidth(40)
                ingredients_btn.clicked.connect(lambda checked, i=item: self.manage_ingredients(i.id))
                actions_layout.addWidget(ingredients_btn)
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setObjectName("danger")
                delete_btn.setMaximumWidth(40)
                delete_btn.clicked.connect(lambda checked, i=item: self.delete_item(i.id))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.items_table.setCellWidget(idx, 7, actions_widget)
                
        finally:
            db.close()
            
    def show_add_category_dialog(self):
        """Show add category dialog"""
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()
            
    def edit_category(self, category_id):
        """Edit existing category"""
        dialog = CategoryDialog(self, category_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()
            
    def delete_category(self, category_id):
        """Delete category"""
        reply = QMessageBox.question(self, "تأكيد الحذف",
            "هل تريد حذف هذا التصنيف؟ ستبقى الأصناف بدون تصنيف.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            db = get_session()
            try:
                category = db.query(MenuCategory).get(category_id)
                if category:
                    db.delete(category)
                    db.commit()
                    self.load_categories()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "خطأ", f"تعذر حذف التصنيف: {e}")
            finally:
                db.close()
                
    def show_add_item_screen(self):
        """Show full-screen add menu item interface"""
        screen = MenuItemManagementScreen()
        screen.back_requested.connect(self.return_to_list)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)
    
    def return_to_list(self):
        """Return to list view and reload"""
        # Remove the edit screen
        if self.stack.count() > 1:
            widget = self.stack.widget(1)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        
        # Go back to list
        self.stack.setCurrentIndex(0)
        self.load_menu_items()
            
    def edit_item(self, item_id):
        """Edit existing menu item"""
        screen = MenuItemManagementScreen(item_id=item_id)
        screen.back_requested.connect(self.return_to_list)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)
            
    def delete_item(self, item_id):
        """Delete menu item"""
        reply = QMessageBox.question(self, "تأكيد الحذف",
            "هل تريد حذف هذا الصنف نهائيًا؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            db = get_session()
            try:
                item = db.query(MenuItem).get(item_id)
                if item:
                    db.delete(item)
                    db.commit()
                    self.load_menu_items()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "خطأ", f"تعذر حذف الصنف: {e}")
            finally:
                db.close()
                
    def manage_ingredients(self, item_id):
        """Manage item ingredients"""
        dialog = IngredientsDialog(item_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_menu_items()


class CategoryDialog(QDialog):
    """Dialog for adding/editing menu categories"""
    
    def __init__(self, parent=None, category_id=None):
        super().__init__(parent)
        self.category_id = category_id
        self.setWindowTitle("تعديل التصنيف" if category_id else "إضافة تصنيف")
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
        
        form_layout.addWidget(QLabel("الأيقونة (رمز):"), 2, 0)
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("🍽️")
        form_layout.addWidget(self.icon_input, 2, 1)
        
        form_layout.addWidget(QLabel("اللون:"), 3, 0)
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit()
        self.color_input.setText("#0088AA")
        color_layout.addWidget(self.color_input)
        color_btn = QPushButton("اختيار اللون")
        color_btn.clicked.connect(self.pick_color)
        color_layout.addWidget(color_btn)
        form_layout.addLayout(color_layout, 3, 1)
        
        form_layout.addWidget(QLabel("ترتيب العرض:"), 4, 0)
        self.order_input = QSpinBox()
        self.order_input.setMinimum(0)
        self.order_input.setMaximum(100)
        form_layout.addWidget(self.order_input, 4, 1)
        
        self.active_checkbox = QCheckBox("نشط")
        self.active_checkbox.setChecked(True)
        form_layout.addWidget(self.active_checkbox, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Load existing data if editing
        if category_id:
            self.load_category()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_category)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def pick_color(self):
        """Open color picker"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_input.setText(color.name())
            
    def load_category(self):
        """Load category data for editing"""
        db = get_session()
        try:
            category = db.query(MenuCategory).get(self.category_id)
            if category:
                self.name_en_input.setText(category.name_en)
                self.name_ar_input.setText(category.name_ar)
                self.icon_input.setText(category.icon)
                self.color_input.setText(category.color)
                self.order_input.setValue(category.display_order)
                self.active_checkbox.setChecked(category.active)
        finally:
            db.close()
            
    def save_category(self):
        """Save category"""
        name_en = self.name_en_input.text().strip()
        name_ar = self.name_ar_input.text().strip()
        
        if not name_en or not name_ar:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال الاسم باللغتين")
            return
        
        db = get_session()
        try:
            if self.category_id:
                category = db.query(MenuCategory).get(self.category_id)
            else:
                category = MenuCategory()
                db.add(category)
            
            category.name_en = name_en
            category.name_ar = name_ar
            category.icon = self.icon_input.text() or "🍽️"
            category.color = self.color_input.text()
            category.display_order = self.order_input.value()
            category.active = self.active_checkbox.isChecked()
            
            db.commit()
            
            QMessageBox.information(self, "تم بنجاح",
                f"تم حفظ التصنيف '{name_ar}' بنجاح")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حفظ التصنيف: {e}")
        finally:
            db.close()


class MenuItemDialog(QDialog):
    """Dialog for adding/editing menu items"""
    
    def __init__(self, parent=None, item_id=None):
        super().__init__(parent)
        self.item_id = item_id
        self.setWindowTitle("تعديل صنف" if item_id else "إضافة صنف")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("التصنيف:"), 0, 0)
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addWidget(self.category_combo, 0, 1)
        
        form_layout.addWidget(QLabel("الاسم (بالإنجليزية):"), 1, 0)
        self.name_en_input = QLineEdit()
        form_layout.addWidget(self.name_en_input, 1, 1)
        
        form_layout.addWidget(QLabel("الاسم (بالعربية):"), 2, 0)
        self.name_ar_input = QLineEdit()
        form_layout.addWidget(self.name_ar_input, 2, 1)
        
        form_layout.addWidget(QLabel("الوصف (بالإنجليزية):"), 3, 0)
        self.desc_en_input = QTextEdit()
        self.desc_en_input.setMaximumHeight(60)
        form_layout.addWidget(self.desc_en_input, 3, 1)
        
        form_layout.addWidget(QLabel("الوصف (بالعربية):"), 4, 0)
        self.desc_ar_input = QTextEdit()
        self.desc_ar_input.setMaximumHeight(60)
        form_layout.addWidget(self.desc_ar_input, 4, 1)
        
        self.weight_based_checkbox = QCheckBox("صنف يباع بالوزن (سعر بالكيلو)")
        self.weight_based_checkbox.stateChanged.connect(self.toggle_price_fields)
        form_layout.addWidget(self.weight_based_checkbox, 5, 1)
        
        form_layout.addWidget(QLabel("السعر الأساسي (د.ل):"), 6, 0)
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.0)
        self.base_price_input.setMaximum(1000000.0)
        self.base_price_input.setDecimals(2)
        form_layout.addWidget(self.base_price_input, 6, 1)
        
        form_layout.addWidget(QLabel("السعر لكل كغ (د.ل):"), 7, 0)
        self.price_per_kg_input = QDoubleSpinBox()
        self.price_per_kg_input.setMinimum(0.0)
        self.price_per_kg_input.setMaximum(1000000.0)
        self.price_per_kg_input.setDecimals(2)
        self.price_per_kg_input.setEnabled(False)
        form_layout.addWidget(self.price_per_kg_input, 7, 1)
        
        form_layout.addWidget(QLabel("ترتيب العرض:"), 8, 0)
        self.order_input = QSpinBox()
        self.order_input.setMinimum(0)
        self.order_input.setMaximum(100)
        form_layout.addWidget(self.order_input, 8, 1)
        
        self.active_checkbox = QCheckBox("نشط")
        self.active_checkbox.setChecked(True)
        form_layout.addWidget(self.active_checkbox, 9, 1)
        
        layout.addLayout(form_layout)
        
        # Load existing data if editing
        if item_id:
            self.load_item()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_item)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_categories(self):
        """Load categories"""
        db = get_session()
        try:
            categories = db.query(MenuCategory).filter_by(active=True).order_by(MenuCategory.name_en).all()
            for category in categories:
                self.category_combo.addItem(f"{category.icon} {category.name_ar}", category.id)
        finally:
            db.close()
            
    def toggle_price_fields(self):
        """Toggle price fields based on weight-based checkbox"""
        is_weight_based = self.weight_based_checkbox.isChecked()
        self.base_price_input.setEnabled(not is_weight_based)
        self.price_per_kg_input.setEnabled(is_weight_based)
        
    def load_item(self):
        """Load item data for editing"""
        db = get_session()
        try:
            item = db.query(MenuItem).get(self.item_id)
            if item:
                # Find and set category
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
        finally:
            db.close()
            
    def save_item(self):
        """Save menu item"""
        name_en = self.name_en_input.text().strip()
        name_ar = self.name_ar_input.text().strip()
        category_id = self.category_combo.currentData()
        
        if not name_en or not name_ar or not category_id:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال جميع الحقول المطلوبة")
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
            item.description_en = self.desc_en_input.toPlainText()
            item.description_ar = self.desc_ar_input.toPlainText()
            item.is_weight_based = self.weight_based_checkbox.isChecked()
            item.base_price = CurrencyFormatter.lyd_to_fils(self.base_price_input.value())
            item.price_per_kg = CurrencyFormatter.lyd_to_fils(self.price_per_kg_input.value()) if item.is_weight_based else None
            item.display_order = self.order_input.value()
            item.active = self.active_checkbox.isChecked()
            
            db.commit()
            
            QMessageBox.information(self, "تم بنجاح",
                f"تم حفظ الصنف '{name_ar}' بنجاح")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حفظ الصنف: {e}")
        finally:
            db.close()


class IngredientsDialog(QDialog):
    """Dialog for managing menu item ingredients"""
    
    def __init__(self, item_id, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.setWindowTitle("إدارة المكونات")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Menu item info
        db = get_session()
        try:
            item = db.query(MenuItem).get(item_id)
            if item:
                info_label = QLabel(f"الصنف: {item.name_ar} ({item.name_en})")
                info_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4ECDC4;")
                layout.addWidget(info_label)
        finally:
            db.close()
        
        # Current ingredients table
        layout.addWidget(QLabel("المكونات الحالية:"))
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(5)
        self.ingredients_table.setHorizontalHeaderLabels([
            "المكون", "الكمية لكل حصة", "الكمية لكل كغ", "الوحدة", "إجراءات"
        ])
        self.ingredients_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.ingredients_table)
        
        # Add ingredient section
        add_group = QGroupBox("إضافة مكون")
        add_layout = QGridLayout()
        
        add_layout.addWidget(QLabel("المكون:"), 0, 0)
        self.ingredient_combo = QComboBox()
        self.load_inventory_items()
        add_layout.addWidget(self.ingredient_combo, 0, 1)
        
        add_layout.addWidget(QLabel("الكمية لكل حصة:"), 1, 0)
        self.qty_serving_input = QDoubleSpinBox()
        self.qty_serving_input.setMinimum(0.0)
        self.qty_serving_input.setMaximum(1000.0)
        self.qty_serving_input.setDecimals(3)
        add_layout.addWidget(self.qty_serving_input, 1, 1)
        
        add_layout.addWidget(QLabel("الكمية لكل كغ (للأصناف بالوزن):"), 2, 0)
        self.qty_kg_input = QDoubleSpinBox()
        self.qty_kg_input.setMinimum(0.0)
        self.qty_kg_input.setMaximum(1000.0)
        self.qty_kg_input.setDecimals(3)
        add_layout.addWidget(self.qty_kg_input, 2, 1)
        
        add_btn = QPushButton("➕ إضافة")
        add_btn.setObjectName("success")
        add_btn.clicked.connect(self.add_ingredient)
        add_layout.addWidget(add_btn, 3, 1)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Close button
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        self.load_ingredients()
        
    def load_inventory_items(self):
        """Load inventory items"""
        db = get_session()
        try:
            items = db.query(InventoryItem).order_by(InventoryItem.name_en).all()
            for item in items:
                self.ingredient_combo.addItem(f"{item.sku} - {item.name_ar} ({item.unit})", item.id)
        finally:
            db.close()
            
    def load_ingredients(self):
        """Load current ingredients"""
        db = get_session()
        try:
            links = db.query(MenuItemIngredient).filter_by(menu_item_id=self.item_id).all()
            
            self.ingredients_table.setRowCount(len(links))
            
            for idx, link in enumerate(links):
                # Ingredient name
                self.ingredients_table.setItem(idx, 0, QTableWidgetItem(link.inventory_item.name_ar))
                
                # Qty per serving
                self.ingredients_table.setItem(idx, 1, QTableWidgetItem(f"{link.quantity_per_serving:.3f}"))
                
                # Qty per kg
                self.ingredients_table.setItem(idx, 2, QTableWidgetItem(f"{link.quantity_per_kg:.3f}"))
                
                # Unit
                self.ingredients_table.setItem(idx, 3, QTableWidgetItem(link.inventory_item.unit))
                
                # Actions
                delete_btn = QPushButton("🗑️")
                delete_btn.setObjectName("danger")
                delete_btn.clicked.connect(lambda checked, l=link: self.delete_ingredient(l.id))
                self.ingredients_table.setCellWidget(idx, 4, delete_btn)
                
        finally:
            db.close()
            
    def add_ingredient(self):
        """Add ingredient to menu item"""
        inventory_id = self.ingredient_combo.currentData()
        qty_serving = self.qty_serving_input.value()
        qty_kg = self.qty_kg_input.value()
        
        if qty_serving == 0 and qty_kg == 0:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال كمية واحدة على الأقل")
            return
        
        db = get_session()
        try:
            # Check if already exists
            existing = db.query(MenuItemIngredient).filter_by(
                menu_item_id=self.item_id,
                inventory_item_id=inventory_id
            ).first()
            
            if existing:
                QMessageBox.warning(self, "مكرر", "تمت إضافة هذا المكون مسبقًا")
                return
            
            link = MenuItemIngredient(
                menu_item_id=self.item_id,
                inventory_item_id=inventory_id,
                quantity_per_serving=qty_serving,
                quantity_per_kg=qty_kg
            )
            db.add(link)
            db.commit()
            
            self.load_ingredients()
            
            # Reset inputs
            self.qty_serving_input.setValue(0.0)
            self.qty_kg_input.setValue(0.0)
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر إضافة المكون: {e}")
        finally:
            db.close()
            
    def delete_ingredient(self, link_id):
        """Delete ingredient from menu item"""
        db = get_session()
        try:
            link = db.query(MenuItemIngredient).get(link_id)
            if link:
                db.delete(link)
                db.commit()
                self.load_ingredients()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حذف المكون: {e}")
        finally:
            db.close()
