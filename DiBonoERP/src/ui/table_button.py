"""
DiBono ERP - Custom Table-Shaped Button
Draws a realistic table shape with rounded corners and legs
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont


class TableButton(QPushButton):
    """Custom button that draws a table shape"""
    
    def __init__(self, table_number, capacity, status='available', parent=None):
        super().__init__(parent)
        self.table_number = table_number
        self.capacity = capacity
        self.status = status  # available, occupied, reserved
        self.setFixedSize(140, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def set_status(self, status):
        """Update table status and repaint"""
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        """Custom paint to draw table shape"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Colors based on status
        if self.status == 'available':
            bg_color = QColor(144, 238, 144)  # Light green
            border_color = QColor(34, 139, 34)  # Dark green
            text_color = QColor(0, 0, 0)  # Black
        elif self.status == 'occupied':
            bg_color = QColor(220, 20, 60)  # Crimson red
            border_color = QColor(139, 0, 0)  # Dark red
            text_color = QColor(255, 255, 255)  # White
        else:  # reserved
            bg_color = QColor(255, 165, 0)  # Orange
            border_color = QColor(255, 140, 0)  # Dark orange
            text_color = QColor(255, 255, 255)  # White
        
        # Adjust colors if disabled
        if not self.isEnabled():
            bg_color.setAlpha(180)
            border_color.setAlpha(180)
            text_color.setAlpha(180)
        
        # Adjust colors on hover
        if self.underMouse() and self.isEnabled():
            border_color = QColor(18, 130, 162)  # Blue border on hover
            painter.setPen(QPen(border_color, 5))
        else:
            painter.setPen(QPen(border_color, 3))
        
        # Draw table top (rounded rectangle)
        table_top_rect = QRect(15, 20, 110, 70)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(table_top_rect, 15, 15)
        
        # Draw table legs (4 small rectangles)
        leg_color = border_color
        painter.setBrush(leg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Front left leg
        painter.drawRect(25, 90, 8, 25)
        # Front right leg
        painter.drawRect(107, 90, 8, 25)
        # Back left leg
        painter.drawRect(25, 90, 8, 15)
        # Back right leg
        painter.drawRect(107, 90, 8, 15)
        
        # Draw text in center of table top
        painter.setPen(text_color)
        
        # Table number (large)
        font = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(table_top_rect, Qt.AlignmentFlag.AlignCenter, str(self.table_number))
        
        # Status text (small, at bottom of table top)
        status_map = {
            'available': 'متاحة',
            'occupied': 'مشغولة',
            'reserved': 'محجوزة'
        }
        status_text = status_map.get(self.status, self.status)
        
        font = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font)
        status_rect = QRect(15, 70, 110, 20)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, status_text)
        
        # Capacity text (small, at top)
        capacity_text = f"{self.capacity} أشخاص"
        capacity_rect = QRect(15, 20, 110, 20)
        painter.drawText(capacity_rect, Qt.AlignmentFlag.AlignCenter, capacity_text)
