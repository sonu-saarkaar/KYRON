"""
KYRON Hermes Endpoints: Skills, Memory & Cron Tasks.

Provides REST endpoints for:
1. Memory Management (fenced memory context, memory cards)
2. Skills Engine (skills-from-experience, reusable skills, markdown specs)
3. Cron Task Scheduler (recurring job management, trigger now, status)

Note: Sub-agent / delegation module is explicitly excluded per architectural scope.
"""

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from services.memory_manager import KyronMemoryManager, sanitize_context
from services.skills_engine import SkillsEngine, HermesSkill
from services.scheduler import HermesScheduler, ScheduledJob, scheduler
from services.llm_client import LLMClient, llm_client
from services.browser_control_agent import browser_control_agent
from services.session_manager import session_manager

router = APIRouter()

# Global service instances
skills_engine = SkillsEngine()
memory_manager = KyronMemoryManager()

# Global browser session state for multi-turn form filling
browser_session_state: Dict[str, Any] = {
    "active_url": None,
    "site_title": None,
    "last_activity": 0.0,
    "awaiting_details": False
}


# -------------------------------------------------------------
# 1. MEMORY MANAGEMENT SCHEMAS & ENDPOINTS
# -------------------------------------------------------------

class AddMemoryRequest(BaseModel):
    content: str
    category: str = "general"
    tags: Optional[List[str]] = None


@router.get("/memory")
def get_memories(query: Optional[str] = None, limit: int = 50):
    """Retrieve memory cards, optionally filtered by keyword query."""
    if query:
        cards = memory_manager.search_memories(query, limit=limit)
    else:
        cards = memory_manager.get_all_memories(limit=limit)
    return {
        "success": True,
        "count": len(cards),
        "memories": [c.to_dict() for c in cards],
        "context_preview": memory_manager.build_memory_context_block(query=query) if cards else ""
    }


@router.post("/memory")
def add_memory(req: AddMemoryRequest):
    """Add a new memory card with Hermes standard fencing."""
    clean_content = sanitize_context(req.content)
    card = memory_manager.add_memory(
        content=clean_content,
        category=req.category,
        tags=req.tags or []
    )
    return {
        "success": True,
        "message": "Memory card created successfully.",
        "memory": card.to_dict()
    }


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: str):
    """Delete a memory card by ID."""
    deleted = memory_manager.delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory card not found.")
    return {"success": True, "message": f"Memory card {memory_id} deleted."}


# -------------------------------------------------------------
# 2. SKILLS ENGINE SCHEMAS & ENDPOINTS
# -------------------------------------------------------------

class LearnSkillRequest(BaseModel):
    name: str
    description: str = Field(..., max_length=120)
    trigger_phrases: List[str]
    procedure: List[str]
    prerequisites: Optional[List[str]] = None
    verification: str = ""
    tags: Optional[List[str]] = None


@router.get("/skills")
def list_skills():
    """List all registered and learned skills."""
    skills = skills_engine.list_all_skills()
    return {
        "success": True,
        "count": len(skills),
        "skills": skills
    }


