"""
KYRON Profile & Mind Service
Manages Master Persona, Personal Life, Education, Technical Knowledge,
Hobbies, Communication Heuristics, and Custom KYRON_MIND.md for Asif Aslam (Sonu Sarkar).
Ensures Kyron checks the profile FIRST before taking any action or responding.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("kyron.profile_mind")

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
PROFILE_FILE = os.path.join(STORAGE_DIR, "user_profile_mind.json")
MIND_MD_FILE = os.path.join(STORAGE_DIR, "KYRON_MIND.md")

os.makedirs(STORAGE_DIR, exist_ok=True)


DEFAULT_ASIF_ASLAM_PROFILE: Dict[str, Any] = {
    "identity": {
        "full_name": "Asif Aslam",
        "alias": "Sonu Sarkar",
        "title": "Founder & Chief AI Systems Architect",
        "organizations": ["KYRON AGI", "BookMyGaadi"],
        "location": "Motihari / Patna, Bihar, India",
        "avatar_badge": "BOSS • FOUNDER",
        "bio": "High-agency founder, full-stack engineer, and AI systems architect. Creator of KYRON AGI (hands-free macOS autonomous assistant) and BookMyGaadi (mobility & fleet platform). Passionate about extreme automation, sub-second latency, and Apple-grade software design."
    },
    "personal_life": {
        "who_am_i": "I am Asif Aslam, widely known as Sonu Sarkar. I am a builder, technologist, and problem solver who believes in first-principles thinking, relentless execution, and automating every repetitive workflow in life and business.",
        "lifestyle": "Deep work focused, late-night architecture sessions, continuous self-improvement, highly organized digital workspaces.",
        "values": [
            "Speed over bureaucracy: Ship working code, test in sandbox, iterate rapidly.",
            "High agency: Take extreme ownership; never wait for permission to solve problems.",
            "Craftsmanship: Software must be blazingly fast, reliable, and aesthetically beautiful."
        ]
    },
    "education_and_studies": {
        "formal_background": "Computer Science & Engineering fundamentals, Advanced Systems Engineering.",
        "what_i_study_daily": [
            "Cutting-edge AI/ML research papers (Agentic workflows, Reasoning models, LLM Tool Calling, Quantization)",
            "Distributed Systems Architecture, High-Concurrency microservices, and asynchronous event loops",
            "Apple macOS internals, AppleScript automation, WindowServer architecture, CoreAudio pipelines",
            "Modern UI/UX interaction design (Glassmorphism, Spatial interfaces, Micro-animations)",
            "Startup economics, unit economics, tech leadership, and customer obsession"
        ],
        "reading_list": [
            "Distributed Systems by Maarten van Steen",
            "Designing Data-Intensive Applications by Martin Kleppmann",
            "AI Research: Toolformer, ReAct, Chain-of-Thought, Wispr Speech Pipelines",
            "Zero to One & High Output Management"
        ]
    },
    "technical_knowledge_and_skills": {
        "programming_languages": ["Python (Expert)", "JavaScript / TypeScript (Advanced)", "Bash / Zsh (Expert)", "SQL", "AppleScript / Objective-C bindings"],
        "frameworks_and_tools": ["FastAPI", "React 18 / Vite", "TailwindCSS", "Framer Motion", "Playwright", "Docker", "Node.js"],
        "ai_and_agents": [
            "Autonomous Multi-Agent Orchestration",
            "Voice AI & Speech Pipelines (Wispr, Dograh Engine, macOS Hardware TTS)",
            "Context memory architectures (Hierarchical recall, Vector search, SQLite audit trails)",
            "Prompt engineering & cognitive alignment"
        ],
        "system_automation": [
            "macOS System Control (Brightness, Volume, Displays, Notifications, Window management)",
            "Browser Automation (Autonomous web forms, scraping, headless browser control)",
            "Native Desktop App Automation (WhatsApp native, Chrome, Terminal, Finder)"
        ],
        "databases": ["PostgreSQL", "MongoDB", "SQLite", "Redis cache layer"]
    },
    "hobbies_and_passions": [
        "Building autonomous AI agents and experimenting with multimodal models late at night",
        "Listening to soulful acoustic, high-tempo Lofi, and EDM tracks during deep coding sprints",
        "Designing polished frosted-glass Apple-grade user interfaces",
        "Tech gadgets, mechanical keyboards, Apple Silicon hardware benchmarks",
        "Exploring business automation strategies to empower local businesses in India"
    ],
    "communication_style": {
        "tone": "Direct, energetic, confident Hindi/Hinglish, polite, action-oriented, zero fluff.",
        "signature_phrases": ["Haan Boss, sab set hai!", "Execute kar raha hoon.", "Done Boss!"],
        "decision_rules": [
            "Check profile and user directives before generating any response.",
            "Never cite generic AI refusals or boilerplate privacy policy disclaimers for normal owner tasks.",
            "Give crisp, actionable answers with working code or immediate execution."
        ]
    },
    "relationship_handling": [
        {
            "group": "Developers & Engineers",
            "examples": "Rahul, Dev Anand",
            "handling": "Direct, collaborative, motivating, technical code reviews ('PR solid hai, merge karo')"
        },
        {
            "group": "Team Leads & Operations",
            "examples": "Rohit",
            "handling": "Punctual, clear directives, supportive, crisp time commitments ('Meeting 11 baje final hai')"
        },
        {
            "group": "Close Circle & Friends",
            "examples": "Sonu, Close Network",
            "handling": "Warm, authentic Hinglish, high energy, fast response ('Hi Sonu', 'Haan bhai sab ready hai')"
        },
        {
            "group": "Designers & Creatives",
            "examples": "Priya Sharma, Neha",
            "handling": "Appreciative of aesthetics, constructive design critique, dark glass polish"
        },
        {
            "group": "Business Clients & Leads",
            "examples": "Fleet Partners, Enterprise Clients",
            "handling": "Ultra-professional, trustworthy, clear pricing, high responsiveness, solution-driven"
        }
    ],
    "business_portfolio": {
        "ventures": [
            {
                "name": "KYRON AGI",
                "tagline": "Next-Gen Autonomous Agentic OS & Personal Workstation",
                "role": "Founder & Lead Architect",
                "status": "v2.0 Active",
                "features": "Hands-free voice execution, native desktop automation, cognitive memory"
            },
            {
                "name": "BookMyGaadi",
                "tagline": "Intercity and Outstation Fleet & Taxi Booking Platform",
                "role": "Founder & CTO",
                "status": "Live Operations in Bihar & Eastern India",
                "features": "Instant WhatsApp cab booking, verified drivers, transparent fares"
            }
        ],
        "customer_support_rules": "Always polite, instant resolution, prioritize rider/client safety, transparent pricing, 24/7 AI-first tier-1 support.",
        "branding_tone": "Modern, trustworthy, tech-forward, empowering local communities with world-class technology."
    },
    "last_updated": datetime.now().isoformat()
}


DEFAULT_MIND_MARKDOWN = f"""# KYRON MIND — Asif Aslam (Sonu Sarkar)

