#!/usr/bin/env python3
"""
PDF to Structured Data Utility - Main CLI Interface
Extract structured data from PDF documents using Google's LangExtract library.
"""

import click
import sys
from pathlib import Path
from typing import Optional, List
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.pdf_processor import PDFProcessor
from src.extractor import StructuredExtractor
from src.templates import TemplateManager
from src.utils import (
    setup_logging, validate_api_key, find_pdf_files, 
    load_custom_template, create_output_directory,
    format_extraction_summary, validate_output_format,
    get_model_recommendations, estimate_processing_time,
    print_banner
)
from src.config_manager import ConfigManager


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output except errors')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file (YAML)')
def cli(verbose, quiet, config):
    """PDF to Structured Data Utility - Extract structured information from PDFs using AI."""
    # Initialize config manager
    config_manager = ConfigManager(config)
    
    # Store config manager in context for subcommands
    ctx = click.get_current_context()
    ctx.ensure_object(dict)
    ctx.obj['config_manager'] = config_manager
    
    # Set up logging based on config and CLI args
    if quiet:
        setup_logging('ERROR')
    elif verbose or config_manager.config.processing.verbose:
        setup_logging('DEBUG')
    else:
        setup_logging('INFO')


@cli.command()
def list_templates():
    """List all available extraction templates."""
    from src.templates import TemplateManager
    
    print_banner()
    
    template_manager = TemplateManager()
    templates = template_manager.list_templates()
    
    click.echo("\n📋 Available Extraction Templates:")
    click.echo("=" * 50)
    
    for template_name in sorted(templates):
        try:
            template = template_manager.get_template(template_name)
            description = template.get('description', 'No description available')
            click.echo(f"\n🔹 {template_name}")
            click.echo(f"   {description}")
        except Exception as e:
            click.echo(f"\n🔹 {template_name}")
            click.echo(f"   Error loading template: {e}")
    
    click.echo("\n💡 Usage: python pdf_extractor.py extract <pdf_file> --template <template_name>")
    click.echo("💡 Example: python pdf_extractor.py extract invoice.pdf --template invoice")


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--template', '-t', help='Template name (use --list-templates to see all available templates)')
@click.option('--custom-template', '-c', type=click.Path(exists=True), help='Path to custom template JSON file')
@click.option('--output', '-o', help='Output file path (default: auto-generated)')
@click.option('--format', '-f', default='json', help='Output format: json, jsonl, csv, html')
@click.option('--model', '-m', default='gemini-2.5-flash', help='LLM model to use')
@click.option('--passes', '-p', default=1, type=int, help='Number of extraction passes (1-3)')
@click.option('--workers', '-w', default=10, type=int, help='Number of parallel workers')
@click.option('--visualize', is_flag=True, help='Generate interactive HTML visualization')
@click.pass_context
def extract(ctx, pdf_path, template, custom_template, output, format, model, passes, workers, visualize):
    """Extract structured data from a single PDF file."""
    
    print_banner()
    
    # Get config manager from context
    config_manager = ctx.obj.get('config_manager')
    
    # Merge CLI args with config file settings (CLI takes precedence)
    if config_manager:
        merged_config = config_manager.merge_with_cli_args(
            template=template,
            custom_template=custom_template,
            output=output,
            format=format,
            model=model,
            passes=passes,
            workers=workers,
            visualize=visualize
        )
        
        # Update variables with merged config
        template = merged_config.get('template')
        custom_template = merged_config.get('custom_template')
        output = merged_config.get('output')
        format = merged_config.get('format')
        model = merged_config.get('model')
        passes = merged_config.get('passes')
        workers = merged_config.get('workers')
        visualize = merged_config.get('visualize')
        
        # Show which config file is being used
        if config_manager.config_path:
            click.echo(f"📄 Using config file: {config_manager.config_path}")
    
    # Validate API key
    api_valid, api_key, recommended_model = validate_api_key(interactive=True)
    if not api_valid:
        click.echo("❌ API key validation failed.", err=True)
        sys.exit(1)
    
    # Use recommended model if user didn't specify a custom model
    if model == 'gemini-2.5-flash' and recommended_model:
        model = recommended_model
        click.echo(f"🎯 Using recommended model for your API provider: {model}")
    
    # Validate parameters
    try:
        format = validate_output_format(format)
    except ValueError as e:
        click.echo(f"❌ {str(e)}", err=True)
        sys.exit(1)
    
    if passes < 1 or passes > 3:
        click.echo("❌ Extraction passes must be between 1 and 3", err=True)
        sys.exit(1)
    
    # Initialize components
    pdf_processor = PDFProcessor()
    extractor = StructuredExtractor(model_id=model)
    template_manager = TemplateManager()
    
    try:
        # Extract text from PDF
        click.echo(f"📄 Processing PDF: {pdf_path}")
        text_result = pdf_processor.extract_text(pdf_path)
        
        # Check if PDF extraction was successful (PDF processor returns 'text' and 'metadata')
        if 'text' not in text_result or not text_result['text']:
            error_msg = text_result.get('error', 'Failed to extract text from PDF')
            click.echo(f"❌ PDF text extraction failed: {error_msg}", err=True)
            sys.exit(1)
        
        text = text_result['text']
        click.echo(f"📊 Extracted {len(text):,} characters from PDF")
        
        # Estimate processing time
        estimated_time = estimate_processing_time(len(text), passes)
        click.echo(f"⏱️  Estimated processing time: {estimated_time}")
        
        # Get template configuration
        if custom_template:
            click.echo(f"📋 Loading custom template: {custom_template}")
            template_config = load_custom_template(custom_template)
        elif template:
            click.echo(f"📋 Using built-in template: {template}")
            template_config = template_manager.get_template(template)
        else:
            click.echo("❌ Please specify either --template or --custom-template", err=True)
            sys.exit(1)
        
        # Override template settings with CLI parameters
        template_config['settings']['extraction_passes'] = passes
        template_config['settings']['max_workers'] = workers
        
        # Perform extraction
        click.echo(f"🤖 Starting extraction with {model}...")
        with click.progressbar(length=100, label='Extracting') as bar:
            try:
                results = extractor.extract_with_template(text, template_config)
                bar.update(100)
            except Exception as e:
                bar.update(100)
                click.echo(f"\n❌ Extraction failed: {str(e)}", err=True)
                sys.exit(1)
        
        # Ensure results is a dictionary
        if not isinstance(results, dict):
            click.echo(f"❌ Error: Expected dictionary result, got {type(results)}: {results}", err=True)
            sys.exit(1)
        
        # Display summary
        summary = format_extraction_summary(results)
        click.echo(f"\n{summary}")
        
        # Check if extraction was successful
        if not results.get('success', False):
            error_msg = results.get('error', 'Unknown error')
            click.echo(f"❌ Extraction failed: {error_msg}", err=True)
            sys.exit(1)
        
        # Generate output filename if not provided
        if not output:
            pdf_name = Path(pdf_path).stem
            template_name = template or Path(custom_template).stem if custom_template else 'custom'
            output = f"{pdf_name}_{template_name}_extracted.{format}"
        
        # Save results
        click.echo(f"💾 Saving results to: {output}")
        success = extractor.save_results(results, output, format)
        
        if not success:
            click.echo("❌ Failed to save results", err=True)
            sys.exit(1)
        
        # Generate visualization if requested
        if visualize and format != 'html':
            # Save as JSONL for visualization
            jsonl_path = str(Path(output).with_suffix('.jsonl'))
            extractor.save_results(results, jsonl_path, 'jsonl')
            
            # Generate HTML visualization
            html_path = str(Path(output).with_suffix('.html'))
            click.echo(f"🎨 Generating visualization: {html_path}")
            viz_result = extractor.generate_visualization(jsonl_path, html_path)
            
            if viz_result:
                click.echo(f"✅ Visualization saved to: {html_path}")
            else:
                click.echo("⚠️  Visualization generation failed")
        
        click.echo("✅ Extraction completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False))
@click.option('--template', '-t', help='Template name for all PDFs')
@click.option('--custom-template', '-c', type=click.Path(exists=True), help='Path to custom template JSON file')
@click.option('--output-dir', '-o', help='Output directory (default: ./batch_results)')
@click.option('--format', '-f', default='json', help='Output format: json, jsonl, csv')
@click.option('--model', '-m', default='gemini-2.5-flash', help='LLM model to use')
@click.option('--passes', '-p', default=1, type=int, help='Number of extraction passes')
@click.option('--workers', '-w', default=5, type=int, help='Number of parallel workers')
@click.option('--max-files', default=None, type=int, help='Maximum number of files to process')
def batch(directory, template, custom_template, output_dir, format, model, passes, workers, max_files):
    """Process multiple PDF files in a directory."""
    
    print_banner()
    
    # Validate API key
    api_valid, api_key, recommended_model = validate_api_key(interactive=True)
    if not api_valid:
        click.echo("❌ API key validation failed.", err=True)
        sys.exit(1)
    
    # Find PDF files
    try:
        pdf_files = find_pdf_files(directory)
        if not pdf_files:
            click.echo(f"❌ No PDF files found in {directory}", err=True)
            sys.exit(1)
        
        if max_files:
            pdf_files = pdf_files[:max_files]
        
        click.echo(f"📁 Found {len(pdf_files)} PDF files to process")
        
    except Exception as e:
        click.echo(f"❌ Error finding PDF files: {str(e)}", err=True)
        sys.exit(1)
    
    # Setup output directory
    if not output_dir:
        output_dir = "./batch_results"
    
    create_output_directory(output_dir)
    
    # Initialize components
    pdf_processor = PDFProcessor()
    extractor = StructuredExtractor(model_id=model)
    template_manager = TemplateManager()
    
    # Get template configuration
    try:
        if custom_template:
            template_config = load_custom_template(custom_template)
        elif template:
            template_config = template_manager.get_template(template)
        else:
            click.echo("❌ Please specify either --template or --custom-template", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Template error: {str(e)}", err=True)
        sys.exit(1)
    
    # Override template settings
    template_config['settings']['extraction_passes'] = passes
    template_config['settings']['max_workers'] = workers
    
    # Process files
    results_summary = []
    
    with click.progressbar(pdf_files, label='Processing PDFs') as bar:
        for pdf_file in bar:
            try:
                # Extract text
                text_result = pdf_processor.extract_text(str(pdf_file))
                # Check if PDF extraction was successful
                if 'text' not in text_result or not text_result['text']:
                    error_msg = text_result.get('error', 'Failed to extract text from PDF')
                    results_summary.append({
                        'file': pdf_file.name,
                        'status': 'failed',
                        'error': error_msg
                    })
                    continue
                
                # Extract structured data
                results = extractor.extract_with_template(text_result['text'], template_config)
                
                # Save results
                output_file = Path(output_dir) / f"{pdf_file.stem}_extracted.{format}"
                success = extractor.save_results(results, str(output_file), format)
                
                results_summary.append({
                    'file': pdf_file.name,
                    'status': 'success' if success else 'save_failed',
                    'extractions': len(results.get('extractions', [])),
                    'output_file': str(output_file) if success else None
                })
                
            except Exception as e:
                results_summary.append({
                    'file': pdf_file.name,
                    'status': 'error',
                    'error': str(e)
                })
    
    # Display summary
    click.echo("\n📊 Batch Processing Summary:")
    successful = sum(1 for r in results_summary if r['status'] == 'success')
    failed = len(results_summary) - successful
    
    click.echo(f"✅ Successful: {successful}")
    click.echo(f"❌ Failed: {failed}")
    
    if failed > 0:
        click.echo("\n❌ Failed files:")
        for result in results_summary:
            if result['status'] != 'success':
                click.echo(f"   • {result['file']}: {result.get('error', result['status'])}")
    
    # Save summary report
    summary_file = Path(output_dir) / "batch_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    click.echo(f"\n📋 Summary report saved to: {summary_file}")
    click.echo("✅ Batch processing completed!")


@cli.command()
def templates():
    """List available built-in templates."""
    template_manager = TemplateManager()
    available_templates = template_manager.list_templates()
    
    click.echo("📋 Available Built-in Templates:")
    for template_name in available_templates:
        template_config = template_manager.get_template(template_name)
        description = template_config.get('description', 'No description available')
        click.echo(f"  • {template_name}: {description}")
    
    click.echo(f"\nTotal: {len(available_templates)} templates")
    click.echo("\nUsage: pdf_extractor.py extract <pdf_file> --template <template_name>")


@cli.command()
def models():
    """Show model recommendations and information."""
    recommendations = get_model_recommendations()
    
    click.echo("🤖 Model Recommendations:")
    for use_case, model in recommendations.items():
        click.echo(f"  • {use_case.replace('_', ' ').title()}: {model}")
    
    click.echo("\nSupported Models:")
    click.echo("  • gemini-2.5-flash (Fast, cost-effective)")
    click.echo("  • gemini-2.5-pro (High accuracy, complex reasoning)")
    click.echo("  • gpt-4 (OpenAI, requires OPENAI_API_KEY)")
    click.echo("  • gpt-3.5-turbo (OpenAI, faster)")
    
    click.echo("\nUsage: pdf_extractor.py extract <pdf_file> --model <model_name>")


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
def info(pdf_path):
    """Get information about a PDF file."""
    pdf_processor = PDFProcessor()
    
    click.echo(f"📄 PDF Information: {pdf_path}")
    
    try:
        # Get PDF metadata and text sample
        text_result = pdf_processor.extract_text(pdf_path)
        
        if 'text' in text_result and text_result['text']:
            text = text_result['text']
            metadata = text_result['metadata']
            
            click.echo(f"📊 Text length: {len(text):,} characters")
            click.echo(f"📖 Pages: {metadata.get('pages', 'Unknown')}")
            click.echo(f"🔧 Extraction method: {metadata.get('method', 'Unknown')}")
            
            # Show text sample
            sample_length = min(500, len(text))
            sample = text[:sample_length]
            if len(text) > sample_length:
                sample += "..."
            
            click.echo(f"\n📝 Text Sample (first {sample_length} characters):")
            click.echo("-" * 60)
            click.echo(sample)
            click.echo("-" * 60)
            
            # Processing time estimate
            estimated_time = estimate_processing_time(len(text))
            click.echo(f"\n⏱️  Estimated processing time: {estimated_time}")
            
        else:
            click.echo(f"❌ Failed to extract text: {text_result['error']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")


if __name__ == '__main__':
    cli()
