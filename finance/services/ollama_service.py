"""
Enhanced Invoice Extraction Service
Integrates: Ollama, n8n, OCR, PO detection, VAT/TRN extraction, and Oracle DB integration
"""

import requests
import json
import time
import re
import os
import traceback
import logging
from django.conf import settings
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

import pprint

def alert(data, label="ALERT"):
    """Helper function to print data prominently to console/logs"""
    separator = "=" * 50
    formatted_data = pprint.pformat(data)
    print(f"\n{separator}\n[ {label} ]\n{separator}\n{formatted_data}\n{separator}\n")
    logger.info(f"\n{separator}\n[ {label} ]\n{separator}\n{formatted_data}\n{separator}\n")

try:
    import pandas as pd
except ImportError:
    pd = None
try:
    import oracledb
except ImportError:
    oracledb = None


# Configuration
# Configuration
OLLAMA_BASE_URL = getattr(settings, 'OLLAMA_BASE_URL', 'http://127.0.0.1:11435')
OLLAMA_MODEL = getattr(settings, 'OLLAMA_MODEL', 'llama3.1:latest')
N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/invoice_extract')

# Folder Configuration
SAVE_FOLDER = "static/invoices"
JSON_FOLDER = "static/json_responses"
AXPERT_DATA_FOLDER = "static/axpert_data"

# Ensure directories exist
for folder in [SAVE_FOLDER, JSON_FOLDER, AXPERT_DATA_FOLDER]:
    os.makedirs(folder, exist_ok=True)


# Oracle DB Configuration (optional - set in settings.py)
ORACLE_USER = getattr(settings, 'ORACLE_USER', None)
ORACLE_PASSWORD = getattr(settings, 'ORACLE_PASSWORD', None)
ORACLE_DSN = getattr(settings, 'ORACLE_DSN', None)

# Tesseract OCR path (optional - set in settings.py)
TESSERACT_PATH = getattr(settings, 'TESSERACT_PATH', None)

# Allowed PO prefixes
PO_PREFIXES = [
    "AVPPO", "INAPO", "ATCPO", "AKJPO", "NREPO", "ABLPO", "TIIPO", "KAYPO", "KADPO", "IECPO",
    "NRAPO", "NRJPO", "ARCPO", "ADLPO", "DXBPO", "TFTPO", "ACSPO", "AIMSPO", "AMSPPO", "HBSPO",
    "CEOPO", "BPCPO", "ITSPO", "AACPO", "TCPPO", "SABPO", "CUIPO", "KAYAPO", "SOBPO", "MLTPO",
    "BTDPO", "BTVPO", "ARPPO"
]

# Extraction prompt
EXTRACTION_PROMPT = """You are given invoice data in various formats (text, PDF extraction, OCR, or raw text). Your task is to extract and output **only the valid JSON object** that strictly follows this format. Your output **must contain only the JSON object**, with **no additional text, explanations, comments, or markdown**. If a field is missing or empty, output it as an empty string `""`.

The structure should be exactly as follows:

{{
  "Invoice_No": "string",
  "Invoice_Date": "YYYY-MM-DD",
  "PO_Number": "string",
  "Order_Number": "string",
  "Customer_Name": "string",
  "Customer_RefNo": "entityId",
  "LPO_reference": "string",
  "VATIN": "string",
  "CustomerTRN": "string",
  "Vendor_Name": "string",
  "VAT_Percentage": "string",
  "Subtotal": "string",
  "Total": "string",
  "Items": [
    {{
      "Item_No": "string",
      "Item_Description": "string",
      "Quantity": "string",
      "Unit": "string",
      "Unit_Price": "string",
      "Amount": "string"
    }}
  ]
}}

Ensure:
- Invoice Number maybe numeric or character or mix. Do not skip invoiceNo
- Invoice_Date is in the format `YYYY-MM-DD`.
- If any field is missing, output it as an empty string.
- If Items exist, the `Items` field must be an array with each object containing all six fields (Item_No, Item_Description, Quantity, Unit, Unit_Price, Amount).
- **Do not include comments, explanations, markdown, or any extra text. Return only the JSON object.**

data = {invoice_text}
"""


# ============================================================================
# VAT/TRN EXTRACTION
# ============================================================================

