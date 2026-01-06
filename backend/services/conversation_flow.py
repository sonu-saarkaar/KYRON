"""
Conversation Flow Handler for KYRON
Manages intelligent conversation flow like ChatGPT/Gemini
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConversationFlow:
    """Manages conversation flow and context"""
    
    def __init__(self):
        self.context = {}
    
    def detect_intent(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Detect user intent from text
        
        Returns:
            Intent dict with type, service, confidence, etc.
        """
        text_lower = text.lower()
        
        # Service intents
        service_intents = {
            "pan_card": {
                "en": ["pan card", "pan", "permanent account number", "apply for pan", "get pan"],
                "hi": ["पैन", "पैन कार्ड", "पैन कार्ड बनवाना", "पैन के लिए आवेदन"]
            },
            "income_certificate": {
                "en": ["income certificate", "income", "salary certificate", "apply for income certificate"],
                "hi": ["आय प्रमाण पत्र", "आय", "वेतन प्रमाण पत्र", "आय प्रमाण पत्र के लिए आवेदन"]
            },
            "caste_certificate": {
                "en": ["caste certificate", "caste", "category certificate"],
                "hi": ["जाति प्रमाण पत्र", "जाति", "श्रेणी प्रमाण पत्र"]
            },
            "domicile": {
                "en": ["domicile", "domicile certificate", "residence certificate"],
                "hi": ["निवास प्रमाण पत्र", "डोमिसाइल", "निवास"]
            },
            "bihar_residence_certificate": {
                "en": ["bihar residence certificate", "bihar residence", "brc", "niwas praman patra", "residence certificate bihar"],
                "hi": ["बिहार निवास प्रमाण पत्र", "बिहार निवास", "निवास प्रमाण पत्र बिहार", "निवास बनवाना"]
            }
        }
        
        # Check for service requests
        for service_id, keywords in service_intents.items():
            lang_keywords = keywords.get(language, keywords.get("en", []))
            if any(keyword in text_lower for keyword in lang_keywords):
                return {
                    "type": "service_request",
                    "service_id": service_id,
                    "confidence": 0.9,
                    "requires_confirmation": True
                }
        
        # Confirmation intents
        confirmation_keywords = {
            "en": ["yes", "proceed", "continue", "ok", "sure", "go ahead", "start"],
            "hi": ["हाँ", "आगे", "जारी", "ठीक", "बिल्कुल", "शुरू करें"]
        }
        
        lang_confirm = confirmation_keywords.get(language, confirmation_keywords["en"])
        if any(keyword in text_lower for keyword in lang_confirm):
            return {
                "type": "confirmation",
                "confidence": 0.85
            }
        
        # Greeting intents
        greeting_keywords = {
            "en": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "hi": ["नमस्ते", "नमस्कार", "हैलो", "सुप्रभात", "शुभ संध्या"]
        }
        
        lang_greetings = greeting_keywords.get(language, greeting_keywords["en"])
        if any(keyword in text_lower for keyword in lang_greetings):
            return {
                "type": "greeting",
                "confidence": 0.9
            }
        
        # Question intents
        question_keywords = {
            "en": ["what", "how", "when", "where", "why", "can you", "help"],
            "hi": ["क्या", "कैसे", "कब", "कहाँ", "क्यों", "क्या आप", "मदद"]
        }
        
        lang_questions = question_keywords.get(language, question_keywords["en"])
        if any(keyword in text_lower for keyword in lang_questions):
            return {
                "type": "question",
                "confidence": 0.7
            }
        
        # Default
        return {
            "type": "general",
            "confidence": 0.5
        }
    
    def generate_response(self, intent: Dict[str, Any], context: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Generate response based on intent and context
        """
        intent_type = intent.get("type")
        
        if intent_type == "service_request":
            service_id = intent.get("service_id")
            service_name = context.get("service_name", service_id)
            
            if language == "hi":
                return {
                    "text": f"मैं {service_name} के लिए आवेदन करने में आपकी मदद कर सकता हूं। क्या आप आगे बढ़ना चाहेंगे?",
                    "actions": [
                        {"label": "हाँ, आगे बढ़ें", "action": "confirm_service", "service_id": service_id},
                        {"label": "नहीं", "action": "cancel"}
                    ],
                    "service_id": service_id,
                    "should_speak": True
                }
            else:
                return {
                    "text": f"I can help you apply for {service_name}. Would you like to proceed?",
                    "actions": [
                        {"label": "Yes, proceed", "action": "confirm_service", "service_id": service_id},
                        {"label": "No", "action": "cancel"}
                    ],
                    "service_id": service_id,
                    "should_speak": True
                }
        
        elif intent_type == "confirmation":
            if context.get("pending_service"):
                if language == "hi":
                    return {
                        "text": "मैं आपकी प्रोफ़ाइल से जानकारी एकत्र कर रहा हूं और आधिकारिक वेबसाइट पर रीडायरेक्ट कर रहा हूं...",
                        "start_automation": True,
                        "service_id": context.get("pending_service"),
                        "service_config": {},
                        "should_speak": True
                    }
                else:
                    return {
                        "text": "I'm gathering information from your profile and redirecting to the official website...",
                        "start_automation": True,
                        "service_id": context.get("pending_service"),
                        "service_config": {},
                        "should_speak": True
                    }
        
        elif intent_type == "greeting":
            if language == "hi":
                return {
                    "text": "नमस्ते! मैं KYRON हूं, आपका AI सहायक। मैं आपकी सरकारी फॉर्म भरने में मदद कर सकता हूं। आप PAN कार्ड, आय प्रमाण पत्र, या अन्य सेवाओं के लिए आवेदन कर सकते हैं।",
                    "should_speak": True
                }
            else:
                return {
                    "text": "Hello! I'm KYRON, your AI assistant. I can help you fill government forms. You can apply for PAN card, income certificate, or other services.",
                    "should_speak": True
                }
        
        # Default response
        if language == "hi":
            return {
                "text": "मैं आपकी कैसे मदद कर सकता हूं? आप PAN कार्ड, आय प्रमाण पत्र, या अन्य सेवाओं के लिए आवेदन कर सकते हैं।",
                "should_speak": False
            }
        else:
            return {
                "text": "How can I help you? You can apply for PAN card, income certificate, or other services.",
                "should_speak": False
            }


# Global instance
_conversation_flow: Optional[ConversationFlow] = None

def get_conversation_flow() -> ConversationFlow:
    """Get or create global conversation flow instance"""
    global _conversation_flow
    if _conversation_flow is None:
        _conversation_flow = ConversationFlow()
    return _conversation_flow

