"""
KYRON Voice Guidance Service
Provides text-to-speech and speech-to-text capabilities
"""

import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VoiceService:
    """Voice guidance service for KYRON"""
    
    def __init__(self):
        """Initialize voice service"""
        self.tts_available = False
        self.stt_available = False
        self._init_services()
    
    def _init_services(self):
        """Initialize TTS and STT services"""
        # Try to import TTS libraries
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_available = True
            logger.info("TTS service initialized (pyttsx3)")
        except ImportError:
            try:
                # Try gTTS as fallback
                from gtts import gTTS
                self.tts_engine = None
                self.gtts = gTTS
                self.tts_available = True
                logger.info("TTS service initialized (gTTS)")
            except ImportError:
                logger.warning("No TTS library available. Install pyttsx3 or gtts")
                self.tts_available = False
        
        # Try to import STT libraries
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.stt_available = True
            logger.info("STT service initialized")
        except ImportError:
            logger.warning("Speech recognition not available. Install SpeechRecognition")
            self.stt_available = False
    
    def speak(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            language: Language code (e.g., "en", "hi")
            
        Returns:
            Operation result
        """
        if not self.tts_available:
            return {
                "success": False,
                "error": "Text-to-speech not available"
            }
        
        try:
            if hasattr(self, 'tts_engine') and self.tts_engine:
                # Using pyttsx3
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            elif hasattr(self, 'gtts'):
                # Using gTTS (requires internet)
                import io
                from pygame import mixer
                import tempfile
                
                tts = self.gtts(text=text, lang=language, slow=False)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                    tts.save(tmp.name)
                    tmp_path = tmp.name
                
                # Play audio
                mixer.init()
                mixer.music.load(tmp_path)
                mixer.music.play()
                
                # Cleanup
                while mixer.music.get_busy():
                    import time
                    time.sleep(0.1)
                os.unlink(tmp_path)
            
            return {
                "success": True,
                "message": "Speech played successfully"
            }
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def listen(self, timeout: int = 5) -> Dict[str, Any]:
        """
        Listen for speech and convert to text
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Recognized text or error
        """
        if not self.stt_available:
            return {
                "success": False,
                "error": "Speech-to-text not available"
            }
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Listening...")
                
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Recognize using Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                return {
                    "success": True,
                    "text": text
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not recognize speech: {str(e)}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listening: {str(e)}"
            }
    
    def guide_user(self, steps: list[str]) -> Dict[str, Any]:
        """
        Guide user through steps with voice
        
        Args:
            steps: List of step descriptions
            
        Returns:
            Guidance result
        """
        results = []
        
        for i, step in enumerate(steps, 1):
            message = f"Step {i}: {step}"
            logger.info(message)
            
            result = self.speak(message)
            results.append({
                "step": i,
                "message": message,
                "success": result.get("success", False)
            })
        
        return {
            "success": True,
            "steps_completed": len(results),
            "results": results
        }


# Global instance
_voice_service: Optional[VoiceService] = None

def get_voice_service() -> VoiceService:
    """Get or create global voice service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service

