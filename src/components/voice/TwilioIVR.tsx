"use client";

import { useState, useEffect, useRef } from "react";
import { Phone, PhoneOff, Mic, MicOff, Volume2, VolumeX } from "lucide-react";
import { Device, Call } from "@twilio/voice-sdk";

interface TwilioIVRProps {
  onCallConnected?: () => void;
  onCallDisconnected?: () => void;
  onSpeechResult?: (transcript: string) => void;
  isEnabled?: boolean;
}

export default function TwilioIVR({
  onCallConnected,
  onCallDisconnected,
  onSpeechResult,
  isEnabled = true
}: TwilioIVRProps) {
  const [device, setDevice] = useState<Device | null>(null);
  const [currentCall, setCurrentCall] = useState<Call | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [callStatus, setCallStatus] = useState<string>("");
  const [isMuted, setIsMuted] = useState(false);
  const [transcript, setTranscript] = useState("");

  // Audio elements for ringtone and call audio
  const ringtoneRef = useRef<HTMLAudioElement | null>(null);
  const callAudioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (isEnabled) {
      initializeDevice();
    }

    return () => {
      if (device) {
        device.destroy();
      }
    };
  }, [isEnabled]);

  const initializeDevice = async () => {
    try {
      // Get access token from backend
      const response = await fetch("/api/ivr/token");
      if (!response.ok) {
        throw new Error("Failed to get Twilio token");
      }

      const { token } = await response.json();

      // Initialize Twilio Device
      const twilioDevice = new Device(token, {
        logLevel: 1, // Enable debug logging
        codecPreferences: [Call.Codec.Opus, Call.Codec.PCMU]
      });

      // Set up event listeners
      twilioDevice.on("ready", () => {
        console.log("Twilio device ready");
        setDevice(twilioDevice);
      });

      twilioDevice.on("error", (error) => {
        console.error("Twilio device error:", error);
        setCallStatus(`Error: ${error.message}`);
      });

      twilioDevice.on("connect", (call) => {
        console.log("Call connected:", call);
        setCurrentCall(call);
        setIsConnected(true);
        setIsConnecting(false);
        setCallStatus("Connected");

        // Stop ringtone if playing
        if (ringtoneRef.current) {
          ringtoneRef.current.pause();
        }

        onCallConnected?.();

        // Set up call event listeners
        setupCallListeners(call);
      });

      twilioDevice.on("disconnect", () => {
        console.log("Call disconnected");
        setCurrentCall(null);
        setIsConnected(false);
        setCallStatus("Disconnected");
        onCallDisconnected?.();
      });

      twilioDevice.on("incoming", (call) => {
        console.log("Incoming call:", call);
        setCallStatus("Incoming call...");
        // Auto-answer for IVR testing
        call.accept();
      });

      // Register the device
      await twilioDevice.register();

    } catch (error) {
      console.error("Failed to initialize Twilio device:", error);
      setCallStatus(`Initialization failed: ${error}`);
    }
  };

  const setupCallListeners = (call: Call) => {
    call.on("accept", () => {
      console.log("Call accepted");
    });

    call.on("cancel", () => {
      console.log("Call cancelled");
      setCallStatus("Call cancelled");
    });

    call.on("reject", () => {
      console.log("Call rejected");
      setCallStatus("Call rejected");
    });

    call.on("warning", (warningName, warningData) => {
      console.warn("Call warning:", warningName, warningData);
    });

    call.on("warning-cleared", (warningName) => {
      console.log("Warning cleared:", warningName);
    });

    // Listen for audio input (basic speech detection)
    call.on("volume", (inputVolume, outputVolume) => {
      // Could implement visual feedback for audio levels
    });
  };

  const makeCall = async () => {
    if (!device) {
      alert("Twilio device not initialized");
      return;
    }

    try {
      setIsConnecting(true);
      setCallStatus("Connecting...");

      // Play ringtone
      if (ringtoneRef.current) {
        ringtoneRef.current.currentTime = 0;
        ringtoneRef.current.play().catch(console.error);
      }

      // Make the call to IVR endpoint
      const call = await device.connect({
        params: {
          To: process.env.NEXT_PUBLIC_TWILIO_IVR_NUMBER || "+1234567890", // IVR number
        }
      });

      setCurrentCall(call);

    } catch (error) {
      console.error("Failed to make call:", error);
      setCallStatus(`Call failed: ${error}`);
      setIsConnecting(false);
    }
  };

  const hangupCall = () => {
    if (currentCall) {
      currentCall.disconnect();
    }
  };

  const toggleMute = () => {
    if (currentCall) {
      if (isMuted) {
        currentCall.unmute();
      } else {
        currentCall.mute();
      }
      setIsMuted(!isMuted);
    }
  };

  const sendDTMF = (digit: string) => {
    if (currentCall) {
      currentCall.sendDigits(digit);
    }
  };

  if (!isEnabled) {
    return (
      <div className="text-center text-gray-500 p-4">
        <p>IVR calling is not enabled</p>
        <p>Please configure Twilio credentials to enable calling</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
      {/* Connection Status */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-500' :
            isConnecting ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
          }`}></div>
          <span className="font-medium text-gray-700">
            {isConnected ? 'IVR কল সংযুক্ত / Call Connected' :
             isConnecting ? 'সংযোগ হচ্ছে / Connecting...' :
             'সংযোগ বিচ্ছিন্ন / Disconnected'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {isConnected && (
            <button
              onClick={toggleMute}
              className={`p-2 rounded-lg transition-colors ${
                isMuted
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          )}

          <button
            onClick={isConnected ? hangupCall : makeCall}
            disabled={isConnecting || !device}
            className={`p-2 rounded-lg transition-colors ${
              isConnected
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title={isConnected ? "Hang up" : "Make call"}
          >
            {isConnected ? <PhoneOff className="w-5 h-5" /> : <Phone className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Call Status */}
      {callStatus && (
        <div className="mb-4 p-3 bg-white rounded-lg border">
          <p className="text-sm text-gray-700 font-medium">{callStatus}</p>
        </div>
      )}

      {/* DTMF Keypad */}
      {isConnected && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">DTMF Keypad</h4>
          <div className="grid grid-cols-3 gap-2">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, '*', 0, '#'].map((digit) => (
              <button
                key={digit}
                onClick={() => sendDTMF(digit.toString())}
                className="p-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg text-lg font-semibold transition-colors"
              >
                {digit}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Transcript Display */}
      {transcript && (
        <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">আপনার কথা / You said:</p>
          <p className="text-gray-800 font-medium">{transcript}</p>
        </div>
      )}

      {/* Audio Elements (hidden) */}
      <audio
        ref={ringtoneRef}
        src="/audio/ringtone.mp3"
        loop
        style={{ display: 'none' }}
      />
      <audio
        ref={callAudioRef}
        style={{ display: 'none' }}
      />

      {/* Instructions */}
      {!isConnected && !isConnecting && (
        <div className="text-center text-gray-600 text-sm">
          <p>Click the phone button to test IVR functionality</p>
          <p>Make sure your browser allows microphone access</p>
        </div>
      )}

      {/* Status Messages */}
      <div className="flex items-center justify-between mt-4 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          {isConnecting && <span>📞 Calling...</span>}
          {isConnected && <span>🟢 Connected</span>}
          {isMuted && <span>🔇 Muted</span>}
        </div>
        <span>Twilio Voice IVR System</span>
      </div>
    </div>
  );
}

// Helper function to get Twilio token
export const getTwilioToken = async (): Promise<string> => {
  const response = await fetch("/api/ivr/token");
  if (!response.ok) {
    throw new Error("Failed to get Twilio token");
  }
  const { token } = await response.json();
  return token;
};
