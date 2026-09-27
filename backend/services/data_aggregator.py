"""
KYRON Data Aggregator Service
Intelligently combines Master Profile + Request Data + Document Vault
to provide complete data for form filling

Priority Order:
1. Request Data (service-specific, user-provided during chat)
2. Master Profile (permanent user data)
3. Document Vault (extracted from uploaded documents)
4. Defaults (fallback values)
"""

from typing import Dict, List, Optional, Any
import logging
from services.database_manager import get_database_manager

logger = logging.getLogger(__name__)

class DataAggregator:
    """
    KYRON's Intelligent Data Aggregator
    Combines all data sources intelligently for form filling
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.master_profile = {}
        self.request_data = {}
        self.document_vault = {}
        self.db_manager = None
        
        try:
            self.db_manager = get_database_manager()
        except:
            pass
    
    def load_master_profile(self) -> Dict[str, Any]:
        """Load user's master profile from database"""
        try:
            if self.db_manager and self.db_manager.is_available():
                profile = self.db_manager.get_profile(self.user_id)
                if profile:
                    self.master_profile = profile
                    logger.info(f"[DataAggregator] Loaded Master Profile with {len(profile)} fields")
                    return profile
        except Exception as e:
            logger.warning(f"[DataAggregator] Could not load Master Profile: {e}")
        
        return {}
    
    def load_document_vault(self) -> Dict[str, Any]:
        """Load data extracted from user's uploaded documents"""
        try:
            if self.db_manager and self.db_manager.is_available():
                documents = self.db_manager.get_user_documents(self.user_id)
                if documents:
                    # Extract data from documents
                    vault_data = {}
                    for doc in documents:
                        extracted_text = doc.get("extracted_text", "")
                        if extracted_text:
                            # Parse extracted text for key-value pairs
                            parsed_data = self._parse_document_text(extracted_text)
                            vault_data.update(parsed_data)
                    
                    self.document_vault = vault_data
                    logger.info(f"[DataAggregator] Loaded Document Vault with {len(vault_data)} fields")
                    return vault_data
        except Exception as e:
            logger.warning(f"[DataAggregator] Could not load Document Vault: {e}")
        
        return {}
    
    def _parse_document_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted document text to extract key-value pairs"""
        parsed = {}
        
        # Common patterns in Indian documents
        patterns = {
            "aadhaarNumber": [
                r"(\d{4}\s?\d{4}\s?\d{4})",  # Aadhaar format
                r"Aadhaar[:\s]+(\d{12})",
                r"UID[:\s]+(\d{12})"
            ],
            "panNumber": [
                r"([A-Z]{5}\d{4}[A-Z])",  # PAN format
                r"PAN[:\s]+([A-Z]{5}\d{4}[A-Z])"
            ],
            "fullName": [
                r"Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
                r"Full Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
            ],
            "dateOfBirth": [
                r"DOB[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})",
                r"Date of Birth[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})"
            ],
            "fatherName": [
                r"Father[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
                r"Father's Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
            ],
            "address": [
                r"Address[:\s]+([A-Za-z0-9\s,.-]+)",
                r"Residential Address[:\s]+([A-Za-z0-9\s,.-]+)"
            ]
        }
        
        import re
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parsed[field] = match.group(1).strip()
                    break
        
        return parsed
    
    def set_request_data(self, request_data: Dict[str, Any]):
        """Set service-specific request data collected during chat"""
        self.request_data = request_data or {}
        logger.info(f"[DataAggregator] Set Request Data with {len(self.request_data)} fields")
    
    def get_unified_data(self, field_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Get unified data combining all sources with priority
        
        Priority Order:
        1. Request Data (highest priority - user explicitly provided)
        2. Master Profile (permanent user data)
        3. Document Vault (extracted from documents)
        4. Defaults (fallback)
        
        Args:
            field_mapping: Optional mapping of form field names to profile field names
        
        Returns:
            Unified data dictionary ready for form filling
        """
        unified = {}
        
        # Load data if not already loaded
        if not self.master_profile:
            self.load_master_profile()
        if not self.document_vault:
            self.load_document_vault()
        
        # Default field mapping (can be overridden)
        default_mapping = {
            # Personal Information
            "name": "fullName",
            "full_name": "fullName",
            "first_name": "firstName",
            "last_name": "lastName",
            "applicant_name": "fullName",
            "candidate_name": "fullName",
            
            # Parent Names
            "father_name": "fatherName",
            "fathername": "fatherName",
            "mother_name": "motherName",
            "mothername": "motherName",
            "parent_name": "fatherName",
            
            # Date & Age
            "dob": "dateOfBirth",
            "date_of_birth": "dateOfBirth",
            "birthdate": "dateOfBirth",
            "birth_date": "dateOfBirth",
            "age": "age",
            
            # Gender & Category
            "gender": "gender",
            "sex": "gender",
            "caste": "caste",
            "category": "category",
            
            # Government IDs
            "aadhaar": "aadhaarNumber",
            "aadhaar_number": "aadhaarNumber",
            "aadhar": "aadhaarNumber",
            "aadhar_number": "aadhaarNumber",
            "uid": "aadhaarNumber",
            "pan": "panNumber",
            "pan_number": "panNumber",
            "pan_card": "panNumber",
            "voter_id": "voterIdNumber",
            "voter_id_number": "voterIdNumber",
            
            # Contact
            "email": "email",
            "email_id": "email",
            "e_mail": "email",
            "phone": "phone",
            "mobile": "phone",
            "mobile_number": "phone",
            "phone_number": "phone",
            "contact": "phone",
            
            # Address
            "address": "address",
            "current_address": "address",
            "residential_address": "address",
            "permanent_address": "permanentAddress",
            "city": "city",
            "state": "state",
            "pincode": "pincode",
            "pin_code": "pincode",
            "postal_code": "pincode",
            "zip": "pincode",
            
            # Additional Address (for state services)
            "district": "district",
            "block": "block",
            "block_circle": "block",
            "panchayat": "panchayat",
            "panchayat_ward": "panchayat",
            "post_office": "postOffice",
            "postoffice": "postOffice",
            
            # Education
            "qualification": "qualification",
            "education": "qualification",
            "university": "university",
            
            # Bank
            "bank_name": "bankName",
            "bank": "bankName",
            "account_number": "accountNumber",
            "account_no": "accountNumber",
            "ifsc": "ifsc",
            "ifsc_code": "ifsc",
            
            # Documents
            "photo": "photoUrl",
            "photo_url": "photoUrl",
            "signature": "signatureUrl",
            "signature_url": "signatureUrl",
        }
        
        # Merge with provided mapping
        if field_mapping:
            default_mapping.update(field_mapping)
        
        # Build unified data with priority
        all_fields = set()
        all_fields.update(self.request_data.keys())
        all_fields.update(self.master_profile.keys())
        all_fields.update(self.document_vault.keys())
        all_fields.update(default_mapping.keys())
        
        for field in all_fields:
            # Priority 1: Request Data
            if field in self.request_data and self.request_data[field]:
                unified[field] = self.request_data[field]
                unified[f"_{field}_source"] = "request_data"
                continue
            
            # Priority 2: Master Profile (check both direct and mapped)
            profile_field = default_mapping.get(field, field)
            if profile_field in self.master_profile and self.master_profile[profile_field]:
                unified[field] = self.master_profile[profile_field]
                unified[f"_{field}_source"] = "master_profile"
                continue
            
            # Also check direct field name in master profile
            if field in self.master_profile and self.master_profile[field]:
                unified[field] = self.master_profile[field]
                unified[f"_{field}_source"] = "master_profile"
                continue
            
            # Priority 3: Document Vault
            if field in self.document_vault and self.document_vault[field]:
                unified[field] = self.document_vault[field]
                unified[f"_{field}_source"] = "document_vault"
                continue
            
            # Priority 4: Defaults (for common fields)
            default_value = self._get_default_value(field)
            if default_value is not None:
                unified[field] = default_value
                unified[f"_{field}_source"] = "default"
        
        logger.info(f"[DataAggregator] Unified Data created with {len([k for k in unified.keys() if not k.startswith('_')])} fields")
        return unified
    
    def _get_default_value(self, field: str) -> Optional[Any]:
        """Get default value for common fields"""
        defaults = {
            "nationality": "Indian",
            "country": "India",
            "applicant_type": "Individual",  # For PAN card
            "delivery_type": "Digital",  # For PAN card
            "pan_card_mode": "epan_only",  # For PAN card
        }
        return defaults.get(field.lower())
    
    def get_field_value(self, field_name: str, field_mapping: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """
        Get value for a specific field using priority order
        
        Args:
            field_name: Name of the field to get value for
            field_mapping: Optional mapping of field names
        
        Returns:
            Field value or None
        """
        unified = self.get_unified_data(field_mapping)
        return unified.get(field_name)
    
    def get_data_source(self, field_name: str) -> str:
        """Get the source of data for a field"""
        unified = self.get_unified_data()
        return unified.get(f"_{field_name}_source", "unknown")
    
    def enrich_master_profile(self, new_data: Dict[str, Any]):
        """
        Enrich master profile with newly collected data
        This is called after successful form submission to learn new data
        """
        try:
            if self.db_manager and self.db_manager.is_available():
                # Update master profile with new data
                current_profile = self.db_manager.get_profile(self.user_id) or {}
                current_profile.update(new_data)
                self.db_manager.create_or_update_profile(self.user_id, current_profile)
                self.master_profile = current_profile
                logger.info(f"[DataAggregator] Enriched Master Profile with {len(new_data)} new fields")
        except Exception as e:
            logger.warning(f"[DataAggregator] Could not enrich Master Profile: {e}")

