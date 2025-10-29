import openai
import os
from django.conf import settings
from decouple import config
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API integration"""
    
    def __init__(self):
        # Use config() from python-decouple to read from .env file
        self.api_key = config('OPENAI_API_KEY', default='')
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def _detect_language(self, text: str) -> str:
        """Detect if the text is in English or Bangla"""
        # More comprehensive Bangla character set
        bangla_chars = set('অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎািীুূৃেৈোৌংঃ')
        
        # Count Bangla characters
        bangla_count = sum(1 for char in text if char in bangla_chars)
        total_chars = len([c for c in text if c.isalpha()])
        
        # If no alphabetic characters, default to English
        if total_chars == 0:
            return 'english'
        
        # If more than 20% of alphabetic characters are Bangla, consider it Bangla
        bangla_ratio = bangla_count / total_chars
        
        # Debug logging
        logger.info(f"Language detection: text='{text[:50]}...', bangla_count={bangla_count}, total_chars={total_chars}, ratio={bangla_ratio:.2f}")
        
        if bangla_ratio > 0.2:
            return 'bangla'
        else:
            return 'english'
    
    def generate_chat_response(
        self, 
        message: str, 
        conversation_history: list = None,
        system_prompt: str = None,
        client_name: str = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate AI chat response in Bangla
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            system_prompt: System prompt for AI behavior
            model: OpenAI model to use
            temperature: Response creativity (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing response, confidence, and metadata
        """
        if not self.api_key:
            return {
                'response': 'দুঃখিত, AI সেবা এখন উপলব্ধ নয়।',
                'confidence': 0.0,
                'error': 'OpenAI API key not configured'
            }
        
        try:
            # Detect language and set appropriate system prompt
            detected_language = self._detect_language(message)
            
            if not system_prompt:
                client_context = f" for {client_name}" if client_name else ""
                if detected_language == 'english':
                    system_prompt = f"""
                    You are a friendly and helpful AI assistant{client_context}.
                    The user is asking in English, so you MUST respond in English only.
                    Do not use Bengali/Bangla language in your response.
                    Be polite, helpful, and respond naturally in English.
                    """
                else:  # Bangla
                    system_prompt = f"""
                    আপনি একজন বন্ধুত্বপূর্ণ এবং সহায়ক AI সহকারী{client_context}।
                    ব্যবহারকারী বাংলায় প্রশ্ন করেছেন, তাই আপনাকে অবশ্যই বাংলায় উত্তর দিতে হবে।
                    ইংরেজি ভাষা ব্যবহার করবেন না।
                    বিনয়ী এবং সহায়ক হন এবং স্বাভাবিক বাংলায় উত্তর দিন।
                    """
            
            # Prepare messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    messages.append({
                        "role": "user" if msg.get('sender') == 'user' else "assistant",
                        "content": msg.get('content', '')
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                'response': ai_response,
                'confidence': 0.9,  # High confidence for successful response
                'detected_language': detected_language,
                'model_used': model,
                'tokens_used': response.usage.total_tokens,
                'finish_reason': response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                'response': 'দুঃখিত, একটি ত্রুটি হয়েছে। দয়া করে আবার চেষ্টা করুন।',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def generate_voice_response(
        self, 
        text: str, 
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate audio response using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice type (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            speed: Speech speed (0.25 to 4.0)
            
        Returns:
            Dict containing audio file path and metadata
        """
        if not self.api_key:
            return {
                'audio_url': None,
                'error': 'OpenAI API key not configured'
            }
        
        try:
            # Generate speech
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Save audio file
            import tempfile
            import os
            
            # Create media directory if it doesn't exist
            media_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
            os.makedirs(media_dir, exist_ok=True)
            
            # Generate unique filename
            import uuid
            filename = f"tts_{uuid.uuid4().hex}.mp3"
            file_path = os.path.join(media_dir, filename)
            
            # Write audio data to file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Return relative URL
            audio_url = f"{settings.MEDIA_URL}audio/{filename}"
            
            return {
                'audio_url': audio_url,
                'file_path': file_path,
                'filename': filename,
                'voice': voice,
                'model': model,
                'speed': speed
            }
            
        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            return {
                'audio_url': None,
                'error': str(e)
            }
    
    def detect_intent(self, message: str, intents: list) -> Dict[str, Any]:
        """
        Detect intent from user message
        
        Args:
            message: User message
            intents: List of available intents
            
        Returns:
            Dict containing detected intent and confidence
        """
        if not self.api_key:
            return {
                'intent': None,
                'confidence': 0.0,
                'error': 'OpenAI API key not configured'
            }
        
        try:
            # Create intent detection prompt
            intent_list = "\n".join([f"- {intent['name']}: {intent['description']}" for intent in intents])
            
            prompt = f"""
            নিচের বার্তা থেকে সবচেয়ে উপযুক্ত ইনটেন্ট খুঁজে বের করুন:
            
            বার্তা: "{message}"
            
            উপলব্ধ ইনটেন্ট:
            {intent_list}
            
            শুধুমাত্র ইনটেন্টের নাম দিন এবং আত্মবিশ্বাসের স্কোর (0-1) দিন।
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response (simple parsing)
            lines = result.split('\n')
            intent_name = None
            confidence = 0.5
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        intent_name = parts[0].strip()
                        try:
                            confidence = float(parts[1].strip())
                        except ValueError:
                            confidence = 0.5
                        break
            
            return {
                'intent': intent_name,
                'confidence': confidence,
                'raw_response': result
            }
            
        except Exception as e:
            logger.error(f"Intent detection error: {str(e)}")
            return {
                'intent': None,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of user message
        
        Args:
            message: User message to analyze
            
        Returns:
            Dict containing sentiment analysis
        """
        if not self.api_key:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'error': 'OpenAI API key not configured'
            }
        
        try:
            prompt = f"""
            নিচের বার্তার আবেগ বিশ্লেষণ করুন:
            
            বার্তা: "{message}"
            
            আবেগ: positive, negative, neutral
            আত্মবিশ্বাস: 0-1 স্কেলে
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            sentiment = 'neutral'
            confidence = 0.5
            
            if 'positive' in result.lower():
                sentiment = 'positive'
            elif 'negative' in result.lower():
                sentiment = 'negative'
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'raw_response': result
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'error': str(e)
            }


# Global instance
openai_service = OpenAIService()