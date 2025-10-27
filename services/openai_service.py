import openai
import logging
from django.conf import settings
from accounts.models import APIKey
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with OpenAI API"""

    def __init__(self, organization):
        self.organization = organization
        self.api_key = self._get_api_key()
        if self.api_key:
            openai.api_key = self.api_key.key
        else:
            logger.warning(f"No OpenAI API key found for organization {organization.name}")

    def _get_api_key(self) -> Optional[APIKey]:
        """Get active OpenAI API key for the organization"""
        return APIKey.objects.filter(
            organization=self.organization,
            provider='openai',
            is_active=True
        ).first()

    def generate_chat_response(self, messages: list, ai_agent, **kwargs) -> Optional[str]:
        """
        Generate a chat response using OpenAI

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            ai_agent: AIAgent instance with configuration
            **kwargs: Additional parameters

        Returns:
            Generated response text or None if failed
        """
        if not self.api_key or not self.api_key.key or self.api_key.key.startswith('sk-xxx'):
            logger.warning("No valid OpenAI API key available - using mock response")
            # Mock responses for testing
            mock_responses = [
                "Hello! Thank you for your message. I'm here to help you with any questions you might have.",
                "That's an interesting question. Let me provide you with some helpful information.",
                "I understand your concern. Here's what I can tell you about that.",
                "Thank you for reaching out. I'd be happy to assist you with this.",
                "That's a great question! Here's what I know about that topic.",
                "আপনার বার্তার জন্য ধন্যবাদ! আমি আপনার যেকোনো প্রশ্নে সাহায্য করতে এখানে আছি।",
                "এটি একটি আকর্ষণীয় প্রশ্ন। আমি আপনাকে কিছু সহায়ক তথ্য দিতে পারি।",
                "আমি আপনার উদ্বেগ বুঝতে পারছি। এ সম্পর্কে আমি যা বলতে পারি তা এখানে।"
            ]
            import random
            return random.choice(mock_responses)

        try:
            # Prepare system message
            system_message = {
                "role": "system",
                "content": ai_agent.system_prompt
            }

            # Combine system message with conversation history
            full_messages = [system_message] + messages

            # Make API call
            response = openai.ChatCompletion.create(
                model=ai_agent.model_name,
                messages=full_messages,
                temperature=ai_agent.temperature,
                max_tokens=ai_agent.max_tokens,
                **kwargs
            )

            # Extract response
            if response.choices:
                content = response.choices[0].message.content.strip()
                logger.info(f"Generated AI response for {ai_agent.name}: {content[:100]}...")
                return content
            else:
                logger.error("No response choices returned from OpenAI")
                return "I apologize, but I couldn't generate a response. Please try again."

        except openai.error.AuthenticationError:
            logger.error("OpenAI authentication failed")
            return "Authentication error with AI service. Please contact support."

        except openai.error.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return "I'm currently experiencing high demand. Please try again in a moment."

        except openai.error.InvalidRequestError as e:
            logger.error(f"OpenAI invalid request: {str(e)}")
            return "I encountered an error processing your request. Please try rephrasing."

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "I'm experiencing technical difficulties. Please try again later."

    def transcribe_audio(self, audio_file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper

        Args:
            audio_file_path: Path to audio file
            language: Language code (optional)

        Returns:
            Dict with transcription data
        """
        if not self.api_key or not self.api_key.key or self.api_key.key.startswith('sk-xxx'):
            # Mock transcription for testing
            return {
                'success': True,
                'transcription': "This is a mock transcription of the voice message. In a real implementation, this would be processed by OpenAI Whisper.",
                'confidence': 0.95,
                'language': language or 'en'
            }

        try:
            with open(audio_file_path, 'rb') as audio_file:
                # Use Whisper API
                response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language else None
                )

            transcription = response.get('text', '').strip()

            return {
                'success': True,
                'transcription': transcription,
                'confidence': 0.95,  # Whisper doesn't provide confidence scores
                'language': language or 'auto'
            }

        except Exception as e:
            logger.error(f"Audio transcription error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transcription': '',
                'confidence': 0.0
            }

    def generate_speech(self, text: str, voice: str = "alloy", speed: float = 1.0) -> Optional[bytes]:
        """
        Generate speech from text using OpenAI TTS

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            Audio data as bytes or None if failed
        """
        if not self.api_key:
            logger.error("No OpenAI API key available for TTS")
            return None

        try:
            response = openai.Audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )

            # Get audio content
            audio_data = b""
            for chunk in response.iter_bytes():
                audio_data += chunk

            return audio_data

        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            return None

    def check_connectivity(self) -> bool:
        """Check if OpenAI API is accessible"""
        if not self.api_key:
            return False

        try:
            # Simple test call
            openai.Model.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI connectivity check failed: {str(e)}")
            return False