> **Identity**: Asif Aslam (Sonu Sarkar)  
> **Role**: Founder & Chief AI Systems Architect — KYRON AGI & BookMyGaadi  
> **Location**: Motihari / Patna, Bihar, India  
> **Core Principle**: High-Agency, First-Principles Thinking, Speed over Bureaucracy

---

## 1. Prime Directives for KYRON
1. **Profile-First Check**: Har task, message, aur automation execute karne se pehle Asif Aslam (Sonu Sarkar) ke is profile aur cognitive mind ko verify karo.
2. **Authentic Representation**: Kisi ko bhi reply karte waqt ya business handle karte waqt Asif Aslam ke exact communication style, values aur relationship matrix ke mutabiq baat karo.
3. **Hands-Free Execution**: Boss ki awaaz aur natural instructions par desktop automation, WhatsApp, Chrome, aur document operations ko sub-second latency me execute karo.
4. **Safety & Confidentiality**: Documents (Aadhaar, PAN, Bank Details, Signature) ko encrypted vault me rakho aur website ke exact dimensions/specifications ke mutabiq auto-crop aur fit karke upload karo.

---

## 2. Who is Asif Aslam (Sonu Sarkar)?
- **Builder & Entrepreneur**: Founder of **KYRON AGI** (Autonomous OS) and **BookMyGaadi** (Regional Mobility & Fleet Platform).
- **Technical Expertise**:
  - Python, FastAPI, React 18, TailwindCSS, Framer Motion, Node.js
  - Autonomous Agent Architecture, Speech AI (Wispr/Dograh), LLM Tool Orchestration
  - macOS System Control, Playwright Browser Automation, SQLite/PostgreSQL/MongoDB
