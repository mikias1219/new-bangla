export interface User {
  _id?: string;
  email: string;
  name: string;
  role: 'customer' | 'admin' | 'agent';
  createdAt: Date;
  lastLogin?: Date;
}

export interface Conversation {
  _id?: string;
  userId: string;
  messages: Message[];
  status: 'active' | 'escalated' | 'resolved' | 'closed';
  escalatedTo?: string; // agent ID
  satisfactionRating?: number;
  createdAt: Date;
  updatedAt: Date;
  metadata?: {
    userAgent?: string;
    ipAddress?: string;
    channel: 'chat' | 'voice';
  };
}

export interface Message {
  _id?: string;
  conversationId: string;
  sender: 'user' | 'ai' | 'agent';
  content: string;
  timestamp: Date;
  messageType: 'text' | 'voice';
  metadata?: {
    confidence?: number;
    intent?: string;
    entities?: Record<string, unknown>[];
    audioUrl?: string;
  };
}

export interface Analytics {
  totalConversations: number;
  activeConversations: number;
  averageResponseTime: number;
  satisfactionRate: number;
  escalationRate: number;
  topQueries: Array<{
    query: string;
    count: number;
  }>;
  dateRange: {
    start: Date;
    end: Date;
  };
}

export interface Intent {
  _id?: string;
  name: string;
  keywords: string[];
  responses: string[];
  escalationThreshold: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface VoiceSettings {
  language: string;
  voice: string;
  rate: number;
  pitch: number;
  volume: number;
}

export interface ChatSettings {
  theme: 'light' | 'dark';
  fontSize: 'small' | 'medium' | 'large';
  soundEnabled: boolean;
  autoScroll: boolean;
}
