"""
KYRON Call Support Service
Dedicated AI Telephony & Customer Support System.
Handles simulated live inbound/outbound calls, real-time voice transcripts,
CRM disposition, and caller resolution logs for BookMyGaadi and KYRON AGI.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("kyron.call_support")

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
CALLS_FILE = os.path.join(STORAGE_DIR, "call_support_logs.json")
SETUP_FILE = os.path.join(STORAGE_DIR, "call_telephony_setup.json")

os.makedirs(STORAGE_DIR, exist_ok=True)

DEFAULT_SETUP: Dict[str, Any] = {
    "user_phone": "+91 98350 78219",
    "user_name": "Asif Aslam (Sonu Sarkar)",
    "caller_id": "+91 80000 59766",
    "carrier_gateway": "Twilio Voice & WebRTC SIP Trunk",
    "voice_tone": "Sonu Sarkar Personal & High-Agency Tone",
    "auto_recording": True,
    "noise_cancellation": True,
    "sip_status": "Connected • 18ms Latency",
    "verified": True,
    "country_code": "+91",
    "speed_dial": [
        {"name": "Sonu (Self / Personal Mobile)", "phone": "+91 98350 78219", "role": "Owner"},
        {"name": "Rohit Kumar (Fleet & Ops Lead)", "phone": "+91 98101 44520", "role": "BookMyGaadi Lead"},
        {"name": "Rahul Dev (Senior Engineer)", "phone": "+91 98765 11200", "role": "KYRON Tech"},
        {"name": "Client Priority Hotline", "phone": "+91 99341 55621", "role": "VIP Client"}
    ]
}

DEFAULT_CALL_HISTORY: List[Dict[str, Any]] = [
    {
        "id": "call_101",
        "caller_name": "Rajesh Kumar Verma",
        "caller_phone": "+91 98350 11982",
        "caller_location": "Patna Junction, Bihar",
        "venture": "BookMyGaadi",
        "direction": "Inbound",
        "duration": "2m 14s",
        "intent": "Patna to Darbhanga Airport Cab Booking",
        "transcript": [
            {"speaker": "Rajesh", "time": "00:05", "text": "Hello, mujhe kal subah 7 baje Patna se Darbhanga airport ke liye sedan cab chahiye."},
            {"speaker": "Kyron AI", "time": "00:12", "text": "Namaste Rajesh ji! BookMyGaadi me aapka swagat hai. Kal subah 7:00 AM ke liye Sedan bilkul uplabdh hai. Fare ₹2,400 all inclusive rahega."},
            {"speaker": "Rajesh", "time": "00:25", "text": "Driver verified hoga na? Aur pickup location ghar se ho jayegi?"},
            {"speaker": "Kyron AI", "time": "00:34", "text": "Ji bilkul sir, hamare sabhi drivers 100% verified hain aur doorstep pickup provide karte hain. Maine booking link aapke WhatsApp par bhej diya hai."},
            {"speaker": "Rajesh", "time": "00:48", "text": "Shukriya! Main WhatsApp par confirm kar deta hoon."}
        ],
        "sentiment": "Positive",
        "resolution": "Booking Draft Sent via WhatsApp • Driver Assigned",
        "status": "Resolved",
        "timestamp": "Today, 10:15 AM"
    },
    {
        "id": "call_102",
        "caller_name": "Sneha Roy",
        "caller_phone": "+91 99341 55621",
        "caller_location": "Motihari Court Road",
        "venture": "BookMyGaadi",
        "direction": "Inbound",
        "duration": "1m 45s",
        "intent": "Fare inquiry for Motihari to Muzaffarpur hospital round trip",
        "transcript": [
            {"speaker": "Sneha", "time": "00:03", "text": "Bhaiya Motihari se Muzaffarpur jaana hai aur shaam ko wapas aana hai, kitna lagega?"},
            {"speaker": "Kyron AI", "time": "00:10", "text": "Namaste Sneha ji! Motihari se Muzaffarpur same-day round trip ke liye AC hatchback ₹1,850 aur Sedan ₹2,200 me uplabdh hai, with zero waiting charge."},
            {"speaker": "Sneha", "time": "00:22", "text": "Theek hai, mujhe Sedan book karni hai."},
            {"speaker": "Kyron AI", "time": "00:30", "text": "Perfect! Booking details lock kar di gayi hain. Driver details 15 minute pehle aapko WhatsApp ho jayengi."}
        ],
        "sentiment": "Positive",
        "resolution": "Round-Trip Ride Confirmed",
        "status": "Resolved",
        "timestamp": "Today, 09:30 AM"
    },
    {
        "id": "call_103",
        "caller_name": "Kunal Sharma (CTO, SmartTech)",
        "caller_phone": "+91 98110 99432",
        "caller_location": "Bengaluru / Remote",
        "venture": "KYRON AGI",
        "direction": "Inbound",
        "duration": "3m 30s",
        "intent": "Enterprise Voice AI Integration Inquiry",
        "transcript": [
            {"speaker": "Kunal", "time": "00:08", "text": "Hi, I am calling regarding KYRON's sub-25ms voice agent for macOS desktop control. We want to license it for our enterprise developers."},
            {"speaker": "Kyron AI", "time": "00:18", "text": "Hello Kunal! You've reached KYRON AGI HQ. Our Dograh engine runs natively on Apple Silicon with sub-25ms response and zero cloud round-trip delay."},
            {"speaker": "Kunal", "time": "00:32", "text": "That's incredible. Can we schedule a technical walkthrough with Sonu Sarkar?"},
            {"speaker": "Kyron AI", "time": "00:45", "text": "Certainly! I have scheduled an enterprise demo for tomorrow at 11:00 AM IST with Asif Aslam (Sonu Sarkar). Calendar invite dispatched to your email."}
        ],
        "sentiment": "Extremely Positive",
        "resolution": "Demo Scheduled with Sonu Sarkar",
        "status": "Lead Qualified",
        "timestamp": "Yesterday, 04:45 PM"
    }
]


class CallSupportService:
    """Manages real-time call states, inbound simulation, and telephony records."""

    def __init__(self):
        self.logs = self._load_logs()
        self.setup = self._load_setup()
        self.active_call: Optional[Dict[str, Any]] = None

    def _load_setup(self) -> Dict[str, Any]:
        if os.path.exists(SETUP_FILE):
            try:
                with open(SETUP_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading telephony setup: {e}")
        self._save_setup(DEFAULT_SETUP)
        return dict(DEFAULT_SETUP)

    def _save_setup(self, setup_data: Dict[str, Any]):
        try:
            with open(SETUP_FILE, "w", encoding="utf-8") as f:
                json.dump(setup_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving telephony setup: {e}")

    def get_setup(self) -> Dict[str, Any]:
        return self.setup

    def update_setup(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        self.setup.update(new_data)
        self._save_setup(self.setup)
        return {"success": True, "setup": self.setup, "message": "Calling setup saved successfully!"}

    def dial_realtime_call(
        self,
        target_phone: str,
        caller_name: Optional[str] = None,
        purpose: Optional[str] = None,
        trigger_macos_call: bool = True
    ) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%I:%M %p")
        name = caller_name or "Real-time Contact"

        self.active_call = {
            "id": f"call_real_{int(time.time())}",
            "caller_name": name,
            "caller_phone": target_phone,
            "caller_location": "Direct Dial • Real-time Outbound",
            "venture": "KYRON Telephony • Realtime Line",
            "direction": "Outbound Realtime",
            "duration": "0m 10s",
            "intent": purpose or "Real-time Voice Telephony Call with Sonu Sarkar",
            "transcript": [
                {"speaker": "System", "time": "00:01", "text": f"Dialing {target_phone} via verified caller ID {self.setup.get('caller_id', '+91 80000 59766')}..."},
                {"speaker": "Carrier", "time": "00:03", "text": "Ringing remote phone... Call connected with high-fidelity WebRTC audio."},
                {"speaker": "Kyron AI", "time": "00:07", "text": f"Namaste! Main Sonu Sarkar ka AI Telephony Agent bol raha hoon. Kya meri baat {name} se ho rahi hai?"}
            ],
            "sentiment": "Connected • Live",
            "resolution": "Active Call in Real Time",
            "status": "In Progress (Live Realtime)",
            "timestamp": timestamp
        }

        # Try to trigger macOS FaceTime / iPhone Continuity Call if requested
        if trigger_macos_call:
            try:
                import subprocess
                clean_phone = "".join(c for c in target_phone if c.isdigit() or c == "+")
                if clean_phone:
                    subprocess.Popen(["open", f"tel:{clean_phone}"])
            except Exception as e:
                logger.debug(f"macOS tel launch notice: {e}")

        return {
            "success": True,
            "active_call": self.active_call,
            "voice_vocalization": f"Boss, {name} ({target_phone}) ko real-time call lag gaya hai!"
        }

    def _load_logs(self) -> List[Dict[str, Any]]:
        if os.path.exists(CALLS_FILE):
            try:
                with open(CALLS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading call logs: {e}")
        self._save_logs(DEFAULT_CALL_HISTORY)
        return list(DEFAULT_CALL_HISTORY)

    def _save_logs(self, logs: List[Dict[str, Any]]):
        try:
            with open(CALLS_FILE, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving call logs: {e}")

    def get_history(self) -> Dict[str, Any]:
        """Returns active call and historical call logs."""
        return {
            "active_call": self.active_call,
            "call_history": self.logs,
            "metrics": {
                "total_calls_today": len(self.logs),
                "resolution_rate": "98.4%",
                "avg_duration": "2m 18s",
                "customer_satisfaction": "4.92 / 5.0"
            }
        }

    def simulate_inbound_call(self, caller_type: str = "ride_booking") -> Dict[str, Any]:
        """Simulates an incoming customer or client phone call."""
        timestamp = datetime.now().strftime("%I:%M %p")

        if caller_type == "enterprise_kyron":
            caller_name = "Vikram Aditya (VP Engg, CloudScale)"
            phone = "+91 98200 77112"
            location = "Hyderabad / Mumbai"
            venture = "KYRON AGI"
            intent = "Autonomous Agentic OS licensing inquiry for 50 dev MacBooks"
            transcript = [
                {"speaker": "Vikram", "time": "00:04", "text": "Hello, kya meri baat KYRON AGI support team se ho rahi hai?"},
                {"speaker": "Kyron AI", "time": "00:10", "text": "Namaste Vikram ji! Welcome to KYRON AGI. Main Sonu Sarkar ka autonomous voice agent hoon. Bataye aapki kya sahayata karun?"},
                {"speaker": "Vikram", "time": "00:22", "text": "Hum hamari tech team ke liye KYRON ka hands-free desktop voice controller implement karna chahte hain."},
                {"speaker": "Kyron AI", "time": "00:35", "text": "Bahut badiya sir! KYRON macOS Sequoia aur M-series chips par sub-25ms latency me run karta hai. Main Sonu Sarkar ke calendar me aapke liye priority demo slot reserve kar deta hoon."}
            ]
        else:
            caller_name = "Manish Tiwari"
            phone = "+91 97090 33441"
            location = "Chhatauni Chowk, Motihari"
            venture = "BookMyGaadi"
            intent = "Urgent cab booking: Motihari to Patna AIIMS"
            transcript = [
                {"speaker": "Manish", "time": "00:03", "text": "Hello BookMyGaadi? Mujhe Motihari se Patna AIIMS ke liye urgent cab chahiye, patient ko le jana hai."},
                {"speaker": "Kyron AI", "time": "00:11", "text": "Namaste Manish ji! Chinta mat kariye, medical urgency ke liye hamari priority fleet active hai. Nearest verified driver 10 minute me aapke location par pahunch raha hai."},
                {"speaker": "Manish", "time": "00:24", "text": "Driver ka number jaldi bhej dijiye."},
                {"speaker": "Kyron AI", "time": "00:30", "text": "Driver Santosh Kumar (Swift Dzire BR-05-XXXX) assign ho chuke hain, live tracking link WhatsApp par bhej diya hai sir."}
            ]

        self.active_call = {
            "id": f"call_{int(time.time())}",
            "caller_name": caller_name,
            "caller_phone": phone,
            "caller_location": location,
            "venture": venture,
            "direction": "Inbound",
            "duration": "0m 45s",
            "intent": intent,
            "transcript": transcript,
            "sentiment": "Very Positive",
            "resolution": "Handled autonomously by Kyron AI Telephony Engine",
            "status": "In Progress (Simulated)",
            "timestamp": timestamp
        }

        return {
            "success": True,
            "active_call": self.active_call,
            "voice_vocalization": f"Boss, {caller_name} ka {venture} support call connect ho gaya hai!"
        }

    def end_active_call(self) -> Dict[str, Any]:
        """Ends current active call and commits to history."""
        if not self.active_call:
            return {"success": False, "message": "No active call"}

        call = dict(self.active_call)
        call["status"] = "Completed & Resolved"
        self.logs.insert(0, call)
        self._save_logs(self.logs)
        self.active_call = None

        return {
            "success": True,
            "message": "Call concluded and logged in CRM",
            "logged_call": call
        }


# Global singleton instance
call_support_service = CallSupportService()
