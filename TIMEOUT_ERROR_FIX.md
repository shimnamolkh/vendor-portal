# Timeout Error Fix - n8n Integration

## Problem

You're getting a timeout error in the frontend even though n8n is successfully extracting the data.

### What's Happening:

```
User clicks Extract
    ↓
Django sends PDF to n8n
    ↓
n8n processes (takes time...)
    ↓
Browser times out (30-60 seconds)
    ↓
User sees timeout error
    ↓
n8n finishes and returns data (but too late!)
    ↓
Django might not receive it properly
```

---

## Root Causes

### 1. **Browser Timeout**
- Most browsers timeout after 30-60 seconds
- n8n processing takes longer than this
- User sees error even though processing continues

### 2. **Escaped JSON Format**
Your n8n output has escaped characters:
```json
{\n"Invoice_No": "0098",\n"Invoice_Date": "2025-08-18",...}
```

This needs to be unescaped to:
```json
{
"Invoice_No": "0098",
"Invoice_Date": "2025-08-18",...
}
```

### 3. **Synchronous Processing**
- Django waits for n8n to finish
- User's browser waits for Django
- Long wait = timeout

---

## Solutions Applied

### ✅ Solution 1: Increased Timeout (Immediate Fix)

**File**: `finance/services/ollama_service.py`

**Changed**:
```python
# Before:
response = requests.post(N8N_WEBHOOK_URL, files=files, timeout=120)  # 2 minutes

# After:
response = requests.post(N8N_WEBHOOK_URL, files=files, timeout=300)  # 5 minutes
```

### ✅ Solution 2: Better JSON Parsing

Added code to handle escaped JSON from n8n:

```python
# Handle escaped newlines and quotes
output_str = output_str.replace('\\n', '\n')
output_str = output_str.replace('\\"', '"')
output_str = output_str.replace("\\'", "'")
```

### ✅ Solution 3: Better Error Logging

Added detailed logging to see what's happening:

```python
print(f"📤 Sending {file_path} to n8n webhook...")
print(f"✅ Received response from n8n (status: {response.status_code})")
print(f"📄 Raw output from n8n: {output_str[:200]}...")
print(f"📄 Cleaned output: {output_str[:200]}...")
print(f"✅ Successfully parsed JSON from 'output' field")
```

---

## Testing the Fix

### **Step 1: Restart Django Server**

The code has changed, so restart Django:

```powershell
# In Django terminal:
# Press Ctrl+C, then:
.\venv\Scripts\python manage.py runserver
```

### **Step 2: Test Extract Button**

1. Open: http://localhost:8000/finance/dashboard/
2. Click: "Submissions List"
3. Find: Approved submission
4. Click: **🔍 Extract**
5. **Wait patiently** (may take 2-3 minutes)

### **Step 3: Watch Django Terminal**

You should see detailed logs:

```
📤 Sending [filename] to n8n webhook...
✅ Received response from n8n (status: 200)
📦 n8n response type: <class 'dict'>
📦 n8n response keys: dict_keys(['output'])
📄 Raw output from n8n: {\n"Invoice_No": "0098",\n"Invoice_Date": ...
📄 Cleaned output: {
"Invoice_No": "0098",
"Invoice_Date": ...
✅ Successfully parsed JSON from 'output' field
✅ Final extracted data has 13 fields
✅ Enhanced PO Number: ATCPO25080595
✅ Extracted VAT/TRN: [...]
```

---

## If Browser Still Times Out

The browser might still timeout before Django finishes. Here's what to check:

### **Check Django Terminal After Timeout**

Even if browser shows timeout, check Django terminal. If you see:

```
✅ Successfully parsed JSON from 'output' field
✅ Final extracted data has 13 fields
```

Then the extraction **DID work**, but browser gave up waiting.

### **Solution: Check Extraction Queue**

Even if you see timeout error:

1. Go to: http://localhost:8000/finance/extraction_queue/
2. Look for the extraction task
3. If status is "Completed", the extraction worked!
4. Click "View Details" to see the data

---

## Long-term Solution: Async Processing

For production, implement asynchronous processing:

### **Option 1: Simple Polling**

1. Click Extract → Create task → Return immediately
2. Show "Processing..." message
3. Poll every 5 seconds to check status
4. Show results when complete

### **Option 2: Celery (Professional)**

1. Install Celery
2. Move extraction to background task
3. Use task ID to check status
4. Much better for production

### **Option 3: WebSockets (Real-time)**

1. Use Django Channels
2. Send real-time updates
3. Show progress as it happens
4. Best UX but most complex

---

## Current Workaround

### **For Now:**

1. Click Extract button
2. **Wait 2-3 minutes** (don't close browser)
3. If you see timeout, **don't panic!**
4. Go to Extraction Queue page
5. Check if task completed
6. View extracted data

### **Expected Behavior:**

- ✅ Extraction completes successfully
- ✅ Data is saved to database
- ✅ You can view it in Extraction Queue
- ❌ Browser might show timeout (ignore it)

---

## Verification Steps

After clicking Extract and seeing timeout:

### **Step 1: Check Django Terminal**

Look for:
```
✅ Successfully parsed JSON from 'output' field
✅ Final extracted data has 13 fields
```

If you see this, extraction worked!

### **Step 2: Check Extraction Queue**

1. Go to: http://localhost:8000/finance/extraction_queue/
2. Find the latest task
3. Status should be: ✅ Completed
4. Click "View Details"

### **Step 3: Verify Data**

In the extraction details, you should see:

- ✅ Invoice_No: "0098"
- ✅ Invoice_Date: "2025-08-18"
- ✅ PO_Number: "ATCPO25080595"
- ✅ Vendor_Name: "FAME FOR INTEGRATED PROJECTS SPC"
- ✅ Total: "3937.500"
- ✅ Items array with 1 item

---

## Summary

### **What I Fixed:**

1. ✅ Increased timeout to 5 minutes
2. ✅ Added JSON unescaping for n8n format
3. ✅ Added detailed logging
4. ✅ Better error handling

### **What You Need to Do:**

1. ⏳ Restart Django server
2. ⏳ Test Extract button
3. ⏳ Wait patiently (2-3 minutes)
4. ⏳ Check Extraction Queue if timeout occurs

### **Expected Result:**

- Extraction completes successfully
- Data is saved and visible in Extraction Queue
- Browser might timeout (but data is still saved!)

---

**Status**: ✅ Code fixed, ready to test  
**Date**: 2025-12-08  
**Next**: Restart Django and test with patience!
