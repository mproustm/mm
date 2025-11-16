# DiBono ERP - Inventory-Based Menu System Implementation Plan

## Overview
This document outlines the implementation of a comprehensive inventory-based menu system with:
- Weight-based and count-based servings
- Recipe costing from inventory ingredients
- Alternative ingredients with automatic cost calculation
- Add-ons linked to inventory with stock deduction
- Profit tracking (selling price - recipe cost)

---

## System Architecture

### Data Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    INVENTORY ITEMS                           │
│  - Stored in bulk units (kg, L, pcs, slices)                │
│  - Purchase price per unit (fils)                           │
│  - Current stock (on_hand)                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─────────────────────┐
                   ▼                     ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   RECIPE INGREDIENTS     │  │  ALTERNATIVES & ADD-ONS      │
│  - Small units (g, ml)   │  │  - Small units (g, ml)       │
│  - Auto cost calculation │  │  - Cost difference tracking  │
└──────────┬──────────────┘  └────────┬─────────────────────┘
           │                          │
           └──────────┬───────────────┘
                      ▼
          ┌─────────────────────────┐
          │    MENU ITEM            │
          │  - Base selling price   │
          │  - Calculated cost      │
          │  - Profit margin        │
          └─────────────────────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │    ORDER (POS)          │
          │  - Deduct inventory     │
          │  - Track profit/item    │
          └─────────────────────────┘
```

---

## Database Schema Updates

### Current Models (Already Exist)
✅ `InventoryItem` - Inventory with bulk units (kg, L, pcs)
✅ `MenuItemIngredient` - Recipe ingredients with small units (g, ml)
✅ `MenuItemAlternative` - Alternative ingredients
✅ `MenuItemAddon` - Add-ons
✅ `MenuItem` - Menu items with pricing

### Schema Verification
```python
# InventoryItem
- unit: kg, L, pcs, slices (bulk)
- cost_per_unit: fils per bulk unit
- on_hand: current stock

# MenuItemIngredient  
- quantity: amount in small units
- unit: g, ml, pc, slice
- [AUTO CALC] cost from inventory

# MenuItemAlternative
- replaces_ingredient_id: base ingredient
- inventory_item_id: alternative ingredient
- quantity: amount of alternative
- unit: g, ml, pc, slice
- price_modifier: AUTO CALCULATED (cost difference)

# MenuItemAddon
- inventory_item_id: linked to inventory
- quantity: deducted amount
- unit: g, ml, pc, slice
- price: selling price (entered by admin)
- [AUTO CALC] cost from inventory

# MenuItem
- base_price: selling price (fils) - entered by admin
- recipe_cost: AUTO CALCULATED from ingredients
- [PROFIT] = base_price - recipe_cost
```

---

## Unit Conversion Logic

### Bulk to Small Unit Conversion
```python
def convert_bulk_to_small(inventory_unit, small_unit, quantity):
    """
    Convert bulk inventory units to recipe small units
    
    Examples:
    - 100g from 1kg inventory = 100/1000 = 0.1kg
    - 50ml from 1L inventory = 50/1000 = 0.05L
    - 5pc from 10pcs inventory = 5/10 = 0.5 units
    """
    
    conversions = {
        ('kg', 'g'): 1000,      # 1kg = 1000g
        ('kg', 'kg'): 1,
        ('l', 'ml'): 1000,      # 1L = 1000ml
        ('l', 'l'): 1,
        ('pcs', 'pc'): 1,       # 1:1
        ('slices', 'slice'): 1  # 1:1
    }
    
    key = (inventory_unit.lower(), small_unit.lower())
    ratio = conversions.get(key, 1)
    
    return quantity / ratio  # Returns bulk units to deduct
```

### Cost Calculation
```python
def calculate_ingredient_cost(inventory_item, quantity, unit):
    """
    Calculate cost of recipe ingredient
    
    Example:
    Inventory: Tomato @ 10,000 fils/kg, stock: 50kg
    Recipe: needs 250g
    
    Conversion: 250g = 0.25kg
    Cost: 0.25kg × 10,000 fils/kg = 2,500 fils
    """
    
    # Convert small unit to bulk unit
    bulk_quantity = convert_bulk_to_small(
        inventory_item.unit,  # 'kg'
        unit,                 # 'g'
        quantity              # 250
    )  # Returns 0.25
    
    # Calculate cost
    cost_fils = bulk_quantity * inventory_item.cost_per_unit
    
    return cost_fils
