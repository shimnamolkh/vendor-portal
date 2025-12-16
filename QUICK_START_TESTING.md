# Extract Button - Ready to Test! 🚀

## ✅ Configuration Complete

### What's Running:
- ✅ **Django Server**: Port 8000
- ✅ **n8n**: Port 5678 
- ✅ **Ollama**: Port 11435
- ✅ **Webhook**: `http://localhost:5678/webhook/invoice_extract` (verified accessible)

### What Was Fixed:
- ✅ Updated `settings.py` with n8n webhook URL
- ✅ System now posts invoices to n8n instead of using Ollama directly

## 🎯 IMPORTANT: Restart Django Server

⚠️ **CRITICAL STEP**: The Django server MUST be restarted to load the new settings!

### How to Restart:

**Option 1: Quick Restart (Recommended)**
1. Find the terminal running Django (terminal 4 or the most recent one)
2. Press `Ctrl+C` to stop the server
3. Run: `.\venv\Scripts\python manage.py runserver`

**Option 2: Force Restart**
```powershell
# In a new terminal:
# Kill all Django processes
Get-Process python | Where-Object {$_.Path -like "*venv*"} | Stop-Process -Force

# Start fresh
.\venv\Scripts\python manage.py runserver
```

## 🧪 Testing Steps

### 1. Activate n8n Workflow
1. Open: `http://localhost:5678`
2. Go to your workflow (ID: `pfGqXH39THKgNOhu`)
3. **Make sure the toggle switch is ON** (activated)

### 2. Test Extract Button
1. Open: `http://localhost:8000/finance/dashboard/`
2. Click **"Submissions List"** or **"Extraction Queue"**
3. Find an **approved** submission (green ✅ badge)
4. Click the **🔍 Extract** button

### 3. What Should Happen

**In Browser:**
- Page redirects to Extraction Queue
- Success message appears: "Invoice extraction completed successfully!"
- New extraction task appears in the list

**In Django Terminal:**
```
📄 Processing invoice: [filename]
🔄 Using n8n workflow for extraction...
📤 Sending [filename] to n8n webhook...
✅ Enhanced PO Number: [PO]
✅ Extracted VAT/TRN: [VAT numbers]
```

**In n8n:**
- New execution appears in "Executions" tab
- Workflow processes the invoice
- Returns extracted data

## 🔍 Verification

### Check Webhook Connection (Already Done ✅)
```
Webhook URL: http://localhost:5678/webhook/invoice_extract
Status: Accessible and responding
```

### Check Django Settings
```python
# In settings.py (line 148):
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'
```

## 📋 Quick Checklist

Before testing, verify:

- [ ] n8n is running (`http://localhost:5678`)
- [ ] n8n workflow is **ACTIVATED** (toggle ON)
- [ ] Ollama is running (`http://127.0.0.1:11435`)
- [ ] Django server has been **RESTARTED** ⚠️
- [ ] At least one approved submission exists
- [ ] Browser console is open (F12) to see any errors

## 🐛 Troubleshooting

### If Extract button does nothing:
1. **Check browser console (F12)** for JavaScript errors
2. **Restart Django server** (most common issue)
3. **Check n8n workflow is activated**

### If you get "n8n connection error":
1. Verify n8n is running: `http://localhost:5678`
2. Check workflow is activated
3. Verify webhook path in n8n matches: `invoice_extract`

### If extraction fails:
1. Check n8n execution logs
2. Verify Ollama is running
3. Check Ollama model is pulled: `ollama list`

## 📚 Documentation Files

- **EXTRACT_BUTTON_FIX.md** - Detailed explanation of the fix
- **TESTING_GUIDE.md** - Comprehensive testing guide
- **This file** - Quick start guide

## 🎬 Next Steps

1. **Restart Django server** (if not done yet)
2. **Activate n8n workflow**
3. **Test Extract button**
4. **Review extracted data**
5. **Report any issues**

---

**Status**: ✅ Ready to test
**Date**: 2025-12-08
**Issue**: Extract button not posting to n8n
**Solution**: Configured N8N_WEBHOOK_URL in settings.py

## Quick Links

- Django: http://localhost:8000/finance/dashboard/
- n8n: http://localhost:5678
- Workflow: http://localhost:5678/workflow/pfGqXH39THKgNOhu

---

**🚨 REMEMBER**: Restart Django server before testing!
