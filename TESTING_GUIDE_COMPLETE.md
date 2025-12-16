# Testing Guide - Complete Flow

## ✅ Setup Complete!

All steps completed:
- ✅ **Step B**: n8n workflow (needs manual check)
- ✅ **Step C**: Oracle enabled for Axpert
- ✅ **Step A**: Queue cleared, submissions reset

---

## 🧪 **Testing Steps**

### **Step 1: Verify n8n Workflow**

1. Open n8n: http://localhost:5678
2. Find the invoice extraction workflow
3. Check:
   - [ ] Workflow is **activated** (toggle in top-right)
   - [ ] Webhook URL is `/webhook/invoice_extract`
   - [ ] No PDF.co node (we don't use it)
   - [ ] Ollama node configured correctly
4. Click "Execute Workflow" to test manually

**Expected**: Workflow executes without errors

---

### **Step 2: Restart Django** (Oracle changes require restart)

```powershell
# In Django terminal (terminal 4):
# Press Ctrl+C to stop, then run:
.\venv\Scripts\python manage.py runserver
```

**Wait for**:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### **Step 3: Login and Navigate**

1. Open browser: http://localhost:8000/
2. Login as finance user
3. Go to Finance Dashboard: http://localhost:8000/finance/dashboard/

**Expected**:
- Dashboard shows statistics
- Supplier Inward: 13 total, 13 pending, 0 approved, 0 rejected
- Direct Purchase: 1 total, 1 pending, 0 approved, 0 rejected

---

### **Step 4: Approve a Submission**

1. Click "Submissions List" or click on "13" in Supplier Inward
2. Find any pending submission
3. Click **✓ Approve** button
4. Submission status changes to "Approved"
5. **Extraction task created automatically!**

**Expected**:
- Message: "Submission approved! Extraction queued automatically."
- Button changes to "✓ Approved - View Queue"

---

### **Step 5: Go to Extraction Queue**

1. Click "✓ Approved - View Queue" button
   OR
2. Go to: http://localhost:8000/finance/extraction_queue/

**Expected**:
- See 1 task with status: **PENDING**
- See blue **"Start Extraction"** button

---

### **Step 6: Start Extraction**

1. Click **"Start Extraction"** button
2. Status changes to **PROCESSING**
3. **Wait 2-3 minutes** (be patient!)

**Watch Django terminal for logs**:
```
📤 Sending [filename] to n8n webhook...
✅ Received response from n8n (status: 200)
📦 n8n response type: <class 'list'>
📄 Raw output from n8n: {...
📄 Cleaned output: {...
✅ Successfully parsed JSON from 'output' field
✅ Enhanced PO Number: ATCPO25080595
🔎 Fetching Axpert data for PO: ATCPO25080595
✅ Axpert data fetched successfully
```

**Expected**:
- Status changes to **COMPLETED**
- Green **"Compare with Axpert"** button appears

---

### **Step 7: Compare with Axpert**

1. Click **"Compare with Axpert"** button (green)
2. Split-screen view loads

**Expected Left Side (PDF)**:
- Original invoice PDF displays
- Scrollable and zoomable

**Expected Right Side (Data)**:

**1. Extracted Invoice Fields**:
- Invoice Number: 0098
- Invoice Date: 2025-08-18
- PO Number: ATCPO25080595 (highlighted yellow)
- Order Number: 0092
- Vendor Name: FAME FOR INTEGRATED PROJECTS SPC
- Customer Name: AL ADRAK TRADING & CONTRACTING LLC.
- Subtotal: 3750.000
- Total: 3937.500 (highlighted yellow)

**2. Axpert Database Information** (Blue box):

**Vendor Information**:
- VENDORID: [number]
- VENDORNAME: FAME FOR INTEGRATED PROJECTS SPC
- CREDITDAYS: [days]
- CURRENCY: AED
- BRANCHNAME: AL ADRAK TRADING & CONTRACTING LLC.
- TRNO: [TRN number]

**Purchase Order Information**:
- POHDRID: [number]
- DOCID: ATCPO25080595
- DOCDT: [date]
- TOTPOVALUE: [amount]
- NETCOSTAMT: [amount]
- PAYTERM: [terms]
- CURRENCY: AED

**3. Invoice Items Table**:
- Item #1: GRANITE SLAB BLACK ABSOLUTE...
- Quantity: 300 SQM
- Unit Price: 12.500
- Amount: 3750.000

**4. Full JSON Data** (Collapsible):
- Click "📋 View Full JSON Data" to expand
- Shows complete extracted data

---

### **Step 8: Send to Axpert**

1. Click **"✓ Send to Axpert"** button (green, top-right)
2. Confirm dialog appears
3. Click "OK"

**Expected**:
- Button changes to "⏳ Sending..."
- After 1.5 seconds: "✅ Data sent to Axpert successfully!"
- Button changes to "✓ Sent to Axpert" (disabled)

**Note**: This is currently a demo. To implement actual Axpert API:
- Create Django view for Axpert submission
- Add URL route
- Update JavaScript to call the view

---

## 🔍 **Troubleshooting**

### **If n8n returns 500 error**:
1. Check n8n workflow is activated
2. Check Ollama is running: http://127.0.0.1:11435/api/tags
3. Test n8n manually in the UI

### **If JSON parsing fails**:
1. Check Django terminal for error details
2. Verify the underscore fix is applied
3. Check n8n output format

### **If Axpert data doesn't show**:
1. Verify Oracle credentials in settings.py
2. Check Django terminal for Oracle connection errors
3. Verify PO number was extracted correctly
4. Check if PO exists in Oracle database

### **If extraction times out**:
1. Wait longer (first extraction can take 3-5 minutes)
2. Check Django terminal for progress
3. Verify Ollama is responding
4. Check n8n logs

---

## 📊 **Success Criteria**

### **✅ Complete Success**:
- [ ] Submission approved
- [ ] Extraction task created automatically
- [ ] Extraction completes without errors
- [ ] Status changes to COMPLETED
- [ ] "Compare with Axpert" button appears
- [ ] Split-screen view loads
- [ ] PDF displays on left
- [ ] Extracted data shows on right
- [ ] Axpert data displays (blue box)
- [ ] Vendor name matches
- [ ] Customer name matches
- [ ] PO details match
- [ ] Invoice items display
- [ ] "Send to Axpert" works

---

## 🚀 **Next Actions After Testing**

### **If Everything Works**:
1. Test with multiple invoices
2. Test different invoice formats
3. Verify data accuracy
4. Implement actual Axpert API integration
5. Add error handling
6. Set up production deployment

### **If Issues Found**:
1. Check Django terminal for errors
2. Check n8n logs
3. Verify Oracle connection
4. Test components individually
5. Share error messages for debugging

---

## 📝 **Quick Commands**

```powershell
# Restart Django (after settings changes)
# Press Ctrl+C, then:
.\venv\Scripts\python manage.py runserver

# Clear queue
.\venv\Scripts\python manage.py clear_extraction_queue --confirm

# Reset submissions
.\venv\Scripts\python manage.py reset_submissions

# Test Ollama
Invoke-WebRequest -Uri "http://127.0.0.1:11435/api/tags" -Method GET

# Test n8n
Invoke-WebRequest -Uri "http://localhost:5678/webhook/invoice_extract" -Method GET
```

---

**Status**: ✅ Ready for testing!  
**Date**: 2025-12-08  
**Next**: Follow the testing steps above!
