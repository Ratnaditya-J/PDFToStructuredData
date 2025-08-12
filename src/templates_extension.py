"""
Extension methods for TemplateManager to load JSON-based templates.
"""

import json
import os
from typing import Dict, Any


def load_json_template(template_name: str) -> Dict[str, Any]:
    """Load a template from a JSON file."""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'templates', 
        f'{template_name}_template.json'
    )
    with open(template_path, 'r') as f:
        return json.load(f)


# Template loader functions for new templates
def get_receipt_template() -> Dict[str, Any]:
    """Template for retail receipts."""
    return load_json_template('receipt')


def get_academic_paper_template() -> Dict[str, Any]:
    """Template for academic papers."""
    return load_json_template('academic_paper')


def get_bank_statement_template() -> Dict[str, Any]:
    """Template for bank statements."""
    return load_json_template('bank_statement')


def get_business_card_template() -> Dict[str, Any]:
    """Template for business cards."""
    return load_json_template('business_card')


def get_tax_document_template() -> Dict[str, Any]:
    """Template for tax documents."""
    return load_json_template('tax_document')


def get_contract_template() -> Dict[str, Any]:
    """Template for contract documents."""
    return load_json_template('contract')
