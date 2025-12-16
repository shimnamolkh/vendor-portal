# Extract Button Fix - n8n Integration

## Problem
When clicking the **Extract** button on approved inward entries, nothing was happening because the system was not configured to send invoices to the n8n workflow.

## Solution Applied
Updated `vendor_portal/settings.py` to enable n8n webhook integration:

```python
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'
```

## How It Works Now

### When you click "Extract" on an approved submission:

1. **Django View** (`finance/views.py` - `start_extraction()`)
   - Creates an `ExtractionTask` record
   - Calls `process_invoice(submission)`

2. **Invoice Processing** (`finance/services/ollama_service.py` - `process_invoice()`)
   - Gets the invoice document from the submission
   - Checks if `N8N_WEBHOOK_URL` is configured
   - **Sends the invoice PDF to n8n webhook** via HTTP POST

3. **n8n Workflow** (Your n8n instance)
   - Receives the invoice file at webhook endpoint
   - Processes it using Ollama/LLM
   - Returns extracted JSON data

4. **Django Saves Results**
   - Receives JSON response from n8n
   - Enhances data with:
     - PO number detection
     - VAT/TRN extraction
     - Oracle Axpert database lookup (if configured)
   - Saves to `ExtractionTask.extracted_data`
   - Redirects to Extraction Queue page

## Next Steps

### 1. Verify n8n Webhook Configuration

Your n8n workflow must have a webhook trigger configured at:
```
http://localhost:5678/webhook/invoice_extract
```

**To check/configure in n8n:**
1. Open n8n at `http://localhost:5678`
2. Open your invoice extraction workflow
3. Check the Webhook node settings:
   - **Webhook Name**: `invoice_extract`
   - **HTTP Method**: `POST`
   - **Response Mode**: `When Last Node Finishes`
   - **Response Data**: `First Entry JSON`

### 2. Test the Integration

1. **Restart Django Server** (the settings change requires restart):
   ```powershell
   # Stop the current server (Ctrl+C in the terminal)
   # Then restart:
   .\venv\Scripts\python manage.py runserver
   ```

2. **Test with an approved submission**:
   - Go to Finance Dashboard
   - Click on "Submissions List"
   - Find an approved submission
   - Click the **🔍 Extract** button
   - You should see the invoice being sent to n8n

### 3. Monitor the Process

**Check Django logs** for:
```
📤 Sending [filename] to n8n webhook...
✅ Enhanced PO Number: [PO]
✅ Extracted VAT/TRN: [VAT numbers]
```

**Check n8n logs** for:
- Webhook received
- Ollama processing
- Response sent back

### 4. Troubleshooting

#### If you get "n8n connection error":
- Verify n8n is running: `http://localhost:5678`
- Check the webhook URL in n8n matches: `/webhook/invoice_extract`
- Ensure the workflow is **activated** (toggle in n8n)

#### If extraction fails:
- Check n8n workflow logs for errors
- Verify Ollama is running on port 11435
- Check that the Ollama model is pulled: `llama3.1:latest`

#### If webhook URL is different:
Update the URL in `settings.py`:
```python
N8N_WEBHOOK_URL = 'http://your-n8n-host:port/webhook/your-webhook-name'
```

## What Changed in the Code

### Before:
```python
N8N_WEBHOOK_URL = None  # System used Ollama directly
```

### After:
```python
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'  # System posts to n8n
```

### Code Flow (ollama_service.py):
```python
def process_invoice(submission):
    # ...
    if N8N_WEBHOOK_URL:  # ✅ Now TRUE
        print("🔄 Using n8n workflow for extraction...")
        result = extract_invoice_via_n8n(file_path)  # Sends to n8n
    else:
        print("🔄 Using Ollama direct extraction...")
        result = extract_invoice_via_ollama(invoice_text)  # Direct Ollama
    # ...
```

## Expected Behavior

When you click **Extract** on an approved submission:

1. ✅ Button click triggers `start_extraction` view
2. ✅ Invoice PDF is sent to n8n webhook
3. ✅ n8n processes with Ollama
4. ✅ Extracted data is returned to Django
5. ✅ Data is enhanced with PO/VAT detection
6. ✅ Results are saved to database
7. ✅ You're redirected to Extraction Queue
8. ✅ Success message is displayed

## Files Modified

- `vendor_portal/settings.py` - Enabled n8n webhook URL

## Files Involved (No Changes)

- `finance/views.py` - Contains `start_extraction()` view
- `finance/services/ollama_service.py` - Contains extraction logic
- `templates/finance/submissions_list.html` - Contains Extract button
- `templates/finance/extraction_queue.html` - Shows extraction results

---

**Created**: 2025-12-08
**Issue**: Extract button not posting to n8n workflow
**Status**: ✅ FIXED - Ready for testing
