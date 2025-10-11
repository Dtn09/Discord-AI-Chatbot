"""
Google Cloud Text-to-Speech utilities
Provides text-to-speech functionality using Google Cloud TTS API
"""

import os
import io
from google.cloud import texttospeech
from typing import Optional

class TTSManager:
    """Manages Google Cloud Text-to-Speech operations"""
    
    def __init__(self):
        """Initialize the TTS client"""
        # Google Cloud credentials should be set via environment variable
        # GOOGLE_APPLICATION_CREDENTIALS or passed as JSON
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Google Cloud TTS client"""
        try:
            # If credentials are in environment
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                self.client = texttospeech.TextToSpeechClient()
            # If credentials are passed as JSON string
            elif os.getenv('GOOGLE_CLOUD_CREDENTIALS_JSON'):
                import json
                from google.oauth2 import service_account
                
                credentials_dict = json.loads(os.getenv('GOOGLE_CLOUD_CREDENTIALS_JSON'))
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                self.client = texttospeech.TextToSpeechClient(credentials=credentials)
            else:
                print("⚠️  Google Cloud credentials not found. TTS will not work.")
                print("Set GOOGLE_CLOUD_CREDENTIALS_JSON in your environment variables.")
        except Exception as e:
            print(f"⚠️  Failed to initialize Google Cloud TTS: {e}")
    
    def text_to_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_name: Optional[str] = None,
        gender: str = "NEUTRAL",
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> Optional[bytes]:
        """
        Convert text to speech using Google Cloud TTS
        
        Args:
            text: Text to convert to speech
            language_code: Language code (e.g., "en-US", "en-GB", "fr-FR")
            voice_name: Specific voice name (e.g., "en-US-Neural2-J")
            gender: Voice gender (NEUTRAL, MALE, FEMALE)
            speaking_rate: Speed (0.25 to 4.0, default 1.0)
            pitch: Pitch adjustment (-20.0 to 20.0, default 0.0)
        
        Returns:
            Audio bytes in MP3 format, or None if failed
        """
        if not self.client:
            return None
        
        if len(text) > 5000:
            text = text[:5000]  # Google Cloud limit per request
        
        try:
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice parameters
            if voice_name:
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=voice_name
                )
            else:
                # Map gender string to enum
                gender_map = {
                    "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL,
                    "MALE": texttospeech.SsmlVoiceGender.MALE,
                    "FEMALE": texttospeech.SsmlVoiceGender.FEMALE
                }
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    ssml_gender=gender_map.get(gender, texttospeech.SsmlVoiceGender.NEUTRAL)
                )
            
            # Configure audio output
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None
    
    def get_available_voices(self, language_code: str = "en-US") -> list:
        """
        Get list of available voices for a language
        
        Args:
            language_code: Language code to filter voices
        
        Returns:
            List of voice names
        """
        if not self.client:
            return []
        
        try:
            voices = self.client.list_voices(language_code=language_code)
            return [voice.name for voice in voices.voices]
        except Exception as e:
            print(f"❌ Error fetching voices: {e}")
            return []


# Popular voice presets - WaveNet voices (better quality, 1M free characters/month)
VOICE_PRESETS = {
    # WaveNet voices (high quality, free tier: 1M characters/month)
    "default": {"language_code": "en-US", "voice_name": "en-US-Wavenet-D", "is_wavenet": True},
    "male": {"language_code": "en-US", "voice_name": "en-US-Wavenet-B", "is_wavenet": True},
    "female": {"language_code": "en-US", "voice_name": "en-US-Wavenet-C", "is_wavenet": True},
    "british": {"language_code": "en-GB", "voice_name": "en-GB-Wavenet-B", "is_wavenet": True},
    "aussie": {"language_code": "en-AU", "voice_name": "en-AU-Wavenet-A", "is_wavenet": True},
    
    # International WaveNet voices
    "french": {"language_code": "fr-FR", "voice_name": "fr-FR-Wavenet-A", "is_wavenet": True},
    "german": {"language_code": "de-DE", "voice_name": "de-DE-Wavenet-B", "is_wavenet": True},
    "spanish": {"language_code": "es-ES", "voice_name": "es-ES-Wavenet-B", "is_wavenet": True},
    "japanese": {"language_code": "ja-JP", "voice_name": "ja-JP-Wavenet-A", "is_wavenet": True},
    "korean": {"language_code": "ko-KR", "voice_name": "ko-KR-Wavenet-A", "is_wavenet": True},
    
    # Standard voices (backup option, 4M free characters/month)
    "standard": {"language_code": "en-US", "voice_name": "en-US-Standard-D", "is_wavenet": False},
}


# Initialize global TTS manager
tts_manager = TTSManager()
