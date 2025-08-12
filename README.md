# PDFToStructuredData

A powerful Python CLI tool that extracts structured data from PDF documents using Google's LangExtract library.

## Features

- **Template-Based Extraction**: Pre-built templates for common document types (invoices, resumes, research papers, medical reports, contracts)
- **Custom Configuration**: Define your own extraction rules via JSON configuration
- **Batch Processing**: Process multiple PDFs at once
- **Multiple Output Formats**: JSON, CSV, Excel, or interactive HTML visualization
- **Confidence Scoring**: Shows extraction confidence for each field
- **PDF Text Extraction**: Robust text extraction from various PDF formats

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd PDFToStructuredData

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Extract invoice data
python pdf_extractor.py --pdf invoice.pdf --template invoice

# Extract resume data
python pdf_extractor.py --pdf resume.pdf --template resume --output json

# Custom extraction with your own template
python pdf_extractor.py --pdf document.pdf --template custom --config my_config.json

# Batch process multiple PDFs
python pdf_extractor.py --folder ./documents/ --template research_paper --output results.json
```

## 📋 Built-in Templates

PDFToStructuredData comes with **10 pre-built templates** for common document types. Each template is optimized for specific document structures and extraction patterns.

### 🧾 **Business & Financial Documents**

#### `invoice`
**Extract from business invoices and bills**
- Vendor/supplier information
- Invoice number and date
- Line items with descriptions and amounts
- Subtotal, tax, and total amounts
- Payment terms and due dates

#### `receipt`
**Extract from retail receipts and purchase records**
- Store name and location
- Transaction date and time
- Itemized purchases with prices
- Tax amounts and payment method
- Receipt/transaction number

#### `bank_statement`
**Extract from bank and financial statements**
- Account holder information
- Account numbers and statement period
- Transaction history with dates and amounts
- Beginning and ending balances
- Fees and charges

#### `contract`
**Extract from legal contracts and agreements**
- Contracting parties and their roles
- Contract terms and conditions
- Important dates (start, end, renewal)
- Financial obligations and amounts
- Termination clauses and governing law

### 🏥 **Healthcare Documents**

#### `medical_report`
**Extract from medical reports and patient records**
- Patient demographics and contact info
- Diagnosis codes and descriptions
- Prescribed medications and dosages
- Vital signs and test results
- Treatment plans and recommendations

### 🎓 **Academic & Research Documents**

#### `academic_paper`
**Extract from academic papers and research publications**
- Paper metadata (title, journal, DOI)
- Author information and affiliations
- Abstract and keywords
- Methodology and research approach
- Key findings and conclusions
- Citation count and references

#### `research_paper`
**Extract from general research documents**
- Title and authors
- Abstract and summary
- Methodology section
- Results and findings
- Conclusions and future work

### 💼 **Professional Documents**

#### `resume`
**Extract from resumes and CVs**
- Personal information and contact details
- Professional summary/objective
- Work experience with dates and descriptions
- Education and certifications
- Skills and competencies

#### `business_card`
**Extract from business cards and contact info**
- Full name and job title
- Company name and department
- Phone numbers (office, mobile, fax)
- Email addresses and websites
- Physical address and social media

### 📊 **Tax & Government Documents**

#### `tax_document`
**Extract from tax forms (W-2, 1099, tax returns)**
- Taxpayer identification and personal info
- Income sources and amounts
- Tax withholdings and payments
- Deductions and credits
- Tax liability and refund amounts

---

### 🚀 **Using Templates**

```bash
# List all available templates
python pdf_extractor.py list-templates

# Use a specific template
python pdf_extractor.py extract invoice.pdf --template invoice
python pdf_extractor.py extract medical_report.pdf --template medical_report

# Batch process with templates
python pdf_extractor.py batch ./receipts/ --template receipt
```

### 🎯 **Template Accuracy**

Each template is designed with:
- **Specific prompts** optimized for document type
- **Example extractions** to guide the AI model
- **Field validation** for data quality
- **Confidence scoring** for extraction reliability

## Custom Templates

Create a JSON configuration file to define your own extraction rules:

```json
{
  "template_name": "custom_document",
  "prompt": "Extract key information from this document",
  "examples": [
    {
      "text": "Sample document text...",
      "extractions": [
        {
          "extraction_class": "entity_type",
          "extraction_text": "extracted text",
          "attributes": {"key": "value"}
        }
      ]
    }
  ]
}
```

## Requirements

- Python 3.8+
- Google API key for Gemini models (or other LLM provider)
- LangExtract library
- PDF processing libraries

## API Key Setup

Set your API key as an environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```
GOOGLE_API_KEY=your-api-key-here
```

## Project Structure

```
PDFToStructuredData/
├── README.md
├── requirements.txt
├── pdf_extractor.py          # Main CLI script
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py      # PDF text extraction
│   ├── extractor.py          # LangExtract integration
│   ├── templates.py          # Built-in templates
│   └── utils.py              # Utility functions
├── templates/                # Template configuration files
│   ├── invoice.json
│   ├── resume.json
│   ├── research_paper.json
│   ├── medical_report.json
│   └── contract.json
├── examples/                 # Sample PDFs for testing
└── tests/                    # Unit tests
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
