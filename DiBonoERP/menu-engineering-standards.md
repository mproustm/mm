# Menu Engineering & Customization UX Standards

## Executive Summary

This document outlines industry-standard practices for implementing menu customization systems, specifically focusing on **alternatives** (ingredient substitutions) and **add-ons** (extra items). Based on UX research principles and analysis of successful food ordering systems, this guide provides comprehensive standards for both customer-facing and administrative interfaces.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [UX Principles for Menu Customization](#ux-principles-for-menu-customization)
3. [Alternatives vs Add-ons: Key Differences](#alternatives-vs-add-ons-key-differences)
4. [Visual Design Standards](#visual-design-standards)
5. [Customer-Facing Interface (POS)](#customer-facing-interface-pos)
6. [Admin Management Interface](#admin-management-interface)
7. [Price Calculation Logic](#price-calculation-logic)
8. [Best Practices & Recommendations](#best-practices--recommendations)
9. [Code Implementation Examples](#code-implementation-examples)

---

## Core Concepts

### Menu Engineering

**Menu Engineering** is a data-driven restaurant management strategy that analyzes menu items based on:
- **Profitability**: Cost vs. selling price
- **Popularity**: Sales frequency and volume
- **Contribution Margin**: Revenue minus food cost
- **Customer Preferences**: Customization patterns and requests

### Alternatives (البدائل)

**Definition**: Substitutions for base ingredients that replace the standard component.

**Characteristics**:
- **Mutually Exclusive**: Customer can only select ONE alternative per item
- **Price Modifier**: Can increase (+) or decrease (-) total price
- **Ingredient Swap**: Replaces a base component (e.g., pasta type, protein choice)
- **Use Cases**: 
  - Dietary restrictions (gluten-free, vegan)
  - Preference variations (whole wheat vs. regular)
  - Premium upgrades (imported cheese vs. local)

**Example**: For a pasta dish, alternatives might be:
- ✅ Standard: Regular pasta (no change)
- 🔄 Penne pasta (+0.500 LYD)
- 🔄 Whole wheat pasta (+1.000 LYD)
- 🔄 Gluten-free pasta (+2.500 LYD)

### Add-ons (الإضافات)

**Definition**: Extra items customers can add to their order for an additional charge.

**Characteristics**:
- **Multi-Select**: Customer can choose multiple add-ons
- **Always Positive Price**: Add-ons increase the total (never negative)
- **Supplementary Items**: Enhance the base dish without replacing anything
- **Use Cases**:
  - Extra portions (double cheese, extra sauce)
  - Side additions (grilled vegetables, extra bread)
  - Premium toppings (truffle oil, imported olives)

**Example**: For a pizza, add-ons might be:
- ➕ Extra mozzarella (+1.500 LYD)
- ➕ Grilled chicken (+3.000 LYD)
- ➕ Fresh basil (+0.500 LYD)
- ➕ Hot chili flakes (+0.250 LYD)

---

## UX Principles for Menu Customization

### 1. **Progressive Disclosure**
Reveal customization options only when relevant. Don't overwhelm customers with all choices upfront.

**✅ Good Practice**:
```
[Menu Item Card] → [Basic Quantity Selection] → [Customization Dialog]
```

**❌ Avoid**:
```
[Menu Item Card with 15 checkboxes and radio buttons visible immediately]
```

### 2. **Clear Visual Hierarchy**

Use distinct visual treatment for different option types:

| Element | Visual Treatment | Purpose |
|---------|------------------|---------|
| **Alternatives** | Radio buttons, Blue theme (#1282A2) | Single selection |
| **Add-ons** | Checkboxes, Green theme (#51CF66) | Multi-selection |
| **Price Changes** | Bold, color-coded (+ green, - red) | Financial clarity |

### 3. **Real-Time Feedback**

Provide immediate price updates as customers make selections.

```
┌─────────────────────────────────────┐
│ 💵 Base Price:        10.000 LYD    │
│ 🔄 Alternative:       +1.500 LYD    │
│ ➕ Add-ons:           +2.250 LYD    │
│ ───────────────────────────────────  │
│ 💰 TOTAL:            13.750 LYD     │
└─────────────────────────────────────┘
```

### 4. **Default Selections**

Always provide a sensible default:
- **Alternatives**: Pre-select "Standard (no modification)"
- **Add-ons**: No pre-selections (opt-in model)
- **Quantity**: Default to 1 or minimum viable quantity

### 5. **Accessibility & Localization**

- **RTL Support**: Arabic interfaces require Right-to-Left layout
- **High Contrast**: Minimum 4.5:1 contrast ratio for text
- **Touch Targets**: Minimum 44x44px for mobile interfaces
- **Clear Labels**: Use icons + text for clarity (🔄 for alternatives, ➕ for add-ons)

---

## Alternatives vs Add-ons: Key Differences

### Comparative Analysis

```
┌──────────────────────┬─────────────────────────┬─────────────────────────┐
│ Aspect               │ Alternatives (البدائل)  │ Add-ons (الإضافات)      │
├──────────────────────┼─────────────────────────┼─────────────────────────┤
│ Selection Type       │ Radio Buttons (Single)  │ Checkboxes (Multiple)   │
│ UI Control           │ QRadioButton            │ QCheckBox               │
│ Default State        │ "Standard" pre-selected │ None selected           │
│ Price Modifier       │ Can be + or -           │ Always positive (+)     │
│ Visual Theme         │ Blue (#1282A2)          │ Green (#51CF66)         │
│ Icon                 │ 🔄                      │ ➕                      │
│ Database Relation    │ MenuItemAlternative     │ MenuItemAddon           │
│ Example Use Cases    │ Pasta type, protein     │ Extra cheese, sauce     │
│ Calculation Logic    │ Base ± modifier         │ Base + all checked      │
└──────────────────────┴─────────────────────────┴─────────────────────────┘
```

### Decision Tree: When to Use Which

```
Is the customer REPLACING a base ingredient?
│
├─ YES → Use ALTERNATIVE
│   │
│   └─ Examples:
│       • Swap regular pasta for whole wheat
│       • Replace beef with chicken
│       • Change cheese type
│
└─ NO → Is the customer ADDING something extra?
    │
    └─ YES → Use ADD-ON
        │
        └─ Examples:
            • Extra toppings
            • Side sauce
            • Additional garnish
```

---

## Visual Design Standards

### Color Palette

```
Primary Colors:
┌───────────────────────────────────────────────────────────┐
│ Alternatives Theme (Blue):                                │
│   Primary:   #1282A2  ████████  (Navigation blue)         │
│   Light:     #E3F2FD  ████████  (Background tint)         │
│   Border:    #B3D9E6  ████████  (Dividers)                │
│                                                             │
│ Add-ons Theme (Green):                                    │
│   Primary:   #51CF66  ████████  (Success green)           │
│   Dark:      #2E7D32  ████████  (Forest green)            │
│   Light:     #F1F8E9  ████████  (Background tint)         │
│   Border:    #A9D5A9  ████████  (Dividers)                │
└───────────────────────────────────────────────────────────┘

Supporting Colors:
  Success:     #51CF66  ████████  (Positive actions)
  Warning:     #FFB020  ████████  (Attention needed)
  Danger:      #E63946  ████████  (Delete/Cancel)
  Info:        #4ECDC4  ████████  (Informational)
  Text:        #495057  ████████  (Body text)
  Background:  #F8F9FA  ████████  (Page background)
```

### Typography

```
┌─────────────────────────────────────────────────────────┐
│ Section Headers:   14pt Bold, Color: Theme Primary     │
│ Item Names:        12pt Semi-bold, Color: #2C3E50      │
│ Prices:            12pt Bold, Color: #51CF66           │
│ Total Price:       16pt Bold, Color: #51CF66           │
│ Hints/Info:        11pt Italic, Color: Theme Primary   │
│ Body Text:         11pt Regular, Color: #495057        │
└─────────────────────────────────────────────────────────┘
```

### Spacing & Layout

```
Card Margins:       15-20px
Section Spacing:    25px between major sections
Item Spacing:       10px between individual options
Border Radius:      8-10px for cards, 5px for inputs
Border Width:       2-3px for emphasis, 1px for subtle
Padding:            12-16px inside cards
Min Touch Target:   44x44px for mobile
```

---

## Customer-Facing Interface (POS)

### UI Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     CUSTOMER ORDER FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: Browse Menu
    │
    ├─ Customer selects menu item
    │
    ▼
Step 2: Customization Dialog Opens
    │
    ├─ Display item name & image
    ├─ Show quantity/weight selector
    │   │
    │   └─ For weight-based items (soft drinks, meat):
    │       • Label: "الوزن" (Weight)
    │       • Unit: "كغ" (kg)
    │       • Decimals: 3
    │   │
    │   └─ For count-based items (pizza, plates):
    │       • Label: "العدد" (Quantity)
    │       • Unit: "قطعة" (piece)
    │       • Decimals: 0
    │
    ▼
Step 3: Select Alternative (Optional)
    │
    ├─ Radio button group with:
    │   • "عادي (بدون تعديل)" [PRE-SELECTED]
    │   • Alternative 1 (+X.XXX د.ل)
    │   • Alternative 2 (+Y.YYY د.ل)
    │   • ...
    │
    ├─ Only ONE can be selected
    ├─ Price updates immediately on selection
    │
    ▼
Step 4: Select Add-ons (Optional)
    │
    ├─ Checkbox group with:
    │   ☐ Add-on 1 (+A.AAA د.ل)
    │   ☐ Add-on 2 (+B.BBB د.ل)
    │   ☐ ...
    │
    ├─ Multiple selections allowed
    ├─ Price updates in real-time
    │
    ▼
Step 5: Review Price Summary
    │
    ├─ Display breakdown:
    │   • Base Price
    │   • Alternative Modifier
    │   • Add-ons Total
    │   • ────────────────
    │   • GRAND TOTAL (highlighted)
    │
    ▼
Step 6: Confirm or Cancel
    │
    ├─ [✅ إضافة للطلب] → Add to cart
    └─ [❌ إلغاء] → Cancel, return to menu
```

### UI Wireframe

```
╔═══════════════════════════════════════════════════════════╗
║                  🍽️ تخصيص الطلب                          ║
║                   (Customize Order)                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  ┌────────────────────────────────────────────────────┐  ║
║  │  🍽️ معكرونة بالصلصة الحمراء                      │  ║
║  │     (Pasta with Red Sauce)                         │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                            ║
║  ┌─ 📏 الكمية ────────────────────────────────────────┐  ║
║  │  العدد:  [▼  1  ▲]  قطعة                          │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                            ║
║  ┌─ 🔄 اختر البديل (Blue #1282A2) ──────────────────┐  ║
║  │  ⦿ عادي (بدون تعديل)              [SELECTED]     │  ║
║  │  ○ معكرونة بيني              +0.500 د.ل          │  ║
║  │  ○ معكرونة كاملة القمح        +1.000 د.ل          │  ║
║  │  ○ معكرونة خالية من الغلوتين  +2.500 د.ل          │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                            ║
║  ┌─ ➕ الإضافات (Green #51CF66) ─────────────────────┐  ║
║  │  ☑ جبنة إضافية               +1.500 د.ل          │  ║
║  │  ☐ صلصة الثوم                 +0.750 د.ل          │  ║
║  │  ☑ خضار مشوي                  +2.000 د.ل          │  ║
║  │  ☐ خبز إضافي                  +0.500 د.ل          │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                            ║
║  ╔══════════════════════════════════════════════════════╗ ║
║  ║  💵 السعر الأساسي:                10.000 د.ل       ║ ║
║  ║  🔄 تعديل البديل:                 +0.000 د.ل       ║ ║
║  ║  ➕ الإضافات:                    +3.500 د.ل       ║ ║
║  ║  ───────────────────────────────────────────────────  ║ ║
║  ║  💰 الإجمالي:                    13.500 د.ل       ║ ║
║  ╚══════════════════════════════════════════════════════╝ ║
║                                                            ║
║  [ ❌ إلغاء ]              [ ✅ إضافة للطلب ]           ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

### Key Design Elements

1. **Header**: Item name in large, bold text with icon
2. **Quantity Card**: Clear labeling based on item type (weight vs count)
3. **Alternatives Section**: 
   - Collapsed/hidden if no alternatives available
   - Blue theme (#1282A2) for visual distinction
   - Radio buttons for mutually exclusive selection
   - Standard option pre-selected
4. **Add-ons Section**:
   - Collapsed/hidden if no add-ons available
   - Green theme (#51CF66) for differentiation
   - Checkboxes for multiple selection
   - None selected by default
5. **Price Summary**: 
   - Always visible
   - Real-time updates
   - Clear breakdown + prominent total
6. **Action Buttons**:
   - Cancel (left/bottom, secondary style)
   - Confirm (right/top, primary style - green success button)

---

## Admin Management Interface

### Multi-Step Wizard Flow

```
┌─────────────────────────────────────────────────────────────┐
│              ADMIN MENU ITEM MANAGEMENT WIZARD               │
└─────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════╗
║  Step Indicator:  [🔵 1] ━━━━ [⚪ 2] ━━━━ [⚪ 3]          ║
╚═══════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────┐
│ STEP 1: Basic Information                                  │
├───────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─ المعلومات الأساسية ──────────────────────────────┐   │
│  │  التصنيف: [مقبلات ▼]                *مطلوب         │   │
│  │  الاسم العربي: [________________]  *مطلوب         │   │
│  │  الاسم الإنجليزي: [________________]  *مطلوب     │   │
│  │  الوصف: [_____________________]                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─ إعدادات المشروب الغازي ────────────────────────────┐   │
│  │  ☑ مشروب غازي                                      │   │
│  │  ☑ يباع بالوزن                                     │   │
│  │  السعر الأساسي: [______] فلس/كغ                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─ التسعير ──────────────────────────────────────────┐   │
│  │  السعر الأساسي: [______] فلس                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  [السابق] ──────────────────────────────── [التالي →]     │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│ STEP 2: Recipe & Ingredients                               │
├───────────────────────────────────────────────────────────┤
│                                                             │
│  Item Name: معكرونة بالصلصة الحمراء (context reminder)    │
│                                                             │
│  ┌─ المكونات والوصفة ────────────────────────────────┐   │
│  │                                                      │   │
│  │  [Scrollable ingredient list]                       │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ طماطم        250 غم     0.500 د.ل          │    │   │
│  │  ├─────────────────────────────────────────────┤    │   │
│  │  │ معكرونة      500 غم     1.200 د.ل          │    │   │
│  │  ├─────────────────────────────────────────────┤    │   │
│  │  │ زيت زيتون     50 مل     0.300 د.ل          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  💰 إجمالي التكلفة: 2.000 د.ل                     │   │
│  │  📊 هامش الربح: 80%                                │   │
│  │                                                      │   │
│  │  [➕ إضافة مكون]                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  [← السابق] ──────────────────────────────── [التالي →]   │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│ STEP 3: Alternatives & Add-ons                             │
├───────────────────────────────────────────────────────────┤
│                                                             │
│  Item Name: معكرونة بالصلصة الحمراء (context reminder)    │
│                                                             │
│  ┌─ 🔄 البدائل المتاحة (Blue Theme #1282A2) ──────────┐   │
│  │  💡 أضف بدائل للمكونات (مثال: بيني بدلاً من         │   │
│  │     معكرونة عادية)                                  │   │
│  │                                                      │   │
│  │  [Scrollable alternatives list]                     │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ معكرونة بيني                                 │    │   │
│  │  │ Modifier: +500 فلس | Order: 1  [🗑️] [↑] [↓]│    │   │
│  │  ├─────────────────────────────────────────────┤    │   │
│  │  │ معكرونة كاملة القمح                          │    │   │
│  │  │ Modifier: +1000 فلس | Order: 2 [🗑️] [↑] [↓]│    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  [➕ إضافة بديل]                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─ ➕ الإضافات المتاحة (Green Theme #51CF66) ────────┐   │
│  │  💡 أضف إضافات يمكن للزبون طلبها مع الصنف           │   │
│  │     (مثال: صوص إضافي، خضار مشوي)                   │   │
│  │                                                      │   │
│  │  [Scrollable add-ons list]                          │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ جبنة إضافية                                   │    │   │
│  │  │ Price: +1500 فلس | Order: 1   [🗑️] [↑] [↓] │    │   │
│  │  ├─────────────────────────────────────────────┤    │   │
│  │  │ صلصة الثوم                                     │    │   │
│  │  │ Price: +750 فلس | Order: 2    [🗑️] [↑] [↓] │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  [➕ إضافة إضافة]                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  [← السابق] ──────────────────────────────── [💾 حفظ]     │
└───────────────────────────────────────────────────────────┘
```

### Design Principles for Admin Interface

1. **Progressive Disclosure**: Multi-step wizard prevents cognitive overload
2. **Contextual Information**: Show item name on steps 2 & 3 for reference
3. **Step Indicators**: Clear visual feedback on current position (🔵 active, ⚪ pending)
4. **Validation Gates**: Can't proceed to next step without required fields
5. **Natural Sizing**: Sections expand based on content (no fixed heights)
6. **Visual Distinction**: 
   - Alternatives use blue theme (#1282A2)
   - Add-ons use green theme (#51CF66)
   - Consistent with customer-facing interface
7. **Inline Editing**: Each alternative/add-on is a separate row with controls
8. **Reordering**: Up/down arrows to control display order
9. **Deletion**: Clear delete button with confirmation

---

## Price Calculation Logic

### Formula Overview

```
FINAL PRICE = BASE_PRICE + ALTERNATIVE_MODIFIER + ADD_ONS_TOTAL

Where:
  BASE_PRICE = {
    if weight-based: base_price_per_kg × weight_kg
    else: base_price_per_unit × quantity
  }
  
  ALTERNATIVE_MODIFIER = {
    if alternative selected:
      if weight-based: modifier_per_kg × weight_kg
      else: modifier_per_unit × quantity
    else: 0
  }
  
  ADD_ONS_TOTAL = Σ(price of each checked add-on)
```

### Calculation Examples

#### Example 1: Count-Based Item (Pizza)

```
Item: Pizza Margherita
Base Price: 15.000 LYD per unit
Customer Selection:
  - Quantity: 2 pizzas
  - Alternative: Whole wheat crust (+1.500 LYD per pizza)
  - Add-ons: 
    • Extra mozzarella (+2.000 LYD total)
    • Grilled vegetables (+3.000 LYD total)

Calculation:
  BASE_PRICE = 15.000 × 2 = 30.000 LYD
  ALTERNATIVE_MODIFIER = 1.500 × 2 = 3.000 LYD
  ADD_ONS_TOTAL = 2.000 + 3.000 = 5.000 LYD
  ─────────────────────────────────────────
  FINAL PRICE = 30.000 + 3.000 + 5.000 = 38.000 LYD
```

#### Example 2: Weight-Based Item (Soft Drink)

```
Item: Cola
Base Price: 3.000 LYD per kg
Customer Selection:
  - Weight: 0.500 kg
  - Alternative: Zero sugar (-0.500 LYD per kg)
  - Add-ons:
    • Ice (+0.250 LYD total)
    • Lemon slice (+0.150 LYD total)

Calculation:
  BASE_PRICE = 3.000 × 0.500 = 1.500 LYD
  ALTERNATIVE_MODIFIER = -0.500 × 0.500 = -0.250 LYD
  ADD_ONS_TOTAL = 0.250 + 0.150 = 0.400 LYD
  ─────────────────────────────────────────
  FINAL PRICE = 1.500 - 0.250 + 0.400 = 1.650 LYD
```

### Implementation Considerations

**Storage Format**: All prices stored in database as **fils (فلس)** (1 LYD = 1000 fils)
- Reason: Avoid floating-point precision errors
- Conversion: `fils_to_lyd = fils / 1000`
- Display: Always show 3 decimal places (e.g., "1.500 د.ل")

**Real-Time Updates**: 
- Connect all input controls (quantity, radio buttons, checkboxes) to `calculate_price()` method
- Use `valueChanged`, `buttonClicked`, `stateChanged` signals
- Update price summary labels immediately

**Validation**:
- Ensure minimum quantity > 0
- Validate alternative selection (only one allowed)
- Verify add-on prices are non-negative
- Check final price doesn't go negative (edge case with large negative modifiers)

---

## Best Practices & Recommendations

### ✅ DO

1. **Provide Clear Defaults**
   - Pre-select "Standard (no modification)" for alternatives
   - Start with minimum quantity (1 or minimum weight)
   - No add-ons selected by default

2. **Use Consistent Visual Language**
   - 🔄 icon for alternatives across all interfaces
   - ➕ icon for add-ons everywhere
   - Blue for alternatives, green for add-ons

3. **Show Price Impact Immediately**
   - Display modifiers next to each option (+X.XXX د.ل)
   - Update total price in real-time
   - Use color coding: green for additions, red for reductions

4. **Optimize for Speed**
   - Most common selections should require fewest clicks
   - Standard option is pre-selected (zero-click default)
   - Large touch targets for mobile (44x44px minimum)

5. **Provide Context**
   - Show item name throughout customization flow
   - Include helpful hints/examples (💡 labels)
   - Display unit labels clearly (قطعة vs كغ)

6. **Enable Easy Correction**
   - Clear "Cancel" button always visible
   - Allow changing selections before confirming
   - Show price breakdown for transparency

7. **Support Accessibility**
   - High contrast text (4.5:1 minimum)
   - Clear focus indicators for keyboard navigation
   - Screen reader compatible (proper ARIA labels)
   - RTL layout for Arabic content

### ❌ DON'T

1. **Don't Mix Control Types**
   - ❌ Never use checkboxes for alternatives (single-select only)
   - ❌ Never use radio buttons for add-ons (multi-select required)

2. **Don't Hide Critical Information**
   - ❌ Don't hide price changes
   - ❌ Don't auto-select expensive add-ons
   - ❌ Don't use vague labels ("Option A", "Extra")

3. **Don't Overwhelm Users**
   - ❌ Avoid showing 20+ alternatives at once
   - ❌ Don't make everything required
   - ❌ Don't use complex pricing formulas without explanation

4. **Don't Ignore Edge Cases**
   - ❌ Handle items with no alternatives/add-ons (hide sections)
   - ❌ Validate negative prices
   - ❌ Test with very large quantities
   - ❌ Consider dietary restrictions (vegan, halal, gluten-free)

5. **Don't Forget Mobile Users**
   - ❌ Tiny touch targets (<40px)
   - ❌ Fixed-width dialogs that don't scale
   - ❌ Horizontal scrolling on small screens

---

## Code Implementation Examples

### Example 1: Customer-Facing Dialog (PyQt6)

```python
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                              QRadioButton, QCheckBox, QButtonGroup, 
                              QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt

class POSItemCustomizeDialog(QDialog):
    """Customer-facing customization dialog"""
    
    def __init__(self, menu_item_id, parent=None):
        super().__init__(parent)
        self.menu_item_id = menu_item_id
        self.setWindowTitle("تخصيص الطلب")
        self.setMinimumWidth(600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # RTL for Arabic
        
        self.init_ui()
        self.load_item()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # === ALTERNATIVES SECTION ===
        self.alternatives_card = QGroupBox("🔄 اختر البديل")
        self.alternatives_card.setStyleSheet("""
            QGroupBox { 
                font-size: 12pt; 
                font-weight: bold;
                color: #1282A2;
                border: 2px solid #1282A2;
                border-radius: 8px;
            }
        """)
        
        alternatives_layout = QVBoxLayout()
        self.alternatives_button_group = QButtonGroup()
        self.alternatives_button_group.buttonClicked.connect(self.calculate_price)
        
        # Standard option (pre-selected)
        standard_radio = QRadioButton("عادي (بدون تعديل)")
        standard_radio.setChecked(True)  # DEFAULT SELECTION
        standard_radio.setProperty("price_modifier", 0)
        self.alternatives_button_group.addButton(standard_radio)
        alternatives_layout.addWidget(standard_radio)
        
        self.alternatives_card.setLayout(alternatives_layout)
        self.alternatives_card.setVisible(False)  # Hide if no alternatives
        layout.addWidget(self.alternatives_card)
        
        # === ADD-ONS SECTION ===
        self.addons_card = QGroupBox("➕ الإضافات")
        self.addons_card.setStyleSheet("""
            QGroupBox { 
                font-size: 12pt; 
                font-weight: bold;
                color: #2E7D32;
                border: 2px solid #51CF66;
                border-radius: 8px;
            }
        """)
        
        addons_layout = QVBoxLayout()
        self.addon_checkboxes = []
        
        self.addons_card.setLayout(addons_layout)
        self.addons_card.setVisible(False)  # Hide if no add-ons
        layout.addWidget(self.addons_card)
        
        # === PRICE SUMMARY ===
        self.total_price_label = QLabel("0.000 د.ل")
        self.total_price_label.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: #51CF66;
        """)
        layout.addWidget(self.total_price_label)
        
        # === ACTION BUTTONS ===
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton("✅ إضافة للطلب")
        add_btn.clicked.connect(self.accept)
        
        layout.addWidget(cancel_btn)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)
    
    def load_item(self):
        """Load alternatives and add-ons from database"""
        # Query MenuItemAlternative and MenuItemAddon models
        # Dynamically create radio buttons and checkboxes
        # Show/hide sections based on availability
        pass
    
    def calculate_price(self):
        """Real-time price calculation"""
        base_price = self.menu_item.base_price * self.quantity
        
        # Alternative modifier (single selection)
        alt_modifier = 0
        selected_btn = self.alternatives_button_group.checkedButton()
        if selected_btn:
            alt_modifier = selected_btn.property("price_modifier") * self.quantity
        
        # Add-ons total (multiple selections)
        addons_total = 0
        for checkbox in self.addon_checkboxes:
            if checkbox.isChecked():
                addons_total += checkbox.property("addon_price")
        
        # Update display
        final_price = base_price + alt_modifier + addons_total
        self.total_price_label.setText(f"{final_price/1000:.3f} د.ل")
```

### Example 2: Admin Management (Step 3 - Alternatives & Add-ons)

```python
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QScrollArea,
                              QPushButton, QLabel)
from PyQt6.QtCore import Qt, QSizePolicy

def create_step3_alternatives_addons(self):
    """Step 3: Alternatives and Add-ons Configuration"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    
    content = QWidget()
    content_layout = QVBoxLayout()
    content_layout.setSpacing(25)
    
    # === ALTERNATIVES SECTION ===
    self.alternatives_card = QGroupBox("🔄 البدائل المتاحة")
    self.alternatives_card.setStyleSheet("""
        QGroupBox {
            font-size: 14pt;
            font-weight: bold;
            color: #1282A2;
            border: 3px solid #1282A2;
            border-radius: 10px;
            background-color: #F8FCFF;
        }
    """)
    
    alternatives_layout = QVBoxLayout()
    
    # Info hint
    info_label = QLabel("💡 أضف بدائل للمكونات (مثال: بيني بدلاً من معكرونة عادية)")
    info_label.setStyleSheet("""
        color: #1282A2;
        font-style: italic;
        font-size: 11pt;
        padding: 10px 15px;
        background-color: #E8F4F8;
        border-radius: 5px;
    """)
    alternatives_layout.addWidget(info_label)
    
    # Scrollable alternatives list
    alternatives_scroll = QScrollArea()
    alternatives_scroll.setWidgetResizable(True)
    alternatives_scroll.setSizePolicy(
        QSizePolicy.Policy.Expanding, 
        QSizePolicy.Policy.MinimumExpanding  # Natural sizing
    )
    
    alternatives_container = QWidget()
    self.alternatives_layout = QVBoxLayout()
    self.alternatives_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    alternatives_container.setLayout(self.alternatives_layout)
    alternatives_scroll.setWidget(alternatives_container)
    
    alternatives_layout.addWidget(alternatives_scroll)
    
    # Add button
    add_alt_btn = QPushButton("➕ إضافة بديل")
    add_alt_btn.setStyleSheet("""
        QPushButton {
            background-color: #1282A2;
            color: white;
            font-size: 13pt;
            font-weight: bold;
            padding: 12px;
            border-radius: 8px;
            min-height: 50px;
        }
        QPushButton:hover {
            background-color: #0D5F7E;
        }
    """)
    add_alt_btn.clicked.connect(self.add_alternative_row)
    alternatives_layout.addWidget(add_alt_btn)
    
    self.alternatives_card.setLayout(alternatives_layout)
    content_layout.addWidget(self.alternatives_card)
    
    # === ADD-ONS SECTION (Similar structure, green theme) ===
    self.addons_card = QGroupBox("➕ الإضافات المتاحة")
    self.addons_card.setStyleSheet("""
        QGroupBox {
            font-size: 14pt;
            font-weight: bold;
            color: #2E7D32;
            border: 3px solid #51CF66;
            border-radius: 10px;
            background-color: #F1F8E9;
        }
    """)
    
    # ... (similar structure to alternatives)
    
    content.setLayout(content_layout)
    scroll.setWidget(content)
    layout.addWidget(scroll)
    widget.setLayout(layout)
    return widget

def add_alternative_row(self):
    """Add new alternative row with controls"""
    row = AlternativeRow()  # Custom widget with name, modifier, order controls
    row.delete_requested.connect(lambda: self.remove_alternative_row(row))
    self.alternatives_layout.addWidget(row)

def add_addon_row(self):
    """Add new add-on row with controls"""
    row = AddonRow()  # Custom widget with name, price, order controls
    row.delete_requested.connect(lambda: self.remove_addon_row(row))
    self.addons_layout.addWidget(row)
```

### Example 3: Alternative Row Widget

```python
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QSpinBox,
                              QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal

class AlternativeRow(QWidget):
    """Single alternative row with inline controls"""
    delete_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Alternative name (Arabic)
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("اسم البديل (عربي)")
        self.name_ar_input.setMinimumWidth(200)
        layout.addWidget(self.name_ar_input)
        
        # Alternative name (English)
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Alternative Name (English)")
        self.name_en_input.setMinimumWidth(200)
        layout.addWidget(self.name_en_input)
        
        # Price modifier label
        modifier_label = QLabel("التعديل (فلس):")
        layout.addWidget(modifier_label)
        
        # Price modifier (can be negative)
        self.price_modifier = QSpinBox()
        self.price_modifier.setRange(-999999, 999999)  # Allow negative
        self.price_modifier.setSingleStep(50)
        self.price_modifier.setValue(0)
        self.price_modifier.setMinimumWidth(120)
        layout.addWidget(self.price_modifier)
        
        # Display order
        order_label = QLabel("الترتيب:")
        layout.addWidget(order_label)
        
        self.display_order = QSpinBox()
        self.display_order.setRange(1, 100)
        self.display_order.setValue(1)
        layout.addWidget(self.display_order)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("حذف البديل")
        delete_btn.setFixedSize(40, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E63946;
                color: white;
                border-radius: 5px;
                font-size: 16pt;
            }
            QPushButton:hover {
                background-color: #C51E2A;
            }
        """)
        delete_btn.clicked.connect(self.delete_requested.emit)
        layout.addWidget(delete_btn)
        
        # Style the row
        self.setStyleSheet("""
            AlternativeRow {
                background-color: white;
                border: 1px solid #B3D9E6;
                border-radius: 5px;
                border-left: 4px solid #1282A2;
            }
        """)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Extract data from controls"""
        return {
            'name_ar': self.name_ar_input.text(),
            'name_en': self.name_en_input.text(),
            'price_modifier': self.price_modifier.value(),
            'display_order': self.display_order.value()
        }
```

### Example 4: Database Models (SQLAlchemy)

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200))
    category_id = Column(Integer, ForeignKey('categories.id'))
    base_price = Column(Integer, nullable=False)  # In fils
    is_weight_based = Column(Boolean, default=False)
    is_soft_drink = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    # Relationships
    alternatives = relationship('MenuItemAlternative', back_populates='menu_item')
    addons = relationship('MenuItemAddon', back_populates='menu_item')

class MenuItemAlternative(Base):
    __tablename__ = 'menu_item_alternatives'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200))
    price_modifier = Column(Integer, default=0)  # Can be negative, in fils
    display_order = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    
    # Relationship
    menu_item = relationship('MenuItem', back_populates='alternatives')

class MenuItemAddon(Base):
    __tablename__ = 'menu_item_addons'
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200))
    price = Column(Integer, nullable=False)  # Always positive, in fils
    display_order = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    
    # Relationship
    menu_item = relationship('MenuItem', back_populates='addons')
```

---

## Summary Checklist

Use this checklist when implementing menu customization:

### Planning Phase
- [ ] Identify which items need alternatives vs add-ons
- [ ] Define price modifiers (can alternatives reduce price?)
- [ ] Determine default selections
- [ ] Plan validation rules
- [ ] Design visual hierarchy (blue for alternatives, green for add-ons)

### Customer Interface
- [ ] Use radio buttons for alternatives (single-select)
- [ ] Use checkboxes for add-ons (multi-select)
- [ ] Pre-select "Standard" alternative by default
- [ ] Show price changes next to each option (+X.XXX د.ل)
- [ ] Implement real-time price calculation
- [ ] Display clear price breakdown
- [ ] Provide cancel and confirm buttons
- [ ] Hide sections if no alternatives/add-ons available
- [ ] Support RTL layout for Arabic
- [ ] Ensure minimum 44x44px touch targets

### Admin Interface
- [ ] Use multi-step wizard to reduce complexity
- [ ] Show contextual information (item name on later steps)
- [ ] Implement step indicators with progress
- [ ] Add validation between steps
- [ ] Provide inline editing for alternatives/add-ons
- [ ] Allow reordering with up/down controls
- [ ] Include delete confirmation
- [ ] Apply consistent color themes (blue/green)
- [ ] Add helpful hints/examples (💡 labels)
- [ ] Enable natural section sizing (no forced heights)

### Data & Logic
- [ ] Store prices in fils (avoid floating-point errors)
- [ ] Allow negative modifiers for alternatives
- [ ] Enforce positive prices for add-ons
- [ ] Handle weight-based vs count-based items correctly
- [ ] Validate minimum quantities
- [ ] Calculate: BASE + ALTERNATIVE_MODIFIER + ADD_ONS_TOTAL
- [ ] Update price in real-time on any change
- [ ] Format display with 3 decimals (X.XXX د.ل)

### Testing
- [ ] Test with items having no alternatives/add-ons
- [ ] Test with many alternatives/add-ons (scrolling)
- [ ] Test negative price modifiers
- [ ] Test weight-based vs count-based calculations
- [ ] Test on mobile devices (touch targets, scrolling)
- [ ] Test RTL layout with Arabic text
- [ ] Test keyboard navigation
- [ ] Test with screen readers (accessibility)

---

## Conclusion

This document provides comprehensive standards for implementing menu customization systems with alternatives and add-ons. Key takeaways:

1. **Alternatives** = Single-select (radio), can modify price +/-, blue theme
2. **Add-ons** = Multi-select (checkboxes), always add cost (+), green theme
3. **Customer Interface** = Simple, clear defaults, real-time pricing
4. **Admin Interface** = Multi-step wizard, visual distinction, inline editing
5. **Pricing** = Store in fils, calculate: BASE + ALT_MODIFIER + ADD_ONS_TOTAL

Following these standards ensures:
- ✅ Consistent user experience
- ✅ Clear financial transparency
- ✅ Efficient admin management
- ✅ Scalable system architecture
- ✅ Accessibility and localization support

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: DiBono ERP Development Team  
**License**: Internal Use Only
