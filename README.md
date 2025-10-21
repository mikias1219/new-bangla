# Bangla Chat Pro

A comprehensive AI-powered chat platform built with FastAPI backend, SQLite database, and Next.js frontend. Features user authentication, subscription management, Stripe payments, and AI chat functionality.

## Features

- 🔐 **User Authentication**: Secure registration and login with JWT tokens
- 💳 **Subscription Management**: Free trial, multiple pricing plans, and Stripe integration
- 🤖 **AI Chat**: Powered by OpenAI GPT models with customizable responses
- 🎤 **Voice Messages**: Support for voice input and output
- 🌐 **Multi-language**: Support for Bangla, English, and other languages
- 📱 **Responsive Design**: Mobile-first design with modern UI
- 🔒 **Security**: End-to-end encryption and GDPR compliance

## Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: Database ORM with SQLite
- **Alembic**: Database migrations
- **JWT**: Authentication tokens
- **Stripe**: Payment processing
- **OpenAI**: AI chat functionality

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy `.env` and update the values:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the backend:**
   ```bash
   python run.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

### Database Setup

The application uses SQLite and will automatically create the database file on first run. The database migrations are handled automatically by SQLAlchemy.

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./bangla_chat_pro.db
SECRET_KEY=your-super-secret-jwt-key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
OPENAI_API_KEY=your_openai_api_key
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## Key Endpoints

- `POST /auth/register` - User registration
- `POST /auth/token` - User login
- `POST /ai/chat` - AI chat conversation
- `GET /subscriptions/current` - Get current subscription
- `POST /payments/create-payment-intent` - Create Stripe payment

## Project Structure

```
bangla-chat-pro/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database configuration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routers/             # API endpoints
│   │   └── auth/                # Authentication utilities
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
├── src/
│   ├── app/                     # Next.js app directory
│   ├── components/              # React components
│   └── lib/                     # Utility functions
├── package.json                 # Node dependencies
└── README.md
```

## Deployment

### Backend
```bash
# Using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
# Build for production
npm run build
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@banglachatpro.com or join our Discord community.

---

**Bangla Chat Pro** - Revolutionizing AI-powered conversations since 2024.