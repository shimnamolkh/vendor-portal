# Enhanced Extraction System - Setup Guide

## 🚀 Overview

The enhanced extraction system integrates multiple powerful features:
- **Ollama/n8n** for AI-powered invoice extraction
- **OCR** (Tesseract) for scanned documents and images
- **Intelligent PO Detection** with database prefix lookup
- **VAT/TRN Extraction** from invoices
- **Oracle Axpert Integration** for vendor and PO data validation

---

## 📦 Required Dependencies

### Core Dependencies (Already Installed)
```bash
pip install requests django
```

### Optional Dependencies (Install as needed)

#### 1. PDF Text Extraction
```bash
pip install PyPDF2
```

#### 2. OCR Support (Tesseract)
```bash
# Install Python packages
pip install pytesseract pdf2image pillow

# Install Tesseract OCR executable
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

#### 3. Oracle Database Integration
```bash
pip install oracledb
```

---

## ⚙️ Configuration

Add the following settings to your `vendor_portal/settings.py`:

```python
# ============================================================================
# EXTRACTION SERVICE CONFIGURATION
# ============================================================================

# Ollama Configuration
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'  # Your Ollama server URL
OLLAMA_MODEL = 'llama3.1:latest'  # Or 'llava:7b' for vision model

# n8n Webhook (Optional - if using n8n workflow)
N8N_WEBHOOK_URL = None  # Set to your n8n webhook URL if using n8n
# Example: N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'

# Tesseract OCR Configuration (Optional - for OCR support)
TESSERACT_PATH = None  # Set to Tesseract executable path
# Windows Example: TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Network Path Example: TESSERACT_PATH = r'\\172.16.1.53\C$\Program Files\Tesseract-OCR\tesseract.exe'

# Oracle Database Configuration (Optional - for Axpert integration)
ORACLE_USER = None  # Your Oracle username
ORACLE_PASSWORD = None  # Your Oracle password
ORACLE_DSN = None  # Oracle connection string
# Example: ORACLE_DSN = '172.16.1.85:1521/orcl'
```

---

## 🔧 Feature Configuration

### Mode 1: Basic Extraction (Ollama Only)
**Requirements:** Ollama installed and running
**Configuration:**
```python
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
OLLAMA_MODEL = 'llama3.1:latest'
N8N_WEBHOOK_URL = None
```

**Features:**
- ✅ AI-powered invoice extraction
- ✅ PDF text extraction (PyPDF2)
- ❌ No OCR
- ❌ No PO prefix lookup
- ❌ No Axpert data

---

### Mode 2: Enhanced Extraction (Ollama + OCR)
**Requirements:** Ollama + Tesseract OCR
**Configuration:**
```python
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
OLLAMA_MODEL = 'llama3.1:latest'
N8N_WEBHOOK_URL = None
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Features:**
- ✅ AI-powered invoice extraction
- ✅ PDF text extraction (PyPDF2)
- ✅ OCR for scanned PDFs and images
- ✅ Intelligent PO detection
- ✅ VAT/TRN extraction
- ❌ No PO prefix lookup
- ❌ No Axpert data

---

### Mode 3: Full Integration (Ollama + OCR + Oracle)
**Requirements:** Ollama + Tesseract OCR + Oracle DB access
**Configuration:**
```python
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
OLLAMA_MODEL = 'llama3.1:latest'
N8N_WEBHOOK_URL = None
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
ORACLE_USER = 'ADK2011'
ORACLE_PASSWORD = 'your_password'
ORACLE_DSN = '172.16.1.85:1521/orcl'
```

**Features:**
- ✅ AI-powered invoice extraction
- ✅ PDF text extraction (PyPDF2)
- ✅ OCR for scanned PDFs and images
- ✅ Intelligent PO detection
- ✅ VAT/TRN extraction
- ✅ PO prefix lookup from Oracle DB
- ✅ Axpert vendor and PO data validation

---

### Mode 4: n8n Workflow (Recommended for Production)
**Requirements:** n8n workflow set up
**Configuration:**
```python
N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'
# Optional enhancements
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
ORACLE_USER = 'ADK2011'
ORACLE_PASSWORD = 'your_password'
ORACLE_DSN = '172.16.1.85:1521/orcl'
```

**Features:**
- ✅ n8n workflow for extraction
- ✅ Intelligent PO detection (post-processing)
- ✅ VAT/TRN extraction (post-processing)
- ✅ PO prefix lookup from Oracle DB
- ✅ Axpert vendor and PO data validation

---
   
## 🎯 PO Number Detection Logic

The system uses intelligent PO detection with the following priority:

