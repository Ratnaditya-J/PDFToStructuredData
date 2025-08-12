"""
Configuration management for PDFToStructuredData.
Handles loading and parsing YAML configuration files.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TemplateConfig:
    """Template configuration settings."""
    name: Optional[str] = None
    custom_template_path: Optional[str] = None


@dataclass
class ModelConfig:
    """Model configuration settings."""
    name: str = "gemini-2.5-flash"
    passes: int = 2
    workers: int = 10


@dataclass
class OutputConfig:
    """Output configuration settings."""
    format: str = "json"
    directory: Optional[str] = None
    visualize: bool = False


@dataclass
class ProcessingConfig:
    """Processing configuration settings."""
    batch_size: int = 5
    skip_existing: bool = True
    verbose: bool = False


@dataclass
class APIConfig:
    """API configuration settings."""
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    langextract_api_key: Optional[str] = None


@dataclass
class Config:
    """Main configuration class."""
    template: TemplateConfig
    model: ModelConfig
    output: OutputConfig
    processing: ProcessingConfig
    api: APIConfig


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager with optional config file path."""
        self.config_path = config_path or self._find_default_config()
        self.config = self._load_config()
    
    def _find_default_config(self) -> Optional[str]:
        """Find default config file in common locations."""
        possible_paths = [
            "config.yaml",
            "config.yml",
            os.path.expanduser("~/.pdf_extractor_config.yaml"),
            os.path.expanduser("~/.pdf_extractor_config.yml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _load_config(self) -> Config:
        """Load configuration from file or use defaults."""
        if not self.config_path or not os.path.exists(self.config_path):
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            return self._parse_config(config_data)
        
        except Exception as e:
            print(f"Warning: Error loading config file {self.config_path}: {e}")
            print("Using default configuration.")
            return self._get_default_config()
    
    def _parse_config(self, config_data: Dict[str, Any]) -> Config:
        """Parse configuration data into Config object."""
        template_data = config_data.get('template', {})
        model_data = config_data.get('model', {})
        output_data = config_data.get('output', {})
        processing_data = config_data.get('processing', {})
        api_data = config_data.get('api', {})
        
        return Config(
            template=TemplateConfig(
                name=template_data.get('name'),
                custom_template_path=template_data.get('custom_template_path')
            ),
            model=ModelConfig(
                name=model_data.get('name', 'gemini-2.5-flash'),
                passes=model_data.get('passes', 2),
                workers=model_data.get('workers', 10)
            ),
            output=OutputConfig(
                format=output_data.get('format', 'json'),
                directory=output_data.get('directory'),
                visualize=output_data.get('visualize', False)
            ),
            processing=ProcessingConfig(
                batch_size=processing_data.get('batch_size', 5),
                skip_existing=processing_data.get('skip_existing', True),
                verbose=processing_data.get('verbose', False)
            ),
            api=APIConfig(
                google_api_key=api_data.get('google_api_key'),
                openai_api_key=api_data.get('openai_api_key'),
                langextract_api_key=api_data.get('langextract_api_key')
            )
        )
    
    def _get_default_config(self) -> Config:
        """Get default configuration."""
        return Config(
            template=TemplateConfig(),
            model=ModelConfig(),
            output=OutputConfig(),
            processing=ProcessingConfig(),
            api=APIConfig()
        )
    
    def get_template_name(self) -> Optional[str]:
        """Get template name from config."""
        return self.config.template.name
    
    def get_custom_template_path(self) -> Optional[str]:
        """Get custom template path from config."""
        return self.config.template.custom_template_path
    
    def get_model_name(self) -> str:
        """Get model name from config."""
        return self.config.model.name
    
    def get_output_format(self) -> str:
        """Get output format from config."""
        return self.config.output.format
    
    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """Get API keys from config (will be overridden by environment variables)."""
        return {
            'google_api_key': self.config.api.google_api_key,
            'openai_api_key': self.config.api.openai_api_key,
            'langextract_api_key': self.config.api.langextract_api_key
        }
    
    def merge_with_cli_args(self, **cli_args) -> Dict[str, Any]:
        """Merge config with CLI arguments, giving priority to CLI args."""
        merged = {
            'template': cli_args.get('template') or self.config.template.name,
            'custom_template': cli_args.get('custom_template') or self.config.template.custom_template_path,
            'model': cli_args.get('model') or self.config.model.name,
            'passes': cli_args.get('passes') or self.config.model.passes,
            'workers': cli_args.get('workers') or self.config.model.workers,
            'format': cli_args.get('format') or self.config.output.format,
            'output': cli_args.get('output') or self.config.output.directory,
            'visualize': cli_args.get('visualize') if cli_args.get('visualize') is not None else self.config.output.visualize,
            'verbose': cli_args.get('verbose') if cli_args.get('verbose') is not None else self.config.processing.verbose
        }
        
        # Remove None values
        return {k: v for k, v in merged.items() if v is not None}
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        if self.config.template.name and self.config.template.custom_template_path:
            print("Warning: Both template name and custom template path specified. Using template name.")
        
        if self.config.model.passes < 1 or self.config.model.passes > 3:
            print("Warning: Invalid extraction passes. Must be between 1 and 3.")
            return False
        
        valid_formats = ['json', 'jsonl', 'csv', 'html', 'yaml', 'table']
        if self.config.output.format not in valid_formats:
            print(f"Warning: Invalid output format. Must be one of: {', '.join(valid_formats)}")
            return False
        
        return True
