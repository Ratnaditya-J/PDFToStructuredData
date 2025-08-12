"""
LangExtract integration module for structured data extraction.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import langextract as lx
from langextract.inference import GeminiLanguageModel, OpenAILanguageModel
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def get_language_model_type(model_id: str):
    """
    Determine the appropriate language model type based on the model ID.
    
    Args:
        model_id: The model identifier (e.g., 'gpt-3.5-turbo', 'gemini-2.5-flash')
        
    Returns:
        The appropriate language model class
    """
    if model_id.startswith('gpt-') or 'gpt' in model_id.lower():
        return OpenAILanguageModel
    elif model_id.startswith('gemini-') or 'gemini' in model_id.lower():
        return GeminiLanguageModel
    else:
        # Default to Gemini for unknown models
        return GeminiLanguageModel


class StructuredExtractor:
    """Handles structured data extraction using LangExtract."""
    
    def __init__(self, model_id: str = "gemini-2.5-flash"):
        """
        Initialize the extractor.
        
        Args:
            model_id: LLM model to use for extraction
        """
        self.model_id = model_id
        self.supported_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro", 
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        if model_id not in self.supported_models:
            logger.warning(f"Model {model_id} not in supported list: {self.supported_models}")
    
    def extract_from_text(
        self, 
        text: str, 
        prompt_description: str, 
        examples: List[lx.data.ExampleData],
        extraction_passes: int = 1,
        max_workers: int = 10,
        max_char_buffer: int = 1000
    ) -> Dict[str, Any]:
        """
        Extract structured data from text using LangExtract.
        
        Args:
            text: Input text to extract from
            prompt_description: Description of what to extract
            examples: Example extractions to guide the model
            extraction_passes: Number of passes for better recall
            max_workers: Number of parallel workers
            max_char_buffer: Character buffer size for chunking
            
        Returns:
            Dictionary containing extraction results and metadata
        """
        try:
            logger.info(f"Starting extraction with model: {self.model_id}")
            logger.info(f"Text length: {len(text)} characters")
            
            # Run LangExtract
            logger.info(f"Calling LangExtract with model: {self.model_id}")
            logger.info(f"Prompt: {prompt_description[:100]}...")
            
            try:
                # Get API key from environment
                api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('LANGEXTRACT_API_KEY')
                
                # Get the correct language model type based on model ID
                language_model_type = get_language_model_type(self.model_id)
                logger.info(f"Using language model type: {language_model_type.__name__}")
                
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=prompt_description,
                    examples=examples,
                    model_id=self.model_id,
                    language_model_type=language_model_type,  # Use correct model type
                    extraction_passes=extraction_passes,
                    max_workers=max_workers,
                    max_char_buffer=max_char_buffer,
                    api_key=api_key  # Pass API key explicitly
                )
                logger.info(f"LangExtract call successful, result type: {type(result)}")
            except Exception as lx_error:
                logger.error(f"LangExtract API call failed: {str(lx_error)}")
                logger.error(f"Error type: {type(lx_error)}")
                raise Exception(f"LangExtract API error: {str(lx_error)}")
            
            # Process results
            extractions = []
            if hasattr(result, 'extractions'):
                for extraction in result.extractions:
                    extractions.append({
                        'class': extraction.extraction_class,
                        'text': extraction.extraction_text,
                        'attributes': extraction.attributes,
                        'confidence': getattr(extraction, 'confidence', None)
                    })
            
            return {
                'extractions': extractions,
                'metadata': {
                    'model_id': self.model_id,
                    'extraction_passes': extraction_passes,
                    'total_extractions': len(extractions),
                    'text_length': len(text)
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return {
                'extractions': [],
                'metadata': {'error': str(e)},
                'success': False,
                'error': str(e)
            }
    
    def extract_with_template(
        self, 
        text: str, 
        template_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract using a predefined template configuration.
        
        Args:
            text: Input text
            template_config: Template configuration dictionary
            
        Returns:
            Extraction results
        """
        try:
            # Parse template configuration
            prompt = template_config.get('prompt', '')
            examples_data = template_config.get('examples', [])
            
            # Convert examples to LangExtract format
            examples = []
            for example_data in examples_data:
                extractions = []
                for ext in example_data.get('extractions', []):
                    extractions.append(
                        lx.data.Extraction(
                            extraction_class=ext['extraction_class'],
                            extraction_text=ext['extraction_text'],
                            attributes=ext.get('attributes', {})
                        )
                    )
                
                examples.append(
                    lx.data.ExampleData(
                        text=example_data['text'],
                        extractions=extractions
                    )
                )
            
            # Extract with template settings
            extraction_settings = template_config.get('settings', {})
            return self.extract_from_text(
                text=text,
                prompt_description=prompt,
                examples=examples,
                extraction_passes=extraction_settings.get('extraction_passes', 1),
                max_workers=extraction_settings.get('max_workers', 10),
                max_char_buffer=extraction_settings.get('max_char_buffer', 1000)
            )
            
        except Exception as e:
            logger.error(f"Template extraction failed: {str(e)}")
            return {
                'extractions': [],
                'metadata': {'error': str(e)},
                'success': False,
                'error': str(e)
            }
    
    def save_results(
        self, 
        results: Dict[str, Any], 
        output_path: str, 
        format: str = 'json'
    ) -> bool:
        """
        Save extraction results to file.
        
        Args:
            results: Extraction results
            output_path: Output file path
            format: Output format ('json', 'jsonl', 'csv')
            
        Returns:
            Success status
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == 'jsonl':
                # Convert to JSONL format for LangExtract visualization
                with open(output_path, 'w', encoding='utf-8') as f:
                    for extraction in results.get('extractions', []):
                        f.write(json.dumps(extraction, ensure_ascii=False) + '\n')
            
            elif format.lower() == 'csv':
                import pandas as pd
                # Flatten extractions for CSV
                flat_data = []
                for ext in results.get('extractions', []):
                    row = {
                        'class': ext['class'],
                        'text': ext['text'],
                        'confidence': ext.get('confidence', '')
                    }
                    # Add attributes as separate columns
                    for key, value in ext.get('attributes', {}).items():
                        row[f'attr_{key}'] = value
                    flat_data.append(row)
                
                df = pd.DataFrame(flat_data)
                df.to_csv(output_path, index=False)
            
            logger.info(f"Results saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            return False
    
    def generate_visualization(
        self, 
        jsonl_path: str, 
        output_html: str = None
    ) -> Optional[str]:
        """
        Generate interactive HTML visualization using LangExtract.
        
        Args:
            jsonl_path: Path to JSONL results file
            output_html: Output HTML file path (optional)
            
        Returns:
            HTML content or file path
        """
        try:
            html_content = lx.visualize(jsonl_path)
            
            if output_html:
                with open(output_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Visualization saved to: {output_html}")
                return output_html
            else:
                return html_content
                
        except Exception as e:
            logger.error(f"Failed to generate visualization: {str(e)}")
            return None