def extract_vat_numbers(text):
    """
    Extract all VAT/TRN numbers from a given text.
    VAT format: OM followed by 10 digits (may contain spaces)
    Returns a list of normalized VATs (spaces removed)
    """
    vat_numbers = []
    # Match OM followed by 10 digits, allowing spaces anywhere
    matches = re.findall(r"OM[\s]*\d[\d\s]{9,}", text, re.IGNORECASE)
    for v in matches:
        # Remove all spaces
        v_clean = re.sub(r"\s+", "", v)
        if len(v_clean) == 12 and v_clean.upper().startswith("OM"):
            if v_clean not in vat_numbers:
                vat_numbers.append(v_clean.upper())
    return vat_numbers


# ============================================================================
# ORACLE DB INTEGRATION
# ============================================================================

def get_prefix_from_db(vat_number):
    """
    Query Oracle to get PO prefix based on VAT/TRN number.
    vat_number should be like 'OM1100020467'
    """
    print(f"[SEARCH] Looking up PO prefix in DB for VAT/TRN: {vat_number}")
    if not all([ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN]):
         print("[WARNING] Oracle DB not configured. Skipping prefix lookup.")
         return None

    try:
        import oracledb
        with oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT a1.BRANCHCODE || 'PO' AS prefix FROM branch a1 WHERE trnno = :ptrnno",
                    ptrnno=vat_number
                )
                result = cursor.fetchone()
                if result:
                    print(f"[SUCCESS] Found prefix in DB: {result[0]}")
                    return result[0]
                else:
                    print(f"[WARNING] No prefix found in DB for VAT/TRN {vat_number}")
    except Exception as e:
        print(f"[ERROR] DB prefix fetch error: {e}")
    return None


def get_axpert_po_data(pono):
    """Fetch vendor + PO details from Oracle."""
    if not all([ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN]):
        logger.warning("[WARNING] Oracle DB not configured. Skipping Axpert data fetch.")
        return None, None
        
    try:
        # Import pandas inside to ensure it's available or fail loudly
        import pandas as pd
        import oracledb
        logger.info(f"[CONNECT] Connecting to Oracle DB for PO: {pono}")
        with oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN) as conn:
            with conn.cursor() as cursor:
                # Vendor
                vendor_query = """
                    SELECT 
                        A0.VENDORID,
                        A0.VENDORNAME,
                        A0.CREDITDAYS,
                        CR.CURRENCY,
                        a1.branchname,
                        DECODE(A0.TRNNO, NULL, 'UNREGISTERED SUPPLIER', A0.TRNNO) TRNO
                    FROM VENDOR A0, CURRENCY CR, POHDR A, branch a1
                    WHERE A0.CANCEL = 'F'
                      AND A0.CURRENCY = CR.CURRENCYID
                      AND A0.INACTIVE = 'F'
                      AND A0.CONTROLACCOUNT <> 7865220001998
                      AND A0.VENDORID = A.SUPPLIER
                      AND a1.branchid= a.branchname
                      AND A.DOCID = :PONO
                    ORDER BY VENDORNAME
                """
                cursor.execute(vendor_query, {"PONO": pono})
                vendor_rows = cursor.fetchall()
                vendor_cols = [d[0] for d in cursor.description]
                if not vendor_rows:
                    print(f"[WARNING] No vendor found for PO {pono}") # User requested print
                    logger.warning(f"[WARNING] No vendor found for PO {pono}")
                    return None, None
                
                vendor_df = pd.DataFrame(vendor_rows, columns=vendor_cols)
                if "VENDORID" in vendor_df.columns:
                    vendor_df = vendor_df.drop(columns=["VENDORID"])
                
                supplier_id = int(vendor_rows[0][0])
                
                # Print Vendor Fields
                print(f"--- Vendor Data for PO {pono} ---")
                for col in vendor_df.columns:
                    val = vendor_df.iloc[0][col]
                    print(f"{col}: {val}")

                # PO
                po_query = """
                    SELECT 
                        p.pohdrid,
                        p.docid,
                        p.docdt,
                        p.TOTPOVALUE,
                        p.NETCOSTAMT,
                        p.payterm,
                        c.CURRENCY
                    FROM pohdr p, currency c
                    WHERE p.CANCEL = 'F'
                      AND TRIM(LOWER(p.approval)) = 'yes'
                      AND p.supplier = :supplierid
                      AND p.CURRENCY = c.currencyid
                      AND p.DOCID = :PONO
                    GROUP BY p.pohdrid, p.docid, p.docdt, p.NETCOSTAMT, p.payterm, c.CURRENCY, p.TOTPOVALUE
                    ORDER BY p.docid
                """
                cursor.execute(po_query, {"supplierid": supplier_id, "PONO": pono})
                po_rows = cursor.fetchall()
                po_cols = [d[0] for d in cursor.description]
                po_df = pd.DataFrame(po_rows, columns=po_cols)
                if "POHDRID" in po_df.columns:
                    po_df = po_df.drop(columns=["POHDRID"])
                
                # Print PO Fields
                print(f"--- PO Line Items for PO {pono} ---")
                print(po_df.to_string())
                
                return vendor_df, po_df

    except Exception as e:
        print(f"[ERROR] Oracle error for PO {pono}: {e}")
        traceback.print_exc()
        return None, None




