"""
DiBono ERP - Admin Dashboard
KPI cards and revenue visualization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from datetime import datetime
from models.database import get_session, Order, OrderItem
from sqlalchemy import func
from utils.helpers import CurrencyFormatter, DateRangeCalculator


class AdminDashboard(QWidget):
    """Admin dashboard with KPIs and charts"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_kpis()
        
    def init_ui(self):
        """Initialize dashboard UI"""
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
        content_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Title
        title = QLabel("لوحة القيادة")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # KPI Grid (3x3)
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(20)
        
        # Create 9 KPI cards
        self.kpi_cards = {}
        
        kpi_definitions = [
            ("cash_day", "المبيعات النقدية - اليوم", "💵"),
            ("cash_week", "المبيعات النقدية - الأسبوع", "💵"),
            ("cash_month", "المبيعات النقدية - الشهر", "💵"),
            ("card_day", "المدفوعات بالبطاقة - اليوم", "💳"),
            ("card_week", "المدفوعات بالبطاقة - الأسبوع", "💳"),
            ("card_month", "المدفوعات بالبطاقة - الشهر", "💳"),
            ("revenue_day", "الإيراد الكلي - اليوم", "💰"),
            ("revenue_week", "الإيراد الكلي - الأسبوع", "💰"),
            ("revenue_month", "الإيراد الكلي - الشهر", "💰"),
            ("profit_day", "صافي الربح - اليوم", "💎"),
            ("profit_week", "صافي الربح - الأسبوع", "💎"),
            ("profit_month", "صافي الربح - الشهر", "💎"),
        ]
        
        row, col = 0, 0
        for key, label, icon in kpi_definitions:
            card = self.create_kpi_card(icon, label)
            self.kpi_cards[key] = card
            kpi_grid.addWidget(card, row, col)
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        layout.addLayout(kpi_grid)
        
        # Chart placeholder
        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_frame.setMinimumHeight(300)
        chart_layout = QVBoxLayout()
        chart_frame.setLayout(chart_layout)
        
        chart_title = QLabel("📊 توزيع طرق الدفع")
        chart_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #4ECDC4;")
        chart_layout.addWidget(chart_title)
        
        chart_placeholder = QLabel("مساحة الرسم البياني\n(تكامل QtCharts)")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("font-size: 14pt; color: #ADB5BD;")
        chart_layout.addWidget(chart_placeholder)
        
        layout.addWidget(chart_frame)
        
        layout.addStretch()
        
    def create_kpi_card(self, icon: str, label: str) -> QFrame:
        """Create a KPI card widget"""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(140)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)
        card.setLayout(card_layout)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32pt;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel("0.00 د.ل")
        value_label.setObjectName("kpi_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setObjectName("kpi_label")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label_widget)
        
        # Delta (change from previous period)
        delta_label = QLabel("")
        delta_label.setStyleSheet("font-size: 9pt; color: #ADB5BD;")
        delta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(delta_label)
        
        # Store references
        card.value_label = value_label
        card.delta_label = delta_label
        
        return card
        
    def load_kpis(self):
        """Load and display KPI data"""
        db = get_session()
        try:
            # Day ranges
            day_start, day_end = DateRangeCalculator.get_day_range()
            week_start, week_end = DateRangeCalculator.get_week_range()
            month_start, month_end = DateRangeCalculator.get_month_range()
            
            # Cash Day
            cash_day = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.payment_method == 'cash',
                Order.timestamp >= day_start,
                Order.timestamp < day_end
            ).scalar() or 0
            self.update_kpi_card('cash_day', cash_day)
            
            # Cash Week
            cash_week = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.payment_method == 'cash',
                Order.timestamp >= week_start,
                Order.timestamp < week_end
            ).scalar() or 0
            self.update_kpi_card('cash_week', cash_week)
            
            # Cash Month
            cash_month = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.payment_method == 'cash',
                Order.timestamp >= month_start,
                Order.timestamp < month_end
            ).scalar() or 0
            self.update_kpi_card('cash_month', cash_month)
            
            # Card Day
            card_day = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.payment_method == 'card',
                Order.timestamp >= day_start,
                Order.timestamp < day_end
            ).scalar() or 0
            self.update_kpi_card('card_day', card_day)
            
            # Card Week
            card_week = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.payment_method == 'card',
                Order.timestamp >= week_start,
                Order.timestamp < week_end
            ).scalar() or 0
            self.update_kpi_card('card_week', card_week)
            
            # Card Month
            card_month = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.payment_method == 'card',
                Order.timestamp >= month_start,
                Order.timestamp < month_end
            ).scalar() or 0
            self.update_kpi_card('card_month', card_month)
            
            # Revenue Day (all payments)
            revenue_day = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.timestamp >= day_start,
                Order.timestamp < day_end
            ).scalar() or 0
            self.update_kpi_card('revenue_day', revenue_day)
            
            # Revenue Week
            revenue_week = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.timestamp >= week_start,
                Order.timestamp < week_end
            ).scalar() or 0
            self.update_kpi_card('revenue_week', revenue_week)
            
            # Revenue Month
            revenue_month = db.query(func.sum(Order.total)).filter(
                Order.status == 'completed',
                Order.timestamp >= month_start,
                Order.timestamp < month_end
            ).scalar() or 0
            self.update_kpi_card('revenue_month', revenue_month)
            
            # Calculate Net Profit from order items (actual cost vs selling price)
            # Sum of all net_profit fields from order_items for completed orders
            
            # Net Profit Day
            profit_day_query = db.query(func.sum(OrderItem.net_profit)).join(Order).filter(
                Order.status == 'completed',
                Order.timestamp >= day_start,
                Order.timestamp < day_end
            ).scalar() or 0
            # Fallback to old calculation if net_profit not set
            if profit_day_query == 0 and revenue_day > 0:
                profit_day = revenue_day - int(cash_day * 0.02) - int(card_day * 0.025)
            else:
                profit_day = profit_day_query
            self.update_kpi_card('profit_day', profit_day)
            
            # Net Profit Week
            profit_week_query = db.query(func.sum(OrderItem.net_profit)).join(Order).filter(
                Order.status == 'completed',
                Order.timestamp >= week_start,
                Order.timestamp < week_end
            ).scalar() or 0
            if profit_week_query == 0 and revenue_week > 0:
                profit_week = revenue_week - int(cash_week * 0.02) - int(card_week * 0.025)
            else:
                profit_week = profit_week_query
            self.update_kpi_card('profit_week', profit_week)
            
            # Net Profit Month
            profit_month_query = db.query(func.sum(OrderItem.net_profit)).join(Order).filter(
                Order.status == 'completed',
                Order.timestamp >= month_start,
                Order.timestamp < month_end
            ).scalar() or 0
            if profit_month_query == 0 and revenue_month > 0:
                profit_month = revenue_month - int(cash_month * 0.02) - int(card_month * 0.025)
            else:
                profit_month = profit_month_query
            self.update_kpi_card('profit_month', profit_month)
            
        finally:
            db.close()
            
    def update_kpi_card(self, key: str, value_fils: int):
        """Update KPI card with value"""
        if key in self.kpi_cards:
            card = self.kpi_cards[key]
            card.value_label.setText(CurrencyFormatter.format_lyd(value_fils))
