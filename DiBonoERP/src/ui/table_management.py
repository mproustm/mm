"""
DiBono ERP - Table Management Screen
Restaurant table configuration and management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QTableWidget, QTableWidgetItem, QDialog, QLineEdit,
                              QSpinBox, QComboBox, QDialogButtonBox, QMessageBox, QFrame,
                              QGridLayout, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.database import get_session, RestaurantTable


class TableManagement(QWidget):
    """Table management interface"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_tables()
        
    def init_ui(self):
        """Initialize table management UI"""
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Title
        title = QLabel("🍽️ إدارة الطاولات")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ إضافة طاولة")
        add_btn.setObjectName("primary_btn")
        add_btn.clicked.connect(self.add_table)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ تعديل")
        edit_btn.clicked.connect(self.edit_table)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("danger_btn")
        delete_btn.clicked.connect(self.delete_table)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.load_tables)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Table list
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels([
            "رقم الطاولة", "السعة", "الحالة", "نشطة", "تاريخ الإضافة"
        ])
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setColumnWidth(0, 120)
        self.table_widget.setColumnWidth(1, 100)
        self.table_widget.setColumnWidth(2, 120)
        self.table_widget.setColumnWidth(3, 100)
        layout.addWidget(self.table_widget)
        
        # Visual table layout
        layout.addWidget(QLabel("📍 تخطيط الطاولات"))
        
        self.visual_grid = QGridLayout()
        self.visual_frame = QFrame()
        self.visual_frame.setObjectName("card")
        self.visual_frame.setLayout(self.visual_grid)
        self.visual_frame.setMinimumHeight(300)
        layout.addWidget(self.visual_frame)
        
    def load_tables(self):
        """Load all tables from database"""
        db = get_session()
        try:
            tables = db.query(RestaurantTable).order_by(RestaurantTable.table_number).all()
            
            self.table_widget.setRowCount(len(tables))
            
            for idx, table in enumerate(tables):
                self.table_widget.setItem(idx, 0, QTableWidgetItem(str(table.table_number)))
                self.table_widget.setItem(idx, 1, QTableWidgetItem(str(table.capacity)))
                
                # Status with color
                status_map = {
                    'available': 'متاحة',
                    'occupied': 'مشغولة',
                    'reserved': 'محجوزة'
                }
                status_item = QTableWidgetItem(status_map.get(table.status, table.status))
                
                if table.status == 'available':
                    status_item.setForeground(QColor(34, 139, 34))  # Green
                elif table.status == 'occupied':
                    status_item.setForeground(QColor(220, 20, 60))  # Red
                else:
                    status_item.setForeground(QColor(255, 165, 0))  # Orange
                
                self.table_widget.setItem(idx, 2, status_item)
                
                self.table_widget.setItem(idx, 3, QTableWidgetItem("نعم" if table.active else "لا"))
                self.table_widget.setItem(idx, 4, QTableWidgetItem(table.created_at.strftime("%Y-%m-%d")))
            
            self.update_visual_layout(tables)
            
        finally:
            db.close()
    
    def update_visual_layout(self, tables):
        """Update visual table layout grid"""
        # Clear existing widgets
        while self.visual_grid.count():
            child = self.visual_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create grid of table buttons (5 columns)
        active_tables = [t for t in tables if t.active]
        
        if not active_tables:
            label = QLabel("لا توجد طاولات نشطة")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.visual_grid.addWidget(label, 0, 0, 1, 5)
            return
        
        for idx, table in enumerate(active_tables):
            row = idx // 5
            col = idx % 5
            
            btn = QPushButton()
            btn.setFixedSize(100, 100)
            btn.setObjectName("table_btn")
            
            # Color based on status
            if table.status == 'available':
                btn.setStyleSheet("background-color: #90EE90; color: black; font-size: 18px; font-weight: bold; border-radius: 10px;")
            elif table.status == 'occupied':
                btn.setStyleSheet("background-color: #DC143C; color: white; font-size: 18px; font-weight: bold; border-radius: 10px;")
            else:
                btn.setStyleSheet("background-color: #FFA500; color: white; font-size: 18px; font-weight: bold; border-radius: 10px;")
            
            btn.setText(f"طاولة\n{table.table_number}\n({table.capacity} أشخاص)")
            
            self.visual_grid.addWidget(btn, row, col)
    
    def add_table(self):
        """Add new table"""
        dialog = TableDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_tables()
    
    def edit_table(self):
        """Edit selected table"""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "لم يتم التحديد", "يرجى تحديد طاولة للتعديل")
            return
        
        table_number = int(self.table_widget.item(current_row, 0).text())
        
        db = get_session()
        try:
            table = db.query(RestaurantTable).filter_by(table_number=table_number).first()
            if table:
                dialog = TableDialog(self, table)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_tables()
        finally:
            db.close()
    
    def delete_table(self):
        """Delete selected table"""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "لم يتم التحديد", "يرجى تحديد طاولة للحذف")
            return
        
        table_number = int(self.table_widget.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف الطاولة رقم {table_number}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db = get_session()
            try:
                table = db.query(RestaurantTable).filter_by(table_number=table_number).first()
                if table:
                    db.delete(table)
                    db.commit()
                    QMessageBox.information(self, "تم بنجاح", "تم حذف الطاولة")
                    self.load_tables()
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "خطأ", f"تعذر حذف الطاولة: {e}")
            finally:
                db.close()