```

---

## Admin Workflow

### Step 1: Basic Information
```
┌────────────────────────────────────────────────────┐
│  التصنيف: [مقبلات ▼]                              │
│  الاسم العربي: [معكرونة بالصلصة الحمراء]          │
│  الاسم الإنجليزي: [Pasta with Red Sauce]         │
│  الوصف (اختياري): [____________________]          │
├────────────────────────────────────────────────────┤
│  نوع الصنف:                                        │
│  ☑ مشروب غازي (يُباع بالوزن من المخزون)          │
│  ☐ طبق عادي (له وصفة مكونات)                     │
│                                                     │
│  IF مشروب غازي:                                    │
│    المخزون المرتبط: [Pepsi 2L ▼]                 │
│    السعر لكل كغ: [3000] فلس                       │
│  ELSE:                                              │
│    ☑ يُباع بالوزن (servings double)              │
│    ☐ يُباع بالقطعة                                │
├────────────────────────────────────────────────────┤
│  [التالي ▶]                                        │
└────────────────────────────────────────────────────┘

Validation:
- التصنيف: required
- الاسم العربي: required
- الاسم الإنجليزي: required
- If مشروب غازي: must select inventory item
```

### Step 2: Recipe & Ingredients
```
┌────────────────────────────────────────────────────┐
│  الصنف: معكرونة بالصلصة الحمراء                   │
├────────────────────────────────────────────────────┤
│  المكونات:                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │ المكون          الكمية    الوحدة    التكلفة │  │
│  ├──────────────────────────────────────────────┤  │
│  │ طماطم           250       غرام      2.500    │  │
│  │ معكرونة         500       غرام      1.200    │  │
│  │ زيت زيتون        50       ملل       0.300    │  │
│  │ بصل             100       غرام      0.150    │  │
│  └──────────────────────────────────────────────┘  │
│  [➕ إضافة مكون]                                  │
├────────────────────────────────────────────────────┤
│  ╔════════════════════════════════════════════════╗│
│  ║  💰 تكلفة الوصفة: 4.150 د.ل                  ║│
│  ║  💵 سعر البيع: [______] فلس  (ادخل السعر)   ║│
│  ║  📊 الربح المتوقع: _____ د.ل (يُحسب تلقائياً)║│
│  ║  📈 هامش الربح: _____ %                       ║│
│  ╚════════════════════════════════════════════════╝│
├────────────────────────────────────────────────────┤
│  [◀ السابق]                         [التالي ▶]  │
└────────────────────────────────────────────────────┘

Auto Calculation Logic:
1. User adds ingredient: طماطم, 250, غرام
2. System finds inventory: Tomato @ 10,000 fils/kg
3. Converts: 250g = 0.25kg
4. Calculates: 0.25 × 10,000 = 2,500 fils
5. Updates تكلفة الوصفة = Σ(all ingredient costs)
6. When user enters سعر البيع: 15,000 fils
7. Calculates profit: 15,000 - 4,150 = 10,850 fils
8. Calculates margin: (10,850 / 15,000) × 100 = 72.3%
```

### Step 3: Alternatives
```
┌────────────────────────────────────────────────────┐
│  الصنف: معكرونة بالصلصة الحمراء                   │
├────────────────────────────────────────────────────┤
│  🔄 البدائل للمكونات:                              │
│  ┌──────────────────────────────────────────────┐  │
│  │ يستبدل      بديل         الكمية   التعديل  │  │
│  ├──────────────────────────────────────────────┤  │
│  │ معكرونة     معكرونة بيني  500غ    +0.000   │  │
│  │             (نفس السعر)                      │  │
│  ├──────────────────────────────────────────────┤  │
│  │ معكرونة     معكرونة كاملة  500غ    +1.500   │  │
│  │             القمح (أغلى)                     │  │
│  ├──────────────────────────────────────────────┤  │
│  │ طماطم       طماطم معلبة    250غ    -0.800   │  │
│  │             (أرخص)                           │  │
│  └──────────────────────────────────────────────┘  │
│  [➕ إضافة بديل]                                  │
├────────────────────────────────────────────────────┤
│  [◀ السابق]                         [التالي ▶]  │
└────────────────────────────────────────────────────┘

Alternative Cost Auto-Calculation:
1. Admin selects:
   - يستبدل: معكرونة (base ingredient)
   - بديل: معكرونة كاملة القمح (alternative)
   - الكمية: 500غ
   
2. System calculates:
   Base cost: 500g regular pasta = 1.200 د.ل
   Alternative cost: 500g whole wheat = 2.700 د.ل
   Difference: 2.700 - 1.200 = +1.500 د.ل
   
3. Auto-fills price_modifier: +1.500 fils
4. Saves to MenuItemAlternative table

