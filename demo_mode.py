#!/usr/bin/env python3
"""
Demo mode for PDFToStructuredData - Shows the interactive API key feature
without requiring a real API key or making actual API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import validate_api_key, print_banner
import click

def demo_interactive_api_key():
    """Demonstrate the interactive API key feature."""
    print_banner()
    
    click.echo("🎯 DEMO MODE: Interactive API Key Feature")
    click.echo("=" * 60)
    click.echo()
    
    click.echo("This demo shows how the utility handles missing API keys:")
    click.echo("1. Detects missing environment variables")
    click.echo("2. Prompts user to choose provider (Google/OpenAI)")
    click.echo("3. Provides direct links to get API keys")
    click.echo("4. Securely accepts API key input (hidden)")
    click.echo("5. Sets the key for the current session")
    click.echo()
    
    # Clear any existing API keys for demo
    if 'GOOGLE_API_KEY' in os.environ:
        del os.environ['GOOGLE_API_KEY']
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    click.echo("🔍 Checking for API keys...")
    click.echo("No API keys found in environment variables.")
    click.echo()
    
    # Demonstrate the interactive API key validation
    click.echo("🚀 Starting interactive API key setup...")
    api_valid, api_key, recommended_model = validate_api_key(interactive=True)
    
    if api_valid:
        click.echo()
        click.echo("✅ API key validation successful!")
        click.echo("🎉 The utility would now proceed with PDF extraction.")
        click.echo()
        click.echo("In real usage, this would:")
        click.echo("  • Extract text from your PDF")
        click.echo("  • Apply the selected template")
        click.echo("  • Use LangExtract to structure the data")
        click.echo("  • Save results in your chosen format")
    else:
        click.echo("❌ Demo cancelled - no API key provided")

if __name__ == "__main__":
    demo_interactive_api_key()
