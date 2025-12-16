# PDF.co API Error - Solution Guide

## Error Message
```
Authorization failed - please check your credentials
Please provide your API key as "x-api-key" header parameter for GET or POST request
```

## Root Cause
Your n8n workflow is using PDF.co service for PDF processing, but the API key is not configured.

---

## 🎯 Recommended Solution: Use Ollama Directly (No PDF.co Needed)

Since you already have Ollama running locally, you don't need PDF.co. Here's how to fix your n8n workflow:

### **Simple n8n Workflow (Without PDF.co)**

#### **Node 1: Webhook Trigger**
- **Name**: Webhook
- **Path**: `invoice_extract`
- **HTTP Method**: POST
- **Response Mode**: When Last Node Finishes
- **Response Data**: First Entry JSON

#### **Node 2: Extract Text from PDF**
Use the **"Execute Command"** node or **"Code"** node:

**Option A: Using Execute Command Node**
```bash
# Install pdftotext if not already installed
# This extracts text from PDF without external APIs

pdftotext {{ $binary.data }} -
```

**Option B: Using Code Node (JavaScript)**
```javascript
// Extract text from PDF using pdf-parse
const binary = $input.item.binary.data;
const buffer = Buffer.from(binary.data, 'base64');

// You may need to install pdf-parse in n8n
// Or use a simpler approach: just pass the file to Ollama

return {
  json: {
    filename: $input.item.binary.data.fileName,
    fileData: binary.data  // Base64 encoded PDF
  }
};
```

#### **Node 3: HTTP Request to Ollama**
- **Method**: POST
- **URL**: `http://127.0.0.1:11435/api/generate`
- **Headers**:
  - `Content-Type`: `application/json`
- **Body** (JSON):
```json
{
  "model": "llama3.1:latest",
  "prompt": "You are given invoice data. Extract and output ONLY a valid JSON object with these fields: Invoice_No, Invoice_Date (YYYY-MM-DD), PO_Number, Order_Number, Customer_Name, Customer_RefNo, LPO_reference, VATIN, CustomerTRN, Vendor_Name, VAT_Percentage, Subtotal, Total. Do not include markdown, comments, or explanations. If a field is missing, use empty string.\n\nInvoice data:\n{{ $json.text }}",
  "stream": false,
  "options": {
    "temperature": 0.1,
    "top_p": 0.9
  }
}
```

#### **Node 4: Parse Response**
Use **Code Node**:
```javascript
// Get Ollama response
const ollamaResponse = $input.item.json.response;

// Clean up markdown if present
let cleaned = ollamaResponse.trim();
if (cleaned.startsWith('```json')) {
  cleaned = cleaned.substring(7);
}
if (cleaned.startsWith('```')) {
  cleaned = cleaned.substring(3);
}
if (cleaned.endsWith('```')) {
  cleaned = cleaned.substring(0, cleaned.length - 3);
}

// Parse JSON
try {
  const extractedData = JSON.parse(cleaned.trim());
  
  return {
    json: {
      output: JSON.stringify(extractedData)
    }
  };
} catch (error) {
  return {
    json: {
      error: 'Failed to parse JSON',
      raw_response: ollamaResponse
    }
  };
}
```

#### **Node 5: Respond to Webhook**
- **Response Code**: 200
- **Response Body**: `{{ $json }}`

---

## 🔧 Alternative Solution: Simplify by Letting Django Handle Everything

If configuring n8n is complex, you can disable n8n and let Django use Ollama directly.

### **Update Django Settings**

**File**: `vendor_portal/settings.py`

```python
# Disable n8n, use Ollama directly
N8N_WEBHOOK_URL = None  # Set back to None

# Ollama will be used automatically
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
OLLAMA_MODEL = 'llama3.1:latest'
```

### **How It Works**

When `N8N_WEBHOOK_URL` is `None`, the system automatically uses Ollama directly:

```python
# In ollama_service.py - process_invoice()
if N8N_WEBHOOK_URL:
    # Use n8n workflow
    result = extract_invoice_via_n8n(file_path)
else:
    # Use Ollama directly (THIS WILL BE USED)
    invoice_text = extract_text_from_pdf(file_path)
    result = extract_invoice_via_ollama(invoice_text)
```

**Advantages:**
- ✅ No n8n configuration needed
- ✅ No PDF.co API key needed
- ✅ Simpler architecture
- ✅ Works immediately

**Disadvantages:**
- ❌ Slower (synchronous processing)
- ❌ No workflow visualization
- ❌ Less flexible

---

## 🎬 Quick Fix: Disable n8n Temporarily

To test if the system works without n8n:

1. **Update settings.py**:
```python
N8N_WEBHOOK_URL = None
```

2. **Restart Django server**:
```powershell
# Press Ctrl+C in Django terminal, then:
.\venv\Scripts\python manage.py runserver
```

3. **Test Extract button**:
- Go to Finance Dashboard
- Click Extract on an approved submission
- System will use Ollama directly

4. **Check Django terminal** for:
```
📄 Processing invoice: [filename]
🔄 Using Ollama direct extraction...
✅ Enhanced PO Number: [PO]
```

---

## 📋 Decision Matrix

### **Use n8n if:**
- ✅ You want workflow visualization
- ✅ You need async processing
- ✅ You want to customize the workflow easily
- ✅ You're willing to configure the workflow

### **Use Ollama directly if:**
- ✅ You want simplicity
- ✅ You don't need workflow visualization
- ✅ Synchronous processing is acceptable
- ✅ You want it to work immediately

---

## 🚀 Recommended Next Steps

### **Option 1: Quick Test (Recommended)**
1. Set `N8N_WEBHOOK_URL = None` in settings.py
2. Restart Django server
3. Test Extract button
4. Verify it works with Ollama directly
5. Decide if you need n8n later

### **Option 2: Fix n8n Workflow**
1. Open n8n: `http://localhost:5678`
2. Edit your workflow
3. Remove PDF.co nodes
4. Add Ollama HTTP Request node
5. Test the workflow
6. Keep `N8N_WEBHOOK_URL` configured

### **Option 3: Get PDF.co API Key**
1. Go to: https://app.pdf.co/account
2. Sign up and get API key
3. Add to n8n workflow credentials
4. Keep current workflow

---

## 🔍 Testing Commands

### Test Ollama Directly
```powershell
# Test if Ollama is working
Invoke-WebRequest -Uri "http://127.0.0.1:11435/api/generate" -Method POST -ContentType "application/json" -Body '{"model":"llama3.1:latest","prompt":"Hello","stream":false}'
```

### Test n8n Webhook
```powershell
# Test if n8n webhook is accessible
Invoke-WebRequest -Uri "http://localhost:5678/webhook/invoice_extract" -Method POST
```

---

## 📝 Summary

**Current Issue**: n8n workflow requires PDF.co API key

**Best Solution**: Use Ollama directly (set `N8N_WEBHOOK_URL = None`)

**Why**: 
- Simpler
- No external dependencies
- Works immediately
- You already have Ollama running

**When to use n8n**:
- When you need async processing
- When you want workflow visualization
- When you have complex processing logic

---

**Created**: 2025-12-08  
**Issue**: PDF.co authorization error in n8n  
**Status**: Solutions provided - choose one approach
