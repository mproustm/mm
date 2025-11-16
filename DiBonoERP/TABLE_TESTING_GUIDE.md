# Table Management Testing Guide

## ✅ Completed Implementation

### 1. **Table-Shaped Buttons** ✅
- Custom `TableButton` widget draws a realistic table shape
- Rounded rectangle top with 4 legs
- Color-coded by status:
  - **Green** = Available (متاحة)
  - **Red** = Occupied (مشغولة)
  - **Orange** = Reserved (محجوزة)
- Shows table number, capacity, and status

### 2. **Auto-Save/Restore Orders** ✅
- **No confirmation dialogs** - seamless workflow
- When selecting a table:
  - If table has a held order → Automatically restores items
  - If table is new → Marks as occupied, starts fresh order
- When clicking "العودة للطاولات":
  - Automatically saves order to database
  - Keeps table marked as occupied
  - Clears items from memory

### 3. **Occupied Table Status** ✅
- Tables with held orders show as "مشغولة" (red)
- Clicking an occupied table resumes the order
- Table stays occupied until payment is completed
- After payment → Table released and becomes available (green)

### 4. **Workflow Changes** ✅
- Removed all confirmation dialogs for table selection
- Orders persist automatically when switching between tables
- "استرجاع" button only for manually held orders (not table-linked)

## Testing Steps

### Test 1: New Table Order
1. Login as employee (ahmed/123456)
2. Click POS from menu
3. See table-shaped buttons in grid
4. Click any green (available) table
5. ✅ Table should turn red immediately
6. ✅ No confirmation dialog - goes straight to ordering screen
7. Add some items to order
8. Click "العودة للطاولات"
9. ✅ Returns to table selection without asking
10. ✅ Table still shows as red (مشغولة)

### Test 2: Resume Occupied Table
1. From table selection screen
2. Click the red (occupied) table from Test 1
3. ✅ No confirmation dialog
4. ✅ Order items automatically restored
5. ✅ Can continue adding items or make payment

### Test 3: Complete Order and Release Table
1. With an order active
2. Click "دفع نقدي" or "دفع بالبطاقة"
3. Complete payment
4. ✅ Returns to table selection
5. ✅ Table now shows as green (available) again

### Test 4: Multiple Tables
1. Select table 1, add items, go back
2. Select table 2, add items, go back
3. Select table 3, add items, go back
4. ✅ All 3 tables should show as red (occupied)
5. Click table 1 → ✅ Sees table 1's order
6. Click table 2 → ✅ Sees table 2's order
7. Click table 3 → ✅ Sees table 3's order

### Test 5: Takeaway Orders
1. Click "🥡 طلب توصيل" button
2. Add items
3. Complete payment
4. ✅ No table involved
5. ✅ Works independently of table system

### Test 6: Empty Order Go Back
1. Select a table
2. Don't add any items
3. Click "العودة للطاولات"
4. ✅ Table released (becomes green)
5. ✅ No held order created

## Visual Verification

### Table Button Appearance
```
┌─────────────────┐
│  4 أشخاص        │  ← Capacity
│                 │
│       5         │  ← Table Number (large)
│                 │
│    متاحة        │  ← Status
└─────────────────┘
  │         │
  │         │       ← Table legs
```

### Color Scheme
- **Available**: Light green (#90EE90) with dark green border
- **Occupied**: Crimson red (#DC143C) with dark red border
- **Reserved**: Orange (#FFA500) with dark orange border
- **Hover**: Blue border (#1282A2)

## Database Structure

### HeldOrder Table
```sql
- id
- employee_id
- table_id (links to table)
- order_type (dine-in/takeaway)
- items_json (order items)
- subtotal
- held_at
- expires_at (4 hours)
```

### Logic Flow
```
1. Select Table
   ↓
2. Check for held_order with table_id
   ↓
   YES → Restore items, delete held_order
   NO → Mark table occupied
   ↓
3. Add items to order
   ↓
4. Go back OR Complete payment
   ↓
   Go Back → Create/Update held_order, keep table occupied
   Payment → Complete order, release table
```

## Key Files Modified

1. **src/ui/table_button.py** (NEW)
   - Custom QPushButton with table shape drawing

2. **src/ui/table_selection.py**
   - Uses TableButton instead of QPushButton
   - Checks for held orders to show occupied status
   - Removed confirmation dialogs

3. **src/ui/pos_interface.py**
   - Auto-restores orders when selecting occupied table
   - Auto-saves orders when going back
   - Only releases table on payment completion

## Known Behaviors

✅ **Expected**: Table stays red (occupied) until payment is made
✅ **Expected**: No confirmation dialogs for seamless workflow
✅ **Expected**: Orders automatically save/restore when switching tables
✅ **Expected**: Can work on multiple table orders simultaneously

## Success Criteria

- [x] Tables drawn as table shapes (not rectangles)
- [x] No "موافق" confirmation when selecting tables
- [x] Orders persist when switching between tables
- [x] Tables show "مشغولة" when they have orders
- [x] Clicking occupied tables resumes orders automatically
- [x] Tables released only when payment completed
- [x] Multiple tables can have active orders simultaneously
