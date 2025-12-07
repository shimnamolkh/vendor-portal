"""
Invoice Extraction Service using Ollama
Supports two modes:
1. Direct Ollama API call (pure Python)
2. n8n webhook call (uses your existing workflow)
"""

import requests
import json
import time
from django.conf import settings

# Configuration
OLLAMA_BASE_URL = getattr(settings, 'OLLAMA_BASE_URL', 'http://127.0.0.1:11435')
OLLAMA_MODEL = getattr(settings, 'OLLAMA_MODEL', 'llama3.1:latest')
N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', None)

# Extraction prompt matching your n8n workflow
EXTRACTION_PROMPT = """You are given invoice data in various formats (text, PDF extraction, OCR, or raw text). Your task is to extract and output **only the valid JSON object** that strictly follows this format. Your output **must contain only the JSON object**, with **no additional text, explanations, comments, or markdown**. If a field is missing or empty, output it as an empty string `""`.

The structure should be exactly as follows:

{
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
    {
      "Item_No": "string",
      "Item_Description": "string",
      "Quantity": "string",
      "Unit": "string",
      "Unit_Price": "string",
      "Amount": "string"
    }
  ]
}

Ensure:
- Invoice Number maybe numeric or character or mix. Do not skip invoiceNo
- Invoice_Date is in the format `YYYY-MM-DD`.
- If any field is missing, output it as an empty string.
- If Items exist, the `Items` field must be an array with each object containing all six fields (Item_No, Item_Description, Quantity, Unit, Unit_Price, Amount).
- **Do not include comments, explanations, markdown, or any extra text. Return only the JSON object.**

data = {invoice_text}
"""


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
            files = {'file': f}
            response = requests.post(N8N_WEBHOOK_URL, files=files, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'data': result,
                'method': 'n8n'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'n8n'
        }


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


def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using PyPDF2 or similar
    This is a simple implementation - you can enhance with OCR if needed
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    try:
        import PyPDF2
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except ImportError:
        # PyPDF2 not installed, return placeholder
        return "PDF text extraction requires PyPDF2. Install with: pip install PyPDF2"
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def process_invoice(submission):
    """
    Main function to process an invoice submission
    
    Args:
        submission: Submission model instance
        
    Returns:
        dict: Processing result
    """
    # Get the invoice document
    invoice_doc = submission.documents.filter(document_type='invoice').first()
    
    if not invoice_doc:
        return {
            'success': False,
            'error': 'No invoice document found'
        }
    
    file_path = invoice_doc.file.path
    
    # Option 1: Use n8n workflow (if configured)
    if N8N_WEBHOOK_URL:
        return extract_invoice_via_n8n(file_path)
    
    # Option 2: Use Ollama directly
    # First, extract text from the file
    if file_path.lower().endswith('.pdf'):
        invoice_text = extract_text_from_pdf(file_path)
    else:
        # For images, you'd need OCR (like PDF.co or Tesseract)
        # For now, return a placeholder
        invoice_text = "Image OCR not implemented. Use n8n workflow or implement OCR."
    
    # Extract data using Ollama
    return extract_invoice_via_ollama(invoice_text)
