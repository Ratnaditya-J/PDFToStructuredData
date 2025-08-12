"""
Utility functions for the PDF to Structured Data utility.
"""

import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import getpass

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_recommended_model_for_provider() -> str:
    """
    Get the recommended model based on the available API key provider.
    
    Returns:
        Recommended model ID
    """
    if os.getenv('OPENAI_API_KEY'):
        return 'gpt-3.5-turbo'
    elif os.getenv('GOOGLE_API_KEY'):
        return 'gemini-2.5-flash'
    else:
        return 'gemini-2.5-flash'  # Default


def validate_api_key(interactive: bool = True) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Validate that required API keys are available, with interactive input option.
    
    Args:
        interactive: If True, prompt user for API key if not found in environment
        
    Returns:
        Tuple of (success: bool, api_key: Optional[str], recommended_model: Optional[str])
    """
    # Check environment variables first
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
    
    if api_key:
        logger.info("API key found in environment variables")
        recommended_model = get_recommended_model_for_provider()
        return True, api_key, recommended_model
    
    if not interactive:
        logger.error("No API key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY environment variable.")
        return False, None, None
    
    # Interactive API key input
    print("\n🔑 API Key Required")
    print("No API key found in environment variables.")
    print("\nSupported providers:")
    print("  1. Google (Gemini) - Recommended for cost-effectiveness")
    print("  2. OpenAI (GPT) - Alternative option")
    
    while True:
        provider_choice = input("\nChoose provider (1 for Google, 2 for OpenAI): ").strip()
        
        if provider_choice == '1':
            print("\n📝 Get your Google API key at: https://makersuite.google.com/app/apikey")
            api_key = getpass.getpass("Enter your Google API key: ").strip()
            if api_key:
                # Set environment variable for this session
                os.environ['GOOGLE_API_KEY'] = api_key
                logger.info("Google API key set for this session")
                recommended_model = get_recommended_model_for_provider()
                return True, api_key, recommended_model
            else:
                print("❌ API key cannot be empty. Please try again.")
                
        elif provider_choice == '2':
            print("\n📝 Get your OpenAI API key at: https://platform.openai.com/api-keys")
            api_key = getpass.getpass("Enter your OpenAI API key: ").strip()
            if api_key:
                # Set environment variable for this session
                os.environ['OPENAI_API_KEY'] = api_key
                logger.info("OpenAI API key set for this session")
                recommended_model = get_recommended_model_for_provider()
                return True, api_key, recommended_model
            else:
                print("❌ API key cannot be empty. Please try again.")
                
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")
            
        # Ask if user wants to try again or exit
        retry = input("\nWould you like to try again? (y/n): ").strip().lower()
        if retry not in ['y', 'yes']:
            print("❌ API key is required to run the utility. Exiting.")
            return False, None, None


def find_pdf_files(directory: str) -> List[Path]:
    """
    Find all PDF files in a directory.
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of PDF file paths
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    pdf_files = list(directory.glob("*.pdf"))
    pdf_files.extend(directory.glob("**/*.pdf"))  # Include subdirectories
    
    logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
    return pdf_files


def load_custom_template(template_path: str) -> Dict[str, Any]:
    """
    Load a custom template from JSON file.
    
    Args:
        template_path: Path to template JSON file
        
    Returns:
        Template configuration dictionary
    """
    template_path = Path(template_path)
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        # Validate required fields
        required_fields = ['name', 'prompt', 'examples']
        for field in required_fields:
            if field not in template:
                raise ValueError(f"Template missing required field: {field}")
        
        logger.info(f"Loaded custom template: {template.get('name', 'unnamed')}")
        return template
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in template file: {str(e)}")


def create_output_directory(output_path: str) -> Path:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_path: Output file or directory path
        
    Returns:
        Path object for the output directory
    """
    output_path = Path(output_path)
    
    # If it's a file path, get the directory
    if output_path.suffix:
        output_dir = output_path.parent
    else:
        output_dir = output_path
    
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory ready: {output_dir}")
    
    return output_dir


def format_extraction_summary(results: Dict[str, Any]) -> str:
    """
    Format extraction results into a readable summary.
    
    Args:
        results: Extraction results dictionary
        
    Returns:
        Formatted summary string
    """
    if not results.get('success', False):
        return f"❌ Extraction failed: {results.get('error', 'Unknown error')}"
    
    extractions = results.get('extractions', [])
    metadata = results.get('metadata', {})
    
    summary = []
    summary.append(f"✅ Extraction completed successfully")
    summary.append(f"📊 Total extractions: {len(extractions)}")
    summary.append(f"🤖 Model used: {metadata.get('model_id', 'Unknown')}")
    summary.append(f"📄 Text length: {metadata.get('text_length', 0):,} characters")
    
    if extractions:
        summary.append("\n📋 Extraction breakdown:")
        class_counts = {}
        for ext in extractions:
            class_name = ext.get('class', 'unknown')
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        for class_name, count in sorted(class_counts.items()):
            summary.append(f"   • {class_name}: {count}")
    
    return "\n".join(summary)


def validate_output_format(format_name: str) -> str:
    """
    Validate and normalize output format name.
    
    Args:
        format_name: Output format name
        
    Returns:
        Normalized format name
        
    Raises:
        ValueError: If format is not supported
    """
    supported_formats = ['json', 'jsonl', 'csv', 'html']
    format_name = format_name.lower().strip()
    
    if format_name not in supported_formats:
        raise ValueError(f"Unsupported format: {format_name}. Supported: {supported_formats}")
    
    return format_name


def get_model_recommendations() -> Dict[str, str]:
    """
    Get model recommendations based on use case.
    
    Returns:
        Dictionary of model recommendations
    """
    return {
        'speed': 'gemini-2.5-flash',
        'accuracy': 'gemini-2.5-pro',
        'cost_effective': 'gemini-2.5-flash',
        'complex_reasoning': 'gemini-2.5-pro',
        'general_purpose': 'gemini-2.5-flash'
    }


def estimate_processing_time(text_length: int, extraction_passes: int = 1) -> str:
    """
    Estimate processing time based on text length.
    
    Args:
        text_length: Length of text to process
        extraction_passes: Number of extraction passes
        
    Returns:
        Estimated time string
    """
    # Rough estimates based on typical LLM processing speeds
    base_time_per_1k_chars = 2  # seconds per 1000 characters
    
    estimated_seconds = (text_length / 1000) * base_time_per_1k_chars * extraction_passes
    
    if estimated_seconds < 60:
        return f"~{int(estimated_seconds)} seconds"
    elif estimated_seconds < 3600:
        return f"~{int(estimated_seconds / 60)} minutes"
    else:
        return f"~{int(estimated_seconds / 3600)} hours"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    return filename


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                 PDF to Structured Data Utility              ║
║                                                              ║
║    Extract structured information from PDFs using AI        ║
║              Powered by Google's LangExtract                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
