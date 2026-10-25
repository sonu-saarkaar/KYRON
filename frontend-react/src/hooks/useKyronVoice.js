import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useKyronVoice - Robust Hands-Free Voice Engine with Echo Shield & High Sensitivity
 * - Acoustic Echo Shield: Completely mutes & drops mic feedback while Kyron is speaking (+ 500ms acoustic decay cooldown)
 * - Echo Rejection Filter: Discards transcripts that match Kyron's recently spoken words
 * - Whisper / Soft Speech Sensitivity: Requests browser/OS Auto Gain Control (AGC) & zero-delay burst restart
 * - Anti-Loop Wake Guard: Prevents repetitive greeting triggers; enforces strict phonetic wake matching
 * - Auto-submission on silence (1.25s)
 * - Windows TTS Voice/Lang synchronization (prevents SAPI silent drop)
 */

const WAKE_REGEX = /\b(hey|hai|hello|hi|ok|okay|suno|bhai|oye|aye|ae|arre)?\s*(kyron|kiron|kiran|karan|kayron|kairon|chiron|kyon|kyo|kyro|kyrun|kyran)\b/i;

function levenshtein(a, b) {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;
  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  return matrix[b.length][a.length];
}

function isFuzzyWakeWord(text) {
  if (!text) return false;
  if (WAKE_REGEX.test(text)) return true;

  const words = text.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/);
  for (const word of words) {
    if (word === 'kyon' || word === 'kyo' || word === 'kyro') {
      return true;
    }
    // Only check words starting with k, c, q to avoid false matches on random English/Hindi words
    if (/^[kcq]/.test(word) && word.length >= 3 && word.length <= 7) {
      if (
        levenshtein(word, 'kyron') <= 1 ||
        levenshtein(word, 'kiron') <= 1 ||
        levenshtein(word, 'kiran') <= 1
      ) {
        return true;
      }
    }
  }
  return false;
}

// Clean markdown for fluid speech synthesis
function cleanTextForSpeech(text) {
  if (!text) return '';
  
  // Pronunciation Fix: Replace KYRON with Kaeyron for TTS engine
  let cleaned = text.replace(/\bKYRON\b/gi, 'Kaeyron');
  
  return cleaned
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/`{1,3}(.*?)`{1,3}/gs, '')
    .replace(/#+\s/g, '')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/[-*•]\s+/g, '')
    .replace(/>\s+/g, '')
    .replace(/\n+/g, '. ')
    .trim();
}

// Check if candidate speech is an echo of Kyron's own voice
function isKyronEcho(candidateText, recentPhrases) {
  if (!candidateText || candidateText.trim().length === 0) return false;
  const candNorm = candidateText.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!candNorm || candNorm.length < 2) return false;

  const candWords = candNorm.split(' ').filter((w) => w.length > 2);
  const now = Date.now();

  for (const item of recentPhrases) {
    // Only compare against phrases spoken within the last 12 seconds
    if (now - item.time > 12000) continue;
    const spokenNorm = item.text.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
    if (!spokenNorm) continue;

    // Substring match
    if (spokenNorm.includes(candNorm) || (candNorm.length > 6 && candNorm.includes(spokenNorm))) {
      return true;
    }

    // Word overlap match (>35% match of significant words)
    if (candWords.length > 0) {
      const spokenWordSet = new Set(spokenNorm.split(' ').filter((w) => w.length > 2));
      let matches = 0;
      for (const w of candWords) {
        if (spokenWordSet.has(w)) matches++;
      }
      if (matches / candWords.length >= 0.35) {
        return true;
      }
    }
  }
  return false;
}

/**
 * Phonetic STT error cleaner for Indian English / Hindi speech.
 * Fixes mistranscriptions like "panka bana sakte ho" -> "pan card bana sakte ho".
 */
