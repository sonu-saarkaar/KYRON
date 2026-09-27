"""
KYRON Master Profile Checker
Checks Master Profile for existing data before requesting from user
"""

from typing import Dict, List, Optional, Set
from services_catalog import ServiceDefinition, ServiceStep

class MasterProfileChecker:
    """Checks Master Profile and determines what data is missing"""
    
    def __init__(self, master_profile: Dict):
        self.master_profile = master_profile or {}
    
    def get_available_fields(self) -> Set[str]:
        """Get set of all available fields in Master Profile"""
        available = set()
        
        # Personal details
        if self.master_profile.get("fullName"):
            available.add("fullName")
        if self.master_profile.get("firstName"):
            available.add("firstName")
        if self.master_profile.get("lastName"):
            available.add("lastName")
        if self.master_profile.get("dateOfBirth"):
            available.add("dateOfBirth")
        if self.master_profile.get("gender"):
            available.add("gender")
        
        # Parent details
        if self.master_profile.get("fatherName"):
            available.add("fatherName")
        if self.master_profile.get("motherName"):
            available.add("motherName")
        
        # Contact details
        if self.master_profile.get("email"):
            available.add("email")
        if self.master_profile.get("phone"):
            available.add("phone")
        
        # Address details
        if self.master_profile.get("address"):
            available.add("address")
        if self.master_profile.get("city"):
            available.add("city")
        if self.master_profile.get("state"):
            available.add("state")
        if self.master_profile.get("pincode"):
            available.add("pincode")
        
        # Identity documents
        if self.master_profile.get("aadhaarNumber"):
            available.add("aadhaarNumber")
        if self.master_profile.get("panNumber"):
            available.add("panNumber")
        
        # Additional fields
        if self.master_profile.get("occupation"):
            available.add("occupation")
        
        return available
    
    def check_service_requirements(self, service: ServiceDefinition) -> Dict[str, any]:
        """
        Check what data is required vs available for a service
        
        Returns:
            {
                "available": {...},  # Data available in profile
                "missing": [...],     # List of missing field names
                "missing_steps": [...] # List of ServiceStep objects that need data
            }
        """
        available_fields = self.get_available_fields()
        available_data = {}
        missing_steps = []
        
        # Map service steps to profile fields
        step_to_profile_map = {
            "applicant_type": "applicant_type",
            "delivery_type": "delivery_type",
            "application_type": "application_type",
            "name": "fullName",
            "first_name": "firstName",
            "last_name": "lastName",
            "dob": "dateOfBirth",
            "date_of_birth": "dateOfBirth",
            "father_name": "fatherName",
            "mother_name": "motherName",
            "email": "email",
            "phone": "phone",
            "mobile": "phone",
            "address": "address",
            "city": "city",
            "state": "state",
            "pincode": "pincode",
            "aadhaar": "aadhaarNumber",
            "aadhaar_number": "aadhaarNumber",
            "pan": "panNumber",
            "pan_number": "panNumber",
            "occupation": "occupation",
            "income_source": "occupation"
        }
        
        # Check each service step
        for step in service.steps:
            step_id = step.id
            profile_field = step_to_profile_map.get(step_id)
            
            if profile_field and profile_field in available_fields:
                # Data is available
                value = self.master_profile.get(profile_field)
                if value:
                    available_data[step_id] = value
            else:
                # Data is missing
                missing_steps.append(step)
        
        # Build missing field names list
        missing_fields = [step.label for step in missing_steps]
        
        return {
            "available": available_data,
            "missing": missing_fields,
            "missing_steps": missing_steps
        }
    
    def get_profile_data_for_service(self, service: ServiceDefinition) -> Dict[str, any]:
        """
        Extract relevant profile data for a service
        """
        service_data = {}
        available_fields = self.get_available_fields()
        
        # Map common fields
        field_mapping = {
            "fullName": "fullName",
            "firstName": "firstName",
            "lastName": "lastName",
            "dateOfBirth": "dateOfBirth",
            "fatherName": "fatherName",
            "motherName": "motherName",
            "email": "email",
            "phone": "phone",
            "address": "address",
            "city": "city",
            "state": "state",
            "pincode": "pincode",
            "aadhaarNumber": "aadhaarNumber",
            "panNumber": "panNumber",
            "occupation": "occupation"
        }
        
        for profile_field, service_field in field_mapping.items():
            if profile_field in available_fields:
                value = self.master_profile.get(profile_field)
                if value:
                    service_data[service_field] = value
        
        return service_data