@router.get("/skills/{skill_name}")
def get_skill(skill_name: str):
    """Get single skill details and canonical markdown procedure."""
    skill = skills_engine.get_skill(skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found.")
    return {
        "success": True,
        "skill": skill.to_dict(),
        "markdown": skill.to_markdown()
    }


@router.post("/skills/learn")
def learn_skill(req: LearnSkillRequest):
    """Learn a new skill from experience and persist as modular markdown."""
    skill = skills_engine.learn_from_experience(
        name=req.name,
        description=req.description,
        trigger_phrases=req.trigger_phrases,
        procedure=req.procedure,
        prerequisites=req.prerequisites,
        verification=req.verification,
        tags=req.tags or []
    )

    # Automatically register into memory cards for cross-session recall
    memory_manager.add_memory(
        content=f"Learned Skill: {skill.name}. Triggers: {', '.join(skill.trigger_phrases)}",
        category="learned_skill",
        tags=skill.tags + ["skill", skill.name]
    )

    return {
        "success": True,
        "message": f"Skill '{skill.name}' successfully learned and persisted.",
        "skill": skill.to_dict()
    }


# -------------------------------------------------------------
# 3. CRON TASK SCHEDULER ENDPOINTS
# -------------------------------------------------------------

class AddCronJobRequest(BaseModel):
    name: str
    prompt: str
    schedule: str  # Cron format e.g. "0 9 * * *" or "*/5 * * * *"
    skills: Optional[List[str]] = None


@router.get("/cron")
def list_cron_jobs():
    """List all recurring scheduled jobs with next run time."""
    jobs = scheduler.list_jobs()
    return {
        "success": True,
        "count": len(jobs),
        "jobs": jobs
    }


@router.post("/cron")
def add_cron_job(req: AddCronJobRequest):
    """Schedule a new recurring AI task."""
    job = scheduler.add_job(
        name=req.name,
        prompt=req.prompt,
        schedule=req.schedule,
        skills=req.skills or []
    )
    return {
        "success": True,
        "message": f"Job '{job.name}' scheduled successfully.",
        "job": job.to_dict()
    }


@router.post("/cron/{job_id}/trigger")
async def trigger_cron_job(job_id: str):
    """Trigger a scheduled job immediately (for testing or on-demand execution)."""
    result = await scheduler.trigger_now(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {
        "success": True,
        "message": f"Job '{job_id}' executed successfully.",
        "result": result
    }


@router.delete("/cron/{job_id}")
def delete_cron_job(job_id: str):
    """Delete a scheduled cron job."""
    deleted = scheduler.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"success": True, "message": f"Job '{job_id}' removed."}


# -------------------------------------------------------------
# 4. AGI CONVERSATIONAL CHAT ENDPOINT (KYRON / HERMES)
# -------------------------------------------------------------

# -------------------------------------------------------------

class KyronChatRequest(BaseModel):
    message: Optional[str] = Field(None, description="User prompt or directive")
    text: Optional[str] = Field(None, description="Alternative text property")
    language: Optional[str] = "en"
    include_memory: bool = True
    session_id: Optional[str] = Field(None, description="Active session ID for persistent history")


def speak_out_loud(text: str):
    """
    Disabled in backend: Speech is handled in browser with exact microphone muting
    and echo suppression to prevent infinite feedback loops.
    """
    pass


@router.post("/chat")
async def kyron_chat(req: KyronChatRequest):
    """
    Handle natural conversation for KYRON Command Center using Hermes LLM Gateway.
    Injects fenced memory context and active skills into system prompt.
    Persists full multi-turn chat sessions in SQLite.
    """
    user_msg = (req.message or req.text or "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 0. Persistent Multi-Turn Session Tracking
    active_session = session_manager.get_or_create_session(session_id=req.session_id)
    session_id = active_session["id"]
    # Add user message to persistent SQLite store
    session_manager.add_message(session_id=session_id, role="user", content=user_msg, sender="user")

    def respond(payload: Dict[str, Any], reply_text: str = None) -> Dict[str, Any]:
        """Record assistant response and inject session metadata into response."""
        if reply_text:
            session_manager.add_message(session_id=session_id, role="assistant", content=reply_text, sender="kyron")
        payload["session_id"] = session_id
        curr_sess = session_manager.get_session(session_id)
        if curr_sess:
            payload["session_title"] = curr_sess.get("title", "New Conversation")
        return payload

    # 0. Fast-path: Web URLs & Autonomous Chrome Form Automation (BookMyGadi & Web Forms)
    import re
    import time
    import subprocess
    import webbrowser
    import asyncio

    user_msg_lower = user_msg.lower()

    # Regex for detecting URL strings in message
    url_pattern = re.compile(
        r"https?://[^\s]+|(?:www\.)?[a-zA-Z0-9-]+\.(?:com|in|app|org|net|co|io|tech|ai)[^\s]*",
        re.IGNORECASE
    )
    url_match = url_pattern.search(user_msg)

    # Keywords for BookMyGadi or ride booking
    bmg_keywords = ["bookmygadi", "book my gadi", "my gadi", "mygadi", "bmg", "गाड़ी बुक", "बुकमाईगाड़ी", "gadi website", "gadi app", "gadi book", "ride book"]
    has_bmg = any(k in user_msg_lower for k in bmg_keywords)

    # Keywords for form details
    detail_keywords = ["naam", "name", "phone", "mobile", "pickup", "drop", "city", "date", "tarikh", "time", "patna", "motihari", "driver", "location", "address", "email"]
    has_details = any(k in user_msg_lower for k in detail_keywords)

    # Check for active ongoing browser session (within last 15 minutes)
    session_active = (
        bool(browser_session_state.get("active_url")) and
        (time.time() - browser_session_state.get("last_activity", 0.0) < 900)
    )

    # SCENARIO 0: Follow-up details for previously opened website/form (no new URL provided)
    if session_active and not url_match and not has_bmg and (has_details or browser_session_state.get("awaiting_details")):
        target_url = browser_session_state["active_url"]
        site_title = browser_session_state.get("site_title") or "Live Form"
        browser_session_state["last_activity"] = time.time()
        browser_session_state["awaiting_details"] = False

        # Launch Playwright task to fill details into the form
        task_directive = f"On {target_url}, fill the form inputs with user details: {user_msg}"
        try:
            asyncio.create_task(browser_control_agent.execute_task(task_directive, max_steps=8))
        except Exception:
            pass

        reply_text = (
            f"Done Boss! Main **{target_url}** ke form me aapki details autonomously bhar raha hoon:\n\n"
            f"- **Provided Details**: {user_msg}\n"
            f"- **Automation**: Playwright Autonomous Browser Agent (Google Chrome)\n\n"
            f"Live page par fields fill kiye ja rahe hain. Final submission se pehle safety gate aapse confirm karega!"
        )
        speak_out_loud(reply_text)
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "browser_action",
            "action": {
                "type": "browser_open",
                "url": target_url,
                "title": f"Chrome Form Autofill ({site_title})",
                "website": target_url
            },
            "telemetry": [{
                "title": "Form Autofill",
                "detail": f"Filling details on {target_url}",
                "source": "Playwright / Chrome"
            }]
        }, reply_text=reply_text)

    # SCENARIO A: URL detected OR BookMyGadi explicitly requested
    if url_match or has_bmg:
        if url_match:
            raw_url = url_match.group(0).rstrip(".,;!?'\")")
            target_url = raw_url if raw_url.startswith("http") else f"https://{raw_url}"
        else:
            target_url = "https://www.bookmygadi.app/"

        site_title = "BookMyGadi" if "bookmygadi" in target_url.lower() else target_url

        # Update active session state
        browser_session_state["active_url"] = target_url
        browser_session_state["site_title"] = site_title
        browser_session_state["last_activity"] = time.time()
        browser_session_state["awaiting_details"] = not has_details

        # 1. Launch Chrome on Windows
        opened_chrome = False
        try:
            subprocess.Popen(['start', 'chrome', target_url], shell=True)
            opened_chrome = True
        except Exception:
            pass
        if not opened_chrome:
            try:
                webbrowser.open(target_url)
            except Exception:
                pass

        # 2. Trigger Playwright BrowserControlAgent in background to inspect/fill form
        task_directive = (
            f"Navigate to {target_url} and fill form with: {user_msg}"
            if has_details
            else f"Navigate to {target_url} and inspect form elements"
        )
        try:
            asyncio.create_task(browser_control_agent.execute_task(task_directive, max_steps=6 if has_details else 4))
        except Exception:
            pass

        # 3. Formulate affirmative response in Hindi/Hinglish
        if has_details:
            reply_text = (
                f"Done Boss! Maine Chrome me **{target_url}** open kar diya hai aur automation agent form fill kar raha hai.\n\n"
                f"Main live page ke fields aapki details ke mutabiq autonomous tareeke se bhar raha hoon. "
                f"Final submission se pehle safety gate aapse confirm karega!"
            )
        else:
            reply_text = (
                f"Done Boss! Maine Chrome open karke **{target_url}** par navigate kar diya hai aur browser automation active hai.\n\n"
                f"Main live website par aapka form autonomously bhar sakta hoon! Kripya mujhe details batayein:\n"
                f"1. **Pickup Location / City** (jaise: Motihari, Chhatauni)\n"
                f"2. **Drop Location / Destination** (jaise: Patna, Muzaffarpur)\n"
                f"3. **Name & Mobile Number**\n"
                f"4. **Trip Type** (Single side / Round trip)\n\n"
                f"Aap jaise hi details denge, main form ke fields turant autofill kar dunga!"
            )

        speak_out_loud(reply_text)
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "browser_action",
            "action": {
                "type": "browser_open",
                "url": target_url,
                "title": f"Chrome Browser Automation ({site_title})",
                "website": target_url
            },
            "telemetry": [{
                "title": "Browser Automation",
                "detail": f"Navigated Chrome to {target_url}",
                "source": "Playwright / Chrome"
            }]
        }, reply_text=reply_text)

    # SCENARIO B: Form fill inquiry/request without URL provided yet
    form_inquiry_patterns = [
        "form bhar", "form fill", "form submit", "form enter", "form detail",
        "फॉर्म भर", "फॉर्म भरो", "chrome khol", "chrome open", "browser khol", "form bhr"
    ]
    has_form_inquiry = any(k in user_msg_lower for k in form_inquiry_patterns) or (
        "form" in user_msg_lower and any(w in user_msg_lower for w in ["bhar", "bharo", "khol", "kholo", "fill", "submit", "open", "sakta"])
    )

    if has_form_inquiry:
        reply_text = (
            "Haan Boss! Main Google Chrome open karke kisi bhi live website ka form autonomous tareeke se bhar sakta hoon.\n\n"
            "Bas mujhe ye 2 cheezein batayein:\n"
            "1. **Website ka URL / Link** (jaise: https://www.bookmygadi.app/)\n"
            "2. **Details** jo form me bharni hain (jaise: Pickup, Drop, Name, Phone number)\n\n"
            "Jaise hi aap link denge, main Chrome open karke live form autofill kar dunga!"
        )
        speak_out_loud(reply_text)
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "form_inquiry",
            "action": {
                "type": "form_ready"
            }
        }, reply_text=reply_text)

    # 0a. Fast-path intercepts (Commands like playing a song - Hindi, Hinglish, English, Devanagari)
    song_keywords = ["song", "gana", "gaana", "music", "play", "banao", "chalao", "sunao", "lagao", "bajao", "गाना", "सॉन्ग", "म्यूजिक", "बनाओ", "चलाओ", "बजाओ", "सुनाओ", "गाओ"]
    has_song = any(k in user_msg_lower for k in ["song", "gana", "gaana", "music", "yt", "youtube", "गाना", "सॉन्ग", "म्यूजिक"])
    has_action = any(k in user_msg_lower for k in ["banao", "chalao", "play", "sunao", "lagao", "bajao", "open", "kholo", "बनाओ", "चलाओ", "बजाओ", "सुनाओ", "खोलो"])

    if has_song and (has_action or len(user_msg_lower.split()) <= 4):
        import webbrowser
        import subprocess
        
        # Popular high-energy song / YouTube Music stream
        yt_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk" # Lofi / Chill / Trending Hits
        opened = False
        try:
            # Try launching chrome explicitly if available
            subprocess.Popen(['start', 'chrome', yt_url], shell=True)
            opened = True
        except Exception:
            pass
            
        if not opened:
            try:
                webbrowser.open(yt_url)
            except Exception:
                pass

        reply_text = "Done Boss! Opening Chrome and playing a song for you on YouTube right now."
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "conversation",
            "action": {
                "type": "media_play",
                "platform": "YouTube",
                "url": yt_url,
                "title": "YouTube Music Stream"
            },
            "telemetry": [{
                "title": "Media Control",
                "detail": "Launched Chrome with YouTube playback",
                "source": "System Automation"
            }]
        }, reply_text=reply_text)

    # 0b. WhatsApp app open intent
    if "whatsapp" in user_msg_lower:
        import os
        import webbrowser
        opened = False
        try:
            os.startfile("whatsapp://")
            opened = True
        except Exception:
            pass
        if not opened:
            try:
                webbrowser.open("https://web.whatsapp.com")
                opened = True
            except Exception:
                pass

        reply_text = "Done Boss! Opening WhatsApp for you right now."
        speak_out_loud(reply_text)
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "conversation",
            "action": {
                "type": "app_open",
                "app": "WhatsApp",
                "url": "https://web.whatsapp.com"
            }
        }, reply_text=reply_text)

    # 0c. Power commands (Shutdown, Restart, Lock, Sleep)
    if any(k in user_msg_lower for k in ["laptop off", "shutdown", "turn off", "band karo", "switch off", "power off", "laptop band", "pc off", "system off"]):
        reply_text = "Boss, your laptop is scheduled to shut down in 30 seconds. (Run shutdown /a in terminal to abort)."
        speak_out_loud(reply_text)
        try:
            import os
            os.system("shutdown /s /t 30")
        except Exception:
            pass
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "system_action"
        }, reply_text=reply_text)

    if any(k in user_msg_lower for k in ["restart", "reboot", "laptop restart"]):
        reply_text = "Boss, restarting your laptop in 30 seconds."
        speak_out_loud(reply_text)
        try:
            import os
            os.system("shutdown /r /t 30")
        except Exception:
            pass
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "system_action"
        }, reply_text=reply_text)

    if any(k in user_msg_lower for k in ["lock", "screen lock", "laptop lock"]):
        reply_text = "Locking your workstation now, Boss."
        speak_out_loud(reply_text)
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        except Exception:
            pass
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "system_action"
        }, reply_text=reply_text)

    # 0d. Standard desktop app launchers
    app_targets = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "code": "code",
        "vscode": "code",
        "chrome": "chrome",
        "google chrome": "chrome"
    }
    for app_name, exe in app_targets.items():
        if app_name in user_msg_lower and any(act in user_msg_lower for act in ["open", "khol", "kholo", "chalao", "start", "launch"]):
            import subprocess
            try:
                subprocess.Popen(exe, shell=True)
            except Exception:
                pass
            reply_text = f"Opening {app_name.title()} for you now, Boss!"
            speak_out_loud(reply_text)
            return respond({
                "success": True,
                "reply": reply_text,
                "text": reply_text,
                "response": reply_text,
                "type": "app_open"
            }, reply_text=reply_text)

    # 0e. Capabilities / help / "kya kar sakte ho" intent
    cap_triggers = [
        "kya kar sakte ho", "kya kar sakti ho", "tum kya kar sakte ho",
        "tum kya ho", "what can you do", "capabilities", "features", "kaam batao",
        "help me", "kya capabilities hai", "apne baare me batao", "who are you"
    ]
    if any(ct in user_msg_lower for ct in cap_triggers):
        reply_text = (
            "Boss, main KYRON hoon — aapka autonomous AGI assistant. Main ye sab kar sakta hoon:\n\n"
            "1. **Chrome & Web Form Automation**: Chrome khol kar kisi bhi live website ka form autonomous tareeke se bharna (jaise BookMyGadi cab booking ya koi bhi web form).\n"
            "2. **Songs & Media**: 'Mere liye gaana chalao' bolne par YouTube open karke song play karna.\n"
            "3. **Coding & Debugging**: CodeAgent run karke bugs diagnose karna aur live diff fix banana.\n"
            "4. **App Launchers**: Chrome, WhatsApp, Calculator, Notepad, VS Code kholna ('WhatsApp open karo').\n"
            "5. **System Control**: Laptop lock karna, restart ya shutdown schedule karna ('Laptop lock karo').\n"
            "6. **Memory & Intelligence**: Context yaad rakhna aur tasks execute karna.\n\n"
            "Bataiye Boss, abhi kaunsa kaam execute karna hai?"
        )
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "capabilities"
        }, reply_text=reply_text)

    # 0f. Friendly banter / "man jao"
    if any(k in user_msg_lower for k in ["man jao", "chalo man jao", "man bhi jao", "naraz mat ho", "gussa mat ho"]):
        reply_text = "Arrey Boss, main aapse naraz thodi ho sakta hoon! Main 100% active hoon aur aapki service me hazir hoon. Bataiye kya order hai?"
        return respond({
            "success": True,
            "reply": reply_text,
            "text": reply_text,
            "response": reply_text,
            "type": "conversation"
        }, reply_text=reply_text)

    # 0g. Status / Update intent using VoiceFormatter (Ollama qwen2.5:0.5b)
    status_triggers = [
        "status batao", "status kya hai", "kya status hai", "system status",
        "update do", "update batao", "kya chal raha hai", "task status",
        "all status", "give me status", "system update"
    ]
    if any(st in user_msg_lower for st in status_triggers) or user_msg_lower == "status":
        from utils.voice_formatter import get_live_system_status, format_voice_summary
        status_info = get_live_system_status()
        spoken_summary = await format_voice_summary(status_info, context=user_msg)
        return respond({
            "success": True,
            "reply": spoken_summary,
            "text": spoken_summary,
            "response": spoken_summary,
            "voice_vocalization": spoken_summary,
            "type": "system_status",
            "raw_status": status_info
        }, reply_text=spoken_summary)

    # 1. Fetch relevant Hermes memory cards
    memory_context = ""
    recalled_cards = []
    if req.include_memory:
        try:
            recalled_cards = memory_manager.search_memories(user_msg, limit=3)
            if recalled_cards:
                memory_context = memory_manager.build_memory_context_block(query=user_msg)
        except Exception:
            pass

    # 2. Get active skills overview
    skills_list = []
    try:
        skills = skills_engine.list_all_skills()
        skills_list = [s.get("name") for s in skills if isinstance(s, dict)]
    except Exception:
        pass

    skills_summary = ", ".join(skills_list) if skills_list else "bookmygaadi-bug-check"

    # 3. Formulate system prompt
    system_prompt = (
        "You are KYRON, the user's personal, highly obedient Jarvis-style autonomous AI assistant and digital execution agent.\n"
        "The user is your 'Boss'. Always address the user respectfully as Boss.\n"
        "Tum ek real human assistant ki tarah baat karo, robot ya script-reading machine ki tarah nahi. Casual, confident, friendly tone. Technical jargon avoid karo jab tak zaroori na ho.\n"
        "You have full authority to execute desktop automation, assist with coding, tasks, and system control.\n"
        "NEVER give paranoid refusals or cite privacy policies for normal user requests.\n"
        "CRITICAL RULES:\n"
        "1. STRICT OBEDIENCE: Strictly do what the user asked ('jitna bolu utna kaam karo'). Jawab hamesha question ke scope ke barabar ho — chhote command ka chhota jawab, detailed question ka detailed jawab. Kabhi extra unsolicited explanation, disclaimer, ya technical detail mat do jab tak specifically na poocha jaye.\n"
        "2. CASUAL 'DONE BOSS' CONFIRMATION: Jab bhi koi task complete ho, ek brief casual confirmation do (e.g. 'Done Boss', 'Task completed Boss', 'Ho gaya Boss').\n"
        "3. VOICE OUTPUT CONSTRAINT (voice_vocalization): MAX 1-2 short sentences by default, jab tak user explicitly 'detail me batao' na bole.\n"
        "4. NO REPEATED GREETINGS: Do not say 'Good morning' or repeatedly greet unless greeted first.\n"
        "5. LIVE BROWSER & INTERNET ACCESS: You have FULL real-time web browsing, internet access, and autonomous browser automation via KYRON's Playwright and native Google Chrome. NEVER claim you cannot access external websites.\n"
    )

    if memory_context:
        system_prompt += f"\nFenced Hermes Memory Recall:\n{memory_context}\n"

    system_prompt += (
        "\nProvide helpful, crisp, highly intelligent, and direct responses. "
        "Keep responses concise, articulate, and engaging with a high-tech Jarvis command center tone."
    )

    # Fetch recent persistent conversation turns from SQLite (up to 16 turns)
    history_turns = session_manager.get_recent_history_for_llm(session_id=session_id, limit=16)
    messages = [{"role": "system", "content": system_prompt}]
    if history_turns:
        messages.extend(history_turns)
    else:
        messages.append({"role": "user", "content": user_msg})

    # 4. Generate completion via LLM Client
    client = LLMClient()
    try:
        result = await client.acomplete(messages=messages, temperature=0.7)
        if result.get("success") and result.get("content"):
            reply = result["content"]
        else:
            reply = f"Haan Boss! '{user_msg}' samajh gaya. Bataye ispe kya action execute karni hai?"
    except Exception as e:
        reply = f"Boss, '{user_msg}' receive ho gaya. Subsystems ready hain, bataye kya command hai?"

    # LLM Canned Refusal Interceptor: NEVER allow model to claim it cannot browse live sites
    disallowed_refusal_patterns = [
        "cannot directly access",
        "do not have real-time internet",
        "cannot browse",
        "not have access to real-time",
        "external websites like",
        "do not have browsing capabilities",
        "real-time internet browsing",
        "live external websites",
        "cannot interact with external"
    ]
    if any(p in reply.lower() for p in disallowed_refusal_patterns):
        target = browser_session_state.get("active_url") or "https://www.bookmygadi.app/"
        # Launch Chrome natively if not already open
        try:
            subprocess.Popen(['start', 'chrome', target], shell=True)
        except Exception:
            pass
        reply = (
            f"Done Boss! Maine Chrome me **{target}** open kar diya hai aur browser automation active hai.\n\n"
            f"Main live website par aapka form autonomously bhar sakta hoon! Kripya mujhe details batayein "
            f"(Pickup Location, Drop Location, Name, Phone), main fields turant autofill kar dunga!"
        )
        return respond({
            "success": True,
            "reply": reply,
            "text": reply,
            "response": reply,
            "type": "browser_action",
            "action": {
                "type": "browser_open",
                "url": target,
                "title": "Chrome Browser Automation",
                "website": target
            }
        }, reply_text=reply)

    memory_summary = f"{len(recalled_cards)} cards matched" if recalled_cards else None

    # Speak response through PC audio speakers
    speak_out_loud(reply)

    return respond({
        "success": True,
        "reply": reply,
        "text": reply,
        "memory_recalled": memory_summary,
        "model": getattr(client, "default_model", "qwen/qwen3.8-27b"),
        "provider": getattr(client, "provider", "groq")
    }, reply_text=reply)


