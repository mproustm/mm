"""
Unit Conversion Utilities
Handles conversions between different measurement units for recipe ingredients
"""

class UnitConverter:
    """Handles unit conversions for recipe management"""
    
    # Weight conversions (base unit: grams)
    WEIGHT_UNITS = {
        'g': 1.0,
        'gram': 1.0,
        'غرام': 1.0,
        'kg': 1000.0,
        'كجم': 1000.0,
        'kilogram': 1000.0,
        'mg': 0.001,
        'ملغ': 0.001,
        'milligram': 0.001,
    }
    
    # Volume conversions (base unit: milliliters)
    VOLUME_UNITS = {
        'ml': 1.0,
        'milliliter': 1.0,
        'ملل': 1.0,
        'l': 1000.0,
        'liter': 1000.0,
        'لتر': 1000.0,
        'cl': 10.0,
        'centiliter': 10.0,
    }
    
    @classmethod
    def convert_weight(cls, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert weight between units
        
        Args:
            value: The quantity to convert
            from_unit: Source unit (g, kg, mg)
            to_unit: Target unit (g, kg, mg)
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If units are not recognized or not compatible
        """
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # Check if units are weight units
        if from_unit_lower not in cls.WEIGHT_UNITS:
            raise ValueError(f"Unknown weight unit: {from_unit}")
        if to_unit_lower not in cls.WEIGHT_UNITS:
            raise ValueError(f"Unknown weight unit: {to_unit}")
        
        # Convert to base unit (grams) then to target unit
        value_in_grams = value * cls.WEIGHT_UNITS[from_unit_lower]
        result = value_in_grams / cls.WEIGHT_UNITS[to_unit_lower]
        
        return result
    
    @classmethod
    def convert_volume(cls, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert volume between units
        
        Args:
            value: The quantity to convert
            from_unit: Source unit (ml, l)
            to_unit: Target unit (ml, l)
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If units are not recognized or not compatible
        """
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # Check if units are volume units
        if from_unit_lower not in cls.VOLUME_UNITS:
            raise ValueError(f"Unknown volume unit: {from_unit}")
        if to_unit_lower not in cls.VOLUME_UNITS:
            raise ValueError(f"Unknown volume unit: {to_unit}")
        
        # Convert to base unit (milliliters) then to target unit
        value_in_ml = value * cls.VOLUME_UNITS[from_unit_lower]
        result = value_in_ml / cls.VOLUME_UNITS[to_unit_lower]
        
        return result
    
    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        """
        Auto-detect and convert between compatible units
        
        Args:
            value: The quantity to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If units are incompatible or not recognized
        """
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # If units are the same, no conversion needed
        if from_unit_lower == to_unit_lower:
            return value
        
        # Check if both are weight units
        if from_unit_lower in cls.WEIGHT_UNITS and to_unit_lower in cls.WEIGHT_UNITS:
            return cls.convert_weight(value, from_unit, to_unit)
        
        # Check if both are volume units
        if from_unit_lower in cls.VOLUME_UNITS and to_unit_lower in cls.VOLUME_UNITS:
            return cls.convert_volume(value, from_unit, to_unit)
        
        # Units are incompatible (e.g., trying to convert weight to volume)
        raise ValueError(f"Cannot convert between incompatible units: {from_unit} and {to_unit}")
    
    @classmethod
    def is_weight_unit(cls, unit: str) -> bool:
        """Check if a unit is a weight unit"""
        return unit.lower().strip() in cls.WEIGHT_UNITS
    
    @classmethod
    def is_volume_unit(cls, unit: str) -> bool:
        """Check if a unit is a volume unit"""
        return unit.lower().strip() in cls.VOLUME_UNITS
    
    @classmethod
    def get_base_unit(cls, unit: str) -> str:
        """Get the base unit for a given unit (g for weight, ml for volume)"""
        unit_lower = unit.lower().strip()
        
        if unit_lower in cls.WEIGHT_UNITS:
            return 'g'
        elif unit_lower in cls.VOLUME_UNITS:
            return 'ml'
        else:
            return unit  # Return as-is if not recognized
    
    @classmethod
    def normalize_unit(cls, value: float, unit: str) -> tuple[float, str]:
        """
        Convert to the most appropriate unit for display
        For example: 1500g -> (1.5, 'kg'), 250ml -> (0.25, 'l')
        
        Args:
            value: The quantity
            unit: Current unit
            
        Returns:
            Tuple of (normalized_value, normalized_unit)
        """
        unit_lower = unit.lower().strip()
        
        # Weight normalization
        if unit_lower in cls.WEIGHT_UNITS:
            value_in_grams = value * cls.WEIGHT_UNITS[unit_lower]
            
            if value_in_grams >= 1000:
                return (value_in_grams / 1000, 'kg')
            elif value_in_grams < 1:
                return (value_in_grams * 1000, 'mg')
            else:
                return (value_in_grams, 'g')
        
        # Volume normalization
        if unit_lower in cls.VOLUME_UNITS:
            value_in_ml = value * cls.VOLUME_UNITS[unit_lower]
            
            if value_in_ml >= 1000:
                return (value_in_ml / 1000, 'l')
            else:
                return (value_in_ml, 'ml')
        
        # Unknown unit - return as-is
        return (value, unit)


# Helper functions for common conversions
def kg_to_g(kg: float) -> float:
    """Convert kilograms to grams"""
    return UnitConverter.convert_weight(kg, 'kg', 'g')

def g_to_kg(g: float) -> float:
    """Convert grams to kilograms"""
    return UnitConverter.convert_weight(g, 'g', 'kg')

def g_to_mg(g: float) -> float:
    """Convert grams to milligrams"""
    return UnitConverter.convert_weight(g, 'g', 'mg')

def mg_to_g(mg: float) -> float:
    """Convert milligrams to grams"""
    return UnitConverter.convert_weight(mg, 'mg', 'g')

def liter_to_ml(liter: float) -> float:
    """Convert liters to milliliters"""
    return UnitConverter.convert_volume(liter, 'l', 'ml')

def ml_to_liter(ml: float) -> float:
    """Convert milliliters to liters"""
    return UnitConverter.convert_volume(ml, 'ml', 'l')


def convert_recipe_to_inventory_units(recipe_quantity: float, recipe_unit: str, inventory_unit: str) -> float:
    """
    Convert recipe small units (g, ml) to inventory bulk units (kg, l)
    
    Example:
        convert_recipe_to_inventory_units(250, 'g', 'kg') -> 0.25
        convert_recipe_to_inventory_units(50, 'ml', 'l') -> 0.05
        convert_recipe_to_inventory_units(5, 'pc', 'pcs') -> 5.0
    
    Args:
        recipe_quantity: Amount in recipe (small units)
        recipe_unit: Recipe unit (g, ml, pc, slice)
        inventory_unit: Inventory bulk unit (kg, l, pcs, slices)
    
    Returns:
        Quantity in inventory bulk units (to deduct from stock)
    """
    recipe_unit_lower = recipe_unit.lower().strip()
    inventory_unit_lower = inventory_unit.lower().strip()
    
    # Weight conversions
    if recipe_unit_lower in UnitConverter.WEIGHT_UNITS and inventory_unit_lower in UnitConverter.WEIGHT_UNITS:
        return UnitConverter.convert_weight(recipe_quantity, recipe_unit, inventory_unit)
    
    # Volume conversions
    if recipe_unit_lower in UnitConverter.VOLUME_UNITS and inventory_unit_lower in UnitConverter.VOLUME_UNITS:
        return UnitConverter.convert_volume(recipe_quantity, recipe_unit, inventory_unit)
    
    # Piece/count units (1:1 ratio)
    piece_units = ['pc', 'piece', 'pcs', 'pieces', 'قطعة', 'قطع']
    slice_units = ['slice', 'slices', 'شريحة', 'شرائح']
    
    if recipe_unit_lower in piece_units and inventory_unit_lower in piece_units:
        return recipe_quantity  # 1:1
    
    if recipe_unit_lower in slice_units and inventory_unit_lower in slice_units:
        return recipe_quantity  # 1:1
    
    # If no conversion available, assume 1:1 ratio
    return recipe_quantity


def calculate_ingredient_cost(inventory_item, recipe_quantity: float, recipe_unit: str) -> int:
    """
    Calculate cost of recipe ingredient based on inventory item
    
    Example:
        Inventory: Tomato @ 10,000 fils/kg, stock: 50kg
        Recipe: needs 250g
        
        Conversion: 250g = 0.25kg
        Cost: 0.25kg × 10,000 fils/kg = 2,500 fils
    
    Args:
        inventory_item: InventoryItem instance
        recipe_quantity: Amount needed in recipe
        recipe_unit: Recipe unit (g, ml, pc)
    
    Returns:
        Cost in fils (integer)
    """
    # Convert recipe unit to inventory bulk unit
    bulk_quantity = convert_recipe_to_inventory_units(
        recipe_quantity,
        recipe_unit,
        inventory_item.unit
    )
    
    # Calculate cost
    cost_fils = int(bulk_quantity * inventory_item.cost_per_unit)
    
    return cost_fils


def calculate_alternative_cost_modifier(base_ingredient, alternative_ingredient, 
                                        quantity: float, unit: str) -> int:
    """
    Calculate price modifier when replacing base ingredient with alternative
    
    Args:
        base_ingredient: Base InventoryItem
        alternative_ingredient: Alternative InventoryItem
        quantity: Amount to use
        unit: Unit of measurement
    
    Returns:
        Price modifier in fils (can be positive or negative)
    """
    base_cost = calculate_ingredient_cost(base_ingredient, quantity, unit)
    alternative_cost = calculate_ingredient_cost(alternative_ingredient, quantity, unit)
    
    # Difference (can be positive if alternative is more expensive, negative if cheaper)
    modifier = alternative_cost - base_cost
    
    return modifier
