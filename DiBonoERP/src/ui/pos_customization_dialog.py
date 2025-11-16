"""
POS Menu Item Customization Dialog
Shows customization options when ordering items that have them
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QRadioButton, QCheckBox, QDialogButtonBox, QGroupBox,
                              QScrollArea, QWidget, QFrame, QButtonGroup)
from PyQt6.QtCore import Qt
from models.database import get_session, MenuItem
from utils.helpers import CurrencyFormatter


class MenuItemCustomizationDialog(QDialog):
    """Dialog for selecting menu item customizations in POS"""
    
    def __init__(self, menu_item_id, parent=None):
        super().__init__(parent)
        self.menu_item_id = menu_item_id
        self.menu_item = None
        self.selected_modifiers = []
        self.total_price_modifier = 0
        
        self.setWindowTitle("تخصيص الطلب")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Load menu item
        db = get_session()
        try:
            self.menu_item = db.query(MenuItem).get(menu_item_id)
            if not self.menu_item:
                raise ValueError("Menu item not found")
        finally:
            db.close()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header with item name
        header = QLabel(f"🍽️ {self.menu_item.name_ar}")
        header.setStyleSheet("font-size: 18pt; font-weight: bold; color: #4ECDC4; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Scroll area for customization groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        # Add each customization group
        self.group_widgets = []
        for group in self.menu_item.customization_groups:
            if not group.active:
                continue
            
            group_widget = self.create_group_widget(group)
            self.group_widgets.append({
                'widget': group_widget,
                'group': group
            })
            content_layout.addWidget(group_widget)
        
        layout.addWidget(scroll)
        
        # Price display frame
        price_frame = QFrame()
        price_frame.setFrameStyle(QFrame.Shape.Box)
        price_frame.setStyleSheet("background-color: #F8F9FA; border: 2px solid #4ECDC4; border-radius: 8px; padding: 15px;")
        price_layout = QHBoxLayout()
        
        price_layout.addWidget(QLabel("💰 السعر الإجمالي:"))
        
        self.price_label = QLabel(CurrencyFormatter.format_lyd(self.menu_item.base_price))
        self.price_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #51CF66;")
        price_layout.addWidget(self.price_label)
        
        price_layout.addStretch()
        price_frame.setLayout(price_layout)
        layout.addWidget(price_frame)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept_order)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("✅ تأكيد")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("❌ إلغاء")
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Set default selections
        self.apply_defaults()
        self.update_price()
    
    def create_group_widget(self, group):
        """Create widget for a customization group"""
        group_box = QGroupBox(group.name_ar)
        group_box.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14pt; }")
        layout = QVBoxLayout()
        
        # Add required indicator
        if group.required:
            required_label = QLabel("⚠️ إلزامي - يجب الاختيار")
            required_label.setStyleSheet("color: #FF6B6B; font-style: italic;")
            layout.addWidget(required_label)
        
        # Create selection widgets based on type
        if group.selection_type == 'single':
            # Radio buttons for single selection
            button_group = QButtonGroup(group_box)
            button_group.setExclusive(True)
            
            for option in group.options:
                if not option.active:
                    continue
                
                # Format label with price modifier
                label_text = option.name_ar
                if option.price_modifier != 0:
                    price_text = CurrencyFormatter.format_lyd(option.price_modifier)
                    if option.price_modifier > 0:
                        label_text += f" (+{price_text})"
                    else:
                        label_text += f" ({price_text})"
                
                radio = QRadioButton(label_text)
                radio.setProperty('option_id', option.id)
                radio.setProperty('option_name_en', option.name_en)
                radio.setProperty('option_name_ar', option.name_ar)
                radio.setProperty('price_modifier', option.price_modifier)
                radio.setProperty('is_default', option.is_default)
                radio.setProperty('group_id', group.id)
                radio.toggled.connect(self.update_price)
                button_group.addButton(radio)
                layout.addWidget(radio)
            
            group_box.setProperty('button_group', button_group)
            group_box.setProperty('selection_type', 'single')
            group_box.setProperty('required', group.required)
        
        else:
            # Checkboxes for multiple selection
            checkboxes = []
            
            for option in group.options:
                if not option.active:
                    continue
                
                # Format label with price modifier
                label_text = option.name_ar
                if option.price_modifier != 0:
                    price_text = CurrencyFormatter.format_lyd(option.price_modifier)
                    if option.price_modifier > 0:
                        label_text += f" (+{price_text})"
                    else:
                        label_text += f" ({price_text})"
                
                checkbox = QCheckBox(label_text)
                checkbox.setProperty('option_id', option.id)
                checkbox.setProperty('option_name_en', option.name_en)
                checkbox.setProperty('option_name_ar', option.name_ar)
                checkbox.setProperty('price_modifier', option.price_modifier)
                checkbox.setProperty('is_default', option.is_default)
                checkbox.setProperty('group_id', group.id)
                checkbox.stateChanged.connect(self.update_price)
                checkboxes.append(checkbox)
                layout.addWidget(checkbox)
            
            group_box.setProperty('checkboxes', checkboxes)
            group_box.setProperty('selection_type', 'multiple')
            group_box.setProperty('required', group.required)
        
        group_box.setLayout(layout)
        return group_box
    
    def apply_defaults(self):
        """Apply default selections"""
        for group_info in self.group_widgets:
            group_widget = group_info['widget']
            
            if group_widget.property('selection_type') == 'single':
                # Radio buttons - select first default or first option
                button_group = group_widget.property('button_group')
                for button in button_group.buttons():
                    if button.property('is_default'):
                        button.setChecked(True)
                        break
                else:
                    # No default - select first option if required
                    if group_widget.property('required') and button_group.buttons():
                        button_group.buttons()[0].setChecked(True)
            
            else:
                # Checkboxes - check all defaults
                checkboxes = group_widget.property('checkboxes')
                for checkbox in checkboxes:
                    if checkbox.property('is_default'):
                        checkbox.setChecked(True)
    
    def update_price(self):
        """Update total price based on selections"""
        total_modifier = 0
        
        for group_info in self.group_widgets:
            group_widget = group_info['widget']
            
            if group_widget.property('selection_type') == 'single':
                # Radio buttons
                button_group = group_widget.property('button_group')
                for button in button_group.buttons():
                    if button.isChecked():
                        total_modifier += button.property('price_modifier')
            
            else:
                # Checkboxes
                checkboxes = group_widget.property('checkboxes')
                for checkbox in checkboxes:
                    if checkbox.isChecked():
                        total_modifier += checkbox.property('price_modifier')
        
        self.total_price_modifier = total_modifier
        final_price = self.menu_item.base_price + total_modifier
        self.price_label.setText(CurrencyFormatter.format_lyd(final_price))
    
    def validate_selections(self):
        """Validate that all required groups have selections"""
        for group_info in self.group_widgets:
            group_widget = group_info['widget']
            
            if not group_widget.property('required'):
                continue
            
            if group_widget.property('selection_type') == 'single':
                # Radio buttons - check if any is selected
                button_group = group_widget.property('button_group')
                if not any(button.isChecked() for button in button_group.buttons()):
                    return False, f"يرجى اختيار أحد الخيارات في: {group_widget.title()}"
            
            else:
                # Checkboxes - check if at least one is selected
                checkboxes = group_widget.property('checkboxes')
                if not any(checkbox.isChecked() for checkbox in checkboxes):
                    return False, f"يرجى اختيار خيار واحد على الأقل في: {group_widget.title()}"
        
        return True, None
    
    def accept_order(self):
        """Validate and accept order with customizations"""
        # Validate required selections
        valid, error_msg = self.validate_selections()
        if not valid:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "اختيارات غير مكتملة", error_msg)
            return
        
        # Collect selected modifiers
        self.selected_modifiers = []
        
        for group_info in self.group_widgets:
            group_widget = group_info['widget']
            
            if group_widget.property('selection_type') == 'single':
                # Radio buttons
                button_group = group_widget.property('button_group')
                for button in button_group.buttons():
                    if button.isChecked():
                        self.selected_modifiers.append({
                            'name_en': button.property('option_name_en'),
                            'name_ar': button.property('option_name_ar'),
                            'price_modifier': button.property('price_modifier')
                        })
            
            else:
                # Checkboxes
                checkboxes = group_widget.property('checkboxes')
                for checkbox in checkboxes:
                    if checkbox.isChecked():
                        self.selected_modifiers.append({
                            'name_en': checkbox.property('option_name_en'),
                            'name_ar': checkbox.property('option_name_ar'),
                            'price_modifier': checkbox.property('price_modifier')
                        })
        
        self.accept()
    
    def get_final_price(self):
        """Get final price with modifiers"""
        return self.menu_item.base_price + self.total_price_modifier
    
    def get_modifiers(self):
        """Get selected modifiers"""
        return self.selected_modifiers