export function normalizeSpeechPhonetics(text) {
  if (!text) return '';
  let cleaned = text;

  // 1. PAN Card phonetic mishearings: "panka bana", "pan ka bana", "pan cake", "pen card", "pancard"
  cleaned = cleaned.replace(/\b(panka|pan\s*ka|pan\s*cake|pen\s*card|pencard|pankard)\b(?=.*?\b(bana|banao|banwa|apply|chahiye|sakte|sakta|karo|banaoge|banwana))/gi, 'pan card');
  cleaned = cleaned.replace(/\b(mere liye\s+)?(panka|pan\s*ka|pan\s*cake)\b(?=\s*(bana|chahiye|apply|banao))/gi, 'pan card');
  cleaned = cleaned.replace(/\b(panka|pan\s*ka)\b/gi, 'pan card');

  // 2. Passport phonetic mishearings
  cleaned = cleaned.replace(/\b(pasport|pass\s*port|passpot|pasfort)\b/gi, 'passport');

  // 3. Ticket phonetic mishearings
  cleaned = cleaned.replace(/\b(tikkat|tikat|tikit)\b/gi, 'ticket');

  // 4. WhatsApp phonetic mishearings
  cleaned = cleaned.replace(/\b(watsapp|watsap|whatsap)\b/gi, 'whatsapp');

  // 5. Mouth / Voice Cursor Control phonetic mishearings
  cleaned = cleaned.replace(/\b(curose|curser|kursor|kursar|courser|coursor|cousor)\b/gi, 'cursor');
  cleaned = cleaned.replace(/\b(uper|uppar)\b/gi, 'upar');
  cleaned = cleaned.replace(/\b(neeche|neche)\b/gi, 'niche');
  cleaned = cleaned.replace(/\b(duble|doble)\b/gi, 'double');
  cleaned = cleaned.replace(/\b(bayein|baayein|baye|baaye)\b/gi, 'left');
  cleaned = cleaned.replace(/\b(daayein|dayein|daye|daaye)\b/gi, 'right');
  cleaned = cleaned.replace(/\b(clik|clck)\b/gi, 'click');
  cleaned = cleaned.replace(/\b(kro|kroo)\b/gi, 'karo');

  return cleaned;
}

