"""
KYRON AI Vision Service
Uses GPT-4o or Gemini 1.5 Pro for vision capabilities to analyze screenshots
and understand form fields, mapping user data to DOM elements.
"""

import os
import base64
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class AIVisionService:
    """AI Vision service for screen analysis and form field detection"""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Initialize AI Vision service
        
        Args:
            provider: "openai" or "google" (for Gemini)
            api_key: API key for the selected provider
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"{provider.upper()}_API_KEY not found in environment variables")
        
        # Lazy import to avoid hard dependency when vision is disabled/missing
        if self.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI  # type: ignore
                self.llm = ChatOpenAI(
                    model="gpt-4o",
                    api_key=self.api_key,
                    temperature=0.1
                )
            except Exception as e:
                raise RuntimeError(f"OpenAI vision backend unavailable: {e}")
        elif self.provider == "google":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    google_api_key=self.api_key,
                    temperature=0.1
                )
            except Exception as e:
                raise RuntimeError(f"Gemini vision backend unavailable: {e}")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def analyze_screenshot(self, screenshot_base64: str, html_snippet: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a screenshot to detect form fields and their purpose
        
        Args:
            screenshot_base64: Base64 encoded screenshot image
            html_snippet: Optional HTML snippet of the page for context
            
        Returns:
            Dictionary containing form analysis results
        """
        try:
            # Prepare the image message
            image_message = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{screenshot_base64}"
                }
            }
            
            # Build the prompt
            prompt = """You are KYRON, an AI agent that analyzes web forms to help users auto-fill them.

Analyze this screenshot and identify:
1. What type of form this is (e.g., PAN Card application, Government form, etc.)
2. All form fields visible in the image
3. For each field, identify:
   - Field label/name
   - Field type (text, dropdown, date, file upload, etc.)
   - What user data should fill this field (map to: fullName, dateOfBirth, fatherName, email, phone, address, city, state, pincode, etc.)
   - Field selector (CSS selector, ID, or name attribute if visible)

Return your analysis as JSON in this format:
{
    "form_type": "description of form",
    "confidence": 0.0-1.0,
    "fields": [
        {
            "label": "field label",
            "type": "text|select|date|file|etc",
            "selector": "CSS selector or #id or [name='field']",
            "maps_to": "profile field name",
            "confidence": 0.0-1.0,
            "required": true/false
        }
    ],
    "suggested_actions": ["action1", "action2"]
}

Be precise and accurate. Only include fields you can clearly identify."""
            
            if html_snippet:
                prompt += f"\n\nHTML Context (if helpful):\n{html_snippet[:2000]}"
            
            # Create messages
            messages = [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        image_message
                    ]
                )
            ]
            
            # Get AI response
            response = self.llm.invoke(messages)
            
            # Parse JSON from response
            response_text = response.content
            
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            return {
                "success": True,
                "analysis": analysis,
                "provider": self.provider
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse AI response as JSON: {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"AI Vision analysis failed: {str(e)}"
            }
    
    def map_fields_to_profile(self, detected_fields: List[Dict], user_profile: Dict) -> List[Dict]:
        """
        Map detected form fields to user profile data
        
        Args:
            detected_fields: List of detected fields from AI analysis
            user_profile: User's profile data
            
        Returns:
            List of fields with mapped values
        """
        mapped_fields = []
        
        field_mapping = {
            # Personal Information (English)
            "fullName": ["fullname", "full_name", "name", "applicant name", "full name"],
            "fatherName": ["father_name", "fathername", "father", "parent name", "father's name"],
            "motherName": ["mother_name", "mothername", "mother", "mother's name"],
            
            # Personal Information (Hindi)
            "fullNameHindi": ["name in hindi", "hindi name", "नाम", "name hindi"],
            "fatherNameHindi": ["father name in hindi", "father hindi", "पिता का नाम"],
            "motherNameHindi": ["mother name in hindi", "mother hindi", "माता का नाम"],
            
            # Date & Age
            "dateOfBirth": ["dob", "date_of_birth", "birthdate", "birth_date", "date of birth"],
            "age": ["age", "आयु", "current age"],
            
            # Gender & Caste
            "gender": ["gender", "sex", "लिंग"],
            "caste": ["caste", "जाति"],
            "category": ["category", "reservation category", "वर्ग", "caste category"],
            
            # Government IDs
            "aadhaarNumber": ["aadhaar", "aadhar", "aadhaar number", "आधार"],
            "panNumber": ["pan", "pan number", "pan card", "पैन"],
            "voterIdNumber": ["voter id", "voter card", "election id"],
            
            # Contact
            "email": ["email", "email_address", "e-mail", "email id"],
            "alternateEmail": ["alternate email", "alternative email", "secondary email"],
            "phone": ["phone", "mobile", "phone_number", "contact_number", "mobile number"],
            "alternatePhone": ["alternate phone", "alternate mobile", "secondary phone"],
            "emergencyPhone": ["emergency phone", "emergency contact"],
            
            # Current Address
            "address": ["address", "street_address", "residential_address", "current address"],
            "city": ["city", "शहर"],
            "state": ["state", "राज्य"],
            "pincode": ["pincode", "pin_code", "postal_code", "zip", "पिन कोड"],
            
            # Permanent Address
            "permanentAddress": ["permanent address", "permanent_address", "home address"],
            "permanentCity": ["permanent city", "home city"],
            "permanentState": ["permanent state", "home state"],
            "permanentPincode": ["permanent pincode", "permanent pin"],
            
            # 10th Grade
            "class10Board": ["10th board", "class 10 board", "10 board", "tenth board"],
            "class10School": ["10th school", "class 10 school", "tenth school"],
            "class10Year": ["10th year", "class 10 year", "10 passing year"],
            "class10Percentage": ["10th percentage", "class 10 percentage", "10 marks"],
            "class10RollNumber": ["10th roll", "class 10 roll", "10 roll number"],
            
            # 12th Grade
            "class12Board": ["12th board", "class 12 board", "12 board", "twelfth board"],
            "class12School": ["12th school", "class 12 school", "twelfth school"],
            "class12Year": ["12th year", "class 12 year", "12 passing year"],
            "class12Percentage": ["12th percentage", "class 12 percentage", "12 marks"],
            "class12RollNumber": ["12th roll", "class 12 roll", "12 roll number"],
            "class12Stream": ["12th stream", "class 12 stream", "subject stream"],
            
            # Current Education
            "currentEducation": ["current education", "education status", "pursuing"],
            "currentInstitution": ["current college", "current university", "current institution"],
            "currentCourse": ["current course", "course name", "program"],
            "currentYear": ["current year", "current semester", "year/semester"],
            
            # Higher Education
            "qualification": ["qualification", "education", "educational qualification", "highest qualification"],
            "university": ["university", "college", "institution"],
            
            # Occupation
            "occupation": ["occupation", "profession", "job", "work", "व्यवसाय"],
            
            # Bank Details
            "bankName": ["bank_name", "bank", "bank name"],
            "accountNumber": ["account_number", "acc_no", "account no", "bank account"],
            "ifsc": ["ifsc", "ifsc_code", "ifsc code"],
            
            # Documents
            "photoUrl": ["photo", "photograph", "image", "passport photo"],
            "signatureUrl": ["signature", "sign", "हस्ताक्षर"]
        }
        
        for field in detected_fields:
            mapped_field = field.copy()
            maps_to = field.get("maps_to", "").lower()
            
            # Find matching profile field
            for profile_key, possible_names in field_mapping.items():
                if maps_to in possible_names or any(name in maps_to for name in possible_names):
                    if profile_key in user_profile and user_profile[profile_key]:
                        mapped_field["value"] = user_profile[profile_key]
                        mapped_field["mapped_profile_field"] = profile_key
                        break
            
            mapped_fields.append(mapped_field)
        
        return mapped_fields
    
    def suggest_filling_strategy(self, form_analysis: Dict) -> Dict[str, Any]:
        """
        Suggest optimal filling strategy based on form analysis
        
        Args:
            form_analysis: Complete form analysis result
            
        Returns:
            Strategy recommendations
        """
        fields = form_analysis.get("analysis", {}).get("fields", [])
        
        required_fields = [f for f in fields if f.get("required", False)]
        optional_fields = [f for f in fields if not f.get("required", False)]
        
        strategy = {
            "fill_order": [],
            "attention_needed": [],
            "estimated_time": len(fields) * 2,  # seconds
            "risks": []
        }
        
        # Order: required fields first, then optional
        strategy["fill_order"] = [f["selector"] for f in required_fields] + [f["selector"] for f in optional_fields]
        
        # Check for risky fields (OTP, CAPTCHA, etc.)
        risky_keywords = ["otp", "captcha", "verification", "code"]
        for field in fields:
            label_lower = field.get("label", "").lower()
            if any(keyword in label_lower for keyword in risky_keywords):
                strategy["attention_needed"].append(field["selector"])
                strategy["risks"].append(f"{field['label']} requires manual input")
        
        return strategy


# Factory function for easy initialization
def create_ai_vision_service(provider: Optional[str] = None) -> Optional[AIVisionService]:
    """
    Factory function to create AI Vision service.
    If required dependencies or API keys are missing, returns None so callers can fall back.
    """
    provider = provider or os.getenv("AI_PROVIDER", "openai")
    try:
        return AIVisionService(provider=provider)
    except Exception as e:
        logger.warning(f"AI Vision disabled (dependency/key missing): {e}")
        return None

