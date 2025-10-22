"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Phone, PhoneOff, Volume2, VolumeX } from "lucide-react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

interface VoiceIVROption {
  key: string;
  label: string;
  action: string;
}

interface VoiceIVRProps {
  onIVRCommand: (command: string, option?: VoiceIVROption) => void;
  isLoading: boolean;
  currentMenu?: string;
}

export default function VoiceIVR({ onIVRCommand, isLoading, currentMenu = "main" }: VoiceIVRProps) {
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [currentStep, setCurrentStep] = useState<"menu" | "input" | "confirmation">("menu");
  const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);

  const {
    transcript,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  // IVR Menu structure
  const ivrMenus = {
    main: {
      message: "স্বাগতম বাংলা চ্যাট প্রো-তে। অনুগ্রহ করে বলুন আপনি কী সাহায্য চান?\n\nWelcome to Bangla Chat Pro. Please say what help you need?",
      options: [
        { key: "order", label: "অর্ডার স্ট্যাটাস / Order Status", action: "check_order" },
        { key: "product", label: "প্রোডাক্ট তথ্য / Product Info", action: "product_info" },
        { key: "support", label: "সাপোর্ট / Support", action: "support" },
        { key: "human", label: "মানুষের সাথে কথা / Speak to Human", action: "human_agent" }
      ]
    },
    order: {
      message: "আপনার অর্ডার আইডি বলুন।\n\nPlease say your order ID.",
      options: []
    },
    product: {
      message: "কোন প্রোডাক্ট খুঁজছেন? নাম বলুন।\n\nWhat product are you looking for? Say the name.",
      options: []
    },
    support: {
      message: "আপনার সমস্যা বর্ণনা করুন।\n\nPlease describe your issue.",
      options: []
    }
  };

  useEffect(() => {
    if (!browserSupportsSpeechRecognition) {
      console.warn("Browser doesn't support speech recognition.");
    }

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      speechSynthesisRef.current = window.speechSynthesis;
    }

    // Auto-connect when component mounts
    handleConnect();
  }, [browserSupportsSpeechRecognition]);

  const handleConnect = () => {
    setIsConnected(true);
    setCurrentStep("menu");
    if (voiceEnabled) {
      speakMenu("main");
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setIsListening(false);
    SpeechRecognition.stopListening();
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
    }
  };

  const speakMenu = (menuKey: string) => {
    if (!speechSynthesisRef.current || !voiceEnabled) return;

    const menu = ivrMenus[menuKey as keyof typeof ivrMenus];
    if (!menu) return;

    speechSynthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(menu.message);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    // Try to use Bangla voice if available
    const voices = speechSynthesisRef.current.getVoices();
    const banglaVoice = voices.find(voice =>
      voice.lang.startsWith('bn') ||
      voice.name.toLowerCase().includes('bangla') ||
      voice.name.toLowerCase().includes('bengali')
    );

    if (banglaVoice) {
      utterance.voice = banglaVoice;
      utterance.lang = 'bn-BD';
    }

    utterance.onend = () => {
      if (menu.options.length > 0) {
        setCurrentStep("input");
        startListening();
      }
    };

    speechSynthesisRef.current.speak(utterance);
  };

  const startListening = () => {
    if (!browserSupportsSpeechRecognition) {
      alert("Your browser doesn't support speech recognition. Please use Chrome, Edge, or Safari.");
      return;
    }

    setIsListening(true);
    resetTranscript();
    SpeechRecognition.startListening({
      continuous: true,
      language: 'bn-BD'  // Bangla (Bengali) language for Bangladesh
    });
  };

  const stopListening = () => {
    setIsListening(false);
    SpeechRecognition.stopListening();

    if (transcript.trim()) {
      processVoiceCommand(transcript.trim());
    }
  };

  const processVoiceCommand = (command: string) => {
    const lowerCommand = command.toLowerCase();

    // Process based on current menu
    if (currentMenu === "main") {
      const menu = ivrMenus.main;

      for (const option of menu.options) {
        if (lowerCommand.includes(option.key) ||
            lowerCommand.includes(option.key.replace('_', ' '))) {
          onIVRCommand(option.action, option);
          return;
        }
      }

      // If no match found, repeat menu
      speakMenu("main");
    } else if (currentMenu === "order") {
      // Extract order ID from speech
      const orderId = extractOrderId(command);
      if (orderId) {
        onIVRCommand("order_status", { key: orderId, label: orderId, action: "check_order_status" });
      } else {
        speakText("দুঃখিত, অর্ডার আইডি বুঝতে পারলাম না। আবার বলুন।\n\nSorry, couldn't understand the order ID. Please say again.");
        setTimeout(() => speakMenu("order"), 2000);
      }
    } else if (currentMenu === "product") {
      onIVRCommand("product_search", { key: command, label: command, action: "search_product" });
    } else if (currentMenu === "support") {
      onIVRCommand("support_query", { key: command, label: command, action: "create_support_ticket" });
    }
  };

  const extractOrderId = (text: string): string | null => {
    // Extract order ID patterns (6+ digits, with or without #)
    const orderPatterns = [
      /#?(\d{6,})/,  // 6+ digits with optional #
      /অর্ডার\s*#?\s*(\d{6,})/i,  // "order" followed by digits
      /(\d{6,})/  // Just 6+ digits
    ];

    for (const pattern of orderPatterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    return null;
  };

  const speakText = (text: string) => {
    if (!speechSynthesisRef.current || !voiceEnabled) return;

    speechSynthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    const voices = speechSynthesisRef.current.getVoices();
    const banglaVoice = voices.find(voice =>
      voice.lang.startsWith('bn') ||
      voice.name.toLowerCase().includes('bangla') ||
      voice.name.toLowerCase().includes('bengali')
    );

    if (banglaVoice) {
      utterance.voice = banglaVoice;
      utterance.lang = 'bn-BD';
    }

    speechSynthesisRef.current.speak(utterance);
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
    if (isSpeaking) {
      if (speechSynthesisRef.current) {
        speechSynthesisRef.current.cancel();
      }
    }
  };

  // Listen for AI responses to speak them
  useEffect(() => {
    const handleAiResponse = (event: CustomEvent) => {
      if (voiceEnabled && isConnected) {
        speakText(event.detail);
      }
    };

    window.addEventListener('aiResponse', handleAiResponse as EventListener);
    return () => window.removeEventListener('aiResponse', handleAiResponse as EventListener);
  }, [voiceEnabled, isConnected]);

  // Check if currently speaking
  const [isSpeaking, setIsSpeaking] = useState(false);
  useEffect(() => {
    if (speechSynthesisRef.current) {
      const handleSpeakingStart = () => setIsSpeaking(true);
      const handleSpeakingEnd = () => setIsSpeaking(false);

      speechSynthesisRef.current.addEventListener('voiceschanged', () => {
        // Voices loaded
      });

      const utterances = speechSynthesisRef.current.pending ? speechSynthesisRef.current.speaking : false;
      setIsSpeaking(utterances);
    }
  }, []);

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="text-center text-gray-500 p-4">
        <p>ভয়েস IVR এই ব্রাউজারে সাপোর্ট করে না।</p>
        <p>Voice IVR is not supported in this browser.</p>
        <p>Please use Chrome, Edge, or Safari for voice functionality.</p>
      </div>
    );
  }

  const currentMenuData = ivrMenus[currentMenu as keyof typeof ivrMenus];

  return (
    <div className="border rounded-lg p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
      {/* Connection Status */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="font-medium text-gray-700">
            {isConnected ? 'ভয়েস IVR সংযুক্ত / Voice IVR Connected' : 'সংযোগ বিচ্ছিন্ন / Disconnected'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleVoice}
            className={`p-2 rounded-lg transition-colors ${
              voiceEnabled
                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
            title={voiceEnabled ? "Disable voice output" : "Enable voice output"}
          >
            {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>

          <button
            onClick={isConnected ? handleDisconnect : handleConnect}
            className={`p-2 rounded-lg transition-colors ${
              isConnected
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
            title={isConnected ? "Disconnect IVR" : "Connect IVR"}
          >
            {isConnected ? <PhoneOff className="w-5 h-5" /> : <Phone className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Current Menu Display */}
      {isConnected && currentMenuData && (
        <div className="mb-4">
          <div className="bg-white rounded-lg p-4 mb-3">
            <p className="text-gray-700 whitespace-pre-line">{currentMenuData.message}</p>
          </div>

          {currentMenuData.options.length > 0 && (
            <div className="grid grid-cols-1 gap-2">
              {currentMenuData.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => onIVRCommand(option.action, option)}
                  className="bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-3 text-left transition-colors"
                  disabled={isLoading}
                >
                  <span className="font-medium text-blue-600">{option.key.toUpperCase()}</span>
                  <span className="ml-3 text-gray-700">{option.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Voice Input Section */}
      {isConnected && (
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between mb-3">
            <span className="font-medium text-gray-700">
              {currentStep === "menu" && "মেনু শুনছি / Listening to menu"}
              {currentStep === "input" && "আপনার কমান্ড বলুন / Say your command"}
              {currentStep === "confirmation" && "নিশ্চিত করুন / Confirm"}
            </span>

            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isLoading || currentStep === "menu"}
              className={`p-3 rounded-full transition-colors ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={isListening ? "Stop listening" : "Start voice input"}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          </div>

          {/* Transcript Display */}
          {transcript && (
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <p className="text-sm text-gray-600 mb-1">আপনি বলেছেন / You said:</p>
              <p className="text-gray-800 font-medium">{transcript}</p>
            </div>
          )}

          {/* Status Indicators */}
          <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
            <div className="flex items-center gap-4">
              {isListening && <span>🎤 শুনছি / Listening...</span>}
              {isSpeaking && <span>🔊 বলছি / Speaking...</span>}
              {isLoading && <span>⏳ প্রসেস হচ্ছে / Processing...</span>}
            </div>
            <span>ভয়েস IVR সিস্টেম / Voice IVR System</span>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to trigger voice response from parent components
export const speakIVRMessage = (text: string) => {
  const event = new CustomEvent('aiResponse', { detail: text });
  window.dispatchEvent(event);
};
