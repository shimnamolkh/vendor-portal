# Split-Screen Comparison View

## ✅ New Comparison Screen Created!

I've created a beautiful split-screen comparison view with:

### **Left Side (50%)**:
- 📄 **PDF Viewer** showing the original invoice
- Full-screen embedded PDF viewer
- Scroll and zoom capabilities

### **Right Side (50%)**:
- 🤖 **Extracted Data** in editable fields
- Key invoice fields (Invoice #, Date, PO, Total, etc.)
- 🗄️ **Axpert Database Match** (if available)
- 📦 **Invoice Items** table
- 📋 **Full JSON Data** (collapsible)

### **Top Bar**:
- ← **Back to Queue** button
- ✓ **Send to Axpert** button (green, prominent)

---

## 🎨 Design Features

### **Split Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  📊 Invoice Comparison          [Back] [Send to Axpert] │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│   📄 Original PDF    │   🤖 Extracted Data             │
│                      │                                  │
│   [PDF Viewer]       │   Invoice Number: 0098          │
│                      │   Invoice Date: 2025-08-18      │
│                      │   PO Number: ATCPO25080595      │
│                      │   Total: 3937.500               │
│                      │                                  │
│                      │   🗄️ Axpert Database Match      │
│                      │   [Vendor Info]                 │
│                      │   [PO Info]                     │
│                      │                                  │
│                      │   📦 Invoice Items              │
│                      │   [Items Table]                 │
│                      │                                  │
└──────────────────────┴──────────────────────────────────┘
```

### **Highlighted Fields**:
- **PO Number**: Yellow highlight (important)
- **Total Amount**: Yellow highlight (important)

### **Axpert Section**:
- Orange gradient background
- Shows vendor information
- Shows PO information
- Only appears if Axpert data is available

---

## 🧪 Testing

### **Step 1: Clear and Reset**

```powershell
# Clear failed tasks
.\venv\Scripts\python manage.py clear_extraction_queue --confirm

# Reset submissions
.\venv\Scripts\python manage.py reset_submissions
```

### **Step 2: Test Extraction**

1. Go to: http://localhost:8000/finance/submissions_list/
2. Approve a submission
3. Go to: http://localhost:8000/finance/extraction_queue/
4. Click: **"Start Extraction"** (blue button)
5. Wait 2-3 minutes
6. Click: **"Compare with Axpert"** (green button)

### **Step 3: See Split-Screen View**

You should see:
- ✅ **Left**: PDF of the original invoice
- ✅ **Right**: All extracted data
- ✅ **Top**: "Send to Axpert" button

---

## 🔘 Send to Axpert Button

### **Current Implementation**:
- Shows confirmation dialog
- Changes to "⏳ Sending..."
- Shows success message
- Changes to "✓ Sent to Axpert" (disabled)

### **TODO: Actual Integration**:
The button currently shows a demo. To integrate with actual Axpert system:

1. **Update the `sendToAxpert()` function** in the template
2. **Create a Django view** to handle the API call
3. **Add URL route** for the Axpert submission
4. **Implement Axpert API** integration

Example implementation:
```javascript
function sendToAxpert() {
    fetch('{% url "finance:send_to_axpert" task.id %}', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Data sent to Axpert successfully!');
        } else {
            alert('❌ Error: ' + data.error);
        }
    });
}
```

---

## 📊 Data Flow

```
1. Finance clicks "Compare with Axpert"
    ↓
2. Split-screen view loads
    ↓
3. Left: PDF loads in iframe
    ↓
4. Right: Extracted data displays
    ↓
5. Finance reviews and compares
    ↓
6. Finance clicks "Send to Axpert"
    ↓
7. Confirmation dialog appears
    ↓
8. Data sent to Axpert system
    ↓
9. Success message shown
```

---

## 🎯 Features

### **PDF Viewer**:
- ✅ Full-screen embedded viewer
- ✅ Scroll and zoom
- ✅ Print capability
- ✅ Download option (browser default)

### **Extracted Data**:
- ✅ Read-only input fields
- ✅ Organized in grid layout
- ✅ Highlighted important fields
- ✅ Responsive design

### **Axpert Data**:
- ✅ Conditional display (only if available)
- ✅ Vendor information
- ✅ PO information
- ✅ Distinct visual styling

### **Invoice Items**:
- ✅ Table format
- ✅ All item details
- ✅ Scrollable if many items

### **JSON Data**:
- ✅ Collapsible section
- ✅ Full raw data
- ✅ Syntax highlighted
- ✅ Copy-friendly

---

## 🔧 Customization

### **To Change PDF Viewer Size**:
Edit the flex values in the template:
```html
<!-- Make PDF 60%, Data 40% -->
<div style="flex: 1.5;">  <!-- PDF side -->
<div style="flex: 1;">    <!-- Data side -->
```

### **To Add More Fields**:
Add to the grid in the template:
```html
<div class="data-field">
    <label>Field Name</label>
    <input type="text" value="{{ extracted_data.FieldName }}" readonly>
</div>
```

### **To Change Colors**:
Update the CSS variables:
```css
.highlight-field {
    background: #your-color;
    border-color: #your-border-color;
}
```

---

## 📝 Summary

### **Created**:
- ✅ Split-screen comparison view
- ✅ PDF viewer on left
- ✅ Extracted data on right
- ✅ "Send to Axpert" button
- ✅ Axpert data display
- ✅ Invoice items table
- ✅ JSON data viewer

### **Features**:
- ✅ Side-by-side comparison
- ✅ Highlighted important fields
- ✅ Responsive layout
- ✅ Professional design
- ✅ Ready for Axpert integration

### **Next Steps**:
1. ⏳ Test the new view
2. ⏳ Implement actual Axpert API
3. ⏳ Add validation if needed
4. ⏳ Add edit capability if needed

---

**Status**: ✅ Created and ready to test  
**Date**: 2025-12-08  
**File**: templates/finance/compare_with_axpert.html  
**Next**: Test the split-screen view!
