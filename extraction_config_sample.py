# ============================================================================
# ENHANCED EXTRACTION SYSTEM CONFIGURATION
# Add these settings to your vendor_portal/settings.py file
# ============================================================================

# ----------------------------------------------------------------------------
# OLLAMA CONFIGURATION (Required for AI extraction)
# ----------------------------------------------------------------------------
OLLAMA_BASE_URL = 'http://127.0.0.1:11435'  # Your Ollama server URL
OLLAMA_MODEL = 'llama3.1:latest'  # Model to use for extraction

# Alternative models you can use:
# OLLAMA_MODEL = 'llava:7b'  # Vision model (for image-based extraction)
# OLLAMA_MODEL = 'mistral:latest'  # Alternative text model


# ----------------------------------------------------------------------------
# N8N WEBHOOK (Optional - for n8n workflow integration)
# ----------------------------------------------------------------------------
N8N_WEBHOOK_URL = None  # Set to your n8n webhook URL if using n8n

# Example:
# N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'
# N8N_WEBHOOK_URL = 'http://172.16.1.100:5678/webhook/invoice_extract'


# ----------------------------------------------------------------------------
# TESSERACT OCR CONFIGURATION (Optional - for OCR support)
# ----------------------------------------------------------------------------
TESSERACT_PATH = None  # Path to Tesseract executable

# Windows Examples:
# TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# TESSERACT_PATH = r'C:\Users\YourName\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Network Path Example (from your old code):
# TESSERACT_PATH = r'\\172.16.1.53\C$\Program Files\Tesseract-OCR\tesseract.exe'

# Linux Example:
# TESSERACT_PATH = '/usr/bin/tesseract'

# Mac Example:
# TESSERACT_PATH = '/usr/local/bin/tesseract'


# ----------------------------------------------------------------------------
# ORACLE DATABASE CONFIGURATION (Optional - for Axpert integration)
# ----------------------------------------------------------------------------
ORACLE_USER = None  # Your Oracle username
ORACLE_PASSWORD = None  # Your Oracle password
ORACLE_DSN = None  # Oracle connection string (host:port/service)

# Example (from your old code):
# ORACLE_USER = 'ADK2011'
# ORACLE_PASSWORD = 'your_password_here'  # NEVER commit this!
# ORACLE_DSN = '172.16.1.85:1521/orcl'

# For production, use environment variables:
# import os
# ORACLE_USER = os.getenv('ORACLE_USER')
# ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD')
# ORACLE_DSN = os.getenv('ORACLE_DSN')


# ============================================================================
# CONFIGURATION PROFILES
# ============================================================================

# ----------------------------------------------------------------------------
# PROFILE 1: BASIC (Ollama Only)
# ----------------------------------------------------------------------------
# Use this for: Testing, development, basic extraction
# Requirements: Ollama installed and running
# Features: AI extraction only
#
# OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
# OLLAMA_MODEL = 'llama3.1:latest'
# N8N_WEBHOOK_URL = None
# TESSERACT_PATH = None
# ORACLE_USER = None
# ORACLE_PASSWORD = None
# ORACLE_DSN = None


# ----------------------------------------------------------------------------
# PROFILE 2: ENHANCED (Ollama + OCR)
# ----------------------------------------------------------------------------
# Use this for: Scanned documents, image invoices
# Requirements: Ollama + Tesseract OCR
# Features: AI extraction + OCR fallback
#
# OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
# OLLAMA_MODEL = 'llama3.1:latest'
# N8N_WEBHOOK_URL = None
# TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ORACLE_USER = None
# ORACLE_PASSWORD = None
# ORACLE_DSN = None


# ----------------------------------------------------------------------------
# PROFILE 3: FULL (Ollama + OCR + Oracle)
# ----------------------------------------------------------------------------
# Use this for: Production, full validation
# Requirements: Ollama + Tesseract OCR + Oracle DB access
# Features: AI extraction + OCR + PO prefix lookup + Axpert validation
#
# OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
# OLLAMA_MODEL = 'llama3.1:latest'
# N8N_WEBHOOK_URL = None
# TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ORACLE_USER = 'ADK2011'
# ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD')  # Use environment variable!
# ORACLE_DSN = '172.16.1.85:1521/orcl'


# ----------------------------------------------------------------------------
# PROFILE 4: N8N WORKFLOW (Recommended for Production)
# ----------------------------------------------------------------------------
# Use this for: Production, high volume
# Requirements: n8n workflow set up
# Features: n8n extraction + PO enhancement + Axpert validation
#
# N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/invoice_extract'
# TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ORACLE_USER = 'ADK2011'
# ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD')
# ORACLE_DSN = '172.16.1.85:1521/orcl'
# # Note: Ollama settings still needed for fallback
# OLLAMA_BASE_URL = 'http://127.0.0.1:11435'
# OLLAMA_MODEL = 'llama3.1:latest'


# ============================================================================
# INSTALLATION COMMANDS
# ============================================================================

# For Basic Profile:
# pip install requests django

# For Enhanced Profile (+ OCR):
# pip install requests django PyPDF2 pytesseract pdf2image pillow
# Also install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

# For Full Profile (+ Oracle):
# pip install requests django PyPDF2 pytesseract pdf2image pillow oracledb

# For n8n Profile:
# pip install requests django PyPDF2 pytesseract pdf2image pillow oracledb
# Also set up n8n workflow


# ============================================================================
# SECURITY BEST PRACTICES
# ============================================================================

# 1. Use environment variables for sensitive data:
#    - Create a .env file (already gitignored)
#    - Add: ORACLE_PASSWORD=your_password
#    - Load with: pip install python-decouple
#    - Use: from decouple import config
#           ORACLE_PASSWORD = config('ORACLE_PASSWORD')

# 2. Never commit credentials to git

# 3. Use read-only Oracle user if possible

# 4. Restrict network access to Oracle DB

# 5. Monitor extraction logs for suspicious activity


# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# For faster extraction:
# - Use n8n workflow instead of direct Ollama
# - Reduce OCR DPI (edit ollama_service.py, line ~217: dpi=300 → dpi=200)
# - Use smaller/faster Ollama model
# - Disable Oracle integration if not needed

# For better accuracy:
# - Use higher OCR DPI (300-600)
# - Use vision model (llava:7b) instead of text model
# - Enable all features (OCR + Oracle validation)


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# Issue: Ollama connection error
# Solution: Ensure Ollama is running on the specified URL/port

# Issue: OCR not working
# Solution: Install Tesseract and set correct path

# Issue: Oracle connection error
# Solution: Check credentials, network access, and DSN format

# Issue: Slow extraction
# Solution: Use n8n workflow or reduce OCR DPI

# Issue: PO not detected
# Solution: Check if PO format is supported, ensure VAT/TRN is present


# ============================================================================
# NEXT STEPS
# ============================================================================

# 1. Choose a configuration profile above
# 2. Copy the relevant settings to your settings.py
# 3. Install required dependencies
# 4. Test with a sample invoice
# 5. Check extraction logs for any issues
# 6. Review EXTRACTION_QUICKSTART.md for usage guide
