"""
Built-in template definitions for common document types.
"""

import langextract as lx
from typing import Dict, Any, List


class TemplateManager:
    """Manages built-in and custom extraction templates."""
    
    def __init__(self):
        self.built_in_templates = {
            'invoice': self._get_invoice_template(),
            'resume': self._get_resume_template(),
            'research_paper': self._get_research_paper_template(),
            'medical_report': self._get_medical_report_template(),
            'contract': self._get_contract_template(),
            'receipt': self._get_receipt_template(),
            'academic_paper': self._get_academic_paper_template(),
            'bank_statement': self._get_bank_statement_template(),
            'business_card': self._get_business_card_template(),
            'tax_document': self._get_tax_document_template()
        }
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Get a template by name."""
        if template_name in self.built_in_templates:
            return self.built_in_templates[template_name]
        else:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.built_in_templates.keys())}")
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.built_in_templates.keys())
    
    def _get_invoice_template(self) -> Dict[str, Any]:
        """Template for invoice documents."""
        return {
            'name': 'invoice',
            'description': 'Extract key information from invoices',
            'prompt': '''Extract invoice information including vendor details, amounts, dates, line items, and tax information. 
            Use exact text from the document. Provide meaningful attributes for context.''',
            'examples': [
                {
                    'text': '''INVOICE #INV-2024-001
                    From: TechSupply Corp
                    123 Business Ave, Tech City, TC 12345
                    To: ABC Company
                    456 Client St, Business Town, BT 67890
                    
                    Date: January 15, 2024
                    Due Date: February 15, 2024
                    
                    Item                    Qty    Price    Total
                    Laptop Computer         2      $1,200   $2,400
                    Software License        1      $500     $500
                    
                    Subtotal: $2,900
                    Tax (8%): $232
                    Total: $3,132''',
                    'extractions': [
                        {
                            'extraction_class': 'vendor',
                            'extraction_text': 'TechSupply Corp',
                            'attributes': {'type': 'company_name'}
                        },
                        {
                            'extraction_class': 'invoice_number',
                            'extraction_text': 'INV-2024-001',
                            'attributes': {'format': 'alphanumeric'}
                        },
                        {
                            'extraction_class': 'total_amount',
                            'extraction_text': '$3,132',
                            'attributes': {'currency': 'USD', 'includes_tax': True}
                        },
                        {
                            'extraction_class': 'due_date',
                            'extraction_text': 'February 15, 2024',
                            'attributes': {'format': 'full_date'}
                        },
                        {
                            'extraction_class': 'line_item',
                            'extraction_text': 'Laptop Computer',
                            'attributes': {'quantity': '2', 'unit_price': '$1,200', 'total': '$2,400'}
                        }
                    ]
                }
            ],
            'settings': {
                'extraction_passes': 2,
                'max_workers': 5,
                'max_char_buffer': 800
            }
        }
    
    def _get_resume_template(self) -> Dict[str, Any]:
        """Template for resume documents."""
        return {
            'name': 'resume',
            'description': 'Extract personal information, skills, experience, and education from resumes',
            'prompt': '''Extract resume information including personal details, skills, work experience, education, and contact information.
            Focus on exact text and provide context through attributes.''',
            'examples': [
                {
                    'text': '''John Smith
                    Software Engineer
                    john.smith@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johnsmith
                    
                    EXPERIENCE
                    Senior Software Engineer | TechCorp Inc. | 2020-2024
                    • Developed web applications using Python and React
                    • Led team of 5 developers on microservices architecture
                    • Improved system performance by 40%
                    
                    EDUCATION
                    Bachelor of Science in Computer Science
                    University of Technology | 2016-2020 | GPA: 3.8
                    
                    SKILLS
                    Programming: Python, JavaScript, Java, SQL
                    Frameworks: React, Django, Spring Boot''',
                    'extractions': [
                        {
                            'extraction_class': 'name',
                            'extraction_text': 'John Smith',
                            'attributes': {'type': 'full_name'}
                        },
                        {
                            'extraction_class': 'contact',
                            'extraction_text': 'john.smith@email.com',
                            'attributes': {'type': 'email'}
                        },
                        {
                            'extraction_class': 'experience',
                            'extraction_text': 'Senior Software Engineer | TechCorp Inc. | 2020-2024',
                            'attributes': {'role': 'Senior Software Engineer', 'company': 'TechCorp Inc.', 'duration': '2020-2024'}
                        },
                        {
                            'extraction_class': 'education',
                            'extraction_text': 'Bachelor of Science in Computer Science',
                            'attributes': {'degree': 'Bachelor of Science', 'field': 'Computer Science', 'gpa': '3.8'}
                        },
                        {
                            'extraction_class': 'skill',
                            'extraction_text': 'Python',
                            'attributes': {'category': 'programming_language'}
                        }
                    ]
                }
            ],
            'settings': {
                'extraction_passes': 2,
                'max_workers': 8,
                'max_char_buffer': 1200
            }
        }
    
    def _get_research_paper_template(self) -> Dict[str, Any]:
        """Template for research papers."""
        return {
            'name': 'research_paper',
            'description': 'Extract title, authors, abstract, methodology, findings from research papers',
            'prompt': '''Extract key information from academic research papers including title, authors, abstract, methodology, 
            key findings, and conclusions. Preserve exact text and provide academic context.''',
            'examples': [
                {
                    'text': '''Deep Learning Approaches for Natural Language Processing
                    
                    Authors: Dr. Jane Doe¹, Prof. John Smith², Dr. Alice Johnson¹
                    ¹University of AI, ²Tech Institute
                    
                    Abstract
                    This paper presents novel deep learning approaches for natural language processing tasks.
                    We propose a transformer-based architecture that achieves state-of-the-art results on 
                    multiple benchmarks. Our method improves accuracy by 15% over previous approaches.
                    
                    1. Introduction
                    Natural language processing has seen significant advances with deep learning...
                    
                    2. Methodology
                    We implemented a multi-head attention mechanism with positional encoding...
                    
                    3. Results
                    Our experiments on the GLUE benchmark show improvements across all tasks...''',
                    'extractions': [
                        {
                            'extraction_class': 'title',
                            'extraction_text': 'Deep Learning Approaches for Natural Language Processing',
                            'attributes': {'type': 'main_title'}
                        },
                        {
                            'extraction_class': 'author',
                            'extraction_text': 'Dr. Jane Doe',
                            'attributes': {'affiliation': 'University of AI', 'position': 'first_author'}
                        },
                        {
                            'extraction_class': 'finding',
                            'extraction_text': 'improves accuracy by 15% over previous approaches',
                            'attributes': {'type': 'performance_improvement', 'metric': 'accuracy'}
                        },
                        {
                            'extraction_class': 'methodology',
                            'extraction_text': 'multi-head attention mechanism with positional encoding',
                            'attributes': {'type': 'architecture_component'}
                        }
                    ]
                }
            ],
            'settings': {
                'extraction_passes': 3,
                'max_workers': 15,
                'max_char_buffer': 1500
            }
        }
    
    def _get_medical_report_template(self) -> Dict[str, Any]:
        """Template for medical reports."""
        return {
            'name': 'medical_report',
            'description': 'Extract patient information, diagnosis, medications, and recommendations from medical reports',
            'prompt': '''Extract medical information including patient details, symptoms, diagnosis, medications, 
            and treatment recommendations. Maintain medical accuracy and provide clinical context.''',
            'examples': [
                {
                    'text': '''MEDICAL REPORT
                    Patient: Mary Johnson, DOB: 03/15/1980, MRN: 12345
                    Date of Visit: January 20, 2024
                    
                    Chief Complaint: Persistent cough and fatigue for 2 weeks
                    
                    Physical Examination:
                    - Temperature: 100.2°F
                    - Blood pressure: 120/80 mmHg
                    - Lung sounds: Mild wheezing in lower lobes
                    
                    Assessment and Plan:
                    1. Bronchitis, likely viral
                    2. Prescribe: Albuterol inhaler, 2 puffs every 4-6 hours as needed
                    3. Follow-up in 1 week if symptoms persist
                    4. Return immediately if breathing difficulty worsens''',
                    'extractions': [
                        {
                            'extraction_class': 'patient',
                            'extraction_text': 'Mary Johnson',
                            'attributes': {'dob': '03/15/1980', 'mrn': '12345'}
                        },
                        {
                            'extraction_class': 'diagnosis',
                            'extraction_text': 'Bronchitis, likely viral',
                            'attributes': {'type': 'primary_diagnosis', 'certainty': 'likely'}
                        },
                        {
                            'extraction_class': 'medication',
                            'extraction_text': 'Albuterol inhaler',
                            'attributes': {'dosage': '2 puffs every 4-6 hours', 'frequency': 'as needed'}
                        },
                        {
                            'extraction_class': 'vital_sign',
                            'extraction_text': 'Temperature: 100.2°F',
                            'attributes': {'type': 'temperature', 'value': '100.2', 'unit': 'fahrenheit'}
                        }
                    ]
                }
            ],
            'settings': {
                'extraction_passes': 2,
                'max_workers': 5,
                'max_char_buffer': 1000
            }
        }
    
    def _get_contract_template(self) -> Dict[str, Any]:
        """Template for contract documents."""
        return {
            'name': 'contract',
            'description': 'Extract parties, terms, dates, obligations, and key clauses from contracts',
            'prompt': '''Extract contract information including parties involved, key terms, dates, obligations, 
            payment terms, and important clauses. Preserve legal language accuracy.''',
            'examples': [
                {
                    'text': '''SERVICE AGREEMENT
                    
                    This Service Agreement ("Agreement") is entered into on January 1, 2024, 
                    between TechServices LLC ("Provider") and BusinessCorp Inc. ("Client").
                    
                    1. SERVICES
                    Provider agrees to provide software development services as detailed in Exhibit A.
                    
                    2. TERM
                    This Agreement shall commence on January 1, 2024, and shall continue for 
                    twelve (12) months, unless terminated earlier in accordance with this Agreement.
                    
                    3. COMPENSATION
                    Client shall pay Provider $10,000 per month, due on the first day of each month.
                    Late payments shall incur a 1.5% monthly fee.
                    
                    4. TERMINATION
                    Either party may terminate this Agreement with thirty (30) days written notice.''',
                    'extractions': [
                        {
                            'extraction_class': 'party',
                            'extraction_text': 'TechServices LLC',
                            'attributes': {'role': 'provider', 'type': 'company'}
                        },
                        {
                            'extraction_class': 'party',
                            'extraction_text': 'BusinessCorp Inc.',
                            'attributes': {'role': 'client', 'type': 'company'}
                        },
                        {
                            'extraction_class': 'term',
                            'extraction_text': 'twelve (12) months',
                            'attributes': {'start_date': 'January 1, 2024', 'type': 'duration'}
                        },
                        {
                            'extraction_class': 'payment',
                            'extraction_text': '$10,000 per month',
                            'attributes': {'frequency': 'monthly', 'due_date': 'first day of each month'}
                        },
                        {
                            'extraction_class': 'termination_clause',
                            'extraction_text': 'thirty (30) days written notice',
                            'attributes': {'notice_period': '30 days', 'method': 'written'}
                        }
                    ]
                }
            ],
            'settings': {
                'extraction_passes': 2,
                'max_workers': 8,
                'max_char_buffer': 1200
            }
        }
    
    def _get_receipt_template(self) -> Dict[str, Any]:
        """Template for retail receipts."""
        from .templates_extension import get_receipt_template
        return get_receipt_template()
    
    def _get_academic_paper_template(self) -> Dict[str, Any]:
        """Template for academic papers."""
        from .templates_extension import get_academic_paper_template
        return get_academic_paper_template()
    
    def _get_bank_statement_template(self) -> Dict[str, Any]:
        """Template for bank statements."""
        from .templates_extension import get_bank_statement_template
        return get_bank_statement_template()
    
    def _get_business_card_template(self) -> Dict[str, Any]:
        """Template for business cards."""
        from .templates_extension import get_business_card_template
        return get_business_card_template()
    
    def _get_tax_document_template(self) -> Dict[str, Any]:
        """Template for tax documents."""
        from .templates_extension import get_tax_document_template
        return get_tax_document_template()
