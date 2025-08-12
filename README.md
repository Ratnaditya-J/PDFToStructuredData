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

## Built-in Templates

- **invoice**: Extract vendor, amount, date, line items, tax information
- **resume**: Extract name, skills, experience, education, contact details
- **research_paper**: Extract title, authors, abstract, methodology, findings
- **medical_report**: Extract patient info, diagnosis, medications, recommendations
- **contract**: Extract parties, terms, dates, obligations, signatures

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
