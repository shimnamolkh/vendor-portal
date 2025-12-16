# New Automated Extraction Workflow

## ✅ Changes Implemented

I've implemented the new automated extraction workflow you requested:

### **Old Flow (Manual)**:
```
1. Finance approves submission
2. Submission appears in "Ready for Extraction" list
3. Finance clicks "Extract" button
4. Extraction starts
5. Results shown
```

### **New Flow (Automated)**:
```
1. Finance approves submission
    ↓
2. Extraction task created AUTOMATICALLY
    ↓
3. Task appears in queue with "Start Extraction" button
    ↓
4. Finance clicks "Start Extraction"
    ↓
5. n8n processes invoice (status: Processing)
    ↓
6. Extraction completes (status: Completed)
    ↓
7. "Compare with Axpert" button appears
    ↓
8. Finance clicks "Compare with Axpert"
    ↓
9. Shows extracted data + Axpert data side by side
```

---

## 🎯 Key Features

### **1. Automatic Task Creation**
- When finance approves a submission → Extraction task is created automatically
- No manual "Extract" button needed on submissions list
- Task appears in Extraction Queue immediately

### **2. Smart Button States**

**Pending Tasks**:
- Show: **"Start Extraction"** button (blue)
- Action: Starts the n8n extraction process

**Processing Tasks**:
- Show: Status badge "PROCESSING"
- No button (processing in progress)

**Completed Tasks**:
- Show: **"Compare with Axpert"** button (green)
- Action: Shows extracted data + Axpert database data

**Failed Tasks**:
- Show: Error message
- No button (needs manual review)

### **3. Compare with Axpert Page**
- Shows all extracted invoice data
- Shows Axpert vendor information (from Oracle)
- Shows Axpert PO information (from Oracle)
- Shows invoice items table
- Shows full JSON data
- Copy/Download buttons

---

## 📁 Files Modified

### **1. finance/views.py**

**approve_submission()** - Auto-creates extraction task:
```python
# Automatically create extraction task
ExtractionTask.objects.create(
    submission=submission,
    status='pending'
)
```

**start_extraction()** - Processes extraction task:
```python
def start_extraction(request, task_id):
    # Get task by ID
    # Update status to 'processing'
    # Process invoice with n8n
    # Update status to 'completed' or 'failed'
```

**compare_with_axpert()** - NEW view:
```python
def compare_with_axpert(request, task_id):
    # Get completed task
    # Show extracted data + Axpert data
```

### **2. finance/urls.py**

Added new URL:
```python
path('extraction/compare/<int:task_id>/', views.compare_with_axpert, name='compare_with_axpert'),
```

Updated start_extraction URL:
```python
# Changed from submission_id to task_id
path('extraction/start/<int:task_id>/', views.start_extraction, name='start_extraction'),
```

### **3. templates/finance/extraction_queue.html**

**Removed**:
- "Ready for Extraction" section (no longer needed)

**Updated**:
- Task buttons based on status:
  - Pending → "Start Extraction"
  - Completed → "Compare with Axpert"

### **4. templates/finance/compare_with_axpert.html**

**Created**: New template (copy of extraction_results.html)
- Shows extracted data
- Shows Axpert vendor info
- Shows Axpert PO info
- Shows invoice items
- Shows full JSON

---

## 🧪 Testing the New Workflow

### **Step 1: Restart Django**

```powershell
# In Django terminal:
# Press Ctrl+C, then:
.\venv\Scripts\python manage.py runserver
```

### **Step 2: Approve a Submission**

1. Login as finance user
2. Go to: http://localhost:8000/finance/submissions_list/
3. Find a pending submission
4. Click: ✓ Approve
5. **Extraction task is created automatically!**

### **Step 3: Go to Extraction Queue**

1. Go to: http://localhost:8000/finance/extraction_queue/
2. See the new task with status: **PENDING**
3. See button: **"Start Extraction"**

### **Step 4: Start Extraction**

1. Click: **"Start Extraction"**
2. Status changes to: **PROCESSING**
3. Wait 2-3 minutes for n8n to process
4. Status changes to: **COMPLETED**
5. Button changes to: **"Compare with Axpert"**

### **Step 5: Compare with Axpert**

1. Click: **"Compare with Axpert"**
2. See beautiful page with:
   - ✅ Extracted invoice data
   - ✅ Axpert vendor information
   - ✅ Axpert PO information
   - ✅ Invoice items table
   - ✅ Full JSON data

---

## 📊 Workflow Diagram

```
┌─────────────────────────────────────┐
│  Finance Approves Submission        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Extraction Task Created (PENDING)  │
│  Status: ⏳ Pending                 │
│  Button: 🔵 Start Extraction        │
└──────────────┬──────────────────────┘
               │
               │ Finance clicks "Start Extraction"
               ▼
┌─────────────────────────────────────┐
│  Task Status: PROCESSING            │
│  Status: ⚙️ Processing              │
│  Button: None (processing...)       │
└──────────────┬──────────────────────┘
               │
               │ n8n completes extraction
               ▼
┌─────────────────────────────────────┐
│  Task Status: COMPLETED             │
│  Status: ✅ Completed               │
│  Button: 🟢 Compare with Axpert     │
└──────────────┬──────────────────────┘
               │
               │ Finance clicks "Compare with Axpert"
               ▼
┌─────────────────────────────────────┐
│  Show Comparison Page               │
│  - Extracted Data                   │
│  - Axpert Vendor Info               │
│  - Axpert PO Info                   │
│  - Invoice Items                    │
│  - Full JSON                        │
└─────────────────────────────────────┘
```

---

## 🎨 Button Colors

- **Start Extraction**: Blue (#3b82f6)
- **Compare with Axpert**: Green (#22c55e)

---

## ⚙️ Configuration

### **Oracle/Axpert Integration**

To enable Axpert data fetching, update `settings.py`:

```python
ORACLE_USER = 'ADK2011'
ORACLE_PASSWORD = 'log'  # Use environment variable in production!
ORACLE_DSN = '172.16.1.85:1521/orcl'
```

Currently set to `None` (disabled).

---

## 🔧 Commands Available

### **Clear Extraction Queue**:
```powershell
.\venv\Scripts\python manage.py clear_extraction_queue --confirm
```

### **Reset Submissions**:
```powershell
.\venv\Scripts\python manage.py reset_submissions
```

---

## 📝 Summary

### **What Changed**:
1. ✅ Extraction starts automatically on approval
2. ✅ No manual "Extract" button on submissions
3. ✅ Smart button states (Start/Compare)
4. ✅ New "Compare with Axpert" page
5. ✅ Cleaner workflow

### **Benefits**:
1. ✅ Less clicks for finance team
2. ✅ Automatic task creation
3. ✅ Clear status indicators
4. ✅ Dedicated comparison page
5. ✅ Better user experience

---

**Status**: ✅ Implemented and ready to test  
**Date**: 2025-12-08  
**Next**: Restart Django and test the new workflow!
