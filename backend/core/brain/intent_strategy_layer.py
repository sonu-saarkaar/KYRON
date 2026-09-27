"""
KYRON CORE BRAIN - Intent & Strategy Layer (Cognitive Mind)

Responsibilities:
- Understand user intent
- Decide which service flow applies
- Predict upcoming steps
- Detect risk points
- Build execution roadmap dynamically
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk levels for execution steps"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskType(Enum):
    """Types of risks in form execution"""
    LOGIN = "login"
    OTP = "otp"
    PAYMENT = "payment"
    CAPTCHA = "captcha"
    FILE_UPLOAD = "file_upload"
    MULTI_STEP = "multi_step"
    DYNAMIC_CONTENT = "dynamic_content"
    EXTERNAL_REDIRECT = "external_redirect"

@dataclass
class ExecutionStep:
    """Atomic execution step"""
    step_id: str
    step_name: str
    step_type: str  # "fill_field", "click_button", "navigate", "wait", "verify"
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    risk_types: List[RiskType] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Step IDs that must complete first
    expected_outcome: str = ""
    fallback_strategies: List[str] = field(default_factory=list)
    verification_required: bool = True
    can_skip: bool = False
    estimated_duration: float = 0.0  # seconds

@dataclass
class ExecutionRoadmap:
    """Dynamic execution plan"""
    service_id: str
    service_name: str
    total_steps: int
    steps: List[ExecutionStep] = field(default_factory=list)
    current_step_index: int = 0
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    risk_points: List[Tuple[int, RiskType]] = field(default_factory=list)  # (step_index, risk_type)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    is_complete: bool = False
    
    def get_current_step(self) -> Optional[ExecutionStep]:
        """Get current step"""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def mark_completed(self, step_id: str):
        """Mark step as completed"""
        if step_id not in self.completed_steps:
            self.completed_steps.append(step_id)
        self.last_updated = datetime.now()
    
    def mark_failed(self, step_id: str):
        """Mark step as failed"""
        if step_id not in self.failed_steps:
            self.failed_steps.append(step_id)
        self.last_updated = datetime.now()
    
    def get_next_risk_point(self) -> Optional[Tuple[int, RiskType]]:
        """Get next risk point in roadmap"""
        for step_idx, risk_type in self.risk_points:
            if step_idx > self.current_step_index:
                return (step_idx, risk_type)
        return None

class IntentStrategyLayer:
    """
    KYRON's Cognitive Mind - Intent & Strategy Layer
    
    Understands intent, builds execution roadmaps, predicts risks
    """
    
    def __init__(self):
        self.active_roadmaps: Dict[str, ExecutionRoadmap] = {}
        self.service_templates: Dict[str, List[ExecutionStep]] = {}
        self._initialize_service_templates()
    
    def _initialize_service_templates(self):
        """Initialize service execution templates"""
        # PAN Card service template
        pan_steps = [
            ExecutionStep(
                step_id="pan_01",
                step_name="Navigate to PAN Portal",
                step_type="navigate",
                description="Open official PAN card application portal",
                risk_level=RiskLevel.LOW,
                estimated_duration=3.0
            ),
            ExecutionStep(
                step_id="pan_02",
                step_name="Select Application Type",
                step_type="click_button",
                description="Click 'Apply for New PAN' or similar",
                risk_level=RiskLevel.LOW,
                estimated_duration=2.0
            ),
            ExecutionStep(
                step_id="pan_03",
                step_name="Select Mode (Physical/Digital)",
                step_type="fill_field",
                description="Select Physical or Digital mode",
                risk_level=RiskLevel.LOW,
                estimated_duration=2.0
            ),
            ExecutionStep(
                step_id="pan_04",
                step_name="Select Status of Applicant",
                step_type="fill_field",
                description="Select Individual/Company/HUF from dropdown",
                risk_level=RiskLevel.MEDIUM,
                risk_types=[RiskType.DYNAMIC_CONTENT],
                estimated_duration=3.0
            ),
            ExecutionStep(
                step_id="pan_05",
                step_name="Fill Personal Details",
                step_type="fill_field",
                description="Fill name, DOB, parent name, etc.",
                risk_level=RiskLevel.LOW,
                estimated_duration=10.0
            ),
            ExecutionStep(
                step_id="pan_06",
                step_name="Fill Contact Details",
                step_type="fill_field",
                description="Fill email, phone, address",
                risk_level=RiskLevel.LOW,
                estimated_duration=5.0
            ),
            ExecutionStep(
                step_id="pan_07",
                step_name="Upload Documents",
                step_type="file_upload",
                description="Upload photo and signature",
                risk_level=RiskLevel.MEDIUM,
                risk_types=[RiskType.FILE_UPLOAD],
                estimated_duration=5.0
            ),
            ExecutionStep(
                step_id="pan_08",
                step_name="Submit Form",
                step_type="click_button",
                description="Click Submit/Next button",
                risk_level=RiskLevel.MEDIUM,
                risk_types=[RiskType.MULTI_STEP],
                estimated_duration=2.0
            ),
            ExecutionStep(
                step_id="pan_09",
                step_name="Payment (if required)",
                step_type="wait",
                description="Wait for payment page, pause for user",
                risk_level=RiskLevel.CRITICAL,
                risk_types=[RiskType.PAYMENT],
                can_skip=True,
                estimated_duration=0.0  # User-controlled
            ),
            ExecutionStep(
                step_id="pan_10",
                step_name="Capture Acknowledgement",
                step_type="verify",
                description="Capture application number and acknowledgement",
                risk_level=RiskLevel.HIGH,
                estimated_duration=3.0
            )
        ]
        self.service_templates["pan_card"] = pan_steps
    
    def understand_intent(self, user_message: str, service_catalog: Dict) -> Optional[Tuple[str, float]]:
        """
        Understand user intent from natural language
        
        Returns:
            Tuple of (service_id, confidence_score) or None
        """
        from services.intent_detector import detect_service_intent
        
        if detect_service_intent:
            result = detect_service_intent(user_message)
            if result:
                service_type, confidence = result
                return (service_type.value, confidence)
        
        # Fallback keyword matching
        message_lower = user_message.lower()
        service_keywords = {
            "pan_card": ["pan", "pan card", "permanent account number"],
            "income_certificate": ["income certificate", "income proof"],
            "caste_certificate": ["caste certificate", "category certificate"]
        }
        
        for service_id, keywords in service_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return (service_id, 0.8)
        
        return None
    
    def build_roadmap(self, service_id: str, service_config: Dict, user_profile: Dict) -> ExecutionRoadmap:
        """
        Build dynamic execution roadmap for a service
        
        Args:
            service_id: Service identifier
            service_config: Service-specific configuration
            user_profile: User's master profile data
            
        Returns:
            ExecutionRoadmap with all steps
        """
        # Get base template
        base_steps = self.service_templates.get(service_id, [])
        
        # Create roadmap
        roadmap = ExecutionRoadmap(
            service_id=service_id,
            service_name=service_config.get("service_name", service_id),
            total_steps=len(base_steps),
            steps=base_steps.copy()
        )
        
        # Identify risk points
        for idx, step in enumerate(roadmap.steps):
            if step.risk_types:
                for risk_type in step.risk_types:
                    roadmap.risk_points.append((idx, risk_type))
        
        # Adjust roadmap based on service_config
        if service_config.get("delivery_type") == "digital":
            # Skip physical card steps if digital
            roadmap.steps = [s for s in roadmap.steps if "physical" not in s.step_name.lower()]
            roadmap.total_steps = len(roadmap.steps)
        
        logger.info(f"Built roadmap for {service_id}: {roadmap.total_steps} steps, {len(roadmap.risk_points)} risk points")
        return roadmap
    
    def predict_next_steps(self, roadmap: ExecutionRoadmap, current_page_info: Dict) -> List[ExecutionStep]:
        """
        Predict upcoming steps based on current page state
        
        Args:
            roadmap: Current execution roadmap
            current_page_info: Information about current page
            
        Returns:
            List of predicted next steps
        """
        predicted = []
        current_idx = roadmap.current_step_index
        
        # Predict next 3-5 steps
        for i in range(current_idx + 1, min(current_idx + 6, len(roadmap.steps))):
            predicted.append(roadmap.steps[i])
        
        return predicted
    
    def detect_risk_points(self, roadmap: ExecutionRoadmap) -> List[Tuple[int, RiskType, RiskLevel]]:
        """
        Detect all risk points in roadmap
        
        Returns:
            List of (step_index, risk_type, risk_level)
        """
        risks = []
        for idx, step in enumerate(roadmap.steps):
            if step.risk_types:
                for risk_type in step.risk_types:
                    risks.append((idx, risk_type, step.risk_level))
        return risks
    
    def adjust_roadmap(self, roadmap: ExecutionRoadmap, new_page_info: Dict, execution_state: Dict):
        """
        Adjust roadmap if website flow changes mid-way
        
        Args:
            roadmap: Current roadmap
            new_page_info: New page information
            execution_state: Current execution state
        """
        # Detect if page structure changed
        page_type = new_page_info.get("page_type", "unknown")
        
        # If we're on a payment page but roadmap doesn't expect it yet
        if page_type == "payment" and not any(
            step.step_id == "pan_09" for step in roadmap.steps[roadmap.current_step_index:]
        ):
            # Insert payment step
            payment_step = ExecutionStep(
                step_id=f"{roadmap.service_id}_payment",
                step_name="Payment",
                step_type="wait",
                description="Payment page detected",
                risk_level=RiskLevel.CRITICAL,
                risk_types=[RiskType.PAYMENT],
                can_skip=False
            )
            roadmap.steps.insert(roadmap.current_step_index + 1, payment_step)
            roadmap.total_steps = len(roadmap.steps)
            roadmap.risk_points.append((roadmap.current_step_index + 1, RiskType.PAYMENT))
            logger.info("Adjusted roadmap: Payment step inserted")
        
        roadmap.last_updated = datetime.now()
    
    def get_roadmap(self, session_id: str) -> Optional[ExecutionRoadmap]:
        """Get roadmap for a session"""
        return self.active_roadmaps.get(session_id)
    
    def save_roadmap(self, session_id: str, roadmap: ExecutionRoadmap):
        """Save roadmap for a session"""
        self.active_roadmaps[session_id] = roadmap

