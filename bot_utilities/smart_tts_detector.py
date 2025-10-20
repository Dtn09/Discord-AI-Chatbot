"""
Smart TTS Detector
Intelligently determines when to automatically generate TTS for bot responses
"""

import re
from typing import Tuple

class SmartTTSDetector:
    """Detects when TTS should be automatically generated"""
    
    # Keywords that suggest TTS should be used
    TTS_TRIGGERS = [
        "read", "speak", "say", "tell me", "voice",
        "listen", "hear", "audio", "sound",
        "tts", "text to speech", "read aloud",
        "erzähl", "sprich", "sag", "hör",  # German equivalents
    ]
    
    # Keywords that suggest TTS should NOT be used
    NO_TTS_TRIGGERS = [
        "code", "programming", "function", "class",
        "json", "xml", "html", "css", "javascript",
        "error", "traceback", "exception", "debug",
        "list", "table", "data", "statistics",
        "```",  # Code blocks
    ]
    
    # Questions that work well with TTS
    QUESTION_PATTERNS = [
        r"what is",
        r"who is",
        r"how do",
        r"why",
        r"when",
        r"where",
        r"can you",
        r"could you",
        r"would you",
        r"tell me about",
        r"explain",
        r"describe",
    ]
    
    def __init__(self):
        self.enabled_channels = set()
    
    def should_use_tts(
        self,
        message_content: str,
        response_content: str,
        channel_id: int
    ) -> Tuple[bool, str]:
        """
        Determine if TTS should be used for this response
        
        Args:
            message_content: The user's message
            response_content: The bot's response
            channel_id: Discord channel ID
        
        Returns:
            Tuple of (should_use: bool, reason: str)
        """
        # Check if auto-TTS is enabled for this channel
        if channel_id not in self.enabled_channels:
            return False, "Auto-TTS disabled for channel"
        
        message_lower = message_content.lower()
        response_lower = response_content.lower()
        
        # 1. Check for explicit TTS triggers in user message
        for trigger in self.TTS_TRIGGERS:
            if trigger in message_lower:
                return True, f"TTS trigger word detected: {trigger}"
        
        # 2. Check if response contains code or technical content
        for no_trigger in self.NO_TTS_TRIGGERS:
            if no_trigger in response_lower:
                return False, f"Technical content detected: {no_trigger}"
        
        # 3. Check for code blocks
        if "```" in response_content:
            return False, "Code block detected"
        
        # 4. Check if response is too long (over 500 chars)
        if len(response_content) > 500:
            return False, "Response too long for TTS"
        
        # 5. Check if response is too short (less than 10 chars)
        if len(response_content.strip()) < 10:
            return False, "Response too short"
        
        # 6. Check if message is a question (questions work well with TTS)
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, message_lower):
                return True, "Question detected"
        
        # 7. Check if response is conversational (has common conversational words)
        conversational_words = ["i", "you", "we", "my", "your", "it's", "im", "that's"]
        word_count = sum(1 for word in conversational_words if f" {word} " in f" {response_lower} ")
        if word_count >= 2:
            return True, "Conversational response"
        
        # Default: Don't use TTS
        return False, "No clear TTS indicators"
    
    def enable_channel(self, channel_id: int):
        """Enable auto-TTS for a channel"""
        self.enabled_channels.add(channel_id)
    
    def disable_channel(self, channel_id: int):
        """Disable auto-TTS for a channel"""
        self.enabled_channels.discard(channel_id)
    
    def is_channel_enabled(self, channel_id: int) -> bool:
        """Check if auto-TTS is enabled for a channel"""
        return channel_id in self.enabled_channels
    
    def toggle_channel(self, channel_id: int) -> bool:
        """Toggle auto-TTS for a channel, returns new state"""
        if channel_id in self.enabled_channels:
            self.enabled_channels.remove(channel_id)
            return False
        else:
            self.enabled_channels.add(channel_id)
            return True


# Global smart TTS detector
smart_tts_detector = SmartTTSDetector()
