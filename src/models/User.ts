import mongoose, { Document, Schema } from 'mongoose';

export interface IUser extends Document {
  email: string;
  name: string;
  role: 'customer' | 'admin' | 'agent';
  password?: string; // Only for admin/agent
  createdAt: Date;
  lastLogin?: Date;
}

const UserSchema: Schema = new Schema({
  email: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  role: { type: String, enum: ['customer', 'admin', 'agent'], default: 'customer' },
  password: { type: String }, // Hashed password for admin/agent
  createdAt: { type: Date, default: Date.now },
  lastLogin: { type: Date }
});

export default mongoose.models.User || mongoose.model<IUser>('User', UserSchema);
