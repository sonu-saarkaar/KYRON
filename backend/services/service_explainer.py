"""
Service Explanation Generator
Creates structured, comprehensive explanations for services (like PAN Card)
"""

from typing import Dict, Any, Optional
from services_catalog import get_service_definition, ServiceType

def generate_service_explanation(service_id: str, language: str = "en") -> Dict[str, Any]:
    """
    Generate a comprehensive, structured explanation for a service.
    Returns explanation with title, sections, and action buttons.
    """
    service = get_service_definition(service_id)
    if not service:
        return None
    
    if service_id == ServiceType.PAN_CARD:
        return _generate_pan_card_explanation(service, language)
    else:
        return _generate_generic_explanation(service, language)

def _generate_pan_card_explanation(service, language: str) -> Dict[str, Any]:
    """Generate detailed PAN Card explanation"""
    
    if language == "hi":
        return {
            "type": "service_explanation",
            "title": "PAN Card Application – Complete Guide",
            "service_id": service.id.value,
            "sections": [
                {
                    "heading": "PAN Card क्या है?",
                    "content": "PAN (Permanent Account Number) एक 10 अंकों का अल्फ़ान्यूमेरिक नंबर है जो आपको Income Tax Department द्वारा जारी किया जाता है। यह आपकी वित्तीय पहचान का प्रमाण है।"
                },
                {
                    "heading": "PAN Card क्यों जरूरी है?",
                    "content": "• आयकर रिटर्न दाखिल करने के लिए अनिवार्य\n• बैंक खाता खोलने के लिए आवश्यक\n• वित्तीय लेनदेन (₹50,000 से अधिक) के लिए जरूरी\n• संपत्ति खरीदने/बेचने के लिए आवश्यक\n• निवेश और म्यूचुअल फंड के लिए जरूरी"
                },
                {
                    "heading": "कौन आवेदन कर सकता है?",
                    "content": "• व्यक्ति (Individual)\n• कंपनी/फर्म (Company/Firm)\n• HUF (Hindu Undivided Family)\n• NRI (Non-Resident Indian)\n• विदेशी नागरिक (Foreign Citizens)"
                },
                {
                    "heading": "आवश्यक दस्तावेज",
                    "content": "• पहचान प्रमाण (आधार/वोटर ID/ड्राइविंग लाइसेंस)\n• पता प्रमाण\n• जन्म तिथि प्रमाण\n• हाल की फोटो"
                },
                {
                    "heading": "लागत",
                    "content": "• e-PAN (Digital): निःशुल्क\n• Physical PAN Card: ₹110 (NSDL) या ₹93 (UTIITSL)"
                },
                {
                    "heading": "समय",
                    "content": "• e-PAN: 24-48 घंटे\n• Physical PAN Card: 15-20 दिन"
                },
                {
                    "heading": "KYRON कैसे मदद करेगा?",
                    "content": "• आधिकारिक वेबसाइट पर आवेदन खोलना\n• फॉर्म को स्वचालित रूप से भरना\n• आवाज मार्गदर्शन के साथ चरण-दर-चरण सहायता\n• वास्तविक समय में प्रगति ट्रैकिंग"
                }
            ],
            "actions": [
                {
                    "label": "PAN Card के लिए आवेदन करें",
                    "action": "apply_service",
                    "service_id": service.id.value
                },
                {
                    "label": "प्रश्न पूछें",
                    "action": "ask_questions",
                    "service_id": service.id.value
                },
                {
                    "label": "रद्द करें",
                    "action": "cancel"
                }
            ]
        }
    else:  # English
        return {
            "type": "service_explanation",
            "title": "PAN Card Application – Complete Guide",
            "service_id": service.id.value,
            "sections": [
                {
                    "heading": "What is PAN Card?",
                    "content": "PAN (Permanent Account Number) is a 10-character alphanumeric number issued by the Income Tax Department. It serves as proof of your financial identity."
                },
                {
                    "heading": "Why is PAN Card Required?",
                    "content": "• Mandatory for filing income tax returns\n• Required for opening bank accounts\n• Essential for financial transactions above ₹50,000\n• Needed for property transactions\n• Required for investments and mutual funds"
                },
                {
                    "heading": "Who Can Apply?",
                    "content": "• Individuals\n• Companies/Firms\n• HUF (Hindu Undivided Family)\n• NRIs (Non-Resident Indians)\n• Foreign Citizens"
                },
                {
                    "heading": "Required Documents",
                    "content": "• Identity proof (Aadhaar/Voter ID/Driving License)\n• Address proof\n• Date of birth proof\n• Recent photograph"
                },
                {
                    "heading": "Cost",
                    "content": "• e-PAN (Digital): Free\n• Physical PAN Card: ₹110 (NSDL) or ₹93 (UTIITSL)"
                },
                {
                    "heading": "Time Required",
                    "content": "• e-PAN: 24-48 hours\n• Physical PAN Card: 15-20 days"
                },
                {
                    "heading": "How KYRON Will Help",
                    "content": "• Opening the application on the official website\n• Automatically filling the form with your information\n• Step-by-step guidance with voice assistance\n• Real-time progress tracking"
                }
            ],
            "actions": [
                {
                    "label": "Apply for PAN Card",
                    "action": "apply_service",
                    "service_id": service.id.value
                },
                {
                    "label": "Ask Questions",
                    "action": "ask_questions",
                    "service_id": service.id.value
                },
                {
                    "label": "Cancel",
                    "action": "cancel"
                }
            ]
        }

def _generate_generic_explanation(service, language: str) -> Dict[str, Any]:
    """Generate generic explanation for other services"""
    
    if language == "hi":
        return {
            "type": "service_explanation",
            "title": f"{service.name} – Complete Guide",
            "service_id": service.id.value,
            "sections": [
                {
                    "heading": "विवरण",
                    "content": service.description
                },
                {
                    "heading": "लाभ",
                    "content": "\n".join([f"• {benefit}" for benefit in service.benefits])
                },
                {
                    "heading": "आवश्यक दस्तावेज",
                    "content": "\n".join([f"• {doc}" for doc in service.required_documents])
                },
                {
                    "heading": "अनुमानित समय",
                    "content": service.estimated_time
                }
            ],
            "actions": [
                {
                    "label": f"{service.name} के लिए आवेदन करें",
                    "action": "apply_service",
                    "service_id": service.id.value
                },
                {
                    "label": "प्रश्न पूछें",
                    "action": "ask_questions",
                    "service_id": service.id.value
                },
                {
                    "label": "रद्द करें",
                    "action": "cancel"
                }
            ]
        }
    else:
        return {
            "type": "service_explanation",
            "title": f"{service.name} – Complete Guide",
            "service_id": service.id.value,
            "sections": [
                {
                    "heading": "Description",
                    "content": service.description
                },
                {
                    "heading": "Benefits",
                    "content": "\n".join([f"• {benefit}" for benefit in service.benefits])
                },
                {
                    "heading": "Required Documents",
                    "content": "\n".join([f"• {doc}" for doc in service.required_documents])
                },
                {
                    "heading": "Estimated Time",
                    "content": service.estimated_time
                }
            ],
            "actions": [
                {
                    "label": f"Apply for {service.name}",
                    "action": "apply_service",
                    "service_id": service.id.value
                },
                {
                    "label": "Ask Questions",
                    "action": "ask_questions",
                    "service_id": service.id.value
                },
                {
                    "label": "Cancel",
                    "action": "cancel"
                }
            ]
        }

