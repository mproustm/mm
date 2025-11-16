"""
DiBono ERP - Table Selection Screen
Table selection for dine-in orders in POS
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QGridLayout, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from models.database import get_session, RestaurantTable, HeldOrder
from ui.table_button import TableButton
from datetime import datetime


class TableSelectionScreen(QWidget):
    """Table selection screen for POS"""
    
    table_selected = pyqtSignal(int)  # Emits table_id
    takeaway_selected = pyqtSignal()
    back_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_tables()
        
    def init_ui(self):
        """Initialize table selection UI"""
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Title
        title = QLabel("اختر الطاولة أو التوصيل")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #4ECDC4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Takeaway button (prominent)
        takeaway_btn = QPushButton("🥡 طلب توصيل")
        takeaway_btn.setMinimumHeight(100)
        takeaway_btn.setStyleSheet("""
            QPushButton {
                font-size: 20pt;
                font-weight: bold;
                background-color: #FF6B35;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #FF8C61;
            }
        """)
        takeaway_btn.clicked.connect(self.takeaway_selected.emit)
        layout.addWidget(takeaway_btn)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)
        
        # Tables grid
        tables_label = QLabel("أو اختر طاولة:")
        tables_label.setStyleSheet("font-size: 16pt; color: #95E1D3;")
        layout.addWidget(tables_label)
        
        self.tables_grid = QGridLayout()
        self.tables_grid.setSpacing(15)
        
        self.tables_frame = QFrame()
        self.tables_frame.setObjectName("card")
        self.tables_frame.setLayout(self.tables_grid)
        
        layout.addWidget(self.tables_frame)
        layout.addStretch()
        
    def load_tables(self):
        """Load and display available tables"""
        # Clear existing widgets
        while self.tables_grid.count():
            child = self.tables_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        db = get_session()
        try:
            tables = db.query(RestaurantTable).filter_by(active=True).order_by(RestaurantTable.table_number).all()
            
            if not tables:
                label = QLabel("لا توجد طاولات متاحة. يرجى إضافة طاولات من قسم الإدارة.")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 14pt; color: #FFA07A;")
                self.tables_grid.addWidget(label, 0, 0, 1, 5)
                return
            
            # Check for held orders to determine actual status
            held_orders = db.query(HeldOrder).filter(
                HeldOrder.table_id.isnot(None),
                HeldOrder.expires_at > datetime.utcnow()
            ).all()
            
            # Create a map of table_id -> held_order
            held_order_map = {ho.table_id: ho for ho in held_orders}
            
            # Display tables in grid (5 columns)
            for idx, table in enumerate(tables):
                row = idx // 5
                col = idx % 5
                
                # Check if table has a held order
                has_held_order = table.id in held_order_map
                
                # Determine actual status
                if has_held_order:
                    actual_status = 'occupied'
                else:
                    actual_status = table.status
                
                # Create table-shaped button
                btn = TableButton(table.table_number, table.capacity, actual_status)
                btn.setProperty("table_id", table.id)
                btn.setProperty("table_number", table.table_number)
                btn.setProperty("has_held_order", has_held_order)
                
                # All tables are clickable
                btn.setEnabled(True)
                
                btn.clicked.connect(lambda checked, tid=table.id, tnum=table.table_number, has_order=has_held_order: 
                                  self.select_table(tid, tnum, has_order))
                
                self.tables_grid.addWidget(btn, row, col)
                
        finally:
            db.close()
    
    def select_table(self, table_id, table_number, has_held_order):
        """Handle table selection"""
        # No confirmation needed - just select the table
        # If table has held order, it will be restored automatically in POS
        self.table_selected.emit(table_id)
    
    def refresh_tables(self):
        """Refresh table display"""
        self.load_tables()
