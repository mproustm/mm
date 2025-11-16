"""
DiBono ERP - Main Application Window
Central window managing navigation between screens
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QStackedWidget, QPushButton, QLabel, QFrame,
                              QMessageBox, QDialog, QLineEdit, QDialogButtonBox,
                              QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models.database import get_session
from utils.helpers import AuthManager
from utils.styles import OCEAN_THEME
from ui.pos_interface import POSInterface
from ui.admin_dashboard import AdminDashboard
from ui.inventory_management import InventoryManagement
from ui.menu_management import MenuManagement
from ui.employee_management import EmployeeManagement
from ui.reports_management import ReportsManagement
from ui.table_management import TableManagement
from datetime import datetime


class MainWindow(QMainWindow):
    """Main application window with navigation"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("دي بونو لإدارة المطعم")
        self.setMinimumSize(1280, 800)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Apply ocean theme
        self.setStyleSheet(OCEAN_THEME)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize main window UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Sidebar for admin, hidden for employees
        if self.user.role == 'admin':
            sidebar = self.create_sidebar()
            main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        
        # Wrap content stack in a scroll area for better responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.content_stack)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        main_layout.addWidget(scroll_area, 1) # Add stretch factor
        
        # Load appropriate screens
        if self.user.role == 'admin':
            self.load_admin_screens()
        else:
            self.load_employee_screens()
            
    def create_sidebar(self) -> QWidget:
        """Create admin sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)
        sidebar.setLayout(layout)
        
        # Logo/Title
        title = QLabel("🌊 دي بونو - نظام الإدارة")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #4ECDC4; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("لوحة التحكم الإدارية")
        subtitle.setStyleSheet("font-size: 11pt; color: #95E1D3; padding-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 لوحة القيادة", 0),
            ("📦 إدارة المخزون", 1),
            ("🍽️ إدارة القائمة", 2),
            ("👥 إدارة الموظفين", 3),
            ("🪑 إدارة الطاولات", 4),
            ("📈 التقارير والتحليلات", 5),
            ("💰 نقطة البيع", 6),
        ]
        
        for text, index in nav_buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(70)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: right;
                    padding-right: 20px;
                    font-size: 11pt;
                    background-color: transparent;
                    border: none;
                    border-right: 4px solid transparent;
                }
                QPushButton:hover {
                    background-color: #1B263B;
                    border-right: 4px solid #1282A2;
                }
                QPushButton:checked {
                    background-color: #1282A2;
                    border-right: 4px solid #51CF66;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self.switch_screen(i))
            layout.addWidget(btn)
            
            if index == 0:
                btn.setChecked(True)
        
        layout.addStretch()
        
        # User info at bottom
        user_label = QLabel(f"👤 {self.user.full_name}")
        user_label.setStyleSheet("font-size: 10pt; color: #ADB5BD; padding: 10px;")
        layout.addWidget(user_label)
        
        logout_btn = QPushButton("تسجيل الخروج")
        logout_btn.setObjectName("danger")
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)
        
        return sidebar
        
    def load_admin_screens(self):
        """Load all admin screens"""
        # Dashboard
        self.dashboard = AdminDashboard()
        self.content_stack.addWidget(self.dashboard)
        
        # Inventory Management (Modern Card-Based UI)
        self.inventory = InventoryManagement()
        self.content_stack.addWidget(self.inventory)
        
        # Menu Management
        self.menu = MenuManagement()
        self.content_stack.addWidget(self.menu)
        
        # Employee Management
        self.employees = EmployeeManagement()
        self.content_stack.addWidget(self.employees)
        
        # Table Management
        self.tables = TableManagement()
        self.content_stack.addWidget(self.tables)
        
        # Reports & Analytics
        self.reports = ReportsManagement()
        self.content_stack.addWidget(self.reports)
        
        # POS
        self.pos = POSInterface()
        self.pos.logout_requested.connect(self.handle_logout)
        self.content_stack.addWidget(self.pos)
        
    def load_employee_screens(self):
        """Load employee screens (POS only)"""
        self.pos = POSInterface()
        self.pos.logout_requested.connect(self.handle_logout)
        self.content_stack.addWidget(self.pos)
        
    def switch_screen(self, index: int):
        """Switch to specified screen"""
        self.content_stack.setCurrentIndex(index)
        
    def handle_logout(self):
        """Handle logout with cash reconciliation"""
        if self.user.role == 'employee' and AuthManager.current_session:
            # Show cash count dialog
            dialog = CashCountDialog(AuthManager.current_session.expected_cash, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                actual_cash = dialog.get_actual_cash()
                
                db = get_session()
                try:
                    AuthManager.logout(db, actual_cash)
                finally:
                    db.close()
                
                self.close()
        else:
            db = get_session()
            try:
                AuthManager.logout(db)
            finally:
                db.close()
            
            self.close()


class CashCountDialog(QDialog):
    """Dialog for cash count on employee logout"""
    
    def __init__(self, expected_cash: int, parent=None):
        super().__init__(parent)
        self.expected_cash = expected_cash
        self.setWindowTitle("إغلاق الوردية - جرد النقدية")
        self.setModal(True)
        self.setFixedWidth(400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Session info
        if AuthManager.current_session:
            duration = datetime.utcnow() - AuthManager.current_session.login_time
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            seconds = duration.seconds % 60
            
            info_label = QLabel(
                f"مدة الوردية: {hours:02d}:{minutes:02d}:{seconds:02d}\n"
                f"عدد الطلبات: {AuthManager.current_session.orders_count}\n"
                f"النقد المتوقع: {expected_cash / 1000:.2f} د.ل"
            )
            info_label.setStyleSheet("font-size: 11pt; padding: 10px;")
            layout.addWidget(info_label)
        
        # Actual cash input
        cash_label = QLabel("أدخل النقد الفعلي (د.ل):")
        cash_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout.addWidget(cash_label)
        
        self.cash_input = QLineEdit()
        self.cash_input.setPlaceholderText(f"{expected_cash / 1000:.2f}")
        self.cash_input.setFixedHeight(45)
        layout.addWidget(self.cash_input)
        
        self.variance_label = QLabel("")
        self.variance_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(self.variance_label)
        
        self.cash_input.textChanged.connect(self.calculate_variance)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_button:
            ok_button.setText("تأكيد")
        if cancel_button:
            cancel_button.setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def calculate_variance(self):
        """Calculate and display variance"""
        try:
            actual = float(self.cash_input.text())
            actual_fils = int(actual * 1000)
            variance = actual_fils - self.expected_cash
            
            color = "#51CF66" if variance >= 0 else "#FF6B6B"
            sign = "+" if variance >= 0 else ""
            self.variance_label.setText(
                f"الفارق: {sign}{variance / 1000:.2f} د.ل"
            )
            self.variance_label.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {color};")
        except ValueError:
            self.variance_label.clear()
            
    def get_actual_cash(self) -> int:
        """Get actual cash count in fils"""
        try:
            return int(float(self.cash_input.text()) * 1000)
        except ValueError:
            return self.expected_cash
