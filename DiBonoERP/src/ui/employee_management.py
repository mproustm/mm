"""
DiBono ERP - Employee Management Screen
Complete employee and session management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QTableWidget, QTableWidgetItem, QDialog, QLineEdit,
                              QSpinBox, QTextEdit, QComboBox, QDialogButtonBox,
                              QMessageBox, QFrame, QGridLayout, QTabWidget, QHeaderView,
                              QScrollArea)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta

from utils.passlib_compat import ensure_bcrypt_about

ensure_bcrypt_about()
from passlib.hash import bcrypt
from models.database import (get_session, User, Session, Order)
from utils.helpers import CurrencyFormatter, DateRangeCalculator
from sqlalchemy import func
import openpyxl
from openpyxl.styles import Font, Alignment


class EmployeeManagement(QWidget):
    """Complete employee management interface"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_employees()
        
    def init_ui(self):
        """Initialize employee UI"""
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll_area)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title and actions
        header = QHBoxLayout()
        
        title = QLabel("👥 إدارة الموظفين")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(title)
        
        header.addStretch()
        
        add_btn = QPushButton("➕ إضافة موظف")
        add_btn.setObjectName("success")
        add_btn.clicked.connect(self.show_add_employee_dialog)
        header.addWidget(add_btn)
        
        export_btn = QPushButton("📊 تصدير إلى إكسل")
        export_btn.clicked.connect(self.export_to_excel)
        header.addWidget(export_btn)
        
        layout.addLayout(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Employees tab
        employees_widget = QWidget()
        employees_layout = QVBoxLayout()
        employees_widget.setLayout(employees_layout)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "اسم المستخدم", "الاسم الكامل", "الدور", "الوردية", "الراتب (د.ل)", "الحالة", "إجراءات"
        ])
        
        header = self.employees_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.employees_table.setColumnWidth(0, 120)
        self.employees_table.setColumnWidth(2, 80)
        self.employees_table.setColumnWidth(3, 150)
        self.employees_table.setColumnWidth(4, 100)
        self.employees_table.setColumnWidth(5, 80)
        
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        employees_layout.addWidget(self.employees_table)
        
        self.tabs.addTab(employees_widget, "👥 الموظفون")
        
        # Activity tab
        activity_widget = QWidget()
        activity_layout = QVBoxLayout()
        activity_widget.setLayout(activity_layout)
        
        # Employee selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("اختر الموظف:"))
        self.activity_employee_combo = QComboBox()
        self.activity_employee_combo.currentIndexChanged.connect(self.load_activity)
        selector_layout.addWidget(self.activity_employee_combo)
        selector_layout.addStretch()
        activity_layout.addLayout(selector_layout)
        
        # Stats cards
        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout()
        stats_frame.setLayout(stats_layout)
        
        self.sessions_label = QLabel("الجلسات: 0")
        self.sessions_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        stats_layout.addWidget(self.sessions_label)
        
        self.orders_label = QLabel("الطلبات: 0")
        self.orders_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        stats_layout.addWidget(self.orders_label)
        
        self.sales_label = QLabel("إجمالي المبيعات: 0.00 د.ل")
        self.sales_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #51CF66;")
        stats_layout.addWidget(self.sales_label)
        
        stats_layout.addStretch()
        activity_layout.addWidget(stats_frame)
        
        # Activity table
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(7)
        self.activity_table.setHorizontalHeaderLabels([
            "التاريخ", "الدخول", "الخروج", "المدة", "الطلبات", "المبيعات", "الفروقات"
        ])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        activity_layout.addWidget(self.activity_table)
        
        self.tabs.addTab(activity_widget, "📊 سجلات النشاط")
        
        layout.addWidget(self.tabs)
        
    def load_employees(self):
        """Load employees"""
        db = get_session()
        try:
            employees = db.query(User).order_by(User.username).all()
            
            self.employees_table.setRowCount(len(employees))
            
            # Also update activity selector
            self.activity_employee_combo.clear()
            
            for idx, employee in enumerate(employees):
                # Username
                self.employees_table.setItem(idx, 0, QTableWidgetItem(employee.username))
                
                # Full Name
                self.employees_table.setItem(idx, 1, QTableWidgetItem(employee.full_name))
                
                # Role
                role_text = "مدير" if employee.role == 'admin' else "موظف"
                role_item = QTableWidgetItem(role_text)
                if employee.role == 'admin':
                    role_item.setForeground(Qt.GlobalColor.yellow)
                self.employees_table.setItem(idx, 2, role_item)
                
                # Shift
                self.employees_table.setItem(idx, 3, QTableWidgetItem(employee.shift or "-"))
                
                # Salary
                self.employees_table.setItem(idx, 4, QTableWidgetItem(
                    f"{CurrencyFormatter.fils_to_lyd(employee.salary):.2f}"
                ))
                
                # Status
                status_item = QTableWidgetItem("✓ نشط" if employee.active else "✗ غير نشط")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.employees_table.setItem(idx, 5, status_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(40)
                edit_btn.clicked.connect(lambda checked, e=employee: self.edit_employee(e.id))
                actions_layout.addWidget(edit_btn)
                
                reset_btn = QPushButton("🔑")
                reset_btn.setMaximumWidth(40)
                reset_btn.clicked.connect(lambda checked, e=employee: self.reset_password(e.id))
                actions_layout.addWidget(reset_btn)
                
                actions_widget.setLayout(actions_layout)
                self.employees_table.setCellWidget(idx, 6, actions_widget)
                
                # Add to activity selector
                self.activity_employee_combo.addItem(f"{employee.full_name} - {employee.username}", employee.id)
                
            self.load_activity()
            
        finally:
            db.close()
            
    def load_activity(self):
        """Load activity logs for selected employee"""
        employee_id = self.activity_employee_combo.currentData()
        if not employee_id:
            return
        
        db = get_session()
        try:
            # Get sessions
            sessions = db.query(Session).filter_by(user_id=employee_id).order_by(
                Session.login_time.desc()
            ).limit(50).all()
            
            self.activity_table.setRowCount(len(sessions))
            
            total_sessions = len(sessions)
            total_orders = 0
            total_sales = 0
            
            for idx, session in enumerate(sessions):
                # Date
                date_str = session.login_time.strftime("%Y-%m-%d")
                self.activity_table.setItem(idx, 0, QTableWidgetItem(date_str))
                
                # Login time
                login_str = session.login_time.strftime("%H:%M:%S")
                self.activity_table.setItem(idx, 1, QTableWidgetItem(login_str))
                
                # Logout time
                logout_str = session.logout_time.strftime("%H:%M:%S") if session.logout_time else "نشط"
                self.activity_table.setItem(idx, 2, QTableWidgetItem(logout_str))
                
                # Duration
                if session.logout_time:
                    duration = session.logout_time - session.login_time
                    hours = duration.seconds // 3600
                    minutes = (duration.seconds % 3600) // 60
                    duration_str = f"{hours}س {minutes}د"
                else:
                    duration_str = "-"
                self.activity_table.setItem(idx, 3, QTableWidgetItem(duration_str))
                
                # Orders
                self.activity_table.setItem(idx, 4, QTableWidgetItem(str(session.orders_count)))
                total_orders += session.orders_count
                
                # Sales
                sales_str = CurrencyFormatter.format_lyd(session.total_sales)
                self.activity_table.setItem(idx, 5, QTableWidgetItem(sales_str))
                total_sales += session.total_sales
                
                # Variance
                if session.actual_cash is not None:
                    variance_str = CurrencyFormatter.format_lyd(session.variance)
                    variance_item = QTableWidgetItem(variance_str)
                    if session.variance < 0:
                        variance_item.setForeground(Qt.GlobalColor.red)
                    elif session.variance > 0:
                        variance_item.setForeground(Qt.GlobalColor.green)
                    self.activity_table.setItem(idx, 6, variance_item)
                else:
                    self.activity_table.setItem(idx, 6, QTableWidgetItem("-"))
            
            # Update stats
            self.sessions_label.setText(f"الجلسات: {total_sessions}")
            self.orders_label.setText(f"الطلبات: {total_orders}")
            self.sales_label.setText(f"إجمالي المبيعات: {CurrencyFormatter.format_lyd(total_sales)}")
            
        finally:
            db.close()
            
    def show_add_employee_dialog(self):
        """Show add employee dialog"""
        dialog = EmployeeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()
            
    def edit_employee(self, employee_id):
        """Edit employee"""
        dialog = EmployeeDialog(self, employee_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()
            
    def reset_password(self, employee_id):
        """Reset employee password"""
        dialog = ResetPasswordDialog(employee_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "تم بنجاح", "تم إعادة تعيين كلمة المرور")
            
    def export_to_excel(self):
        """Export employee data to Excel"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "تصدير إلى إكسل", "", "ملفات إكسل (*.xlsx)"
        )
        
        if not filename:
            return
        
        db = get_session()
        try:
            # Create workbook
            wb = openpyxl.Workbook()
            
            # Employees sheet
            ws_emp = wb.active
            ws_emp.title = "الموظفون"
            
            # Headers
            headers = ["اسم المستخدم", "الاسم الكامل", "الدور", "الوردية", "الراتب (د.ل)", "الحالة"]
            ws_emp.append(headers)
            
            # Style headers
            for cell in ws_emp[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
            
            # Data
            employees = db.query(User).order_by(User.username).all()
            for emp in employees:
                ws_emp.append([
                    emp.username,
                    emp.full_name,
                    ("مدير" if emp.role == 'admin' else "موظف"),
                    emp.shift or "-",
                    CurrencyFormatter.fils_to_lyd(emp.salary),
                    "نشط" if emp.active else "غير نشط"
                ])
            
            # Activity sheet
            ws_act = wb.create_sheet("ملخص النشاط")
            ws_act.append(["اسم المستخدم", "إجمالي الجلسات", "إجمالي الطلبات", "إجمالي المبيعات (د.ل)"])
            
            for cell in ws_act[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
            
            for emp in employees:
                sessions = db.query(Session).filter_by(user_id=emp.id).all()
                total_orders = sum(s.orders_count for s in sessions)
                total_sales = sum(s.total_sales for s in sessions)
                
                ws_act.append([
                    emp.username,
                    len(sessions),
                    total_orders,
                    CurrencyFormatter.fils_to_lyd(total_sales)
                ])
            
            # Save
            wb.save(filename)
            
            QMessageBox.information(self, "تم بنجاح", f"تم تصدير البيانات إلى {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر التصدير: {e}")
        finally:
            db.close()


class EmployeeDialog(QDialog):
    """Dialog for adding/editing employees"""
    
    def __init__(self, parent=None, employee_id=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.setWindowTitle("تعديل موظف" if employee_id else "إضافة موظف")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("اسم المستخدم:"), 0, 0)
        self.username_input = QLineEdit()
        form_layout.addWidget(self.username_input, 0, 1)
        
        form_layout.addWidget(QLabel("الاسم الكامل:"), 1, 0)
        self.fullname_input = QLineEdit()
        form_layout.addWidget(self.fullname_input, 1, 1)
        
        form_layout.addWidget(QLabel("الدور:"), 2, 0)
        self.role_combo = QComboBox()
        self.role_combo.addItem("موظف", "employee")
        self.role_combo.addItem("مدير", "admin")
        form_layout.addWidget(self.role_combo, 2, 1)
        
        form_layout.addWidget(QLabel("الوردية:"), 3, 0)
        self.shift_input = QLineEdit()
        self.shift_input.setPlaceholderText("مثال: صباحية 8ص-4م")
        form_layout.addWidget(self.shift_input, 3, 1)
        
        form_layout.addWidget(QLabel("الراتب الشهري (د.ل):"), 4, 0)
        self.salary_input = QSpinBox()
        self.salary_input.setMinimum(0)
        self.salary_input.setMaximum(100000)
        self.salary_input.setSingleStep(100)
        self.salary_input.setValue(500)
        form_layout.addWidget(self.salary_input, 4, 1)
        
        if not employee_id:
            form_layout.addWidget(QLabel("كلمة المرور:"), 5, 0)
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addWidget(self.password_input, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Load existing data if editing
        if employee_id:
            self.load_employee()
            self.username_input.setEnabled(False)  # Can't change username
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_employee)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_employee(self):
        """Load employee data for editing"""
        db = get_session()
        try:
            employee = db.query(User).get(self.employee_id)
            if employee:
                self.username_input.setText(employee.username)
                self.fullname_input.setText(employee.full_name)
                for idx in range(self.role_combo.count()):
                    if self.role_combo.itemData(idx) == employee.role:
                        self.role_combo.setCurrentIndex(idx)
                        break
                self.shift_input.setText(employee.shift or "")
                self.salary_input.setValue(int(CurrencyFormatter.fils_to_lyd(employee.salary)))
        finally:
            db.close()
            
    def save_employee(self):
        """Save employee"""
        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        
        if not username or not fullname:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال اسم المستخدم والاسم الكامل")
            return
        
        if not self.employee_id:
            password = self.password_input.text()
            if not password:
                QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال كلمة المرور")
                return
        
        db = get_session()
        try:
            if self.employee_id:
                employee = db.query(User).get(self.employee_id)
            else:
                # Check username doesn't exist
                existing = db.query(User).filter_by(username=username).first()
                if existing:
                    QMessageBox.warning(self, "مكرر", "اسم المستخدم موجود مسبقًا")
                    return
                
                employee = User()
                employee.username = username
                employee.password_hash = bcrypt.hash(password)
                db.add(employee)
            
            employee.full_name = fullname
            employee.role = self.role_combo.currentData()
            employee.shift = self.shift_input.text()
            employee.salary = CurrencyFormatter.lyd_to_fils(self.salary_input.value())
            
            db.commit()
            
            QMessageBox.information(self, "تم بنجاح", f"تم حفظ الموظف '{username}'")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر حفظ بيانات الموظف: {e}")
        finally:
            db.close()


class ResetPasswordDialog(QDialog):
    """Dialog for resetting employee password"""
    
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.setWindowTitle("إعادة تعيين كلمة المرور")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        db = get_session()
        try:
            employee = db.query(User).get(employee_id)
            if employee:
                info_label = QLabel(f"تعيين كلمة مرور لـ: {employee.full_name} ({employee.username})")
                info_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
                layout.addWidget(info_label)
        finally:
            db.close()
        
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("كلمة المرور الجديدة:"), 0, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input, 0, 1)
        
        form_layout.addWidget(QLabel("تأكيد كلمة المرور:"), 1, 0)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.confirm_input, 1, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.reset_password)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def reset_password(self):
        """Reset password"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not password:
            QMessageBox.warning(self, "بيانات غير مكتملة", "يرجى إدخال كلمة المرور الجديدة")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "تعارض", "كلمتا المرور غير متطابقتين")
            return
        
        db = get_session()
        try:
            employee = db.query(User).get(self.employee_id)
            if employee:
                employee.password_hash = bcrypt.hash(password)
                db.commit()
                self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "خطأ", f"تعذر إعادة التعيين: {e}")
        finally:
            db.close()