Customer Selection Logic:
- Default: عادي (0 modifier) - uses base ingredients
- If selects "معكرونة كاملة القمح": adds +1.500 to total
```

### Step 4: Add-ons
```
┌────────────────────────────────────────────────────┐
│  الصنف: معكرونة بالصلصة الحمراء                   │
├────────────────────────────────────────────────────┤
│  ➕ الإضافات:                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ الإضافة        الكمية   التكلفة   السعر    │  │
│  ├──────────────────────────────────────────────┤  │
│  │ جبنة إضافية    50غ      0.800     [____]   │  │
│  │                                 ↑ ادخل السعر │  │
│  ├──────────────────────────────────────────────┤  │
│  │ صلصة الثوم      30مل     0.200     [____]   │  │
│  ├──────────────────────────────────────────────┤  │
│  │ خضار مشوي      100غ     1.500     [____]   │  │
│  └──────────────────────────────────────────────┘  │
│  [➕ إضافة إضافة]                                 │
├────────────────────────────────────────────────────┤
│  💡 تُخصم الكميات من المخزون عند البيع            │
├────────────────────────────────────────────────────┤
│  [◀ السابق]                         [💾 حفظ]    │
└────────────────────────────────────────────────────┘

Add-on Logic:
1. Admin selects inventory: جبنة موزاريلا
2. Enters quantity: 50, غرام
3. System calculates cost:
   Cheese @ 40,000 fils/kg
   50g = 0.05kg
   Cost = 0.05 × 40,000 = 2,000 fils (0.800 د.ل)
   
4. Admin enters selling price: 1,500 fils (customer pays this)
5. When customer orders:
   - Adds +1.500 fils to total
   - Deducts 0.05kg from cheese inventory
   - Tracks profit: 1,500 - 2,000 = -500 fils (loss on this add-on)
```

---

## POS Customer Flow

### Weight-Based Item (Multiple Orders = Multiply)
```
Customer orders soft drink (weight-based):

Order 1: Pepsi 0.5kg
┌────────────────────────────────────┐
│  🥤 Pepsi                          │
│  الوزن: [0.500] كغ                │
│  السعر: 0.500 × 3,000 = 1.500 د.ل│
│  [✅ إضافة للطلب]                 │
└────────────────────────────────────┘

Inventory: Pepsi -0.5kg

Order 2: Same customer wants more Pepsi 0.3kg
┌────────────────────────────────────┐
│  🥤 Pepsi                          │
│  الوزن: [0.300] كغ                │
│  السعر: 0.300 × 3,000 = 0.900 د.ل│
│  [✅ إضافة للطلب]                 │
└────────────────────────────────────┘

Inventory: Pepsi -0.3kg (additional)

Total in cart:
- Pepsi 0.5kg @ 1.500 د.ل
- Pepsi 0.3kg @ 0.900 د.ل
────────────────────────────
Total: 2.400 د.ل
Total inventory deducted: 0.8kg
```

### Recipe-Based Item with Alternatives & Add-ons
```
Customer orders pasta:

┌────────────────────────────────────────────────┐
│  🍝 معكرونة بالصلصة الحمراء                   │
│  السعر الأساسي: 10.000 د.ل                   │
├────────────────────────────────────────────────┤
│  🔄 اختر نوع المعكرونة:                        │
│  ⦿ عادي (بدون تعديل)           +0.000 د.ل    │
│  ○ معكرونة بيني                 +0.000 د.ل    │
│  ○ معكرونة كاملة القمح           +1.500 د.ل    │
├────────────────────────────────────────────────┤
│  ➕ الإضافات:                                  │
│  ☑ جبنة إضافية                  +1.500 د.ل    │
│  ☐ صلصة الثوم                    +0.750 د.ل    │
│  ☑ خضار مشوي                     +2.000 د.ل    │
├────────────────────────────────────────────────┤
│  ╔════════════════════════════════════════════╗│
│  ║  💵 السعر الأساسي:      10.000 د.ل       ║│
│  ║  🔄 تعديل البديل:       +1.500 د.ل       ║│
│  ║  ➕ الإضافات:            +3.500 د.ل       ║│
│  ║  ──────────────────────────────────────── ║│
│  ║  💰 الإجمالي:            15.000 د.ل       ║│
│  ╚════════════════════════════════════════════╝│
├────────────────────────────────────────────────┤
│  [❌ إلغاء]               [✅ إضافة للطلب]   │
└────────────────────────────────────────────────┘

When customer clicks إضافة للطلب:

Inventory Deductions:
1. Base recipe (with whole wheat alternative):
   - طماطم: -250g
   - معكرونة كاملة القمح: -500g (NOT regular pasta)
   - زيت زيتون: -50ml
   - بصل: -100g

2. Add-ons:
   - جبنة موزاريلا: -50g
   - خضار مشوي: -100g

Cost Calculation:
- Base recipe cost (whole wheat): 4.150 + 1.500 = 5.650 د.ل
- Add-ons cost: 0.800 + 1.500 = 2.300 د.ل
- Total cost: 7.950 د.ل