# ============================================================================
# OCR FUNCTIONALITY
# ============================================================================

def extract_text_via_ocr(file_path):
    """
    Extract text from PDF/image using OCR (Tesseract + pdf2image)
    
    Args:
        file_path: Path to the PDF or image file
        
    Returns:
        str: Extracted text
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
        
        # Set Tesseract path if configured
        if TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        
        text = ""
        
        if file_path.lower().endswith('.pdf'):
            print(f"[SEARCH] Performing OCR on PDF: {file_path}")
            images = convert_from_path(file_path, dpi=300)
            for img in images:
                text += pytesseract.image_to_string(img, lang="eng") + "\n"
        else:
            # Image file
            print(f"[SEARCH] Performing OCR on image: {file_path}")
            from PIL import Image
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="eng")
        
        print(f"[FILE] OCR extracted {len(text)} characters")
        return text
        
    except ImportError as e:
        print(f"[WARNING] OCR dependencies not installed: {e}")
        print("Install with: pip install pytesseract pdf2image pillow")
        return ""
    except Exception as e:
        print(f"[WARNING] OCR failed: {e}")
        return ""


def extract_po_from_ocr(ocr_text):
    """
    Extract PO number from OCR text with intelligent prefix detection
    """
    print(f"[SEARCH] Extracting PO from OCR text...")
    
    # Print OCR text preview for debugging
    print(f"[FILE] OCR Text Preview:\n{ocr_text[:500]}")
    
    # Check known PO prefixes first
    for prefix in PO_PREFIXES:
        match = re.search(rf"({prefix}-?\d+)", ocr_text, re.IGNORECASE)
        if match:
            po = match.group(1).replace("-", "").upper()
            print(f"✅ Found PO via OCR with prefix: {po}")
            return po

    # Check for 8-digit PO without prefix (YYMMXXXX format)
    num_match = re.search(r"\b(\d{8})\b", ocr_text)
    if num_match:
        po_candidate = num_match.group(1)
        yy, mm = int(po_candidate[:2]), int(po_candidate[2:4])
        if 1 <= mm <= 12:  # Validate month
            print(f"💡 Found PO via OCR without prefix: {po_candidate}")
            
            # Try to get VAT/TRN from OCR text and lookup prefix
            vat_numbers = extract_vat_numbers(ocr_text)
            if vat_numbers:
                print(f"💡 Found VAT/TRN via OCR: {vat_numbers}")
                for vat in vat_numbers:
                    prefix = get_prefix_from_db(vat)
                    if prefix:
                        po_full = f"{prefix}{po_candidate}"
                        print(f"✅ PO with DB prefix applied via OCR: {po_full}")
                        return po_full
            
            return po_candidate
    
    print("⚠️ PO not found via OCR")
    return ""


# ============================================================================
# PO NUMBER EXTRACTION (MAIN LOGIC)
# ============================================================================

def extract_po_number(json_data, pdf_path=None):
    """
    Extract PO number with VAT/TRN detection (JSON first, then OCR)
    and apply DB prefix if PO has no prefix.
    Handles multiple VAT/TRN numbers in OCR.
    """
    print("📝 Extracting PO from JSON data...")

    fields_to_check = [
        json_data.get("Invoice_No", ""),
        json_data.get("PO_Number", ""),
        json_data.get("Order_Number", ""),
        json_data.get("LPO_reference", ""),
        json_data.get("Customer_RefNo", "")
    ]

    # 1️⃣ Detect all VAT/TRN from JSON fields
    vat_numbers = []
    for field in fields_to_check:
        if not field:
            continue
        vat_numbers += extract_vat_numbers(str(field))
    vat_numbers = list(set(vat_numbers))
    if vat_numbers:
        print(f"💡 Found VAT/TRN in JSON: {vat_numbers}")

    # 2️⃣ If none found or to supplement, extract VAT/TRN via OCR
    ocr_text = ""
    # Initialize imports to None
    pytesseract = None
    convert_from_path = None
    
    if pdf_path:
        try:
            import pytesseract
            from pdf2image import convert_from_path
            if TESSERACT_PATH:
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        except ImportError:
             print("⚠️ OCR libraries not installed (pytesseract/pdf2image)")

        if pytesseract and convert_from_path:
            try:
                images = convert_from_path(pdf_path, dpi=300)
                for img in images:
                    ocr_text += pytesseract.image_to_string(img, lang="eng") + "\n"
            except Exception as e:
                print(f"⚠️ OCR failed: {e}")

            if ocr_text.strip():
                print(f"📄 OCR Text Preview:\n{ocr_text[:1000]}")
                ocr_vats = extract_vat_numbers(ocr_text)
                for v in ocr_vats:
                    if v not in vat_numbers:
                        vat_numbers.append(v)
                if ocr_vats:
                    print(f"💡 Found VAT/TRN via OCR: {ocr_vats}")
                else:
                    print("⚠️ VAT/TRN not found via OCR")
            else:
                print("⚠️ OCR returned empty text")
        else:
            print("⚠️ Skipping OCR: dependencies missing")

    # 3️⃣ Check PO numbers in JSON fields
    for field in fields_to_check:
        if not field:
            continue
        print(f"🔹 Checking field for PO: {field}")

        # Known PO prefixes
        for prefix in PO_PREFIXES:
            match = re.search(rf"({prefix}-?\d+)", str(field), re.IGNORECASE)
            if match:
                po = match.group(1).replace("-", "").upper()
                print(f"✅ Found PO with known prefix: {po}")
                return po

        # PO without prefix: 8-digit YYMMXXXX
        num_match = re.search(r"\b(\d{8})\b", str(field))
        if num_match:
            po_candidate = num_match.group(1)
            yy, mm = int(po_candidate[:2]), int(po_candidate[2:4])
            if 1 <= mm <= 12:
                print(f"💡 Found PO without prefix: {po_candidate}")

                # Apply DB prefixes from all detected VATs
                for vat in vat_numbers:
                    prefix = get_prefix_from_db(vat)
                    if prefix:
                        po_full = f"{prefix}{po_candidate}"
                        print(f"✅ PO with DB prefix applied: {po_full} (VAT: {vat})")
                        return po_full

                # No DB prefix found, return raw PO
                return po_candidate

    # 4️⃣ OCR fallback for PO
    if pdf_path and ocr_text:
        print("[SEARCH] PO not found in JSON. Trying OCR fallback...")
        
        # Check known PO prefixes first in OCR
        for prefix in PO_PREFIXES:
            match = re.search(rf"({prefix}-?\d+)", ocr_text, re.IGNORECASE)
            if match:
                po = match.group(1).replace("-", "").upper()
                print(f"[SUCCESS] Found PO via OCR with prefix: {po}")
                return po

        # Check for 8-digit PO without prefix
        num_match = re.search(r"\b(\d{8})\b", ocr_text)
        if num_match:
            po_candidate = num_match.group(1)
            yy, mm = int(po_candidate[:2]), int(po_candidate[2:4])
            if 1 <= mm <= 12:
                print(f"[SEARCH] Found PO via OCR without prefix: {po_candidate}")
                # Try to get VAT/TRN from OCR text
                vat_match = re.search(r"OM\d{10}", ocr_text)
                vat_number = vat_match.group(0) if vat_match else None
                if vat_number:
                    prefix = get_prefix_from_db(vat_number)
                    if prefix:
                        po_full = f"{prefix}{po_candidate}"
                        print(f"[SUCCESS] PO with DB prefix applied via OCR: {po_full}")
                        return po_full
                return po_candidate

    print("[WARNING] PO not found")
    return ""



# ============================================================================
# PDF TEXT EXTRACTION
# ============================================================================

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using PyPDF2
    Falls back to OCR if PyPDF2 extraction is poor or fails
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    try:
        import PyPDF2
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            text += page.extract_text()
        except Exception as e:
            print(f"[WARNING] PyPDF2 failed to read PDF ({e}). trying OCR...")
            # If PyPDF2 fails (e.g. corrupt PDF), try OCR as fallback
            return extract_text_via_ocr(file_path)
            
        # If extraction is poor (very short), try OCR
        if len(text.strip()) < 100:
            print("[WARNING] PyPDF2 extraction poor, trying OCR...")
            ocr_text = extract_text_via_ocr(file_path)
            if len(ocr_text) > len(text):
                return ocr_text
        
        return text
            
    except ImportError:
        print("[WARNING] PyPDF2 not installed, trying OCR...")
        return extract_text_via_ocr(file_path)
    except Exception as e:
        print(f"[WARNING] PDF extraction error: {e}, trying OCR...")
        return extract_text_via_ocr(file_path)


# ============================================================================
# N8N INTEGRATION
# ============================================================================

def extract_invoice_via_n8n(file_path):
    """
    Extract invoice data using your n8n workflow
    
    Args:
        file_path: Path to the invoice file
        
    Returns:
        dict: Extracted invoice data
    """
    if not N8N_WEBHOOK_URL:
        raise ValueError("N8N_WEBHOOK_URL not configured in settings")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'data': (os.path.basename(file_path), f, 'application/pdf')}
            print(f"[UPLOAD] Sending {file_path} to n8n webhook...")
            # Increased timeout to 5 minutes for complex invoices
            response = requests.post(N8N_WEBHOOK_URL, files=files, timeout=300)
        
        print(f"[SUCCESS] Received response from n8n (status: {response.status_code})")
        response.raise_for_status()
        result = response.json()
        
        print(f"[DATA] n8n response type: {type(result)}")
        print(f"[DATA] n8n response keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
        
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        
        if isinstance(result, dict) and "output" in result:
            try:
                output_str = result["output"].strip()
                if output_str.startswith("```json"):
                    output_str = output_str[7:].strip()
                if output_str.startswith("```"):
                    output_str = output_str[3:].strip()
                if output_str.endswith("```"):
                    output_str = output_str[:-3].strip()
                    
                # Attempt to clean common JSON errors (like invalid backslashes in paths)
                try:
                    result = json.loads(output_str)
                except json.JSONDecodeError:
                    # Retry with cleaned string: escape backslashes that aren't valid escapes
                    print("[WARNING] Initial JSON parse failed. Attempting to fix invalid escapes...")
                    # Regex to find backslashes that are NOT followed by valid escape chars
                    cleaned_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', output_str)
                    result = json.loads(cleaned_str)

            except json.JSONDecodeError as e:
                print(f"[ERROR] Error decoding 'output' JSON: {e}")
                print(f"[FILE] Problematic output start: {output_str[:200]}...")
                return {
                    'success': False,
                    'error': f'Failed to parse n8n output: {str(e)}',
                    'method': 'n8n',
                    'raw_output': str(output_str)[:500]
                }
        
        print(f"[SUCCESS] Final extracted data has {len(result)} fields")
        
        # [CLEAN] Clean keys (remove backslashes often added by some models)
        def clean_json_keys(data):
            if isinstance(data, dict):
                clean_data = {}
                for k, v in data.items():
                    clean_key = k.replace('\\', '')
                    clean_data[clean_key] = clean_json_keys(v)
                return clean_data
            elif isinstance(data, list):
                return [clean_json_keys(item) for item in data]
            else:
                return data

        result = clean_json_keys(result)

        return {
            'success': True,
            'data': result,
            'method': 'n8n'
        }
        
    except requests.exceptions.Timeout as e:
        print(f"[TIMEOUT] Timeout error: {e}")
        return {
            'success': False,
            'error': f'Request timeout after 300 seconds: {str(e)}',
            'method': 'n8n'
        }
    except requests.exceptions.RequestException as e:
        print(f"[NETWORK] Request error: {e}")
        return {
            'success': False,
            'error': f'Network error: {str(e)}',
            'method': 'n8n'
        }
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'method': 'n8n'
        }


# ============================================================================
# OLLAMA DIRECT INTEGRATION
# ============================================================================

def extract_invoice_via_ollama(invoice_text):
    """
    Extract invoice data using Ollama directly (pure Python)
    
    Args:
        invoice_text: Text content of the invoice (from OCR or PDF extraction)
        
    Returns:
        dict: Extracted invoice data
    """
    start_time = time.time()
    
    try:
        # Prepare the prompt
        prompt = EXTRACTION_PROMPT.format(invoice_text=invoice_text)
        
        # Call Ollama API
        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent extraction
                "top_p": 0.9
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get('response', '')
        
        # Try to parse the JSON from the response
        # Remove markdown code blocks if present
        cleaned_text = generated_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        # Parse JSON
        extracted_data = json.loads(cleaned_text)

        # [CLEAN] Clean keys (remove backslashes often added by some models)
        def clean_json_keys(data):
            if isinstance(data, dict):
                clean_data = {}
                for k, v in data.items():
                    clean_key = k.replace('\\', '')
                    clean_data[clean_key] = clean_json_keys(v)
                return clean_data
            elif isinstance(data, list):
                return [clean_json_keys(item) for item in data]
            else:
                return data

        extracted_data = clean_json_keys(extracted_data)
        
        processing_time = time.time() - start_time
        
        return {
            'success': True,
            'data': extracted_data,
            'method': 'ollama_direct',
            'processing_time': processing_time,
            'model': OLLAMA_MODEL
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse JSON: {str(e)}',
            'raw_response': generated_text if 'generated_text' in locals() else None,
            'method': 'ollama_direct'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Ollama API error: {str(e)}',
            'method': 'ollama_direct'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'method': 'ollama_direct'
        }


# ============================================================================
# VISION EXTRACTION
# ============================================================================
def extract_invoice_vision(file_path):
    """
    Extract invoice data using Vision model (e.g. Moondream) directly on image
    """
    import base64
    print(f"[VISION] Using Vision extraction with {OLLAMA_MODEL} for {file_path}")
    
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        # Modified prompt for Vision
        vision_prompt = """Analyze this invoice image and extract the data into a JSON object.
        Focus on: Invoice_No, Invoice_Date, PO_Number, Vendor_Name, Total.
        Return ONLY valid JSON.
        """ + EXTRACTION_PROMPT.split('data =')[0] # Reuse the schema part
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": vision_prompt,
            "images": [encoded_string],
            "stream": False,
            "options": {"temperature": 0.1}
        }
        
        print("[UPLOAD] Sending image to Ollama...")
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        output_text = result.get('response', '')
        
        # Clean and parse JSON (Reuse logic from extract_invoice_direct)
        cleaned_text = output_text.strip()
        if cleaned_text.startswith('```json'): cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'): cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'): cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        try:
            data = json.loads(cleaned_text)
            return {'success': True, 'data': data, 'model': OLLAMA_MODEL}
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse Vision JSON: {cleaned_text[:100]}...")
            return {'success': False, 'error': 'Failed to parse Vision output', 'raw_output': cleaned_text}
            
    except Exception as e:
        print(f"[ERROR] Vision extraction error: {e}")
        return {'success': False, 'error': f'Vision error: {str(e)}'}


# ============================================================================
# EXCEL & EMAIL FUNCTIONALITY
# ============================================================================




# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_invoice(submission):
    """
    Main function to process an invoice submission with enhanced extraction
    
    Args:
        submission: Submission model instance
        
    Returns:
        dict: Processing result with extracted data, PO info, and Axpert data
    """
    start_time = time.time()
    
    # Get the invoice document
    invoice_doc = submission.documents.filter(document_type='invoice').first()
    
    if not invoice_doc:
        return {
            'success': False,
            'error': 'No invoice document found'
        }
    
    file_path = invoice_doc.file.path
    logger.info(f"[FILE] Processing invoice: {file_path}")
    
    # Step 1: Extract invoice data via n8n or Ollama
    result = None
    
    if N8N_WEBHOOK_URL:
        logger.info("[PROCESS] Using n8n workflow for extraction...")
        result = extract_invoice_via_n8n(file_path)
        
        if not result['success']:
            logger.warning(f"[WARNING] n8n extraction failed ({result.get('error')}). Falling back to local processing...")
            result = None  # Reset to trigger local fallback

    if not result:
        logger.info(f"[PROCESS] Using Ollama direct extraction with {OLLAMA_MODEL}...")
        
        # VISION PATH: If model is Moondream/Vision AND finding is an Image
        is_image = file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        is_vision_model = 'moondream' in OLLAMA_MODEL or 'llava' in OLLAMA_MODEL
        
        if is_image and is_vision_model:
            result = extract_invoice_vision(file_path)
            # If Vision fails, fall back to OCR text?
            if not result['success']:
                logger.warning("[WARNING] Vision extraction failed, falling back to Text/OCR...")
            else:
                # Success! Skip text extraction
                pass
        
        if not 'result' in locals() or not result or not result.get('success'):
            # TEXT PATH (Default or Fallback)
            # Extract text from file
            if file_path.lower().endswith('.pdf'):
                invoice_text = extract_text_from_pdf(file_path)
            else:
                # For images, use OCR
                invoice_text = extract_text_via_ocr(file_path)
            
            if not invoice_text or len(invoice_text.strip()) < 50:
                logger.error("[ERROR] Failed to extract meaningful text from document.")
                return {
                    'success': False,
                    'error': 'Failed to extract text from document (scanned/empty content). OCR may be required.'
                }
            
            result = extract_invoice_via_ollama(invoice_text)
    
    if not result['success']:
        return result
    
    # Step 2: Enhance extracted data with PO detection
    extracted_data = result['data']
    alert(extracted_data, "EXTRACTED AI DATA")
    
    po_number = extract_po_number(extracted_data, file_path)
    alert(po_number, "DETECTED PO NUMBER")
    
    if po_number:
        extracted_data['PO_Number'] = po_number
        logger.info(f"[SUCCESS] Enhanced PO Number: {po_number}")
    
    # Step 3: Extract VAT/TRN numbers
    vat_numbers = extract_vat_numbers(json.dumps(extracted_data))
    if vat_numbers:
        extracted_data['extracted_vat_numbers'] = vat_numbers
        alert(vat_numbers, "EXTRACTED VAT NUMBERS")
        logger.info(f"[SUCCESS] Extracted VAT/TRN: {vat_numbers}")
    
    # Step 4: Fetch Axpert data if PO is available
    axpert_data = None
    if po_number and ORACLE_USER:
        logger.info(f"[SEARCH] Fetching Axpert data for PO: {po_number}")
        vendor_df, po_df = get_axpert_po_data(po_number)
        
        # Check if DFs are valid
        has_vendor = vendor_df is not None and not vendor_df.empty
        has_po = po_df is not None and not po_df.empty
        
        if has_vendor:
            alert(vendor_df.to_dict('records'), "AXPERT VENDOR DATA")
        if has_po:
            alert(po_df.to_dict('records'), "AXPERT PO DATA")
        
        if has_vendor or has_po:
            # Convert DFs to dict for JSON storage and UI display
            vendor_dict = None
            if has_vendor:
                # Handle NaN/Inf values that break JSON
                vendor_df = vendor_df.fillna("") 
                vendor_dict = {
                    'columns': vendor_df.columns.tolist(),
                    'rows': vendor_df.astype(str).values.tolist()
                }

            po_dict = None
            if has_po:
                po_df = po_df.fillna("")
                po_dict = {
                    'columns': po_df.columns.tolist(),
                    'rows': po_df.astype(str).values.tolist()
                }

            axpert_data = {
                'vendor': vendor_dict,
                'po': po_dict
            }
            extracted_data['axpert_data'] = axpert_data
            logger.info("[SUCCESS] Axpert data fetched successfully")
            
            # Update extracted_data with Axpert Vendor and Customer Name
            try:
                if has_vendor and 'VENDORNAME' in vendor_df.columns:
                    ax_vendor_name = vendor_df.iloc[0]['VENDORNAME']
                    if ax_vendor_name:
                        extracted_data['Vendor_Name'] = ax_vendor_name
                        extracted_data['Axpert_Vendor_Name'] = ax_vendor_name
                        logger.info(f"[UPDATE] Updated Vendor Name from Axpert: {ax_vendor_name}")
                
                if has_vendor and 'BRANCHNAME' in vendor_df.columns:
                    ax_branch_name = vendor_df.iloc[0]['BRANCHNAME']
                    if ax_branch_name:
                        extracted_data['Customer_Name'] = ax_branch_name
                        extracted_data['Axpert_Customer_Name'] = ax_branch_name
                        logger.info(f"[UPDATE] Updated Customer Name from Axpert: {ax_branch_name}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to parse Axpert data for name update: {e}")
            
            

    
    processing_time = time.time() - start_time
    
    return {
        'success': True,
        'data': extracted_data,
        'method': result.get('method', 'unknown'),
        'processing_time': processing_time,
        'model': result.get('model', OLLAMA_MODEL),
        'po_number': po_number,
        'vat_numbers': vat_numbers,
        'has_axpert_data': axpert_data is not None
    }
