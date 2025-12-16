# n8n Workflow Fix - Remove PDF.co Dependency

## Problem
Your n8n workflow is trying to use PDF.co API which requires an API key. Since you have Ollama running locally, you don't need PDF.co.

## Solution: Update n8n Workflow to Use Local Tools

### Current Error
```
Authorization failed - please check your credentials
Please provide your API key as "x-api-key" header parameter
```

This means your workflow has a PDF.co node that needs an API key.

---

## Recommended n8n Workflow Structure

### **Workflow Nodes:**

1. **Webhook Trigger** (Already configured)
   - Path: `invoice_extract`
   - Method: POST
   - Response Mode: When Last Node Finishes

2. **Code Node** (Extract PDF Text)
   ```javascript
   // This node extracts text from the PDF file
   const binary = items[0].binary.data;
   const buffer = Buffer.from(binary.data, 'base64');
   
   // Save to temp file
   const fs = require('fs');
   const path = require('path');
   const tempFile = path.join('/tmp', 'invoice_' + Date.now() + '.pdf');
   fs.writeFileSync(tempFile, buffer);
   
   // Extract text using pdf-parse (you may need to install this in n8n)
   const pdfParse = require('pdf-parse');
   const dataBuffer = fs.readFileSync(tempFile);
   const pdfData = await pdfParse(dataBuffer);
   
   return [{
     json: {
       text: pdfData.text,
       pages: pdfData.numpages
     }
   }];
   ```

3. **HTTP Request Node** (Send to Ollama)
   - Method: POST
   - URL: `http://127.0.0.1:11435/api/generate`
   - Headers:
     - Content-Type: `application/json`
   - Body (JSON):
   ```json
   {
     "model": "llama3.1:latest",
     "prompt": "Extract invoice data from the following text and return ONLY a JSON object with these fields: Invoice_No, Invoice_Date, PO_Number, Order_Number, Customer_Name, Customer_RefNo, LPO_reference, VATIN, CustomerTRN, Vendor_Name, VAT_Percentage, Subtotal, Total. Do not include any explanations or markdown.\n\nInvoice text:\n{{ $json.text }}",
     "stream": false,
     "options": {
       "temperature": 0.1
     }
   }
   ```

4. **Code Node** (Parse Ollama Response)
   ```javascript
   const response = items[0].json.response;
   
   // Clean up the response (remove markdown if present)
   let cleaned = response.trim();
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
   const extractedData = JSON.parse(cleaned.trim());
   
   return [{
     json: {
       output: JSON.stringify(extractedData)
     }
   }];
   ```

5. **Respond to Webhook**
   - Return the extracted data

---

## Alternative: Simpler Workflow (If PDF Text Extraction is Complex)

If extracting text from PDF in n8n is too complex, you can:

### **Option A: Let Django Handle PDF Extraction**

Modify the Django code to extract text before sending to n8n:

**Update `finance/services/ollama_service.py`:**

<function_calls>
<invoke name="view_code_item">
<parameter name="File">c:\Users\ITS38\Desktop\vENDORPORTAL\finance\services\ollama_service.py