### 1. Known Prefix Detection
Searches for PO numbers with known prefixes:
```
AVPPO, INAPO, ATCPO, AKJPO, NREPO, ABLPO, TIIPO, KAYPO, KADPO, IECPO,
NRAPO, NRJPO, ARCPO, ADLPO, DXBPO, TFTPO, ACSPO, AIMSPO, AMSPPO, HBSPO,
CEOPO, BPCPO, ITSPO, AACPO, TCPPO, SABPO, CUIPO, KAYAPO, SOBPO, MLTPO,
BTDPO, BTVPO, ARPPO
```

Example: `AVPPO25010001` → Detected ✅

### 2. Prefix Lookup via VAT/TRN
For PO numbers without prefix (8-digit format: YYMMXXXX):
1. Extract VAT/TRN numbers from invoice (format: OM1100020467)
2. Query Oracle database to get branch prefix
3. Combine prefix with PO number

Example:
- Found PO: `25010001`
- Found VAT: `OM1100020467`
- DB Lookup: `OM1100020467` → `AVPPO`
- Final PO: `AVPPO25010001` ✅

### 3. OCR Fallback
If PO not found in extracted JSON:
1. Perform OCR on the invoice
2. Search OCR text for PO patterns
3. Apply same prefix detection logic

---

## 📊 Extracted Data Structure

The enhanced extraction returns:

```json
{
  "Invoice_No": "INV-2025-001",
  "Invoice_Date": "2025-01-15",
  "PO_Number": "AVPPO25010001",  // Enhanced with prefix
  "Order_Number": "ORD-123",
  "Customer_Name": "ABC Company",
  "Customer_RefNo": "CUST-001",
  "LPO_reference": "LPO-456",
  "VATIN": "OM1100020467",
  "CustomerTRN": "OM1100020467",
  "Vendor_Name": "XYZ Supplier",
  "VAT_Percentage": "5",
  "Subtotal": "1000.00",
  "Total": "1050.00",
  "Items": [
    {
      "Item_No": "1",
      "Item_Description": "Product A",
      "Quantity": "10",
      "Unit": "PCS",
      "Unit_Price": "100.00",
      "Amount": "1000.00"
    }
  ],
  "extracted_vat_numbers": ["OM1100020467"],  // Auto-extracted
  "axpert_data": {  // If Oracle configured
    "vendor": {
      "columns": ["VENDORNAME", "CREDITDAYS", "CURRENCY", "BRANCHNAME", "TRNO"],
      "rows": [["XYZ Supplier", 30, "OMR", "Main Branch", "OM1100020467"]]
    },
    "po": {
      "columns": ["DOCID", "DOCDT", "TOTPOVALUE", "NETCOSTAMT", "PAYTERM", "CURRENCY"],
      "rows": [["AVPPO25010001", "2025-01-10", 1050.00, 1000.00, "30 Days", "OMR"]]
    }
  }
}
```

---

## 🧪 Testing

### Test Basic Extraction
1. Upload an invoice through vendor portal
2. Finance team approves it
3. Go to Extraction Queue
4. Click "Start Extraction"
5. View extracted data

### Test OCR (if configured)
Upload a scanned PDF or image invoice to test OCR capabilities.

### Test PO Detection
Upload invoices with:
- PO with known prefix: `AVPPO25010001`
- PO without prefix: `25010001` (requires VAT/TRN in invoice)

### Test Oracle Integration (if configured)
Upload invoice with valid PO number and check if Axpert data is fetched.

---

## 🐛 Troubleshooting

### Issue: "OCR dependencies not installed"
**Solution:** Install OCR packages:
```bash
pip install pytesseract pdf2image pillow
```
And install Tesseract executable.

### Issue: "Oracle DB not configured"
**Solution:** This is informational. Set Oracle credentials in settings.py if you want Axpert integration.

### Issue: "PyPDF2 extraction poor, trying OCR"
**Solution:** This is automatic fallback. Install OCR dependencies for better results.

### Issue: "PO not found"
**Possible causes:**
1. PO format not recognized (add to PO_PREFIXES list)
2. VAT/TRN not found for prefix lookup
3. OCR quality poor

**Solution:** Check extraction logs for details.

---

## 📈 Performance Tips

1. **Use n8n for production** - Better for handling large volumes
2. **Configure OCR only if needed** - Adds processing time
3. **Oracle integration is optional** - Use only if you need Axpert validation
4. **Monitor processing times** - Displayed in extraction queue

---

## 🔒 Security Notes

1. **Never commit credentials** - Keep `.env` file gitignored
2. **Use environment variables** for sensitive data
3. **Restrict Oracle DB access** to read-only if possible
4. **Validate extracted data** before using in production

---

## 📞 Support

For issues or questions:
1. Check the extraction logs in console
2. Review the `ExtractionTask` error_log field
3. Test with sample invoices first
4. Contact development team

---

**Built with ❤️ for efficient invoice processing**
