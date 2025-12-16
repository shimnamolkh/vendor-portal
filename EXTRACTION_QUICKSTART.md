# 🚀 Quick Start Guide - Enhanced Extraction System

## Overview
Your vendor portal now has **advanced invoice extraction** with intelligent PO detection, VAT/TRN extraction, and Oracle database integration!

---

## ✅ What's New

### 1. **Intelligent PO Number Detection**
- Automatically detects PO numbers with or without prefixes
- Supports 33 different PO prefixes (AVPPO, INAPO, ATCPO, etc.)
- Falls back to OCR if not found in extracted data
- **Database Prefix Lookup**: Queries Oracle DB to get correct prefix based on VAT/TRN

### 2. **VAT/TRN Extraction**
- Automatically extracts all VAT/TRN numbers from invoices
- Format: OM followed by 10 digits (e.g., OM1100020467)
- Used for PO prefix lookup

### 3. **OCR Fallback**
- If text extraction fails, automatically uses OCR
- Supports both PDFs and images
- Improves accuracy for scanned documents

### 4. **Oracle Axpert Integration**
- Fetches vendor information from Oracle database
- Retrieves PO details for validation
- Displays in beautiful tables on extraction view

---

## 🎯 How to Use

### Step 1: Configure (One-Time Setup)

Edit `vendor_portal/settings.py` and add:

```python
# Basic Configuration (Required)
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
OLLAMA_MODEL = 'llama3.1:latest'

# Optional: n8n Webhook
N8N_WEBHOOK_URL = None  # Or your n8n webhook URL

# Optional: OCR Support
TESSERACT_PATH = None  # Or path to tesseract.exe

# Optional: Oracle Database
ORACLE_USER = None  # Your Oracle username
ORACLE_PASSWORD = None  # Your Oracle password
ORACLE_DSN = None  # e.g., '172.16.1.85:1521/orcl'
```

### Step 2: Install Dependencies (Optional)

```bash
# For OCR support
pip install pytesseract pdf2image pillow

# For Oracle integration
pip install oracledb

# For better PDF extraction
pip install PyPDF2
```

### Step 3: Use the System

1. **Vendor uploads invoice** → Vendor Dashboard
2. **Finance approves submission** → Finance Dashboard
3. **Go to Extraction Queue** → Click "Extraction Queue" button
4. **Start extraction** → Click "Start Extraction" on any approved submission
5. **View results** → Click "View Data" on completed tasks

---

## 📊 What You'll See

### Extraction Results Page Shows:

#### 1. **Key Metrics Cards**
- 📦 PO Number (with auto-detected prefix)
- 📄 Invoice Number
- 💰 Total Amount
- 🏢 Vendor Name

#### 2. **VAT/TRN Numbers**
- All extracted VAT/TRN numbers in highlighted badges
- Used for PO prefix lookup

#### 3. **Axpert Database Validation** (if Oracle configured)
- **Vendor Information Table**:
  - Vendor Name, Credit Days, Currency, Branch, TRN
- **Purchase Order Table**:
  - PO Number, Date, Total Value, Net Cost, Payment Terms, Currency

#### 4. **Full JSON Data**
- Complete extraction in formatted JSON
- Copy to clipboard
- Download as JSON file
- Download Axpert data as Excel/CSV

---

## 🔍 PO Detection Examples

### Example 1: PO with Known Prefix
**Invoice contains:** `AVPPO25010001`
**Result:** ✅ Detected immediately as `AVPPO25010001`

### Example 2: PO without Prefix
**Invoice contains:** 
- PO: `25010001`
- VAT: `OM1100020467`

**Process:**
1. Detects 8-digit PO: `25010001`
2. Extracts VAT: `OM1100020467`
3. Queries Oracle: `OM1100020467` → `AVPPO`
4. **Result:** ✅ `AVPPO25010001`

### Example 3: OCR Fallback
**Scenario:** Scanned PDF, text extraction fails
**Process:**
1. PyPDF2 extraction returns poor results
2. Automatically triggers OCR
3. Searches OCR text for PO patterns
4. **Result:** ✅ PO found via OCR

---

## 🎨 Feature Modes

### Mode 1: Basic (No Extra Setup)
- ✅ AI extraction via Ollama
- ✅ Basic PO detection
- ❌ No OCR
- ❌ No DB prefix lookup
- ❌ No Axpert data

### Mode 2: Enhanced (+ OCR)
- ✅ AI extraction via Ollama
- ✅ Advanced PO detection
- ✅ OCR for scanned documents
- ❌ No DB prefix lookup
- ❌ No Axpert data

### Mode 3: Full (+ Oracle)
- ✅ AI extraction via Ollama
- ✅ Advanced PO detection
- ✅ OCR for scanned documents
- ✅ DB prefix lookup
- ✅ Axpert vendor/PO validation

---

## 🐛 Troubleshooting

### Issue: "OCR dependencies not installed"
**Solution:**
```bash
pip install pytesseract pdf2image pillow
```
Then set `TESSERACT_PATH` in settings.py

### Issue: "Oracle DB not configured"
**This is informational**, not an error. Set Oracle credentials if you want Axpert integration.

### Issue: PO not detected
**Check:**
1. Is PO in a recognized format? (8 digits: YYMMXXXX)
2. Is VAT/TRN present in invoice?
3. Check extraction logs for details

### Issue: Extraction taking too long
**Possible causes:**
- OCR processing (can take 10-30 seconds for multi-page PDFs)
- Ollama model is slow
- Network issues with n8n

**Solutions:**
- Use n8n for production (faster)
- Reduce OCR DPI (currently 300)
- Use smaller Ollama model

---

## 📈 Performance Tips

1. **Use n8n for production** - Better for handling multiple extractions
2. **Configure OCR only if needed** - Adds processing time
3. **Oracle integration is optional** - Use only for validation
4. **Monitor extraction queue** - Check processing times

---

## 🔐 Security Notes

1. **Never commit credentials** - Keep `.env` file gitignored
2. **Use environment variables** for sensitive data
3. **Restrict Oracle DB access** to read-only if possible

---

## 📞 Need Help?

1. Check `EXTRACTION_SETUP.md` for detailed configuration
2. Review extraction logs in console output
3. Check `ExtractionTask.error_log` in database
4. Test with sample invoices first

---

## 🎉 Success Indicators

You'll know it's working when you see:

✅ **In Console:**
```
📄 Processing invoice: /path/to/invoice.pdf
📝 Extracting PO from JSON data...
💡 Found VAT/TRN in JSON: ['OM1100020467']
🔎 Looking up PO prefix in DB for VAT/TRN: OM1100020467
✅ Found prefix in DB: AVPPO
✅ PO with DB prefix applied: AVPPO25010001 (VAT: OM1100020467)
✅ Extracted VAT/TRN: ['OM1100020467']
🔎 Fetching Axpert data for PO: AVPPO25010001
✅ Axpert data fetched successfully
```

✅ **In UI:**
- Green PO Number card showing detected PO
- VAT/TRN badges displayed
- Axpert data tables populated
- No errors in extraction task

---

**Happy Extracting! 🚀**
