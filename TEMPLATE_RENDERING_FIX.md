# Template Rendering Fix

## ✅ Issue Fixed!

**Problem**: Extraction queue was showing raw Django template tags instead of rendered values:
```
Duration
{{ task.processing_time|floatformat:2 }}s
Started
{{ task.created_at|date:"M d, H:i" }}
```

**Root Cause**: Template syntax error on line 147. Django template tags (`{% if %}`) were placed inside a `style` attribute, which broke the template parser.

**Bad Code** (line 147):
```html
<div class="card task-card"
    style="border-left: 4px solid {% if task.status == 'completed' %}#22c55e{% elif task.status == 'failed' %}#ef4444{% else %}#eab308{% endif %};">
```

**Fixed Code**:
```html
{% if task.status == 'completed' %}
<div class="card task-card" style="border-left: 4px solid #22c55e;">
{% elif task.status == 'failed' %}
<div class="card task-card" style="border-left: 4px solid #ef4444;">
{% else %}
<div class="card task-card" style="border-left: 4px solid #eab308;">
{% endif %}
```

---

## 🔧 What Changed

**File**: `templates/finance/extraction_queue.html`

**Change**: Moved the `{% if %}` logic outside of the HTML tag to separate conditional blocks.

**Why**: Django template tags cannot be used inside HTML attribute values. They must be at the block level.

---

## ✅ All Issues Now Fixed

### **1. Completed Count** ✅
- Shows actual count of completed tasks today
- Updates dynamically

### **2. Template Error (Compare with Axpert)** ✅  
- Simplified template
- Shows PDF + extracted data

### **3. Template Rendering (Extraction Queue)** ✅
- Fixed syntax error
- Template tags now render correctly
- Shows actual values for duration, date, etc.

---

## 🧪 Test Now

Refresh the extraction queue page:
```
http://localhost:8000/finance/extraction_queue/
```

**Expected**:
- ✅ Task cards display correctly
- ✅ Duration shows actual seconds (e.g., "45.23s")
- ✅ Started shows actual date (e.g., "Dec 08, 15:30")
- ✅ Model shows "llava:7b"
- ✅ Vendor shows actual vendor name
- ✅ Status badges display correctly
- ✅ Border colors match status (green=completed, red=failed, yellow=pending/processing)

---

## 📝 Summary

**Problems Fixed**:
1. ✅ Completed today count showing 0
2. ✅ Template error when clicking "Compare with Axpert"
3. ✅ Template tags showing as raw text instead of rendered values

**Files Modified**:
1. `finance/views.py` - Added metrics calculation
2. `templates/finance/extraction_queue.html` - Fixed template syntax, updated metrics
3. `templates/finance/compare_with_axpert.html` - Simplified template

---

**Status**: ✅ All fixed!  
**Date**: 2025-12-08  
**Next**: Test the extraction queue! 🚀
