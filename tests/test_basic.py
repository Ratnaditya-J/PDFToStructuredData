"""
Basic tests for PDFToStructuredData components.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.pdf_processor import PDFProcessor
from src.templates import TemplateManager
from src.utils import validate_output_format, sanitize_filename


class TestPDFProcessor(unittest.TestCase):
    """Test PDF processing functionality."""
    
    def setUp(self):
        self.processor = PDFProcessor()
    
    def test_initialization(self):
        """Test PDFProcessor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(len(self.processor.extraction_methods), 3)
    
    def test_supported_methods(self):
        """Test that all expected extraction methods are available."""
        # Check that we have 3 extraction methods
        self.assertEqual(len(self.processor.extraction_methods), 3)
        
        # Check that the methods have the expected names
        method_names = [method.__name__ for method in self.processor.extraction_methods]
        expected_method_names = ['_extract_with_pdfplumber', '_extract_with_pymupdf', '_extract_with_pypdf2']
        
        for expected_name in expected_method_names:
            self.assertIn(expected_name, method_names)


class TestTemplateManager(unittest.TestCase):
    """Test template management functionality."""
    
    def setUp(self):
        self.template_manager = TemplateManager()
    
    def test_initialization(self):
        """Test TemplateManager initialization."""
        self.assertIsNotNone(self.template_manager)
        self.assertGreater(len(self.template_manager.built_in_templates), 0)
    
    def test_list_templates(self):
        """Test template listing."""
        templates = self.template_manager.list_templates()
        expected_templates = ['invoice', 'resume', 'research_paper', 'medical_report', 'contract']
        
        for template in expected_templates:
            self.assertIn(template, templates)
    
    def test_get_template(self):
        """Test getting a specific template."""
        template = self.template_manager.get_template('invoice')
        
        self.assertIsInstance(template, dict)
        self.assertIn('name', template)
        self.assertIn('prompt', template)
        self.assertIn('examples', template)
        self.assertIn('settings', template)
    
    def test_invalid_template(self):
        """Test getting an invalid template raises error."""
        with self.assertRaises(ValueError):
            self.template_manager.get_template('nonexistent_template')


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_validate_output_format(self):
        """Test output format validation."""
        # Valid formats
        self.assertEqual(validate_output_format('json'), 'json')
        self.assertEqual(validate_output_format('CSV'), 'csv')
        self.assertEqual(validate_output_format('  JSONL  '), 'jsonl')
        
        # Invalid format
        with self.assertRaises(ValueError):
            validate_output_format('invalid_format')
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test invalid characters
        self.assertEqual(sanitize_filename('file<>name.pdf'), 'file__name.pdf')
        self.assertEqual(sanitize_filename('file|name?.pdf'), 'file_name_.pdf')
        
        # Test long filename
        long_name = 'a' * 250 + '.pdf'
        sanitized = sanitize_filename(long_name)
        self.assertLessEqual(len(sanitized), 200)
        self.assertTrue(sanitized.endswith('.pdf'))


if __name__ == '__main__':
    unittest.main()