Revenue: 15.000 د.ل
Profit: 15.000 - 7.950 = 7.050 د.ل
Margin: (7.050 / 15.000) × 100 = 47%
```

---

## Implementation Checklist

### Phase 1: Database & Models ✅
- [x] Verify MenuItemAlternative schema
- [x] Verify MenuItemAddon schema
- [x] Verify MenuItemIngredient schema
- [x] Add auto-calculation fields

### Phase 2: Unit Converter
- [ ] Create UnitConverter class
- [ ] Implement bulk_to_small conversion
- [ ] Implement cost calculation helpers

### Phase 3: Admin UI - Step 1
- [ ] Soft drink checkbox logic
- [ ] Disable/enable controls based on item type
- [ ] Inventory linking for soft drinks

### Phase 4: Admin UI - Step 2
- [ ] Auto-calculate ingredient costs
- [ ] Display running total
- [ ] Selling price input with profit display
- [ ] Real-time profit/margin calculation

### Phase 5: Admin UI - Step 3 (Alternatives)
- [ ] Select base ingredient to replace
- [ ] Select alternative ingredient
- [ ] Auto-calculate cost difference
- [ ] Set price_modifier automatically

### Phase 6: Admin UI - Step 4 (Add-ons)
- [ ] Select inventory item
- [ ] Auto-calculate cost
- [ ] Admin enters selling price
- [ ] Show profit/loss per add-on

### Phase 7: POS Integration
- [ ] Weight-based serving doubling
- [ ] Alternative ingredient replacement
- [ ] Add-on inventory deduction
- [ ] Cost tracking per order item
- [ ] Profit calculation per order

### Phase 8: Reporting
- [ ] Profit per item report
- [ ] Margin analysis
- [ ] Inventory usage by recipe
- [ ] Add-on popularity

---

## Code Snippets

### Auto-Calculate Alternative Cost
```python
def calculate_alternative_modifier(base_ingredient_id, alternative_ingredient_id, quantity, unit):
    """
    Calculate price modifier when replacing base ingredient with alternative
    """
    db = get_session()
    
    # Get base ingredient cost
    base_item = db.query(InventoryItem).get(base_ingredient_id)
    base_cost = calculate_ingredient_cost(base_item, quantity, unit)
    
    # Get alternative ingredient cost
    alt_item = db.query(InventoryItem).get(alternative_ingredient_id)
    alt_cost = calculate_ingredient_cost(alt_item, quantity, unit)
    
    # Calculate difference
    modifier = alt_cost - base_cost  # Can be positive or negative
    
    db.close()
    return modifier
```

### Deduct Inventory on Order
```python
def process_order_inventory_deduction(order_item):
    """
    Deduct inventory when order is completed
    """
    db = get_session()
    
    menu_item = order_item.menu_item
    
    if menu_item.item_type == 'beverage':
        # Direct inventory deduction
        inventory_item = menu_item.linked_inventory
        weight_kg = order_item.weight_kg or 1.0
        inventory_item.on_hand -= weight_kg
    else:
        # Recipe-based deduction
        if order_item.selected_alternative_id:
            # Use alternative ingredient
            alternative = db.query(MenuItemAlternative).get(order_item.selected_alternative_id)
            
            # Deduct alternative instead of base
            bulk_qty = convert_bulk_to_small(
                alternative.inventory_item.unit,
                alternative.unit,
                alternative.quantity
            )
            alternative.inventory_item.on_hand -= bulk_qty
            
            # Deduct other ingredients (not replaced)
            for ingredient in menu_item.ingredients:
                if ingredient.inventory_item_id != alternative.replaces_ingredient_id:
                    bulk_qty = convert_bulk_to_small(
                        ingredient.inventory_item.unit,
                        ingredient.unit,
                        ingredient.quantity
                    )
                    ingredient.inventory_item.on_hand -= bulk_qty
        else:
            # Standard recipe
            for ingredient in menu_item.ingredients:
                bulk_qty = convert_bulk_to_small(
                    ingredient.inventory_item.unit,
                    ingredient.unit,
                    ingredient.quantity
                )
                ingredient.inventory_item.on_hand -= bulk_qty
        
        # Deduct add-ons
        for addon in order_item.addons:
            addon_model = db.query(MenuItemAddon).get(addon.addon_id)
            bulk_qty = convert_bulk_to_small(
                addon_model.inventory_item.unit,
                addon_model.unit,
                addon_model.quantity
            )
            addon_model.inventory_item.on_hand -= bulk_qty
    
    db.commit()
    db.close()
```

---

**Document Status**: Implementation Guide  
**Next Step**: Begin Phase 2 - Unit Converter Implementation
