"""
KYRON Form Field Mapper Service
Intelligently maps detected form fields to user profile data using AI
"""

from typing import Dict, List, Optional, Any
from services.ai_vision import create_ai_vision_service
from services.date_formatter import DateFormatter
import logging

logger = logging.getLogger(__name__)

class FormFieldMapper:
    """Service to map form fields to user profile data"""
    
    def __init__(self):
        """Initialize form field mapper"""
        self.ai_vision_service = None
        try:
            self.ai_vision_service = create_ai_vision_service()
        except Exception as e:
            logger.warning(f"AI Vision service not available: {str(e)}")
    
    def map_fields_to_profile(self, detected_fields: List[Dict], user_profile: Dict) -> List[Dict]:
        """
        Map detected form fields to user profile data
        
        Args:
            detected_fields: List of detected fields from AI analysis or DOM scan
            user_profile: User's profile data dictionary
            
        Returns:
            List of mapped fields with values and confidence scores
        """
        mapped_fields = []
        
        # Comprehensive Field name mapping patterns for all profile fields
        field_mapping_patterns = {
            # Personal Information (English)
            "fullName": {
                "patterns": ["fullname", "full_name", "name", "applicant name", "full name", "candidate name", "applicant's name"],
                "variations": ["firstname", "lastname", "given name", "surname", "complete name"]
            },
            "fatherName": {
                "patterns": ["father_name", "fathername", "father", "parent name", "father's name", "fathers name", "father name"],
                "variations": ["guardian name", "parent's name"]
            },
            "motherName": {
                "patterns": ["mother_name", "mothername", "mother", "mother's name", "mothers name", "mother name"],
                "variations": []
            },
            
            # Personal Information (Hindi)
            "fullNameHindi": {
                "patterns": ["name in hindi", "hindi name", "नाम", "हिंदी में नाम", "name hindi"],
                "variations": ["naam hindi", "naam"]
            },
            "fatherNameHindi": {
                "patterns": ["father name in hindi", "father hindi", "पिता का नाम", "father name hindi"],
                "variations": ["pita ka naam"]
            },
            "motherNameHindi": {
                "patterns": ["mother name in hindi", "mother hindi", "माता का नाम", "mother name hindi"],
                "variations": ["mata ka naam"]
            },
            
            # Date of Birth & Age
            "dateOfBirth": {
                "patterns": ["dob", "date_of_birth", "birthdate", "birth_date", "date of birth", "birth date", "जन्म तिथि"],
                "variations": ["birthday", "birth day", "date_birth"]
            },
            "age": {
                "patterns": ["age", "आयु", "current age"],
                "variations": ["years old", "yrs"]
            },
            
            # Gender & Caste/Category
            "gender": {
                "patterns": ["gender", "sex", "लिंग"],
                "variations": ["male/female"]
            },
            "caste": {
                "patterns": ["caste", "जाति", "caste name"],
                "variations": ["community"]
            },
            "category": {
                "patterns": ["category", "reservation category", "वर्ग", "social category", "caste category"],
                "variations": ["gen/obc/sc/st", "reservation", "quota"]
            },
            
            # Government ID Documents
            "aadhaarNumber": {
                "patterns": ["aadhaar", "aadhar", "aadhaar number", "aadhar number", "uid", "आधार", "aadhaar no"],
                "variations": ["aadhar card", "aadhaar card number", "uid number"]
            },
            "panNumber": {
                "patterns": ["pan", "pan number", "pan card", "पैन", "pan no", "pan card number"],
                "variations": ["permanent account number", "income tax pan"]
            },
            "voterIdNumber": {
                "patterns": ["voter id", "voter card", "election id", "epic number", "voter id number"],
                "variations": ["voter card number", "election card"]
            },
            
            # Contact Information
            "email": {
                "patterns": ["email", "email_address", "e-mail", "e mail", "email id", "ईमेल"],
                "variations": ["emailid", "mail", "email address"]
            },
            "alternateEmail": {
                "patterns": ["alternate email", "alternative email", "secondary email", "other email", "email 2"],
                "variations": ["backup email", "second email"]
            },
            "phone": {
                "patterns": ["phone", "mobile", "phone_number", "contact_number", "mobile number", "phone no", "मोबाइल"],
                "variations": ["contact", "mobile no", "phone number", "tel", "telephone"]
            },
            "alternatePhone": {
                "patterns": ["alternate phone", "alternate mobile", "alternative phone", "secondary phone", "phone 2"],
                "variations": ["second phone", "other phone", "alternate contact"]
            },
            "emergencyPhone": {
                "patterns": ["emergency phone", "emergency contact", "emergency mobile", "emergency number"],
                "variations": ["emergency contact number"]
            },
            
            # Current Address
            "address": {
                "patterns": ["address", "street_address", "residential_address", "current address", "house address", "पता"],
                "variations": ["addr", "street", "residential address", "correspondence address"]
            },
            "city": {
                "patterns": ["city", "शहर", "town"],
                "variations": ["municipality"]
            },
            "state": {
                "patterns": ["state", "राज्य", "province"],
                "variations": ["state/ut"]
            },
            "pincode": {
                "patterns": ["pincode", "pin_code", "postal_code", "zip", "zipcode", "zip code", "पिन कोड", "pin"],
                "variations": ["postal code", "pin no"]
            },
            
            # Permanent Address
            "permanentAddress": {
                "patterns": ["permanent address", "permanent_address", "home address", "native address", "स्थायी पता"],
                "variations": ["permanent addr", "native place"]
            },
            "permanentCity": {
                "patterns": ["permanent city", "home city", "native city"],
                "variations": ["permanent town"]
            },
            "permanentState": {
                "patterns": ["permanent state", "home state", "native state"],
                "variations": []
            },
            "permanentPincode": {
                "patterns": ["permanent pincode", "permanent pin", "home pincode"],
                "variations": ["permanent postal code"]
            },
            
            # 10th Grade Details
            "class10Board": {
                "patterns": ["10th board", "class 10 board", "10 board", "ssc board", "matriculation board", "tenth board"],
                "variations": ["board 10th", "10th class board"]
            },
            "class10School": {
                "patterns": ["10th school", "class 10 school", "10 school", "ssc school", "tenth school"],
                "variations": ["school 10th", "10th class school"]
            },
            "class10Year": {
                "patterns": ["10th year", "class 10 year", "10 passing year", "ssc year", "tenth year"],
                "variations": ["year of passing 10th", "10th pass year"]
            },
            "class10Percentage": {
                "patterns": ["10th percentage", "class 10 percentage", "10 marks", "ssc percentage", "tenth percentage"],
                "variations": ["10th cgpa", "10th grade", "10th score"]
            },
            "class10RollNumber": {
                "patterns": ["10th roll", "class 10 roll", "10 roll number", "ssc roll", "tenth roll"],
                "variations": ["roll no 10th", "10th roll no"]
            },
            
            # 12th Grade Details
            "class12Board": {
                "patterns": ["12th board", "class 12 board", "12 board", "hsc board", "intermediate board", "twelfth board"],
                "variations": ["board 12th", "12th class board", "senior secondary board"]
            },
            "class12School": {
                "patterns": ["12th school", "class 12 school", "12 school", "hsc school", "twelfth school"],
                "variations": ["school 12th", "12th class school"]
            },
            "class12Year": {
                "patterns": ["12th year", "class 12 year", "12 passing year", "hsc year", "twelfth year"],
                "variations": ["year of passing 12th", "12th pass year"]
            },
            "class12Percentage": {
                "patterns": ["12th percentage", "class 12 percentage", "12 marks", "hsc percentage", "twelfth percentage"],
                "variations": ["12th cgpa", "12th grade", "12th score"]
            },
            "class12RollNumber": {
                "patterns": ["12th roll", "class 12 roll", "12 roll number", "hsc roll", "twelfth roll"],
                "variations": ["roll no 12th", "12th roll no"]
            },
            "class12Stream": {
                "patterns": ["12th stream", "class 12 stream", "12 stream", "hsc stream", "subject stream"],
                "variations": ["stream 12th", "science/commerce/arts"]
            },
            
            # Current Education
            "currentEducation": {
                "patterns": ["current education", "education status", "pursuing", "current study"],
                "variations": ["studying", "current course status"]
            },
            "currentInstitution": {
                "patterns": ["current college", "current university", "current institution", "studying at"],
                "variations": ["present college", "present institution"]
            },
            "currentCourse": {
                "patterns": ["current course", "course name", "program", "pursuing course"],
                "variations": ["current program", "degree pursuing"]
            },
            "currentYear": {
                "patterns": ["current year", "current semester", "year/semester", "present year"],
                "variations": ["studying in year", "current sem"]
            },
            
            # Higher Education
            "qualification": {
                "patterns": ["qualification", "education", "educational qualification", "highest qualification", "शिक्षा"],
                "variations": ["degree", "education level", "highest education"]
            },
            "university": {
                "patterns": ["university", "college", "institution", "विश्वविद्यालय"],
                "variations": ["school", "educational institution", "varsity"]
            },
            
            # Occupation
            "occupation": {
                "patterns": ["occupation", "profession", "job", "work", "व्यवसाय", "employment"],
                "variations": ["career", "job title", "profession"]
            },
            
            # Bank Details
            "bankName": {
                "patterns": ["bank_name", "bank", "bank name", "बैंक का नाम"],
                "variations": ["financial institution", "bank's name"]
            },
            "accountNumber": {
                "patterns": ["account_number", "acc_no", "account no", "account number", "खाता संख्या", "bank account"],
                "variations": ["acc number", "bank account no", "account"]
            },
            "ifsc": {
                "patterns": ["ifsc", "ifsc_code", "ifsc code", "आईएफएससी"],
                "variations": ["ifs code", "bank code", "ifsc no"]
            },
            
            # Documents
            "photoUrl": {
                "patterns": ["photo", "photograph", "image", "passport photo", "picture", "फोटो"],
                "variations": ["photo upload", "profile photo"]
            },
            "signatureUrl": {
                "patterns": ["signature", "sign", "हस्ताक्षर", "digital signature"],
                "variations": ["signature upload", "sign upload"]
            }
        }
        
        for field in detected_fields:
            mapped_field = field.copy()
            maps_to = field.get("maps_to", "").lower() if field.get("maps_to") else ""
            label = field.get("label", "").lower() if field.get("label") else ""
            name = field.get("name", "").lower() if field.get("name") else ""
            field_id = field.get("id", "").lower() if field.get("id") else ""
            
            # Combine all text to match against
            all_text = f"{maps_to} {label} {name} {field_id}".lower().strip()
            
            # Try to find matching profile field
            best_match = None
            best_confidence = 0.0
            
            for profile_key, mapping_info in field_mapping_patterns.items():
                patterns = mapping_info.get("patterns", [])
                variations = mapping_info.get("variations", [])
                
                # Check exact match
                if any(pattern in all_text for pattern in patterns):
                    confidence = 0.95
                    if profile_key in user_profile and user_profile[profile_key]:
                        best_match = profile_key
                        best_confidence = confidence
                        break
                
                # Check variations
                for variation in variations:
                    if variation in all_text:
                        confidence = 0.85
                        if profile_key in user_profile and user_profile[profile_key]:
                            if confidence > best_confidence:
                                best_match = profile_key
                                best_confidence = confidence
            
            # If AI suggested a mapping, use it with higher confidence
            if maps_to and not best_match:
                # Try to match AI suggestion directly
                for profile_key, mapping_info in field_mapping_patterns.items():
                    if any(pattern in maps_to for pattern in mapping_info.get("patterns", [])):
                        if profile_key in user_profile and user_profile[profile_key]:
                            best_match = profile_key
                            best_confidence = 0.90
                            break
            
            # Assign value if match found (check both original and normalized keys)
            value = None
            if best_match:
                # Try camelCase first
                if best_match in user_profile and user_profile[best_match]:
                    value = user_profile[best_match]
                # Try snake_case
                elif '_' in best_match:
                    snake_key = ''.join(word if i == 0 else word.capitalize() for i, word in enumerate(best_match.replace('_', ' ').split()))
                    if snake_key in user_profile and user_profile[snake_key]:
                        value = user_profile[snake_key]
                # Try direct match with different case
                else:
                    for key, val in user_profile.items():
                        if key.lower() == best_match.lower() and val:
                            value = val
                            break
            
            if value:
                # Format value based on field type (especially dates)
                field_label = field.get("label", "")
                field_name = field.get("name", "") or field.get("id", "")
                field_type = field.get("type", "")
                
                # Format date fields to DD/MM/YYYY
                formatted_value = DateFormatter.format_for_field(
                    str(value), 
                    field_name, 
                    field_label, 
                    field_type
                )
                
                mapped_field["value"] = formatted_value
                mapped_field["mapped_profile_field"] = best_match
                mapped_field["mapping_confidence"] = best_confidence
            else:
                mapped_field["value"] = None
                mapped_field["mapped_profile_field"] = None
                mapped_field["mapping_confidence"] = 0.0
            
            mapped_fields.append(mapped_field)
        
        return mapped_fields
    
    def get_fillable_fields(self, mapped_fields: List[Dict], min_confidence: float = 0.7) -> List[Dict]:
        """
        Filter fields that can be filled with high confidence
        
        Args:
            mapped_fields: List of mapped fields
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of fillable fields
        """
        fillable = []
        
        for field in mapped_fields:
            confidence = field.get("mapping_confidence", 0.0)
            value = field.get("value")
            selector = field.get("selector")
            
            # Skip if no selector or value
            if not selector or not value:
                continue
            
            # Skip password, OTP, CAPTCHA fields
            field_type = field.get("type", "").lower()
            label = field.get("label", "").lower()
            
            if any(keyword in field_type or keyword in label for keyword in ["password", "otp", "captcha", "verification"]):
                continue
            
            # Only include high confidence mappings
            if confidence >= min_confidence:
                fillable.append({
                    "selector": selector,
                    "value": value,
                    "label": field.get("label", ""),
                    "confidence": confidence,
                    "profile_field": field.get("mapped_profile_field")
                })
        
        # Sort by confidence (highest first)
        fillable.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return fillable


# Global instance
_form_mapper: Optional[FormFieldMapper] = None

def get_form_mapper() -> FormFieldMapper:
    """Get or create global form mapper instance"""
    global _form_mapper
    if _form_mapper is None:
        _form_mapper = FormFieldMapper()
    return _form_mapper

