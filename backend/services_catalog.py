"""
Service Catalog for KYRON
Defines all available government services and their configuration.
Each service has steps, options, and field mappings.
"""

from typing import List, Dict, Any, Optional
from enum import Enum

class ServiceType(str, Enum):
    """Available service types"""
    PAN_CARD = "pan_card"
    INCOME_CERTIFICATE = "income_certificate"
    CASTE_CERTIFICATE = "caste_certificate"
    DOMICILE = "domicile"
    BIHAR_RESIDENCE_CERTIFICATE = "bihar_residence_certificate"

class ServiceOption:
    """Represents an option for a service step"""
    def __init__(self, id: str, label: str, value: str, description: Optional[str] = None):
        self.id = id
        self.label = label
        self.value = value
        self.description = description

class ServiceStep:
    """Represents a step in a service application"""
    def __init__(
        self,
        id: str,
        label: str,
        field_type: str,  # "radio", "select", "checkbox", "text", "file"
        options: Optional[List[ServiceOption]] = None,
        required: bool = True,
        description: Optional[str] = None,
        field_mapping: Optional[Dict[str, str]] = None  # Maps option value to form field values
    ):
        self.id = id
        self.label = label
        self.field_type = field_type
        self.options = options or []
        self.required = required
        self.description = description
        self.field_mapping = field_mapping or {}  # Maps selected option to form field data

