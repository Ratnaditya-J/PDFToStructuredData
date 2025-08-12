"""
PDF text extraction module using multiple libraries for robust PDF processing.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction using multiple fallback methods."""
    
    def __init__(self):
        self.extraction_methods = [
            self._extract_with_pdfplumber,
            self._extract_with_pymupdf,
            self._extract_with_pypdf2
        ]
    
    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF using the best available method.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        # Try extraction methods in order of preference
        for method in self.extraction_methods:
            try:
                result = method(pdf_path)
                if result['text'].strip():  # Only return if we got meaningful text
                    logger.info(f"Successfully extracted text using {method.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Failed to extract with {method.__name__}: {str(e)}")
                continue
        
        raise RuntimeError(f"Failed to extract text from PDF: {pdf_path}")
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text using pdfplumber (best for structured documents)."""
        text_content = []
        metadata = {'method': 'pdfplumber', 'pages': 0}
        
        with pdfplumber.open(pdf_path) as pdf:
            metadata['pages'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
        
        return {
            'text': '\n\n'.join(text_content),
            'metadata': metadata
        }
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text using PyMuPDF (good for complex layouts)."""
        text_content = []
        metadata = {'method': 'pymupdf', 'pages': 0}
        
        doc = fitz.open(pdf_path)
        metadata['pages'] = doc.page_count
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text.strip():
                text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
        
        doc.close()
        
        return {
            'text': '\n\n'.join(text_content),
            'metadata': metadata
        }
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text using PyPDF2 (fallback method)."""
        text_content = []
        metadata = {'method': 'pypdf2', 'pages': 0}
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata['pages'] = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
        
        return {
            'text': '\n\n'.join(text_content),
            'metadata': metadata
        }
    
    def batch_extract(self, pdf_paths: list) -> Dict[str, Dict[str, Any]]:
        """
        Extract text from multiple PDFs.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            Dictionary mapping file paths to extraction results
        """
        results = {}
        
        for pdf_path in pdf_paths:
            try:
                results[str(pdf_path)] = self.extract_text(pdf_path)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {str(e)}")
                results[str(pdf_path)] = {
                    'text': '',
                    'metadata': {'error': str(e)},
                    'error': True
                }
        
        return results
