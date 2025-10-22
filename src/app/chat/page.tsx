"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useRouter } from "next/navigation";
import { Send, Bot, User, ArrowLeft, MessageSquare, Mic, MicOff, Volume2, VolumeX, Settings } from "lucide-react";
import { useSearchParams } from "next/navigation";
import VoiceChat, { speakAiResponse } from "@/components/voice/VoiceChat";

interface Message {
  id: number;
  content: string;
  sender_type: string;
  sender_name: string | null;
  created_at: string;
  confidence_score: number | null;
}

interface AIAgent {
  id: number;
  name: string;
  description: string;
  training_status: string;
}

function ChatPageContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [agent, setAgent] = useState<AIAgent | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [voiceResponseEnabled, setVoiceResponseEnabled] = useState(false);
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const [recordedVoiceText, setRecordedVoiceText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const router = useRouter();
  const agentId = searchParams.get("agent");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadAgent = useCallback(async (id: number) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/organizations/ai-agents`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const agents = await response.json();
        const foundAgent = agents.find((a: AIAgent) => a.id === id);
        if (foundAgent) {
          setAgent(foundAgent);
        } else {
          alert("AI Agent not found");
          router.push("/dashboard");
        }
      }
    } catch (error) {
      console.error("Failed to load agent:", error);
      router.push("/dashboard");
    }
  }, [router]);

  useEffect(() => {
    if (agentId) {
      loadAgent(parseInt(agentId));
    }
  }, [agentId, loadAgent]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || loading) return;

    const messageToSend = newMessage.trim();
    setNewMessage(""); // Clear immediately for better UX
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/chat/agents/${agentId}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          message: messageToSend,
          conversation_id: conversationId
        })
      });

      if (response.ok) {
        const data = await response.json();

        // Add user message
        const userMessage: Message = {
          id: Date.now(),
          content: messageToSend,
          sender_type: "user",
          sender_name: "You",
          created_at: new Date().toISOString(),
          confidence_score: null
        };

        // Add AI response
        const aiMessage: Message = {
          id: Date.now() + 1,
          content: data.response,
          sender_type: "ai_agent",
          sender_name: agent?.name || "AI Assistant",
          created_at: new Date().toISOString(),
          confidence_score: data.confidence_score
        };

        setMessages(prev => [...prev, userMessage, aiMessage]);
        setConversationId(data.conversation_id);
        setNewMessage("");
        setRecordedVoiceText(""); // Clear recorded voice text too

        // Speak the AI response only if user has enabled voice responses
        if (data.response && voiceResponseEnabled) {
          speakAiResponse(data.response);
        }
      } else {
        const error = await response.json();
        alert(`Failed to send message: ${error.detail}`);
        // Restore the message if sending failed
        setNewMessage(messageToSend);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message. Please try again.");
      // Restore the message if sending failed
      setNewMessage(messageToSend);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceMessage = (voiceMessage: string) => {
    if (isRecordingVoice) {
      // Voice recording mode - set as recorded text, don't send automatically
      setRecordedVoiceText(voiceMessage);
      setIsRecordingVoice(false);
      setIsVoiceMode(false);
    } else {
      // Voice input mode - send immediately
      setNewMessage(voiceMessage);
      setIsVoiceMode(false); // Exit voice mode after sending
      // Send the message immediately
      const event = { preventDefault: () => {} } as React.FormEvent;
      sendMessage(event);
    }
  };

  const startVoiceRecording = () => {
    setIsRecordingVoice(true);
    setIsVoiceMode(true);
  };

  const sendRecordedVoice = () => {
    if (recordedVoiceText.trim()) {
      setNewMessage(recordedVoiceText);
      const event = { preventDefault: () => {} } as React.FormEvent;
      sendMessage(event);
    }
  };

  if (!agent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading AI agent...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between h-auto sm:h-16 gap-4 py-4 sm:py-0">
            <button
              onClick={() => router.push("/dashboard")}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 self-start"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">Back to Dashboard</span>
              <span className="sm:hidden">Back</span>
            </button>
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              <div className="flex items-center gap-3">
                <Bot className="w-6 h-6 sm:w-8 sm:h-8 text-blue-600 flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <h1 className="text-base sm:text-lg font-semibold text-gray-900 truncate">{agent.name}</h1>
                  <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">{agent.description}</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium self-start sm:self-auto ${
                agent.training_status === "trained"
                  ? "bg-green-100 text-green-800"
                  : agent.training_status === "training"
                  ? "bg-yellow-100 text-yellow-800"
                  : "bg-red-100 text-red-800"
              }`}>
                {agent.training_status}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="bg-white rounded-lg shadow-lg h-[500px] sm:h-[600px] flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-12">
                <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Start a conversation with {agent.name}
                </h3>
                <p className="text-gray-600">
                  Ask questions and get responses based on your trained documents.
                </p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.sender_type === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.sender_type === "ai_agent" && (
                  <Bot className="w-8 h-8 text-blue-600 flex-shrink-0" />
                )}

                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender_type === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  {message.confidence_score !== null && message.sender_type === "ai_agent" && (
                    <div className="mt-2 text-xs opacity-70">
                      Confidence: {Math.round(message.confidence_score * 100)}%
                    </div>
                  )}
                </div>

                {message.sender_type === "user" && (
                  <User className="w-8 h-8 text-gray-600 flex-shrink-0" />
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start">
                <Bot className="w-8 h-8 text-blue-600 flex-shrink-0" />
                <div className="bg-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            {/* Voice Response Toggle */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setVoiceResponseEnabled(!voiceResponseEnabled)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    voiceResponseEnabled
                      ? 'bg-green-100 text-green-800 border border-green-300'
                      : 'bg-gray-100 text-gray-600 border border-gray-300'
                  }`}
                >
                  {voiceResponseEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                  Voice Responses
                </button>

                {/* Voice Recording */}
                <button
                  onClick={startVoiceRecording}
                  disabled={loading || isVoiceMode}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isRecordingVoice
                      ? 'bg-red-100 text-red-800 border border-red-300 animate-pulse'
                      : 'bg-blue-100 text-blue-800 border border-blue-300 hover:bg-blue-200'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title="Record voice message"
                >
                  <Mic className="w-4 h-4" />
                  Record
                </button>
              </div>

              <div className="text-xs text-gray-500">
                Voice: {voiceResponseEnabled ? 'On' : 'Off'} | Recording: {recordedVoiceText ? 'Ready' : 'None'}
              </div>
            </div>

            {/* Recorded Voice Preview */}
            {recordedVoiceText && (
              <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-900">Recorded Voice:</span>
                  <button
                    onClick={sendRecordedVoice}
                    className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                  >
                    Send Recording
                  </button>
                </div>
                <p className="text-sm text-blue-800">{recordedVoiceText}</p>
              </div>
            )}

            <form onSubmit={sendMessage} className="flex flex-col sm:flex-row gap-2">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder={
                    isVoiceMode
                      ? (isRecordingVoice ? "Recording voice..." : "Voice input active...")
                      : `Ask ${agent.name} a question...`
                  }
                  className="w-full pr-12 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base disabled:bg-gray-100 disabled:cursor-not-allowed"
                  disabled={loading || isVoiceMode}
                />
                {/* Voice Recording Icon in Input */}
                <button
                  onClick={startVoiceRecording}
                  disabled={loading || isVoiceMode}
                  className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1.5 rounded-full transition-colors ${
                    isRecordingVoice
                      ? 'bg-red-100 text-red-600 animate-pulse'
                      : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title="Record voice message"
                >
                  <Mic className="w-4 h-4" />
                </button>
              </div>
              <button
                type="submit"
                disabled={!newMessage.trim() || loading || isVoiceMode}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 min-w-[80px] sm:min-w-0"
              >
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
          </div>
        </div>

        {/* Voice Chat Component - Simple Icon Only */}
        <div className="mt-4 flex justify-center">
          <VoiceChat
            onVoiceMessage={handleVoiceMessage}
            isLoading={loading}
            onVoiceModeChange={setIsVoiceMode}
            voiceResponseEnabled={voiceResponseEnabled}
          />
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading chat...</p>
        </div>
      </div>
    }>
      <ChatPageContent />
    </Suspense>
  );
}

// Force dynamic rendering to avoid SSR issues with useSearchParams
export const dynamic = 'force-dynamic';