export function useKyronVoice({
  onDirectiveSubmit,
  onTranscriptChange,
  onStatusChange,
  onWake,
  language = 'en-IN'
}) {
  const [isWakeWordActive, setIsWakeWordActive] = useState(false);
  const [isListening, setIsListening] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [liveTranscript, setLiveTranscript] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState(language);

  // Core references
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const restartTimerRef = useRef(null);
  const ttsSafetyTimerRef = useRef(null);
  const ttsCooldownTimerRef = useRef(null);
  const audioContextRef = useRef(null);
  const audioStreamRef = useRef(null);
  const analyserRef = useRef(null);
  const animFrameRef = useRef(null);

  const isIntentionalStopRef = useRef(false);
  const isRecognitionRunningRef = useRef(false);
  const isMutedDuringTTSRef = useRef(false);
  const latestTranscriptRef = useRef('');
  const hasUserInteractedRef = useRef(false);
  const recentSpokenPhrasesRef = useRef([]);
  const lastSubmittedPhraseRef = useRef({ text: '', time: 0 });

  // Synchronized callback refs
  const onDirectiveSubmitRef = useRef(onDirectiveSubmit);
  const onTranscriptChangeRef = useRef(onTranscriptChange);
  const onStatusChangeRef = useRef(onStatusChange);
  const onWakeRef = useRef(onWake);
  const isWakeWordActiveRef = useRef(false);
  const isListeningRef = useRef(true);
  const isSpeakingRef = useRef(false);
  const isMutedRef = useRef(false);

  useEffect(() => {
    onDirectiveSubmitRef.current = onDirectiveSubmit;
    onTranscriptChangeRef.current = onTranscriptChange;
    onStatusChangeRef.current = onStatusChange;
    onWakeRef.current = onWake;
    isWakeWordActiveRef.current = isWakeWordActive;
    isListeningRef.current = isListening;
    isSpeakingRef.current = isSpeaking;
    isMutedRef.current = isMuted;
  });

  // High-Tech Audio Chime (AudioContext unlocked on demand)
  const playChime = useCallback((type = 'activate') => {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
        audioContextRef.current = new AudioCtx();
      }
      const ctx = audioContextRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      if (type === 'activate') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(659.25, now);
        osc.frequency.exponentialRampToValueAtTime(1046.5, now + 0.12);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      } else if (type === 'submit') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(440, now + 0.14);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
        osc.start(now);
        osc.stop(now + 0.2);
      }
    } catch (_) {}
  }, []);

  // Safe Start helper for SpeechRecognition
  const safeStartRecognition = useCallback(() => {
    if (isIntentionalStopRef.current || !isListeningRef.current) return;
    if (isSpeakingRef.current || isMutedDuringTTSRef.current) return;
    if (isRecognitionRunningRef.current) return;

    try {
      if (recognitionRef.current) {
        recognitionRef.current.start();
        isRecognitionRunningRef.current = true;
      }
    } catch (_) {
      // Ignore already-started state
    }
  }, []);

  // Safe Stop helper
  const safeStopRecognition = useCallback(() => {
    isIntentionalStopRef.current = true;
    isRecognitionRunningRef.current = false;

    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current);
      restartTimerRef.current = null;
    }

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
    }

    setIsListening(false);
    isListeningRef.current = false;
    setIsWakeWordActive(false);
    isWakeWordActiveRef.current = false;
    setAudioLevel(0);
  }, []);

  // Text-to-Speech (TTS) with Echo Shield muting & acoustic decay protection
  const speak = useCallback((text, onEnd) => {
    if (isMutedRef.current || !('speechSynthesis' in window)) {
      if (onEnd) onEnd();
      return;
    }

    const clean = cleanTextForSpeech(text);
    if (!clean) {
      if (onEnd) onEnd();
      return;
    }

    try {
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume();
    } catch (_) {}

    // 1. Register phrase in Echo Shield buffer
    recentSpokenPhrasesRef.current.push({
      text: clean,
      time: Date.now()
    });
    if (recentSpokenPhrasesRef.current.length > 10) {
      recentSpokenPhrasesRef.current.shift();
    }

    // 2. Clear any pending user directive auto-submit timers
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    latestTranscriptRef.current = '';
    setTranscript('');
    setLiveTranscript('');
    if (onTranscriptChangeRef.current) {
      onTranscriptChangeRef.current('');
    }

    // 3. Immediately mute & abort speech recognition so mic never captures speaker sound
    setIsSpeaking(true);
    isSpeakingRef.current = true;
    isMutedDuringTTSRef.current = true;
    if (recognitionRef.current && isRecognitionRunningRef.current) {
      try {
        recognitionRef.current.abort();
        isRecognitionRunningRef.current = false;
      } catch (_) {}
    }

    const utterance = new SpeechSynthesisUtterance(clean);
    window.__kyronActiveUtterance = utterance;

    utterance.rate = 1.0;
    utterance.pitch = 1.05; // Slightly elevated pleasant female pitch

    const selectVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      if (!voices || voices.length === 0) {
        utterance.lang = 'en-US';
        return;
      }

      // Explicitly ban all male and legacy robotic voices (Lekha, etc.)
      const bannedVoices = [
        'male', 'aman', 'rishi', 'alex', 'fred', 'daniel', 'albert', 'george',
        'david', 'mark', 'ravi', 'reed', 'rocko', 'eddy', 'ralph', 'junior',
        'jester', 'grandpa', 'bad news', 'bahh', 'bells', 'boing', 'bubbles',
        'cellos', 'wobble', 'zarvox', 'trinoids', 'organ', 'lekha'
      ];

      const isBanned = (v) => {
        const name = (v.name || '').toLowerCase();
        return bannedVoices.some((m) => name.includes(m));
      };

      const naturalFemaleOnly = voices.filter((v) => !isBanned(v));
      const candidates = naturalFemaleOnly.length > 0 ? naturalFemaleOnly : voices;

      // Priority: Tara (Apple Siri Natural Female) is the absolute #1 real human voice
      const preferred =
        candidates.find((v) => v.name.toLowerCase().includes('tara')) ||
        candidates.find((v) => v.name.toLowerCase().includes('samantha')) ||
        candidates.find((v) =>
          v.name.toLowerCase().includes('victoria') ||
          v.name.toLowerCase().includes('karen') ||
          v.name.toLowerCase().includes('tessa') ||
          v.name.toLowerCase().includes('veena') ||
          v.name.toLowerCase().includes('google us english') ||
          v.name.toLowerCase().includes('google uk english female')
        ) ||
        candidates.find((v) => v.lang === 'en-IN' && !isBanned(v)) ||
        candidates.find((v) => v.lang.startsWith('en') && !isBanned(v)) ||
        candidates[0];

      if (preferred) {
        utterance.voice = preferred;
        utterance.lang = preferred.lang;
      } else {
        utterance.lang = 'en-US';
      }
    };

    selectVoice();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = selectVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      isSpeakingRef.current = true;
      isMutedDuringTTSRef.current = true;
      if (onStatusChangeRef.current) {
        onStatusChangeRef.current('speaking', 'KYRON VOCALIZING RESPONSE');
      }
      if (recognitionRef.current && isRecognitionRunningRef.current) {
        try {
          recognitionRef.current.abort();
          isRecognitionRunningRef.current = false;
        } catch (_) {}
      }
    };

    const handleSpeechFinish = () => {
      setIsSpeaking(false);
      isSpeakingRef.current = false;
      window.__kyronActiveUtterance = null;
      if (onStatusChangeRef.current) {
        onStatusChangeRef.current('idle', 'KYRON CORE ONLINE // AWAITING COMMAND');
      }
      if (onEnd) onEnd();

      // 4. Acoustic decay cooldown: Keep mic closed for 500ms so speaker reverberation dies down
      if (ttsCooldownTimerRef.current) clearTimeout(ttsCooldownTimerRef.current);
      ttsCooldownTimerRef.current = setTimeout(() => {
        isMutedDuringTTSRef.current = false;
        if (!isIntentionalStopRef.current && isListeningRef.current) {
          safeStartRecognition();
        }
      }, 500);
    };

    utterance.onend = handleSpeechFinish;
    utterance.onerror = (e) => {
      console.warn('[TTS] Synthesis event:', e);
      handleSpeechFinish();
    };

    // Safety watchdog to prevent permanent speaking lock
    if (ttsSafetyTimerRef.current) clearTimeout(ttsSafetyTimerRef.current);
    const estDuration = Math.max(3000, (clean.length / 8) * 1000);
    ttsSafetyTimerRef.current = setTimeout(() => {
      if (isSpeakingRef.current) {
        handleSpeechFinish();
      }
    }, estDuration);

    setTimeout(() => {
      try {
        window.speechSynthesis.resume();
        window.speechSynthesis.speak(utterance);
      } catch (err) {
        console.error('Speech synthesis error:', err);
        handleSpeechFinish();
      }
    }, 40);
  }, [safeStartRecognition]);

  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (_) {}
    }
    setIsSpeaking(false);
    isSpeakingRef.current = false;
    window.__kyronActiveUtterance = null;
    if (onStatusChangeRef.current) {
      onStatusChangeRef.current('idle', 'KYRON CORE ONLINE // AWAITING COMMAND');
    }
    if (ttsCooldownTimerRef.current) clearTimeout(ttsCooldownTimerRef.current);
    ttsCooldownTimerRef.current = setTimeout(() => {
      isMutedDuringTTSRef.current = false;
      if (!isIntentionalStopRef.current && isListeningRef.current) {
        safeStartRecognition();
      }
    }, 250);
  }, [safeStartRecognition]);

  // Programmatic Wakeup Trigger
  const triggerWakeup = useCallback(() => {
    hasUserInteractedRef.current = true;
    playChime('activate');
    setIsWakeWordActive(true);
    isWakeWordActiveRef.current = true;
    if (onWakeRef.current) {
      onWakeRef.current(speak);
    }
  }, [playChime, speak]);

  // External notification helper: Mute mic and drop self-echo when assistant speaks (Dograh or Web Speech)
  const notifyAssistantSpeaking = useCallback((phrase, durationMs) => {
    if (phrase) {
      const clean = cleanTextForSpeech(phrase);
      recentSpokenPhrasesRef.current.push({
        text: clean,
        time: Date.now()
      });
      if (recentSpokenPhrasesRef.current.length > 20) {
        recentSpokenPhrasesRef.current.shift();
      }
    }

    setIsSpeaking(true);
    isSpeakingRef.current = true;
    isMutedDuringTTSRef.current = true;

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    latestTranscriptRef.current = '';
    setTranscript('');
    setLiveTranscript('');
    if (onTranscriptChangeRef.current) {
      onTranscriptChangeRef.current('');
    }

    if (recognitionRef.current && isRecognitionRunningRef.current) {
      try {
        recognitionRef.current.abort();
        isRecognitionRunningRef.current = false;
      } catch (_) {}
    }

    const words = phrase ? phrase.split(/\s+/).length : 6;
    const estDuration = durationMs || Math.max(2500, (words / 2.0) * 1000);

    if (ttsCooldownTimerRef.current) clearTimeout(ttsCooldownTimerRef.current);
    ttsCooldownTimerRef.current = setTimeout(() => {
      setIsSpeaking(false);
      isSpeakingRef.current = false;
      isMutedDuringTTSRef.current = false;
      latestTranscriptRef.current = '';
      if (!isIntentionalStopRef.current && isListeningRef.current) {
        safeStartRecognition();
      }
    }, estDuration + 1000);
  }, [safeStartRecognition]);

  // Fast & Snappy Silence Auto-Submit Timer
  const resetSilenceTimer = useCallback((customDelay) => {
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

    const delay = customDelay || 800;

    silenceTimerRef.current = setTimeout(() => {
      const pendingText = latestTranscriptRef.current.trim();
      // Drop if it matches Kyron's recently spoken words (Echo Shield)
      if (isKyronEcho(pendingText, recentSpokenPhrasesRef.current)) {
        console.log('[KYRON ECHO SHIELD] Blocked pending submission matching Kyron speech:', pendingText);
        latestTranscriptRef.current = '';
        setTranscript('');
        setLiveTranscript('');
        return;
      }

      const now = Date.now();
      // Drop if exact same phrase was already submitted within last 3.0 seconds
      if (
        now - lastSubmittedPhraseRef.current.time < 3000 &&
        lastSubmittedPhraseRef.current.text.toLowerCase() === pendingText.toLowerCase()
      ) {
        console.log('[KYRON] Dropped duplicate submission:', pendingText);
        latestTranscriptRef.current = '';
        setTranscript('');
        setLiveTranscript('');
        return;
      }

      if (pendingText.length >= 3) {
        lastSubmittedPhraseRef.current = { text: pendingText, time: now };
        setIsSpeaking(false);
        isSpeakingRef.current = false;

        playChime('submit');
        if (onDirectiveSubmitRef.current) {
          onDirectiveSubmitRef.current(pendingText);
        }
        latestTranscriptRef.current = '';
        setTranscript('');
        setLiveTranscript('');
        if (onTranscriptChangeRef.current) {
          onTranscriptChangeRef.current('');
        }
        setIsWakeWordActive(false);
        isWakeWordActiveRef.current = false;
        setAudioLevel(0);

        // Abort to reset recognition buffer for the next sentence
        if (recognitionRef.current) {
          try {
            recognitionRef.current.abort();
          } catch (_) {}
        }
      }
    }, delay);
  }, [playChime]);

  // Initialize Hardware Auto-Gain Control (AGC) & Live Equalizer
  const initAudioProcessing = useCallback(async () => {
    try {
      if (audioStreamRef.current) return;
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          autoGainControl: true, // Automatically amplifies whispers and soft voices
          echoCancellation: true, // Hardware OS-level acoustic echo cancellation
          noiseSuppression: true // Lowers fan / background noise floor
        }
      });
      audioStreamRef.current = stream;

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
          audioContextRef.current = new AudioCtx();
        }
        if (audioContextRef.current.state === 'suspended') {
          await audioContextRef.current.resume();
        }
        const source = audioContextRef.current.createMediaStreamSource(stream);
        const analyser = audioContextRef.current.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;

        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        const pollAudioLevel = () => {
          if (!analyserRef.current || !isListeningRef.current) {
            animFrameRef.current = requestAnimationFrame(pollAudioLevel);
            return;
          }
          if (isSpeakingRef.current || isMutedDuringTTSRef.current) {
            setAudioLevel(0);
            animFrameRef.current = requestAnimationFrame(pollAudioLevel);
            return;
          }

          analyserRef.current.getByteFrequencyData(dataArray);
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
          }
          const avg = sum / dataArray.length;
          // Scale non-linearly to visibly boost quiet speech and whispers
          const boostedLevel = Math.min(100, Math.round(Math.pow(avg / 35, 0.7) * 85));
          setAudioLevel(boostedLevel);

          animFrameRef.current = requestAnimationFrame(pollAudioLevel);
        };
        pollAudioLevel();
      }
    } catch (err) {
      console.warn('[KYRON] Audio hardware processing note:', err?.message);
    }
  }, []);

  // Master Activation Function (turns mic ON)
  const activateVoice = useCallback(() => {
    hasUserInteractedRef.current = true;
    isIntentionalStopRef.current = false;
    setIsListening(true);
    isListeningRef.current = true;
    setIsSpeaking(false);
    isSpeakingRef.current = false;
    isMutedDuringTTSRef.current = false;

    // Resume AudioContext and TTS on user gesture
    try {
      if (audioContextRef.current && audioContextRef.current.state === 'suspended') {
        audioContextRef.current.resume();
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.resume();
      }
    } catch (_) {}

    initAudioProcessing();
    safeStartRecognition();
  }, [initAudioProcessing, safeStartRecognition]);

  // Language switcher helper
  const setVoiceLanguage = useCallback((lang) => {
    setSelectedLanguage(lang);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.lang = lang;
      } catch (_) {}
    }
  }, []);

  // Speech Recognition Initialization
  useEffect(() => {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      console.warn('[KYRON] SpeechRecognition is not supported in this browser.');
      return;
    }

    const recognition = new SpeechRec();
    recognition.continuous = true; // Continuous listening so user can complete whole sentences without cut-off
    recognition.interimResults = true;
    recognition.lang = selectedLanguage;
    recognition.maxAlternatives = 5; // More alternatives help detect whispered/soft speech

    recognition.onstart = () => {
      isRecognitionRunningRef.current = true;
      setIsListening(true);
      isListeningRef.current = true;
    };

    recognition.onresult = (event) => {
      // 1. If Kyron is currently speaking or in post-TTS acoustic decay, DROP IMMEDIATELY!
      if (isSpeakingRef.current || isMutedDuringTTSRef.current) {
        return;
      }

      let fullTranscript = '';
      let isLastFinal = false;

      // Accumulate sentence and inspect alternatives for known Indian Hindi/English intent terms
      for (let i = 0; i < event.results.length; i++) {
        const item = event.results[i];
        let chosen = item[0]?.transcript || '';

        // Check if secondary alternatives contain high-confidence intended phrases
        for (let a = 0; a < item.length; a++) {
          const altText = (item[a]?.transcript || '').toLowerCase();
          if (
            altText.includes('pan card') ||
            altText.includes('pancard') ||
            altText.includes('passport') ||
            altText.includes('ticket') ||
            altText.includes('whatsapp')
          ) {
            chosen = item[a].transcript;
            break;
          }
        }

        fullTranscript += chosen + ' ';
        if (i === event.results.length - 1 && item.isFinal) {
          isLastFinal = true;
        }
      }

      const rawSpeech = fullTranscript.replace(/\s+/g, ' ').trim();
      const currentSpeech = normalizeSpeechPhonetics(rawSpeech);
      if (!currentSpeech) return;

      // 2. Echo Shield: If transcript matches Kyron's recently spoken output, DROP IT!
      if (isKyronEcho(currentSpeech, recentSpokenPhrasesRef.current)) {
        console.log('[KYRON ECHO SHIELD] Discarded self-echo:', currentSpeech);
        return;
      }

      // 3. Wake-word detection (e.g. 'Hey Kyron', 'Hey Kyon', 'Suno Kyron')
      if (!isWakeWordActiveRef.current && isFuzzyWakeWord(currentSpeech)) {
        // Strip wake-words to check if the user spoke a command in the same breath
        const stripped = currentSpeech
          .replace(WAKE_REGEX, '')
          .replace(/^[,\.\-!\?\s]+|[,\.\-!\?\s]+$/g, '')
          .trim();

        const alphaNumericChars = stripped.replace(/[^a-zA-Z0-9]/g, '');

        if (alphaNumericChars.length >= 3 && !isFuzzyWakeWord(stripped)) {
          // User said wake-word AND instruction together (e.g. "Hey Kyron open Chrome" or "Hey Kyon good morning")
          // DO NOT call triggerWakeup() which would vocalize a greeting and overlap with the command!
          setIsWakeWordActive(true);
          isWakeWordActiveRef.current = true;
          hasUserInteractedRef.current = true;
          playChime('activate');

          latestTranscriptRef.current = stripped;
          setTranscript(stripped);
          setLiveTranscript(stripped);
          if (onTranscriptChangeRef.current) {
            onTranscriptChangeRef.current(stripped);
          }
          resetSilenceTimer(750);
        } else {
          // Pure wake trigger (e.g. "Hey Kyon", "Hey Kyron"): DO NOT send to chat!
          // Clear any pending transcript & silence timer so wake word is never submitted.
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
          latestTranscriptRef.current = '';
          setTranscript('');
          setLiveTranscript('');
          if (onTranscriptChangeRef.current) {
            onTranscriptChangeRef.current('');
          }
          // Only trigger wake vocalization when it's purely a wake call without a directive
          triggerWakeup();
        }
        return;
      }

      // 4. Stream live speech directly to input field
      latestTranscriptRef.current = currentSpeech;
      setTranscript(currentSpeech);
      setLiveTranscript(currentSpeech);

      if (onTranscriptChangeRef.current) {
        onTranscriptChangeRef.current(currentSpeech);
      }

      // Snappy responsiveness: 750ms when browser marks end of phrase; 1100ms for natural mid-sentence pauses
      resetSilenceTimer(isLastFinal ? 750 : 1100);
    };

    recognition.onerror = (e) => {
      isRecognitionRunningRef.current = false;

      if (isIntentionalStopRef.current || e.error === 'aborted') {
        return;
      }

      if (e.error === 'not-allowed') {
        console.warn('[KYRON] Microphone permission pending user gesture.');
        return;
      }
    };

    recognition.onend = () => {
      isRecognitionRunningRef.current = false;

      // In burst mode, restart within 15ms to eliminate dead zones (critical for quiet speech!)
      if (
        !isIntentionalStopRef.current &&
        isListeningRef.current &&
        !isSpeakingRef.current &&
        !isMutedDuringTTSRef.current
      ) {
        if (restartTimerRef.current) clearTimeout(restartTimerRef.current);
        restartTimerRef.current = setTimeout(() => {
          if (
            !isIntentionalStopRef.current &&
            isListeningRef.current &&
            !isSpeakingRef.current &&
            !isMutedDuringTTSRef.current
          ) {
            safeStartRecognition();
          }
        }, 15);
      }
    };

    recognitionRef.current = recognition;

    // Unlock on first user gesture
    const unlockOnGesture = () => {
      if (!hasUserInteractedRef.current) {
        hasUserInteractedRef.current = true;
        activateVoice();
      }
    };

    window.addEventListener('click', unlockOnGesture, { once: true });
    window.addEventListener('keydown', unlockOnGesture, { once: true });

    // Attempt start
    safeStartRecognition();

    return () => {
      window.removeEventListener('click', unlockOnGesture);
      window.removeEventListener('keydown', unlockOnGesture);
      isIntentionalStopRef.current = true;
      isRecognitionRunningRef.current = false;

      if (restartTimerRef.current) clearTimeout(restartTimerRef.current);
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (ttsSafetyTimerRef.current) clearTimeout(ttsSafetyTimerRef.current);
      if (ttsCooldownTimerRef.current) clearTimeout(ttsCooldownTimerRef.current);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);

      if (audioStreamRef.current) {
        try {
          audioStreamRef.current.getTracks().forEach((t) => t.stop());
        } catch (_) {}
      }

      try {
        recognition.stop();
      } catch (_) {}
    };
  }, [activateVoice, resetSilenceTimer, safeStartRecognition, selectedLanguage, triggerWakeup]);

  const toggleListening = useCallback(() => {
    if (isListeningRef.current) {
      safeStopRecognition();
    } else {
      activateVoice();
      playChime('activate');
    }
  }, [activateVoice, playChime, safeStopRecognition]);

  const toggleMute = useCallback(() => {
    if (!isMuted) {
      stopSpeaking();
    }
    setIsMuted(!isMuted);
  }, [isMuted, stopSpeaking]);

  return {
    isListening,
    isSpeaking,
    isMuted,
    isWakeWordActive,
    transcript,
    liveTranscript,
    audioLevel,
    selectedLanguage,
    setVoiceLanguage,
    speak,
    stopSpeaking,
    startListening: activateVoice,
    stopListening: safeStopRecognition,
    toggleListening,
    toggleMute,
    activateVoice,
    triggerWakeup,
    playChime,
    notifyAssistantSpeaking
  };
}