class ServiceDefinition:
    """Complete definition of a service"""
    def __init__(
        self,
        id: ServiceType,
        name: str,
        description: str,
        benefits: List[str],
        steps: List[ServiceStep],
        required_documents: List[str],
        estimated_time: str,
        official_url: str = "",
        alternative_urls: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.benefits = benefits
        self.steps = steps
        self.required_documents = required_documents
        self.estimated_time = estimated_time
        self.official_url = official_url
        self.alternative_urls = alternative_urls or []

# ==================== SERVICE DEFINITIONS ====================

def get_service_catalog() -> Dict[str, ServiceDefinition]:
    """Returns the complete service catalog"""
    
    catalog = {}
    
    # PAN Card Service
    pan_steps = [
        ServiceStep(
            id="applicant_type",
            label="Applicant Type",
            field_type="radio",
            options=[
                ServiceOption("individual", "Individual", "individual", "For personal use"),
                ServiceOption("company", "Company/HUF", "company", "For business/company use")
            ],
            description="Select the type of applicant",
            field_mapping={
                "individual": {"applicant_type": "Individual"},
                "company": {"applicant_type": "Company"}
            }
        ),
        ServiceStep(
            id="application_type",
            label="Application Type",
            field_type="radio",
            options=[
                ServiceOption("new", "New PAN Card", "new", "Applying for first time"),
                ServiceOption("correction", "Correction/Update", "correction", "Update existing PAN details")
            ],
            description="Select the type of application",
            field_mapping={
                "new": {"application_type": "New"},
                "correction": {"application_type": "Correction"}
            }
        ),
        ServiceStep(
            id="delivery_type",
            label="Delivery Type",
            field_type="radio",
            options=[
                ServiceOption("epan", "e-PAN (Digital)", "epan", "Free digital PAN card"),
                ServiceOption("physical", "Physical Card", "physical", "Physical PAN card with charges")
            ],
            description="Choose delivery method",
            field_mapping={
                "epan": {"delivery_type": "Digital"},
                "physical": {"delivery_type": "Physical"}
            }
        )
    ]
    
    catalog[ServiceType.PAN_CARD] = ServiceDefinition(
        id=ServiceType.PAN_CARD,
        name="PAN Card",
        description="Apply for a new PAN card or update existing PAN card details",
        benefits=[
            "Mandatory for financial transactions",
            "Required for income tax filing",
            "Needed for opening bank accounts",
            "Essential for property transactions"
        ],
        steps=pan_steps,
        required_documents=[
            "Identity proof (Aadhaar/Voter ID/Driving License)",
            "Address proof",
            "Date of birth proof",
            "Recent photograph"
        ],
        estimated_time="15-20 minutes",
        official_url="https://www.pan.utiitsl.com/PAN/newA.html",
        alternative_urls=[
            "https://www.pan.utiitsl.com/panonline_ipg/forms/csfPan.html/csfReGeneration",
            "https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html",
            "https://www.tin-nsdl.com/services/pan/pan.html"
        ]
    )
    
    # Income Certificate Service
    income_steps = [
        ServiceStep(
            id="certificate_type",
            label="Certificate Type",
            field_type="radio",
            options=[
                ServiceOption("annual", "Annual Income Certificate", "annual", "Yearly income certificate"),
                ServiceOption("monthly", "Monthly Income Certificate", "monthly", "Monthly income certificate")
            ],
            field_mapping={
                "annual": {"certificate_type": "Annual"},
                "monthly": {"certificate_type": "Monthly"}
            }
        ),
        ServiceStep(
            id="purpose",
            label="Purpose",
            field_type="select",
            options=[
                ServiceOption("scholarship", "Scholarship", "scholarship"),
                ServiceOption("admission", "Admission", "admission"),
                ServiceOption("reservation", "Reservation Benefits", "reservation"),
                ServiceOption("other", "Other", "other")
            ],
            description="Select the purpose for which certificate is needed"
        )
    ]
    
    catalog[ServiceType.INCOME_CERTIFICATE] = ServiceDefinition(
        id=ServiceType.INCOME_CERTIFICATE,
        name="Income Certificate",
        description="Apply for income certificate required for scholarships, admissions, and other benefits",
        benefits=[
            "Required for scholarship applications",
            "Needed for educational institution admissions",
            "Eligible for various government schemes",
            "Proof of income for financial assistance"
        ],
        steps=income_steps,
        required_documents=[
            "Salary certificate or income proof",
            "Affidavit of income",
            "Identity proof",
            "Address proof"
        ],
        estimated_time="20-30 minutes"
    )
    
    # Caste Certificate Service
    caste_steps = [
        ServiceStep(
            id="caste_category",
            label="Caste Category",
            field_type="select",
            options=[
                ServiceOption("sc", "Scheduled Caste (SC)", "sc"),
                ServiceOption("st", "Scheduled Tribe (ST)", "st"),
                ServiceOption("obc", "Other Backward Class (OBC)", "obc"),
                ServiceOption("vjnt", "VJNT", "vjnt")
            ],
            description="Select your caste category",
            required=True
        ),
        ServiceStep(
            id="sub_caste",
            label="Sub-Caste (if applicable)",
            field_type="text",
            description="Enter your specific sub-caste if required",
            required=False
        )
    ]
    
    catalog[ServiceType.CASTE_CERTIFICATE] = ServiceDefinition(
        id=ServiceType.CASTE_CERTIFICATE,
        name="Caste Certificate",
        description="Apply for caste certificate for reservation benefits and government schemes",
        benefits=[
            "Required for reservation in education and jobs",
            "Eligible for government scholarship programs",
            "Needed for various welfare schemes",
            "Proof of social category for benefits"
        ],
        steps=caste_steps,
        required_documents=[
            "Caste certificate of father/mother or relative",
            "School leaving certificate with caste mention",
            "Identity proof",
            "Address proof"
        ],
        estimated_time="25-35 minutes"
    )
    
    # Domicile Certificate Service
    domicile_steps = [
        ServiceStep(
            id="domicile_type",
            label="Domicile Type",
            field_type="radio",
            options=[
                ServiceOption("birth", "Birth Domicile", "birth", "Born in the state"),
                ServiceOption("residence", "Residence Domicile", "residence", "Residing in the state for required period")
            ],
            field_mapping={
                "birth": {"domicile_type": "Birth"},
                "residence": {"domicile_type": "Residence"}
            }
        ),
        ServiceStep(
            id="purpose",
            label="Purpose",
            field_type="select",
            options=[
                ServiceOption("education", "Education", "education"),
                ServiceOption("job", "Government Job", "job"),
                ServiceOption("scholarship", "Scholarship", "scholarship"),
                ServiceOption("other", "Other", "other")
            ]
        )
    ]
    
    catalog[ServiceType.DOMICILE] = ServiceDefinition(
        id=ServiceType.DOMICILE,
        name="Domicile Certificate",
        description="Apply for domicile certificate to prove residence in a particular state",
        benefits=[
            "Required for state government jobs",
            "Needed for state quota admissions",
            "Eligible for state scholarship schemes",
            "Proof of residence for various benefits"
        ],
        steps=domicile_steps,
        required_documents=[
            "Birth certificate or school leaving certificate",
            "Address proof (ration card/electricity bill)",
            "Identity proof",
            "Affidavit of residence"
        ],
        estimated_time="20-30 minutes"
    )
    
    # Bihar Residence Certificate Service
    brc_steps = [
        ServiceStep(
            id="applicant_name",
            label="Applicant Full Name",
            field_type="text",
            description="Full name as per Aadhaar card",
            required=True
        ),
        ServiceStep(
            id="father_name",
            label="Father's Name",
            field_type="text",
            description="Father's full name",
            required=True
        ),
        ServiceStep(
            id="mother_name",
            label="Mother's Name",
            field_type="text",
            description="Mother's full name",
            required=True
        ),
        ServiceStep(
            id="date_of_birth",
            label="Date of Birth",
            field_type="text",
            description="Date of birth in DD-MM-YYYY format",
            required=True
        ),
        ServiceStep(
            id="gender",
            label="Gender",
            field_type="select",
            options=[
                ServiceOption("male", "Male", "male"),
                ServiceOption("female", "Female", "female"),
                ServiceOption("other", "Other", "other")
            ],
            description="Select gender",
            required=True
        ),
        ServiceStep(
            id="mobile_number",
            label="Mobile Number",
            field_type="text",
            description="10-digit mobile number (OTP capable)",
            required=True
        ),
        ServiceStep(
            id="aadhaar_number",
            label="Aadhaar Number",
            field_type="text",
            description="12-digit Aadhaar number",
            required=True
        ),
        ServiceStep(
            id="permanent_address",
            label="Permanent Address",
            field_type="text",
            description="Complete permanent address in Bihar",
            required=True
        ),
        ServiceStep(
            id="district",
            label="District",
            field_type="select",
            description="Select your district in Bihar",
            required=True
        ),
        ServiceStep(
            id="block_circle",
            label="Block / Circle",
            field_type="text",
            description="Block or Circle name",
            required=True
        ),
        ServiceStep(
            id="panchayat_ward",
            label="Panchayat / Ward",
            field_type="text",
            description="Panchayat or Ward number/name",
            required=True
        ),
        ServiceStep(
            id="post_office",
            label="Post Office",
            field_type="text",
            description="Post office name",
            required=True
        ),
        ServiceStep(
            id="pin_code",
            label="Pin Code",
            field_type="text",
            description="6-digit PIN code",
            required=True
        ),
        ServiceStep(
            id="purpose",
            label="Purpose of Certificate",
            field_type="select",
            options=[
                ServiceOption("job", "Government Job", "job"),
                ServiceOption("education", "Education/Admission", "education"),
                ServiceOption("scholarship", "Scholarship", "scholarship"),
                ServiceOption("other", "Other", "other")
            ],
            description="Purpose for which certificate is needed",
            required=True
        )
    ]
    
    catalog[ServiceType.BIHAR_RESIDENCE_CERTIFICATE] = ServiceDefinition(
        id=ServiceType.BIHAR_RESIDENCE_CERTIFICATE,
        name="Bihar Residence Certificate",
        description="Apply for Bihar Residence Certificate (Niwas Praman Patra) - proof of permanent residence in Bihar",
        benefits=[
            "Required for government jobs in Bihar",
            "Needed for educational institution admissions",
            "Eligible for Bihar state scholarship schemes",
            "Proof of residence for various government benefits"
        ],
        steps=brc_steps,
        required_documents=[
            "Aadhaar Card",
            "Ration Card (optional)",
            "Voter ID (optional)",
            "Electricity Bill (optional)",
            "School Certificate with Bihar address (optional)"
        ],
        estimated_time="15-20 minutes",
        official_url="https://rtps.bihar.gov.in/",
        alternative_urls=[
            "https://serviceonline.bihar.gov.in/"
        ]
    )
    
    return catalog

def get_service_definition(service_id: str) -> Optional[ServiceDefinition]:
    """Get service definition by ID"""
    try:
        catalog = get_service_catalog()
        # Try to convert to ServiceType enum
        try:
            service_type = ServiceType(service_id)
        except ValueError:
            # If not a valid enum, return None
            print(f"Warning: Invalid service_id: {service_id}")
            return None
        return catalog.get(service_type)
    except Exception as e:
        print(f"Error getting service definition for {service_id}: {e}")
        return None

def serialize_service_definition(service: ServiceDefinition) -> Dict[str, Any]:
    """Convert ServiceDefinition to dictionary for JSON response"""
    return {
        "id": service.id.value,
        "name": service.name,
        "description": service.description,
        "benefits": service.benefits,
        "steps": [
            {
                "id": step.id,
                "label": step.label,
                "field_type": step.field_type,
                "options": [
                    {
                        "id": opt.id,
                        "label": opt.label,
                        "value": opt.value,
                        "description": opt.description
                    } for opt in step.options
                ],
                "required": step.required,
                "description": step.description
            } for step in service.steps
        ],
        "required_documents": service.required_documents,
        "estimated_time": service.estimated_time
    }

def get_all_services() -> List[Dict[str, Any]]:
    """Get all services as serialized dictionaries"""
    catalog = get_service_catalog()
    return [serialize_service_definition(service) for service in catalog.values()]

