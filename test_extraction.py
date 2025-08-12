#!/usr/bin/env python3
"""
Test the PDF extraction workflow without requiring a real API key.
Shows what the utility extracts from the PDF and what structured data would be generated.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_processor import PDFProcessor
from templates import TemplateManager
from utils import print_banner
import click
import json

def test_pdf_extraction():
    """Test PDF extraction and show what would be structured."""
    print_banner()
    
    click.echo("🧪 TEST MODE: PDF Extraction Workflow")
    click.echo("=" * 60)
    click.echo()
    
    # Initialize components
    pdf_processor = PDFProcessor()
    template_manager = TemplateManager()
    
    # Extract text from the sample PDF
    click.echo("📄 Extracting text from sample_invoice.pdf...")
    text_result = pdf_processor.extract_text("sample_invoice.pdf")
    
    # Check if extraction was successful (PDF processor returns different format)
    if 'text' not in text_result or not text_result['text']:
        click.echo(f"❌ PDF extraction failed: {text_result.get('error', 'No text extracted')}")
        return
    
    extracted_text = text_result['text']
    click.echo(f"✅ Successfully extracted {len(extracted_text)} characters")
    click.echo()
    
    # Show extracted text
    click.echo("📋 EXTRACTED TEXT FROM PDF:")
    click.echo("-" * 40)
    click.echo(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
    click.echo("-" * 40)
    click.echo()
    
    # Get invoice template
    template_config = template_manager.get_template('invoice')
    click.echo("📝 INVOICE TEMPLATE CONFIGURATION:")
    click.echo(f"Prompt: {template_config['prompt'][:100]}...")
    click.echo(f"Examples: {len(template_config['examples'])} training examples")
    click.echo(f"Settings: {template_config['settings']}")
    click.echo()
    
    # Show what would be extracted (mock structure)
    click.echo("🎯 MOCK STRUCTURED DATA (What LangExtract would extract):")
    mock_extraction = {
        "extractions": [
            {
                "class": "Invoice",
                "text": "INVOICE #2024-TEST-001",
                "attributes": {
                    "invoice_number": "2024-TEST-001",
                    "vendor_name": "TechSupply Solutions",
                    "vendor_address": "456 Vendor Avenue, Supply Town, ST 67890",
                    "customer_name": "Acme Corporation", 
                    "customer_address": "123 Business Street, Suite 100, Business City, BC 12345",
                    "invoice_date": "March 15, 2024",
                    "due_date": "April 15, 2024",
                    "subtotal": "$2,809.95",
                    "tax": "$238.85",
                    "total": "$3,073.80"
                },
                "confidence": 0.95
            },
            {
                "class": "LineItem",
                "text": "Laptop Computer Dell XPS    2      $1,299.99     $2,599.98",
                "attributes": {
                    "description": "Laptop Computer Dell XPS",
                    "quantity": "2",
                    "unit_price": "$1,299.99",
                    "amount": "$2,599.98"
                },
                "confidence": 0.92
            },
            {
                "class": "LineItem", 
                "text": "Wireless Mouse Logitech     2      $29.99        $59.98",
                "attributes": {
                    "description": "Wireless Mouse Logitech",
                    "quantity": "2", 
                    "unit_price": "$29.99",
                    "amount": "$59.98"
                },
                "confidence": 0.89
            }
        ],
        "metadata": {
            "model_id": "gemini-2.5-flash",
            "extraction_passes": 1,
            "total_extractions": 3,
            "text_length": len(extracted_text)
        },
        "success": True
    }
    
    click.echo(json.dumps(mock_extraction, indent=2))
    click.echo()
    
    click.echo("🚀 WHAT HAPPENS WITH A REAL API KEY:")
    click.echo("✅ The utility would send this text + template to LangExtract")
    click.echo("✅ LangExtract would return structured data like the mock above")
    click.echo("✅ Results would be saved to JSON/CSV/HTML format")
    click.echo("✅ Interactive visualization would be generated")
    click.echo()
    
    click.echo("🔑 TO USE WITH REAL DATA:")
    click.echo("1. Get a Google API key: https://makersuite.google.com/app/apikey")
    click.echo("2. Run: python pdf_extractor.py extract sample_invoice.pdf --template invoice")
    click.echo("3. Follow the interactive prompts")

if __name__ == "__main__":
    test_pdf_extraction()
