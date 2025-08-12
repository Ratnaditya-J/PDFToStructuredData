#!/bin/bash

# Example automation script for batch PDF processing
# This script demonstrates fully automated processing with config file and environment variables

# Set up environment variables for API keys
export GOOGLE_API_KEY="your-google-api-key-here"
# export OPENAI_API_KEY="your-openai-api-key-here"  # Alternative
# export LANGEXTRACT_API_KEY="your-langextract-api-key-here"  # Alternative

# Create output directory
mkdir -p ./output

# Process single PDF with config file (no user interaction required)
echo "Processing single invoice PDF..."
python pdf_extractor.py --config examples/automation_example.yaml extract sample_invoice.pdf

# Process multiple PDFs in batch
echo "Processing multiple PDFs..."
for pdf_file in pdfs_to_process/*.pdf; do
    if [ -f "$pdf_file" ]; then
        echo "Processing: $pdf_file"
        python pdf_extractor.py --config examples/automation_example.yaml extract "$pdf_file"
    fi
done

# Process with different template for different document types
echo "Processing contracts with contract template..."
python pdf_extractor.py --config examples/automation_example.yaml extract contract.pdf --template contract

echo "Automation complete! Check ./output directory for results."
