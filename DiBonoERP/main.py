"""
DiBono ERP - Main Application Entry Point
Seafood Restaurant Management System
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import init_db, get_session
from models.seed_data import seed_database
from ui.login_screen import LoginScreen
from ui.main_window import MainWindow
from utils.styles import OCEAN_THEME


class DiBonoApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application metadata
        self.setApplicationName("DiBono ERP")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("DiBono Seafood")
        
        # Set default font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Initialize database
        self.init_database()
        
        # Create main widget stack
        self.widget_stack = QStackedWidget()
        self.widget_stack.setWindowTitle("DiBono ERP - Seafood Restaurant Management")
        self.widget_stack.setMinimumSize(1024, 768)
        
        # Apply global theme
        self.setStyleSheet(OCEAN_THEME)
        
        # Show login screen
        self.show_login()
        
        self.widget_stack.show()
        
    def init_database(self):
        """Initialize and seed database if needed"""
        try:
            print("Initializing database...")
            init_db()
            
            # Check if seeding is needed
            db = get_session()
            try:
                from models.database import User
                user_count = db.query(User).count()
                if user_count == 0:
                    print("Database empty, seeding...")
                    seed_database()
            finally:
                db.close()
                
        except Exception as e:
            QMessageBox.critical(None, "Database Error", 
                               f"Failed to initialize database:\n{str(e)}")
            sys.exit(1)
            
    def show_login(self):
        """Show login screen"""
        login_screen = LoginScreen()
        login_screen.login_successful.connect(self.on_login_success)
        
        # Clear stack and add login
        while self.widget_stack.count() > 0:
            widget = self.widget_stack.widget(0)
            self.widget_stack.removeWidget(widget)
            widget.deleteLater()
            
        self.widget_stack.addWidget(login_screen)
        self.widget_stack.setCurrentWidget(login_screen)
        
    def on_login_success(self, user):
        """Handle successful login"""
        print(f"Login successful: {user.full_name} ({user.role})")
        
        # Create and show main window
        main_window = MainWindow(user)
        
        # Connect close event to show login
        main_window.destroyed.connect(self.show_login)
        
        self.widget_stack.addWidget(main_window)
        self.widget_stack.setCurrentWidget(main_window)
        
        # Maximize window
        self.widget_stack.showMaximized()


def main():
    """Application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = DiBonoApp(sys.argv)
    
    print("=" * 60)
    print("DiBono ERP - Seafood Restaurant Management System")
    print("=" * 60)
    print("Hard-configured Admin Account:")
    print("  Username: admin")
    print("  Password: CatchTheWave!")
    print("=" * 60)
    print("Employee Test Accounts:")
    print("  Username: ahmed   Password: 123456")
    print("  Username: fatima  Password: 123456")
    print("=" * 60)
    print("Admin PIN for POS overrides: 1234")
    print("=" * 60)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
