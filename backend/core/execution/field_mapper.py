"""
KYRON Execution Engine - FieldMapper

Maps form fields to data using meaning, not selectors
Uses master profile + newly collected data
Handles conditional and dynamic fields
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FieldMapper:
    """
    Maps form fields to user data semantically
    """
    
    def __init__(self, memory_layer):
        self.memory_layer = memory_layer
    
    def map_fields_to_data(
        self,
        fields: List[Any],
        master_profile: Any,
        service_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map fields to data from master profile and service config
        
        Returns:
            Dict mapping field_id -> value
        """
        field_mappings = {}
        
        # Priority: service_config > master_profile > defaults
        
        for field in fields:
            semantic_meaning = field.semantic_meaning
            if not semantic_meaning:
                continue
            
            # Try service_config first
            value = service_config.get(semantic_meaning)
            
            # Try master profile
            if not value:
                value = self._get_from_master_profile(master_profile, semantic_meaning)
            
            # Use default if available
            if not value:
                value = self._get_default_value(semantic_meaning)
            
            if value:
                field_mappings[field.field_id] = {
                    "value": value,
                    "field": field,
                    "source": "service_config" if semantic_meaning in service_config else "master_profile"
                }
                logger.debug(f"Mapped {semantic_meaning} -> {field.field_id}: {value}")
        
        return field_mappings
    
    def _get_from_master_profile(self, master_profile: Any, semantic_meaning: str) -> Optional[Any]:
        """Get value from master profile"""
        if not master_profile:
            return None
        
        # Map semantic meanings to profile fields
        profile_field_map = {
            "first_name": "firstName",
            "last_name": "lastName",
            "full_name": "fullName",
            "date_of_birth": "dateOfBirth",
            "email": "email",
            "phone": "phone",
            "address": "address",
            "city": "city",
            "state": "state",
            "pincode": "pincode",
            "father_name": "fatherName",
            "mother_name": "motherName",
            "aadhaar": "aadhaarNumber",
            "pan": "panNumber",
            "gender": "gender",
            "occupation": "occupation"
        }
        
        profile_field = profile_field_map.get(semantic_meaning)
        if profile_field:
            # Check personal_details first
            if hasattr(master_profile, 'personal_details'):
                return master_profile.personal_details.get(profile_field)
            # Fallback to direct attribute
            return getattr(master_profile, profile_field, None)
        
        return None
    
    def _get_default_value(self, semantic_meaning: str) -> Optional[Any]:
        """Get default value for semantic meaning"""
        defaults = {
            "applicant_type": "Individual",
            "delivery_type": "Digital"
        }
        return defaults.get(semantic_meaning)

