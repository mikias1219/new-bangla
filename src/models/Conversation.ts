import mongoose, { Document, Schema } from 'mongoose';

export interface IConversation extends Document {
  userId: string;
  messages: mongoose.Types.ObjectId[];
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

const ConversationSchema: Schema = new Schema({
  userId: { type: String, required: true },
  messages: [{ type: Schema.Types.ObjectId, ref: 'Message' }],
  status: { type: String, enum: ['active', 'escalated', 'resolved', 'closed'], default: 'active' },
  escalatedTo: { type: String },
  satisfactionRating: { type: Number, min: 1, max: 5 },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
  metadata: {
    userAgent: String,
    ipAddress: String,
    channel: { type: String, enum: ['chat', 'voice'], default: 'chat' }
  }
});

// Update the updatedAt field before saving
ConversationSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.models.Conversation || mongoose.model<IConversation>('Conversation', ConversationSchema);
