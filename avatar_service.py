"""
ElevenLabs Avatar Service
Integration with ElevenLabs API for AI voice/avatar generation.
"""

import os
import requests
from typing import Optional, Dict
import base64
import logging

logger = logging.getLogger(__name__)


class ElevenLabsAvatarService:
    """
    Integration with ElevenLabs for AI avatar/voice interactions.
    """
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not configured - avatar features will be disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    def generate_voice(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM", 
                      model_id: str = "eleven_multilingual_v2") -> Optional[bytes]:
        """
        Generate speech from text using ElevenLabs.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (default: Rachel - professional female)
            model_id: Model to use
        
        Returns:
            Audio bytes (MP3 format) or None if error
        """
        if not self.enabled:
            logger.warning("ElevenLabs not configured - cannot generate voice")
            return None
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating voice with ElevenLabs: {str(e)}")
            return None
    
    def create_avatar_conversation(self, lead_data: Dict) -> Dict:
        """
        Create a personalized voice message for a lead.
        
        Args:
            lead_data: Company lead information
        
        Returns:
            Dict with audio base64 and transcript
        """
        if not self.enabled:
            return {
                "error": "ElevenLabs not configured",
                "transcript": "",
                "format": "mp3"
            }
        
        # Generate personalized message
        company_name = lead_data.get('company_name', 'there')
        industry = lead_data.get('key_products_services', 'business')
        if not industry or len(industry) > 50:
            industry = 'business'
        
        message = f"""
        Hello {company_name}, this is Sarah from LeadGen AI. 
        I noticed your company operates in the {industry} sector, and I believe 
        we have solutions that could help accelerate your growth. 
        Would you be open to a brief 15-minute conversation to explore how we can help?
        You can reach me directly or reply to this message. Looking forward to connecting!
        """
        
        # Generate voice
        audio_bytes = self.generate_voice(message.strip())
        
        if not audio_bytes:
            return {
                "error": "Failed to generate voice",
                "transcript": message.strip(),
                "format": "mp3"
            }
        
        # Convert to base64 for API response
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "audio_base64": audio_base64,
            "transcript": message.strip(),
            "format": "mp3",
            "duration_estimate": len(message.split()) * 0.5  # Rough estimate
        }
    
    def generate_lead_summary_voice(self, leads: list) -> Dict:
        """
        Generate voice summary of lead generation results.
        
        Args:
            leads: List of lead dictionaries
        
        Returns:
            Dict with audio base64 and transcript
        """
        if not self.enabled:
            return {
                "error": "ElevenLabs not configured",
                "transcript": "",
                "format": "mp3"
            }
        
        total_leads = len(leads)
        premium_leads = sum(1 for lead in leads if lead.get('quality_tier') == 'Premium')
        high_leads = sum(1 for lead in leads if lead.get('quality_tier') == 'High')
        
        message = f"""
        Great news! I've generated {total_leads} leads for you. 
        Out of these, {premium_leads} are premium quality leads and {high_leads} are high quality leads. 
        I recommend prioritizing these for outreach. 
        You can view the full details in your dashboard.
        """
        
        audio_bytes = self.generate_voice(message.strip())
        
        if not audio_bytes:
            return {
                "error": "Failed to generate voice",
                "transcript": message.strip(),
                "format": "mp3"
            }
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "audio_base64": audio_base64,
            "transcript": message.strip(),
            "format": "mp3"
        }
    
    def generate_custom_voice(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Dict:
        """
        Generate voice from custom text.
        
        Args:
            text: Custom text to convert to speech
            voice_id: Voice ID to use
        
        Returns:
            Dict with audio base64 and transcript
        """
        if not self.enabled:
            return {
                "error": "ElevenLabs not configured",
                "transcript": text,
                "format": "mp3"
            }
        
        audio_bytes = self.generate_voice(text, voice_id)
        
        if not audio_bytes:
            return {
                "error": "Failed to generate voice",
                "transcript": text,
                "format": "mp3"
            }
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "audio_base64": audio_base64,
            "transcript": text,
            "format": "mp3"
        }
    
    def get_available_voices(self) -> list:
        """
        Get list of available ElevenLabs voices.
        
        Returns:
            List of voice dictionaries
        """
        if not self.enabled:
            return []
        
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get('voices', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching voices: {str(e)}")
            return []


def get_avatar_service() -> Optional[ElevenLabsAvatarService]:
    """
    Get avatar service instance if configured.
    
    Returns:
        ElevenLabsAvatarService instance or None if not configured
    """
    try:
        service = ElevenLabsAvatarService()
        if service.enabled:
            return service
        return None
    except Exception as e:
        logger.warning(f"Avatar service not available: {str(e)}")
        return None

