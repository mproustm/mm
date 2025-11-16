"""
DiBono ERP - Login Screen
Animated ocean-themed authentication interface
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QCheckBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont
from models.database import get_session
from utils.helpers import AuthManager
from utils.styles import LOGIN_ANIMATION_STYLE


class LoginScreen(QWidget):
    """Login screen with marine animation and authentication"""
    
    login_successful = pyqtSignal(object)  # Emits User object
    
    def __init__(self):
        super().__init__()
        self.failed_attempts = 0
        self.shake_offset = 0
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        """Initialize UI components"""
        self.setObjectName("loginContainer")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)
        
        # Login box (card)
        login_box = QFrame()
        login_box.setObjectName("loginBox")
        login_box.setFixedWidth(450)
        login_layout = QVBoxLayout()
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(40, 40, 40, 40)
        login_box.setLayout(login_layout)
        
        # Logo
        logo_label = QLabel("🌊 دي بونو")
        logo_label.setObjectName("logo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("مطعم دي بونو للمأكولات البحرية")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #4ECDC4;")
        login_layout.addWidget(title_label)
        
        # Spacing
        login_layout.addSpacing(30)
        
        # Username field
        username_label = QLabel("اسم المستخدم")
        username_label.setStyleSheet("font-size: 11pt; color: #95E1D3;")
        login_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("أدخل اسم المستخدم")
        self.username_input.setFixedHeight(45)
        self.username_input.returnPressed.connect(self.handle_login)
        login_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("كلمة المرور")
        password_label.setStyleSheet("font-size: 11pt; color: #95E1D3;")
        login_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.returnPressed.connect(self.handle_login)
        login_layout.addWidget(self.password_input)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("تذكرني (للمدير فقط)")
        self.remember_checkbox.setStyleSheet("font-size: 10pt; color: #ADB5BD;")
        login_layout.addWidget(self.remember_checkbox)
        
        # Spacing
        login_layout.addSpacing(20)
        
        # Login button
        self.login_button = QPushButton("تسجيل الدخول ▶")
        self.login_button.setObjectName("primary")
        self.login_button.setFixedHeight(50)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(self.login_button)
        
        # Error message label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #FF6B6B; font-size: 10pt; font-weight: bold;")
        self.error_label.setWordWrap(True)
        login_layout.addWidget(self.error_label)
        
        # Tagline
        tagline = QLabel("\"أشهى المأكولات البحرية في طرابلس\"")
        tagline.setObjectName("tagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-size: 11pt; font-style: italic; color: #95E1D3; margin-top: 20px;")
        login_layout.addWidget(tagline)
        
        main_layout.addWidget(login_box)
        
        # Set focus to username
        self.username_input.setFocus()
        
    def apply_styles(self):
        """Apply ocean theme styles"""
        self.setStyleSheet(LOGIN_ANIMATION_STYLE)
        
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText("جاري تسجيل الدخول...")
        
        # Perform authentication
        db = get_session()
        try:
            success, message = AuthManager.login(db, username, password)
            
            if success:
                self.error_label.clear()
                self.login_successful.emit(AuthManager.current_user)
            else:
                self.failed_attempts += 1
                self.show_error(message)
                
                if self.failed_attempts >= 3:
                    self.shake_animation()
                    self.error_label.setText(f"{message}\n(محاولات كثيرة فاشلة!)")
                
                # Clear password field
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            self.show_error(f"خطأ أثناء تسجيل الدخول: {str(e)}")
        finally:
            db.close()
            self.login_button.setEnabled(True)
            self.login_button.setText("تسجيل الدخول ▶")
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_label.setText(message)
        
        # Flash error label
        QTimer.singleShot(3000, self.error_label.clear)
    
    def shake_animation(self):
        """Shake animation for failed login attempts"""
        login_box = self.findChild(QFrame, "loginBox")
        if not login_box:
            return
        
        original_pos = login_box.pos()
        
        def shake_step(step):
            if step > 6:
                login_box.move(original_pos)
                return
            
            offset = 15 if step % 2 == 0 else -15
            login_box.move(original_pos.x() + offset, original_pos.y())
            QTimer.singleShot(50, lambda: shake_step(step + 1))
        
        shake_step(0)
    
    def reset_fields(self):
        """Reset input fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self.error_label.clear()
        self.failed_attempts = 0
        self.username_input.setFocus()
