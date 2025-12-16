# n8n Test Webhook Configuration - FINAL FIX

## ✅ Configuration Updated

I've updated the settings to use your working test webhook URL:

```python
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook-test/invoice_extract'
```

---

## ⚠️ IMPORTANT: Activate n8n Workflow First!

The webhook endpoint won't work until you **activate and execute** the workflow in n8n.

### **Error Message Explained:**
```
"The requested webhook 'invoice_extract' is not registered."
"Hint: Click the 'Execute workflow' button"
```

This means the n8n workflow needs to be activated/executed first.

---

## 🎯 Steps to Make It Work

### **Step 1: Activate n8n Workflow**

1. **Open n8n**: http://localhost:5678
2. **Go to your workflow** (ID: `pfGqXH39THKgNOhu`)
3. **Click the toggle switch** in the top-right to **ACTIVATE** the workflow (should turn green/ON)
4. **OR Click "Execute Workflow"** button to test it

### **Step 2: Verify Webhook is Registered**

After activating, the webhook should be registered at:
- **Test URL**: `http://localhost:5678/webhook-test/invoice_extract`
- **Production URL**: `http://localhost:5678/webhook/invoice_extract`

### **Step 3: Restart Django Server**

Since we updated the settings, restart Django:

1. Go to Django terminal (terminal 3 or 4)
2. Press `Ctrl+C`
3. Run: `.\venv\Scripts\python manage.py runserver`

### **Step 4: Test Extract Button**

1. Open: http://localhost:8000/finance/dashboard/
2. Click "Submissions List"
3. Find an **approved** submission
4. Click **🔍 Extract**

---

## 📊 Expected Flow

```
User clicks Extract
    ↓
Django sends invoice PDF to:
http://localhost:5678/webhook-test/invoice_extract
    ↓
n8n receives file
    ↓
n8n processes with workflow
    ↓
n8n returns extracted JSON
    ↓
Django saves results
    ↓
User sees extraction results
```

---

## 🔍 Webhook URL Differences

### **Test URL** (What you're using now):
```
http://localhost:5678/webhook-test/invoice_extract
```
- Used for testing workflows
- Available when workflow is in test mode
- Good for development

### **Production URL** (For later):
```
http://localhost:5678/webhook/invoice_extract
```
- Used when workflow is activated
- Available 24/7 once workflow is active
- Good for production

---

## 🐛 Troubleshooting

### Issue: "Webhook not registered"

**Cause**: Workflow not activated in n8n

**Solution**:
1. Open n8n: http://localhost:5678
2. Open your workflow
3. Click **"Activate"** toggle (top-right)
4. OR click **"Execute Workflow"** button

### Issue: "PDF.co authorization error"

**Cause**: Workflow still using PDF.co node

**Solutions**:
1. **Option A**: Remove PDF.co node from workflow
2. **Option B**: Add PDF.co API key to workflow
3. **Option C**: Use Ollama directly (set `N8N_WEBHOOK_URL = None`)

### Issue: Extract button does nothing

**Cause**: Django server not restarted

**Solution**: Restart Django server (Ctrl+C, then run again)

---

## 📋 Quick Checklist

Before testing:

- [ ] n8n workflow is **ACTIVATED** (toggle ON)
- [ ] Webhook is registered (no "not registered" error)
- [ ] Django server has been **RESTARTED**
- [ ] Ollama is running (http://127.0.0.1:11435)
- [ ] At least one approved submission exists

---

## 🎬 Testing Steps

### **1. Activate Workflow in n8n**
```
1. Open: http://localhost:5678
2. Go to workflow: pfGqXH39THKgNOhu
3. Click "Activate" toggle (top-right)
4. Verify it's ON/green
```

### **2. Test Webhook (Optional)**
```powershell
# Test if webhook is now registered
Invoke-WebRequest -Uri "http://localhost:5678/webhook-test/invoice_extract" -Method POST
```

Expected: Should NOT return "webhook not registered" error

### **3. Restart Django**
```powershell
# In Django terminal:
# Press Ctrl+C, then:
.\venv\Scripts\python manage.py runserver
```

### **4. Test Extract Button**
```
1. Open: http://localhost:8000/finance/dashboard/
2. Click "Submissions List"
3. Find approved submission
4. Click 🔍 Extract
5. Watch for success!
```

---

## 📝 What to Watch For

### **In Django Terminal:**
```
📄 Processing invoice: [filename]
🔄 Using n8n workflow for extraction...
📤 Sending [filename] to n8n webhook...
✅ Enhanced PO Number: [PO]
✅ Extracted VAT/TRN: [VAT numbers]
```

### **In n8n Interface:**
- Go to "Executions" tab
- New execution should appear
- Click to see workflow progress
- Check for success/failure

### **In Browser:**
- Redirects to Extraction Queue
- Success message appears
- New extraction task visible
- Status: ✅ Completed

---

## 🔄 If You Need to Switch Back to Ollama Direct

If n8n workflow has issues, you can always switch back:

**File**: `vendor_portal/settings.py`
```python
# Disable n8n, use Ollama directly
N8N_WEBHOOK_URL = None
```

Then restart Django server.

---

## 📚 Current Configuration

**Settings File**: `vendor_portal/settings.py`

```python
# n8n webhook (ENABLED)
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook-test/invoice_extract'

# Ollama (fallback if n8n fails)
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
OLLAMA_MODEL = 'llava:7b'
```

---

## 🚀 Next Steps

1. **Activate n8n workflow** (most important!)
2. **Restart Django server**
3. **Test Extract button**
4. **Check results**
5. **Report any issues**

---

## 💡 Pro Tips

### **For Development:**
- Use test webhook: `/webhook-test/invoice_extract`
- Keep workflow in test mode
- Easy to debug and modify

### **For Production:**
- Switch to production webhook: `/webhook/invoice_extract`
- Activate workflow permanently
- More stable and reliable

### **To Switch to Production URL Later:**
```python
# In settings.py:
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'
```

---

**Status**: ✅ Configured with test webhook  
**Date**: 2025-12-08  
**Webhook**: `http://localhost:5678/webhook-test/invoice_extract`  
**Next**: Activate n8n workflow and restart Django!

---

## 🎯 Summary

1. ✅ Settings updated with test webhook URL
2. ⏳ Need to activate n8n workflow
3. ⏳ Need to restart Django server
4. ⏳ Ready to test Extract button

**Action Required**: Activate workflow in n8n, then restart Django!
