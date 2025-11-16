"""
DiBono ERP - Styles and Theme
Ocean-themed styling with blue/teal/coral palette
"""

OCEAN_THEME = """
QMainWindow, QWidget {
    background-color: #0A1128;
    color: #E8F1F2;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
}

QPushButton {
    background-color: #1282A2;
    color: #FEFCFB;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #0F4C75;
}

QPushButton:pressed {
    background-color: #034078;
}

QPushButton:disabled {
    background-color: #2A2D3A;
    color: #6C757D;
}

QPushButton#primary {
    background-color: #FF6B6B;
    font-size: 13pt;
    padding: 14px 28px;
}

QPushButton#primary:hover {
    background-color: #EE5A52;
}

QPushButton#success {
    background-color: #51CF66;
}

QPushButton#success:hover {
    background-color: #40C057;
}

QPushButton#danger {
    background-color: #FF6B6B;
}

QPushButton#danger:hover {
    background-color: #FA5252;
}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #1B263B;
    border: 2px solid #415A77;
    border-radius: 6px;
    padding: 10px;
    color: #E8F1F2;
    font-size: 11pt;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid: #1282A2;
}

QLabel {
    color: #E8F1F2;
    font-size: 11pt;
}

QLabel#title {
    font-size: 24pt;
    font-weight: bold;
    color: #4ECDC4;
}

QLabel#subtitle {
    font-size: 16pt;
    color: #95E1D3;
}

QLabel#kpi_value {
    font-size: 28pt;
    font-weight: bold;
    color: #51CF66;
}

QLabel#kpi_label {
    font-size: 10pt;
    color: #ADB5BD;
}

QTableWidget {
    background-color: #1B263B;
    alternate-background-color: #0E1A2F;
    border: 1px solid #415A77;
    border-radius: 8px;
    color: #E8F1F2;
    gridline-color: #415A77;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #1282A2;
    color: #FEFCFB;
}

QHeaderView::section {
    background-color: #0F4C75;
    color: #E8F1F2;
    padding: 10px;
    border: none;
    font-weight: bold;
}

QTabWidget::pane {
    border: 2px solid #415A77;
    border-radius: 8px;
    background-color: #0E1A2F;
}

QTabBar::tab {
    background-color: #1B263B;
    color: #ADB5BD;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #1282A2;
    color: #FEFCFB;
}

QTabBar::tab:hover {
    background-color: #0F4C75;
}

QScrollBar:vertical {
    background-color: #1B263B;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #415A77;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #1282A2;
}

QScrollBar:horizontal {
    background-color: #1B263B;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #415A77;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #1282A2;
}

QComboBox {
    background-color: #1B263B;
    border: 2px solid #415A77;
    border-radius: 6px;
    padding: 8px;
    color: #E8F1F2;
}

QComboBox:hover {
    border: 2px solid #1282A2;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #1B263B;
    border: 2px solid #415A77;
    selection-background-color: #1282A2;
    color: #E8F1F2;
}

QCheckBox {
    color: #E8F1F2;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #415A77;
    border-radius: 4px;
    background-color: #1B263B;
}

QCheckBox::indicator:checked {
    background-color: #1282A2;
    border-color: #1282A2;
}

QGroupBox {
    border: 2px solid #415A77;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    color: #E8F1F2;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}

QFrame#card {
    background-color: #1B263B;
    border: 2px solid #415A77;
    border-radius: 12px;
    padding: 16px;
}

QFrame#sidebar {
    background-color: #0E1A2F;
    border-right: 3px solid #1282A2;
}

QMessageBox {
    background-color: #0A1128;
}

QMessageBox QLabel {
    color: #E8F1F2;
    min-width: 300px;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

LOGIN_ANIMATION_STYLE = """
QWidget#loginContainer {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #001233, stop:0.5 #003B5C, stop:1 #001233
    );
}

QLabel#logo {
    font-size: 48pt;
    font-weight: bold;
    color: #4ECDC4;
    background: transparent;
}

QLabel#tagline {
    font-size: 12pt;
    font-style: italic;
    color: #95E1D3;
    background: transparent;
}

QFrame#loginBox {
    background-color: rgba(27, 38, 59, 180);
    border: 3px solid #1282A2;
    border-radius: 20px;
}
"""

POS_MENU_TILE_STYLE = """
QPushButton#menuTile {
    background-color: #1B263B;
    border: 2px solid #415A77;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    font-size: 12pt;
    font-weight: bold;
    min-width: 140px;
    min-height: 120px;
}

QPushButton#menuTile:hover {
    background-color: #0F4C75;
    border: 2px solid #1282A2;
}

QPushButton#menuTile:pressed {
    background-color: #1282A2;
}
"""

CATEGORY_CHIP_STYLE = """
QPushButton#categoryChip {
    background-color: #415A77;
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    font-size: 11pt;
    font-weight: bold;
    min-height: 36px;
}

QPushButton#categoryChip:checked {
    background-color: #1282A2;
    color: #FEFCFB;
}

QPushButton#categoryChip:hover {
    background-color: #0F4C75;
}
"""
