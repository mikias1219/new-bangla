"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Volume2, VolumeX } from "lucide-react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

interface VoiceChatProps {
  onVoiceMessage: (message: string) => void;
  isLoading: boolean;
  onVoiceModeChange?: (isVoiceMode: boolean) => void;
}

export default function VoiceChat({ onVoiceMessage, isLoading, onVoiceModeChange }: VoiceChatProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);

  const {
    transcript,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  useEffect(() => {
    if (!browserSupportsSpeechRecognition) {
      console.warn("Browser doesn't support speech recognition.");
    }

    // Initialize speech synthesis
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      speechSynthesisRef.current = window.speechSynthesis;
    }
  }, [browserSupportsSpeechRecognition]);

  const startListening = () => {
    if (!browserSupportsSpeechRecognition) {
      alert("Your browser doesn't support speech recognition. Please use Chrome, Edge, or Safari.");
      return;
    }

    setIsListening(true);
    onVoiceModeChange?.(true);
    resetTranscript();
    SpeechRecognition.startListening({
      continuous: true,
      language: 'bn-BD'  // Bangla (Bengali) language for Bangladesh
    });
  };

  const stopListening = () => {
    setIsListening(false);
    onVoiceModeChange?.(false);
    SpeechRecognition.stopListening();

    if (transcript.trim()) {
      onVoiceMessage(transcript.trim());
    }
  };

  const speakText = (text: string) => {
    if (!speechSynthesisRef.current || !voiceEnabled) return;

    // Stop any ongoing speech
    speechSynthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    // Try to use Bangla voice if available
    const voices = speechSynthesis.getVoices();
    const banglaVoice = voices.find(voice =>
      voice.lang.startsWith('bn') ||
      voice.name.toLowerCase().includes('bangla') ||
      voice.name.toLowerCase().includes('bengali')
    );

    if (banglaVoice) {
      utterance.voice = banglaVoice;
      utterance.lang = 'bn-BD';
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    speechSynthesisRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
    if (isSpeaking) {
      stopSpeaking();
    }
  };

  // Auto-speak AI responses (this would be called from parent component)
  useEffect(() => {
    const handleAiResponse = (event: CustomEvent) => {
      if (voiceEnabled) {
        speakText(event.detail);
      }
    };

    window.addEventListener('aiResponse', handleAiResponse as EventListener);
    return () => window.removeEventListener('aiResponse', handleAiResponse as EventListener);
  }, [voiceEnabled, speakText]);

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="text-center text-gray-500 p-4">
        <p>Voice features are not supported in this browser.</p>
        <p>Please use Chrome, Edge, or Safari for voice functionality.</p>
      </div>
    );
  }

  return (
    <button
      onClick={isListening ? stopListening : startListening}
      disabled={isLoading}
      className={`p-3 rounded-full transition-all duration-200 ${
        isListening
          ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-lg'
          : 'bg-blue-500 hover:bg-blue-600 text-white shadow-md hover:shadow-lg'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      title={isListening ? "Stop recording and send message" : "Start voice recording"}
    >
      {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
    </button>
  );
}

// Helper function to trigger voice response from parent components
export const speakAiResponse = (text: string) => {
  const event = new CustomEvent('aiResponse', { detail: text });
  window.dispatchEvent(event);
};