class TableDialog(QDialog):
    """Dialog for adding/editing tables"""
    
    def __init__(self, parent=None, table=None):
        super().__init__(parent)
        self.table = table
        self.setWindowTitle("تعديل طاولة" if table else "إضافة طاولة")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("رقم الطاولة:"), 0, 0)
        self.number_input = QSpinBox()
        self.number_input.setMinimum(1)
        self.number_input.setMaximum(999)
        if table:
            self.number_input.setValue(table.table_number)
            self.number_input.setEnabled(False)  # Don't allow changing table number
        form_layout.addWidget(self.number_input, 0, 1)
        
        form_layout.addWidget(QLabel("السعة (عدد الأشخاص):"), 1, 0)
        self.capacity_input = QSpinBox()
        self.capacity_input.setMinimum(1)
        self.capacity_input.setMaximum(20)
        self.capacity_input.setValue(table.capacity if table else 4)
        form_layout.addWidget(self.capacity_input, 1, 1)
        
        form_layout.addWidget(QLabel("الحالة:"), 2, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["متاحة", "مشغولة", "محجوزة"])
        if table:
            status_map = {'available': 0, 'occupied': 1, 'reserved': 2}
            self.status_combo.setCurrentIndex(status_map.get(table.status, 0))
        form_layout.addWidget(self.status_combo, 2, 1)
        
        self.active_checkbox = QCheckBox("نشطة")
        self.active_checkbox.setChecked(table.active if table else True)
        form_layout.addWidget(self.active_checkbox, 3, 0, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_table)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_table(self):
        """Save table to database"""
        status_map = {0: 'available', 1: 'occupied', 2: 'reserved'}
        
        db = get_session()
        try:
            if self.table:
                # Update existing
                self.table.capacity = self.capacity_input.value()
                self.table.status = status_map[self.status_combo.currentIndex()]
                self.table.active = self.active_checkbox.isChecked()
            else:
                # Check if table number exists
                existing = db.query(RestaurantTable).filter_by(
                    table_number=self.number_input.value()
                ).first()
                
                if existing:
                    QMessageBox.warning(self, "رقم مكرر", "رقم الطاولة موجود مسبقًا")
                    return
                
                # Create new
                table = RestaurantTable(
                    table_number=self.number_input.value(),
                    capacity=self.capacity_input.value(),
                    status=status_map[self.status_combo.currentIndex()],
                    active=self.active_checkbox.isChecked()
                )
                db.add(table)
            
            db.commit()
            QMessageBox.information(self, "تم بنجاح", "تم حفظ الطاولة")
            self.accept()
            
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حفظ الطاولة: {e}")
        finally:
            db.close()
