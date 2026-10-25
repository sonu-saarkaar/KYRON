"""
KYRON Business Automation Service
Handles Client Inquiries, Customer Support Tickets, Promotion & Branding Campaigns,
and Omnichannel Auto-Responses for Asif Aslam's ventures (KYRON AGI & BookMyGaadi).
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("kyron.business_automation")

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
BUSINESS_FILE = os.path.join(STORAGE_DIR, "business_operations.json")

os.makedirs(STORAGE_DIR, exist_ok=True)

DEFAULT_BUSINESS_DATA: Dict[str, Any] = {
    "ventures": [
        {
            "id": "v_kyron",
            "name": "KYRON AGI",
            "tagline": "Personal Autonomous Agentic OS & High-Speed Workstation",
            "metrics": {"active_users": "2,400+", "tasks_automated": "148,000+", "status": "Operational"},
            "services": ["Hands-free Voice AI", "macOS Automation", "Enterprise Agentic Workflow Development"]
        },
        {
            "id": "v_bmg",
            "name": "BookMyGaadi",
            "tagline": "Intercity Fleet & Outstation Cab Booking Network in Bihar & Eastern India",
            "metrics": {"total_rides": "12,500+", "verified_drivers": "450+", "rating": "4.9/5"},
            "services": ["Instant WhatsApp Cab Booking", "Airport Transfers", "Outstation Round-Trips"]
        }
    ],
    "client_leads": [
        {
            "id": "lead_101",
            "client_name": "Apex Logistics Ltd.",
            "contact_person": "Vikram Malhotra",
            "email": "vikram@apexlogistics.in",
            "phone": "+91 98100 44321",
            "service_requested": "Custom Autonomous Fleet Tracking & WhatsApp Dispatch Agent",
            "estimated_value": "₹4,50,000",
            "status": "Proposal Sent",
            "priority": "High",
            "date": "Today, 11:30 AM"
        },
        {
            "id": "lead_102",
            "client_name": "Zenith FinTech Solutions",
            "contact_person": "Pooja Singhania",
            "email": "pooja@zenithfin.co",
            "phone": "+91 99201 88765",
            "service_requested": "Document Vault & KYC Form Autofill Engine Integration",
            "estimated_value": "₹3,20,000",
            "status": "In Negotiation",
            "priority": "Medium",
            "date": "Yesterday"
        },
        {
            "id": "lead_103",
            "client_name": "Bihar Tourism & Travel Corp",
            "contact_person": "Rameshwar Prasad",
            "email": "tours@bihartravel.org",
            "phone": "+91 94310 11223",
            "service_requested": "BookMyGaadi Outstation API Partnership & Fleet Integration",
            "estimated_value": "₹8,00,000",
            "status": "Contract Drafted",
            "priority": "Urgent",
            "date": "Oct 24"
        }
    ],
    "support_tickets": [
        {
            "id": "tkt_801",
            "venture": "BookMyGaadi",
            "customer_name": "Amitabh Sen",
            "phone": "+91 98300 22114",
            "issue": "Patna to Motihari cab booking confirmation receipt required on WhatsApp",
            "status": "Resolved",
            "resolution": "Automated PDF invoice dispatched via WhatsApp API",
            "satisfaction": "5/5"
        },
        {
            "id": "tkt_802",
            "venture": "KYRON AGI",
            "customer_name": "Siddharth Rao",
            "phone": "+91 97410 55667",
            "issue": "Wispr voice recognition latency calibration query on M2 Mac",
            "status": "In Progress",
            "resolution": "Dograh fast-path audio buffer setting optimized to 20ms",
            "satisfaction": "Pending"
        }
    ],
    "promotions": [
        {
            "id": "promo_01",
            "title": "KYRON v2.0 Tahoe Edition Launch",
            "platform": "LinkedIn & Twitter",
            "reach": "18.4K Impressions",
            "status": "Published"
        },
        {
            "id": "promo_02",
            "title": "BookMyGaadi Festive Season Outstation Fares",
            "platform": "WhatsApp Broadcast & Instagram",
            "reach": "42.1K Views",
            "status": "Active"
        }
    ]
}


class BusinessAutomationService:
    """Manages business operations, client CRM, support agent, and branding generation."""

    def __init__(self):
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(BUSINESS_FILE):
            try:
                with open(BUSINESS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading business operations: {e}")
        self._save_data(DEFAULT_BUSINESS_DATA)
        return dict(DEFAULT_BUSINESS_DATA)

    def _save_data(self, data: Dict[str, Any]):
        try:
            with open(BUSINESS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving business data: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Returns full business overview."""
        return self.data

    def add_client_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a new inbound client lead."""
        lead["id"] = f"lead_{int(datetime.now().timestamp())}"
        lead["date"] = "Just now"
        self.data["client_leads"].insert(0, lead)
        self._save_data(self.data)
        return lead

    def generate_branding_campaign(self, venture_name: str, topic: str, platform: str) -> Dict[str, Any]:
        """
        Generates high-converting promotional content for LinkedIn, Twitter, Instagram, or WhatsApp
        tailored to Asif Aslam's high-agency branding style.
        """
        venture = "KYRON AGI" if "kyron" in venture_name.lower() else "BookMyGaadi"

        if venture == "KYRON AGI":
            copy_linkedin = (
                f"🚀 Announcing: {topic}\n\n"
                f"At KYRON AGI, we believe humans shouldn't spend hours clicking repetitive forms or context switching between apps. "
                f"We built an autonomous cognitive workstation that controls macOS, automates WhatsApp & browser flows, "
                f"and recalls your entire memory in sub-100ms.\n\n"
                f"⚡ Highlights:\n"
                f"• Apple Silicon native hardware execution (Dograh Voice Engine)\n"
                f"• Zero-click document vault & smart form autofill\n"
                f"• Deep personal memory & first-principles cognitive alignment\n\n"
                f"Building the future of personal agency right here from India. Try KYRON today! #AGI #Automation #BuildInPublic"
            )
            copy_twitter = (
                f"Stop doing manually what an autonomous agent can do in 20ms. ⚡\n\n"
                f"{topic} is now live on KYRON AGI. Hands-free voice, native macOS control, and encrypted document vault.\n\n"
                f"Built for high-agency builders. DM for private enterprise access."
            )
        else:
            copy_linkedin = (
                f"🚖 Expanding Regional Mobility with BookMyGaadi: {topic}\n\n"
                f"Travel across Bihar and Eastern India should be reliable, comfortable, and transparent. "
                f"With BookMyGaadi, riders can book verified outstation cabs directly via WhatsApp in under 30 seconds with zero surge pricing.\n\n"
                f"🌟 Safe journeys, professional drivers, transparent fares.\n"
                f"Book your next intercity ride at www.bookmygaadi.app #Mobility #BookMyGaadi #Bihar"
            )
            copy_twitter = (
                f"Need an outstation cab from Patna or Motihari? 🚗\n\n"
                f"BookMyGaadi gives you guaranteed cabs, verified drivers, and zero surge. "
                f"Book directly on WhatsApp in 30 seconds: https://bookmygaadi.app"
            )

        selected_copy = copy_linkedin if "linkedin" in platform.lower() else copy_twitter

        campaign = {
            "id": f"promo_{int(datetime.now().timestamp())}",
            "venture": venture,
            "topic": topic,
            "platform": platform,
            "generated_copy": selected_copy,
            "status": "Ready to Publish",
            "created_at": datetime.now().strftime("%I:%M %p")
        }

        self.data["promotions"].insert(0, campaign)
        self._save_data(self.data)

        return {
            "success": True,
            "campaign": campaign,
            "voice_vocalization": f"Boss, {venture} ke liye '{topic}' promotional campaign generate kar diya hai!"
        }

    def generate_client_reply(self, client_name: str, inquiry: str, service_type: str = "KYRON Enterprise") -> Dict[str, Any]:
        """Crafts a professional, high-agency response to client inquiries in Sonu's tone."""
        reply_draft = (
            f"Hi {client_name},\n\n"
            f"Thank you for reaching out regarding {service_type}. "
            f"We reviewed your requirements for '{inquiry}' and our architecture is designed to execute this autonomously.\n\n"
            f"We can schedule a 15-minute high-bandwidth technical demo tomorrow at 11:00 AM or 4:00 PM. "
            f"I will walk you through our live sandbox and provide a detailed scope-of-work.\n\n"
            f"Best regards,\n"
            f"Asif Aslam (Sonu Sarkar)\n"
            f"Founder & Chief Architect — KYRON AGI & BookMyGaadi"
        )

        return {
            "success": True,
            "client_name": client_name,
            "reply_draft": reply_draft,
            "voice_vocalization": f"Boss, {client_name} ke inquiry ke liye professional proposal draft ready hai."
        }


# Global singleton instance
business_automation_service = BusinessAutomationService()