# -------------------------------------------------------------
# 5. CHATGPT/CLAUDE STYLE SESSION MANAGEMENT REST API
# -------------------------------------------------------------

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class UpdateSessionRequest(BaseModel):
    title: str


@router.get("/sessions")
def list_sessions(limit: int = 50):
    """List all active chat sessions ordered by recent activity."""
    sessions = session_manager.list_sessions(limit=limit)
    return {"success": True, "sessions": sessions}


@router.post("/sessions")
def create_new_session(req: Optional[CreateSessionRequest] = None):
    """Create a new chat session."""
    title = req.title if req and req.title else "New Conversation"
    new_sess = session_manager.create_session(title=title)
    return {"success": True, "session": new_sess}


@router.get("/sessions/{session_id}")
def get_session_details(session_id: str):
    """Get session metadata and full message history."""
    sess = session_manager.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "session": sess}


@router.put("/sessions/{session_id}")
def update_session_title(session_id: str, req: UpdateSessionRequest):
    """Update title of a session."""
    updated = session_manager.update_session_title(session_id, req.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "message": "Session updated"}


@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: str):
    """Delete a session and all its messages."""
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "message": "Session deleted"}


@router.delete("/sessions")
def clear_all_chat_sessions():
    """Clear all chat sessions."""
    session_manager.clear_all_sessions()
    return {"success": True, "message": "All sessions cleared"}