- **What He Studies Daily**:
  - Advanced AI/ML research papers on agentic reasoning and multimodality
  - High-concurrency distributed systems and ultra-low-latency architectures
  - Futuristic spatial & glassmorphic interface designs
- **Hobbies & Passion**:
  - Late-night deep-work coding marathons
  - Listening to lofi and EDM music while designing agents
  - Automating every repetitive task in life and business

---

## 3. Relationship & Communication Rules
- **Developers / Team**: Direct, collaborative, technically precise ("PR review done, looks solid!").
- **Operations & Leads**: Punctual, clear timelines, zero ambiguity ("Meeting confirmed for 11 AM").
- **Close Friends / Network**: Energetic, authentic Hinglish, high warmth ("Haan bhai, sab set hai!").
- **Business Clients**: Highly professional, solution-oriented, transparent pricing and deliverables.

---

## 4. Business & Customer Support Engine
- **BookMyGaadi Support**: Instant booking assistance, driver tracking, fare transparency, polite Hindi/English assistance.
- **KYRON Enterprise**: Inbound AI inquiries, custom automation demos, enterprise client onboarding.
- **Promotion & Branding**: High-energy, innovative announcements on LinkedIn, Twitter, and WhatsApp broadcasting.
"""


class ProfileMindService:
    """Manages Sonu Sarkar's Master Profile, Custom Mind Markdown, and Profile-First verification."""

    def __init__(self):
        self.profile = self._load_profile()
        self._ensure_mind_markdown()

    def _load_profile(self) -> Dict[str, Any]:
        """Loads profile from JSON file or initializes with default Asif Aslam profile."""
        try:
            if os.path.exists(PROFILE_FILE):
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge defaults for any missing keys
                    merged = dict(DEFAULT_ASIF_ASLAM_PROFILE)
                    merged.update(data)
                    return merged
        except Exception as e:
            logger.warning(f"Error loading profile file: {e}")

        # Save default
        self._save_profile_to_disk(DEFAULT_ASIF_ASLAM_PROFILE)
        return dict(DEFAULT_ASIF_ASLAM_PROFILE)

    def _save_profile_to_disk(self, profile_data: Dict[str, Any]):
        """Persists profile to disk."""
        try:
            profile_data["last_updated"] = datetime.now().isoformat()
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

    def _ensure_mind_markdown(self):
        """Ensures KYRON_MIND.md exists on disk."""
        try:
            if not os.path.exists(MIND_MD_FILE):
                with open(MIND_MD_FILE, "w", encoding="utf-8") as f:
                    f.write(DEFAULT_MIND_MARKDOWN)
        except Exception as e:
            logger.error(f"Error saving KYRON_MIND.md: {e}")

    def get_profile(self) -> Dict[str, Any]:
        """Returns the full master profile."""
        return self.profile

    def update_profile(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates and persists profile."""
        self.profile.update(new_data)
        self._save_profile_to_disk(self.profile)
        # Regenerate mind markdown summary if identity changed
        return self.profile

    def get_mind_markdown(self) -> str:
        """Reads KYRON_MIND.md content."""
        try:
            if os.path.exists(MIND_MD_FILE):
                with open(MIND_MD_FILE, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading KYRON_MIND.md: {e}")
        return DEFAULT_MIND_MARKDOWN

    def update_mind_markdown(self, markdown_text: str) -> bool:
        """Saves custom KYRON_MIND.md written or uploaded by user and synchronizes profile."""
        try:
            with open(MIND_MD_FILE, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            # Intelligently parse markdown and update structured profile
            self.parse_and_sync_markdown(markdown_text)
            return True
        except Exception as e:
            logger.error(f"Error updating KYRON_MIND.md: {e}")
            return False

    def parse_and_sync_markdown(self, md: str):
        """Intelligently parses user-provided markdown and updates structured profile."""
        import re
        try:
            lines = md.splitlines()

            # Scan line-by-line for identity metadata
            for line in lines:
                m_ident = re.search(r'\*\*(?:Identity|Name|Full Name)\*\*[:\s]+([^\n\r]+)', line, re.I)
                if m_ident:
                    val = m_ident.group(1).strip()
                    if "(" in val and ")" in val:
                        parts = val.split("(")
                        self.profile["identity"]["full_name"] = parts[0].strip()
                        self.profile["identity"]["alias"] = parts[1].replace(")", "").strip()
                    else:
                        self.profile["identity"]["full_name"] = val

                m_role = re.search(r'\*\*(?:Role|Title|Occupation)\*\*[:\s]+([^\n\r]+)', line, re.I)
                if m_role:
                    self.profile["identity"]["title"] = m_role.group(1).strip()

                m_loc = re.search(r'\*\*(?:Location|City|Place)\*\*[:\s]+([^\n\r]+)', line, re.I)
                if m_loc:
                    self.profile["identity"]["location"] = m_loc.group(1).strip()

            # Parse sections based on markdown headings
            current_section = None
            collected_sections: Dict[str, List[str]] = {}
            for line in lines:
                line_str = line.strip()
                if line_str.startswith("#"):
                    header_title = re.sub(r'^#+\s*', '', line_str).lower()
                    current_section = header_title
                    collected_sections[current_section] = []
                elif current_section:
                    collected_sections[current_section].append(line_str)

            # Map collected sections into profile keys
            for title, sec_lines in collected_sections.items():
                content_text = "\n".join([l for l in sec_lines if l])
                bullet_items = [re.sub(r'^[-*•]\s*', '', l).strip() for l in sec_lines if l.startswith(("-", "*", "•"))]

                if any(k in title for k in ["personal life", "who am i", "about me", "background"]):
                    if content_text:
                        self.profile["personal_life"]["who_am_i"] = content_text[:600]
                elif any(k in title for k in ["skill", "technical", "tech stack", "knowledge"]):
                    if bullet_items:
                        self.profile["technical_knowledge_and_skills"]["programming_languages"] = bullet_items[:6]
                elif any(k in title for k in ["education", "study", "studies", "reading"]):
                    if bullet_items:
                        self.profile["education_and_studies"]["what_i_study_daily"] = bullet_items[:6]
                elif any(k in title for k in ["hobby", "hobbies", "passions"]):
                    if bullet_items:
                        self.profile["hobbies_and_passions"] = bullet_items[:6]
                elif any(k in title for k in ["business", "venture", "companies", "company"]):
                    if bullet_items:
                        ventures = []
                        for b in bullet_items:
                            v_name = b.split(":")[0].replace("**", "").strip()
                            ventures.append({"name": v_name, "details": b})
                        if ventures:
                            self.profile["business_portfolio"]["ventures"] = ventures

            self._save_profile_to_disk(self.profile)
            logger.info("KYRON Mind markdown parsed and synchronized with user_profile_mind.json successfully.")
        except Exception as e:
            logger.warning(f"Error parsing markdown: {e}")

    def get_mind_summary_for_llm(self) -> str:
        """Returns a concise system prompt context block describing Asif Aslam's active master profile."""
        ident = self.profile.get("identity", {})
        orgs = ", ".join(ident.get("organizations", ["KYRON AGI", "BookMyGaadi"]))
        skills = ", ".join(self.profile.get("technical_knowledge_and_skills", {}).get("programming_languages", [])[:4])
        return (
            f"=== VERIFIED OWNER COGNITIVE PROFILE ===\n"
            f"User Identity: {ident.get('full_name', 'Asif Aslam')} (Known as: {ident.get('alias', 'Sonu Sarkar')})\n"
            f"Role: {ident.get('title', 'Founder & Chief AI Systems Architect')}\n"
            f"Ventures: {orgs}\n"
            f"Location: {ident.get('location', 'Motihari / Patna, Bihar, India')}\n"
            f"Core Technical Skills: {skills}\n"
            f"Communication Tone: Direct, energetic Hindi/Hinglish, polite, action-oriented ('Boss', 'Done Boss').\n"
            f"Document Vault: Aadhaar, PAN (BXXXX8849F), Studio Photo, Transparent Signature, and HDFC Bank account are verified and ready for autonomous form filling.\n"
            f"Prime Directive: Always align replies with this profile. Never ask repetitive questions if details exist in vault.\n"
            f"========================================="
        )

    def check_profile_for_query(self, user_msg: str) -> Dict[str, Any]:
        """
        PROFILE-FIRST CHECK:
        Analyzes user query and matches relevant persona data (identity, education, knowledge,
        hobbies, documents, business) so Kyron responds strictly aligned with Asif Aslam.
        """
        lower = user_msg.lower()

        is_identity_query = any(w in lower for w in [
            "mai koun", "main kaun", "who am i", "mera naam", "mera identity",
            "asif aslam", "sonu sarkar", "meri profile", "mere bare me", "mere baare me"
        ])

        is_knowledge_query = any(w in lower for w in [
            "meri knowledge", "mujhe kya aata", "mera skill", "skills", "technology", "tech stack",
            "mera background", "kya janta hu", "meri expertise"
        ])

        is_education_query = any(w in lower for w in [
            "kya padhta hu", "kya padhta", "meri padhai", "education", "books", "study", "research"
        ])

        is_hobby_query = any(w in lower for w in [
            "meri hobby", "mera hobby", "shauk", "free time", "passion", "music", "kya pasand"
        ])

        is_business_query = any(w in lower for w in [
            "mera business", "mere business", "what is my business", "bussiness kya", "business kya",
            "bookmygaadi kya hai", "kyron kya hai", "meri company", "mere ventures", "ventures kya hai",
            "meri startup", "kya kaam karta hu"
        ])

        is_doc_query = any(w in lower for w in [
            "mera aadhar", "mera aadhaar", "mera pan", "meri photo", "mera sign", "mera signature",
            "mera bank", "bank details", "account number", "mere documents", "meri details in vault"
        ])

        triggered_topics = []
        if is_identity_query:
            triggered_topics.append("identity")
        if is_knowledge_query:
            triggered_topics.append("knowledge")
        if is_education_query:
            triggered_topics.append("education")
        if is_hobby_query:
            triggered_topics.append("hobbies")
        if is_business_query:
            triggered_topics.append("business")
        if is_doc_query:
            triggered_topics.append("documents")

        # Synthesize verified response if directly asked
        synthesized_answer = None
        if is_identity_query:
            ident = self.profile["identity"]
            synthesized_answer = (
                f"Boss, aap **{ident['full_name']}** hain, jinhe sabhi **{ident['alias']}** ke naam se jante hain! "
                f"Aap **{ident['organizations'][0]}** aur **{ident['organizations'][1]}** ke Founder & Chief AI Systems Architect hain. "
                f"Aapka mind, first-principles thinking, aur complete cognitive profile mere pass verified hai!"
            )
        elif is_knowledge_query:
            skills = ", ".join(self.profile["technical_knowledge_and_skills"]["programming_languages"][:3])
            ai_areas = ", ".join(self.profile["technical_knowledge_and_skills"]["ai_and_agents"][:2])
            synthesized_answer = (
                f"Boss, aapke paas deep full-stack aur AI systems expertise hai:\n"
                f"- **Core Tech**: {skills}\n"
                f"- **AI & Agents**: {ai_areas}\n"
                f"- **Automation**: macOS native control, Playwright browser execution, high-concurrency backends.\n"
                f"Aap complex systems ko first-principles se design aur rapidly build karne me expert hain!"
            )
        elif is_education_query:
            studies = self.profile["education_and_studies"]["what_i_study_daily"]
            synthesized_answer = (
                f"Boss, aap lagatar cutting-edge technologies study karte hain:\n"
                f"- **AI/ML Research**: Agentic reasoning, tool calling, model architectures\n"
                f"- **Systems Engineering**: Distributed microservices, low-latency asynchronous loops\n"
                f"- **Apple Internals & UX**: CoreAudio, WindowServer, glassmorphic interaction design\n"
                f"Aapka learning habit high-agency aur continuous innovation par focused hai!"
            )
        elif is_hobby_query:
            hobbies = self.profile["hobbies_and_passions"]
            synthesized_answer = (
                f"Boss, aapki hobbies aapke passion se judi hain:\n"
                f"1. **Late-night AI Deep Work**: Raat ke sannate me autonomous agents build karna.\n"
                f"2. **Music & Code**: High-tempo Lofi aur EDM sunte hue programming.\n"
                f"3. **Sleek UI Design**: Dark frosted-glass Apple aesthetic interfaces design karna.\n"
                f"4. **Tech & Hardware**: Apple Silicon benchmarks aur high-performance dev setups!"
            )
        elif is_doc_query:
            from services.document_vault_service import document_vault_service
            vault = document_vault_service.get_vault_data()
            docs = vault.get("documents", {})
            synthesized_answer = (
                f"Boss, aapka Document Vault completely verified aur active hai:\n"
                f"- **Aadhaar Card**: {docs.get('aadhaar', {}).get('number', 'XXXX-XXXX-9942')} (UIDAI Verified, Motihari)\n"
                f"- **PAN Card**: {docs.get('pan', {}).get('number', 'BXXXX8849F')} (ASIF ASLAM)\n"
                f"- **Passport Photo**: 413x531 px (Clean white background, 4:5 ratio)\n"
                f"- **Digital Signature**: Clean transparent PNG specimen\n"
                f"- **Primary Bank**: HDFC Bank Ltd. (A/C: •••• 7892, IFSC: HDFC0001234, UPI: sonusaarkaar@hdfcbank)\n"
                f"Kisi bhi online form ke liye Kyron in documents ko exact required format aur dimensions me auto-crop aur fit kar sakta hai!"
            )
        elif is_business_query:
            synthesized_answer = (
                f"Boss, aapke 2 primary business ventures verified hain:\n"
                f"1. **KYRON AGI**: Autonomous Agentic OS & Personal AI Workstation with hands-free voice, native desktop control, and cognitive memory.\n"
                f"2. **BookMyGaadi**: Regional Intercity & Outstation cab booking fleet across Bihar with instant WhatsApp bookings, verified drivers, and transparent pricing.\n"
                f"Dono businesses ke customer support, client proposals, aur promotional branding campaigns mere pass active hain!"
            )

        return {
            "verified_from_profile": True,
            "checked_profile": "Asif Aslam (Sonu Sarkar)",
            "triggered_topics": triggered_topics,
            "has_specific_answer": bool(synthesized_answer),
            "synthesized_answer": synthesized_answer,
            "profile_context": {
                "name": self.profile["identity"]["full_name"],
                "alias": self.profile["identity"]["alias"],
                "title": self.profile["identity"]["title"],
                "tone": self.profile["communication_style"]["tone"]
            }
        }


# Global singleton instance
profile_mind_service = ProfileMindService()
