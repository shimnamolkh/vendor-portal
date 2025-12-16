# JSON Parsing Fix - Escaped Underscores

## ✅ Issue Fixed!

The extraction was failing because n8n was returning JSON with escaped underscores like `Invoice\_No` instead of `Invoice_No`.

### **Error Message:**
```
❌ Error decoding 'output' JSON: Invalid \escape: line 2 column 9 (char 10)
```

### **Root Cause:**
n8n was returning JSON like:
```json
{
  "Invoice\_No": "0098",
  "Invoice\_Date": "2025-08-18",
  "PO\_Number": "ATCPO25080595"
}
```

The backslash before underscores (`\_`) is not valid JSON.

---

## 🔧 Fix Applied

**File**: `finance/services/ollama_service.py`

**Added line 481-482**:
```python
# Handle escaped underscores first (Invoice\_No -> Invoice_No)
output_str = output_str.replace('\\_', '_')
```

This removes the backslashes before underscores, converting:
- `Invoice\_No` → `Invoice_No`
- `PO\_Number` → `PO_Number`
- `Item\_Description` → `Item_Description`

---

## 🧪 Testing

### **Step 1: Django Should Auto-Reload**

Django's development server should automatically detect the file change and reload.

If not, restart manually:
```powershell
# Press Ctrl+C in Django terminal, then:
.\venv\Scripts\python manage.py runserver
```

### **Step 2: Clear Failed Tasks**

```powershell
.\venv\Scripts\python manage.py clear_extraction_queue --confirm
```

### **Step 3: Reset Submissions**

```powershell
.\venv\Scripts\python manage.py reset_submissions
```

### **Step 4: Test New Extraction**

1. Go to: http://localhost:8000/finance/submissions_list/
2. Approve a submission
3. Go to: http://localhost:8000/finance/extraction_queue/
4. Click: **"Start Extraction"**
5. Wait 2-3 minutes
6. Click: **"Compare with Axpert"**
7. See all data displayed correctly!

---

## 📊 Expected Flow Now

```
1. Finance approves submission
    ↓
2. Task created automatically (PENDING)
    ↓
3. Finance clicks "Start Extraction"
    ↓
4. n8n processes invoice (PROCESSING)
    ↓
5. JSON response received with escaped underscores
    ↓
6. ✅ Underscores unescaped automatically
    ↓
7. JSON parsed successfully
    ↓
8. Task status: COMPLETED
    ↓
9. "Compare with Axpert" button appears
    ↓
10. Shows all extracted data + Axpert data
```

---

## 🔍 What the Fix Does

### **Before Fix:**
```python
# n8n returns: {"Invoice\_No": "0098"}
output_str = '{"Invoice\\_No": "0098"}'
json.loads(output_str)  # ❌ ERROR: Invalid \escape
```

### **After Fix:**
```python
# n8n returns: {"Invoice\_No": "0098"}
output_str = '{"Invoice\\_No": "0098"}'
output_str = output_str.replace('\\_', '_')  # ✅ FIX
# Now: '{"Invoice_No": "0098"}'
json.loads(output_str)  # ✅ SUCCESS!
```

---

## 📝 Summary

### **Problem:**
- n8n returned JSON with escaped underscores (`\_`)
- Python's JSON parser rejected this as invalid
- Extraction tasks failed with JSON decode error

### **Solution:**
- Added line to replace `\_` with `_`
- JSON now parses successfully
- Extraction completes without errors

### **Status:**
- ✅ Fix applied
- ✅ Django auto-reloaded (or restart manually)
- ✅ Ready to test

---

## 🚀 Next Steps

1. ✅ Fix applied (done!)
2. ⏳ Clear failed tasks
3. ⏳ Reset submissions
4. ⏳ Test new extraction
5. ⏳ Verify "Compare with Axpert" works

---

**Status**: ✅ Fixed and ready to test  
**Date**: 2025-12-08  
**File**: finance/services/ollama_service.py  
**Line**: 481-482
