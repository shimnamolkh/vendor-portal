# Testing the Extract Button - n8n Integration

## Current Status ✅

### Configuration
- ✅ n8n is running on `http://localhost:5678`
- ✅ Webhook URL configured: `http://localhost:5678/webhook/invoice_extract`
- ✅ Django settings updated with n8n webhook URL
- ✅ Ollama is running on port 11435
- ✅ Django server is running

### Workflow Information
- **Workflow ID**: `pfGqXH39THKgNOhu`
- **Test URL**: `http://localhost:5678/workflow/pfGqXH39THKgNOhu/b8191c`
- **Production Webhook**: `http://localhost:5678/webhook/invoice_extract`

## Testing Steps

### Step 1: Verify n8n Workflow is Active

1. Open n8n in browser: `http://localhost:5678`
2. Navigate to your workflow (ID: `pfGqXH39THKgNOhu`)
3. **IMPORTANT**: Make sure the workflow is **ACTIVATED** (toggle switch in top-right corner should be ON/green)
4. Check the Webhook node settings:
   - Path should be: `invoice_extract`
   - Method should be: `POST`
   - Response mode: `When Last Node Finishes`

### Step 2: Restart Django Server (CRITICAL)

⚠️ **The Django server MUST be restarted to pick up the new N8N_WEBHOOK_URL setting**

You have Django running on terminal 4. To restart:

**Option A: Use the existing terminal**
1. Go to the terminal running Django
2. Press `Ctrl+C` to stop
3. Run: `.\venv\Scripts\python manage.py runserver`

**Option B: Kill and restart from new terminal**
```powershell
# Kill existing Django processes
Get-Process python | Where-Object {$_.CommandLine -like "*manage.py runserver*"} | Stop-Process -Force

# Start fresh
.\venv\Scripts\python manage.py runserver
```

### Step 3: Test the Extract Button

1. **Open Finance Dashboard**
   - URL: `http://localhost:8000/finance/dashboard/`
   - Or: `http://127.0.0.1:8000/finance/dashboard/`

2. **Navigate to Submissions**
   - Click "Submissions List" button, OR
   - Click "Extraction Queue" button

3. **Find an Approved Submission**
   - Look for submissions with status: ✅ Approved
   - These will have the **🔍 Extract** button visible

4. **Click Extract Button**
   - Click the **🔍 Extract** button
   - Watch the browser for redirect
   - Check Django terminal for logs

### Step 4: Monitor the Process

#### In Django Terminal, you should see:
```
📄 Processing invoice: [file_path]
🔄 Using n8n workflow for extraction...
📤 Sending [filename] to n8n webhook...
```

#### In n8n Interface:
- Go to "Executions" tab
- You should see a new execution appear
- Click on it to see the workflow progress
- Check each node for success/failure

#### Expected Success Messages:
```
✅ Enhanced PO Number: [PO_NUMBER]
✅ Extracted VAT/TRN: [VAT_NUMBERS]
✅ Axpert data fetched successfully (if Oracle is configured)
```

### Step 5: Verify Results

After extraction completes:

1. **You'll be redirected to**: Extraction Queue page
2. **Check for**:
   - Success message: "Invoice extraction completed successfully!"
   - New task in "Extraction Tasks" section
   - Task status should be: ✅ Completed

3. **Click "View Details"** on the task to see:
   - Extracted invoice data (JSON)
   - PO Number
   - Invoice Number
   - Total Amount
   - Vendor Name
   - VAT/TRN numbers
   - Axpert data (if configured)

## Troubleshooting

### Issue: "Nothing happens when I click Extract"

**Possible Causes:**
1. Django server not restarted (settings not loaded)
2. n8n workflow not activated
3. JavaScript error in browser

**Solutions:**
1. Restart Django server (see Step 2)
2. Activate n8n workflow
3. Open browser console (F12) and check for errors

### Issue: "Connection refused" or "n8n error"

**Possible Causes:**
1. n8n not running
2. Wrong webhook URL
3. Workflow not activated

**Solutions:**
1. Check n8n is running: `http://localhost:5678`
2. Verify webhook URL in settings.py matches n8n
3. Activate the workflow in n8n

### Issue: "Extraction failed" message

**Possible Causes:**
1. Ollama not running
2. Ollama model not pulled
3. n8n workflow error

**Solutions:**
1. Check Ollama: `http://127.0.0.1:11435`
2. Pull model: `ollama pull llama3.1:latest`
3. Check n8n execution logs for errors

### Issue: "No invoice document found"

**Possible Causes:**
1. Submission doesn't have an invoice document
2. Document type is not set to 'invoice'

**Solutions:**
1. Check the submission has documents
2. Verify document type in database

## Testing Checklist

- [ ] n8n is running on port 5678
- [ ] n8n workflow is activated
- [ ] Webhook path is `invoice_extract`
- [ ] Ollama is running on port 11435
- [ ] Django server has been restarted
- [ ] Settings.py has correct N8N_WEBHOOK_URL
- [ ] At least one approved submission exists
- [ ] Approved submission has invoice document

## Quick Test Command

To quickly test if n8n webhook is accessible:

```powershell
# Test webhook endpoint
Invoke-WebRequest -Uri "http://localhost:5678/webhook/invoice_extract" -Method POST -ContentType "application/json" -Body '{"test": "data"}'
```

Expected: Should return a response (not 404)

## Expected Complete Flow

```
1. User clicks 🔍 Extract button
   ↓
2. Django: start_extraction() view called
   ↓
3. Django: Creates ExtractionTask (status: pending)
   ↓
4. Django: Calls process_invoice(submission)
   ↓
5. Django: Detects N8N_WEBHOOK_URL is set
   ↓
6. Django: Sends invoice PDF to n8n webhook
   ↓
7. n8n: Webhook receives file
   ↓
8. n8n: Processes with Ollama
   ↓
9. n8n: Returns extracted JSON
   ↓
10. Django: Receives JSON response
    ↓
11. Django: Enhances with PO/VAT detection
    ↓
12. Django: Updates ExtractionTask (status: completed)
    ↓
13. Django: Saves extracted_data to database
    ↓
14. Django: Shows success message
    ↓
15. Django: Redirects to Extraction Queue
    ↓
16. User: Sees extraction results
```

## Next Steps After Successful Test

1. ✅ Verify extracted data is accurate
2. ✅ Test with different invoice formats
3. ✅ Configure Oracle integration (optional)
4. ✅ Configure OCR for scanned documents (optional)
5. ✅ Set up production deployment

---

**Created**: 2025-12-08
**Purpose**: Testing Extract button with n8n integration
**Status**: Ready for testing

## Quick Reference

- **Django**: `http://localhost:8000`
- **n8n**: `http://localhost:5678`
- **Ollama**: `http://127.0.0.1:11435`
- **Webhook**: `http://localhost:5678/webhook/invoice_extract`
