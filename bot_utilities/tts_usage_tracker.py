"""
TTS Usage Tracker
Tracks monthly character usage to stay within Google Cloud TTS free tier
"""

import json
import os
from datetime import datetime
from typing import Dict

USAGE_FILE = "tts_usage.json"
WAVENET_LIMIT = 1_000_000  # 1 million characters/month for WaveNet (free tier)
STANDARD_LIMIT = 4_000_000  # 4 million characters/month for Standard voices (free tier)

class TTSUsageTracker:
    """Track TTS character usage to prevent exceeding free tier"""
    
    def __init__(self):
        self.usage_file = USAGE_FILE
        self.usage_data = self._load_usage()
    
    def _load_usage(self) -> Dict:
        """Load usage data from file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading TTS usage data: {e}")
                return self._create_new_usage()
        return self._create_new_usage()
    
    def _create_new_usage(self) -> Dict:
        """Create new usage data structure"""
        return {
            "month": datetime.now().strftime("%Y-%m"),
            "wavenet_characters": 0,
            "standard_characters": 0,
            "last_reset": datetime.now().isoformat()
        }
    
    def _save_usage(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving TTS usage data: {e}")
    
    def _check_month_reset(self):
        """Check if we need to reset monthly usage"""
        current_month = datetime.now().strftime("%Y-%m")
        if self.usage_data["month"] != current_month:
            print(f"🔄 Resetting TTS usage for new month: {current_month}")
            self.usage_data = self._create_new_usage()
            self._save_usage()
    
    def can_use_tts(self, text: str, is_wavenet: bool = True) -> tuple[bool, str]:
        """
        Check if TTS can be used without exceeding free tier
        
        Args:
            text: Text to be synthesized
            is_wavenet: Whether using WaveNet voice (True) or Standard voice (False)
        
        Returns:
            Tuple of (can_use: bool, reason: str)
        """
        self._check_month_reset()
        
        char_count = len(text)
        
        if is_wavenet:
            current_usage = self.usage_data["wavenet_characters"]
            limit = WAVENET_LIMIT
            voice_type = "WaveNet"
        else:
            current_usage = self.usage_data["standard_characters"]
            limit = STANDARD_LIMIT
            voice_type = "Standard"
        
        new_total = current_usage + char_count
        
        if new_total > limit:
            remaining = limit - current_usage
            return False, (
                f"❌ TTS limit reached! You've used {current_usage:,}/{limit:,} characters this month.\n"
                f"Remaining: {remaining:,} characters. Your request needs {char_count:,} characters.\n"
                f"Resets next month."
            )
        
        return True, ""
    
    def add_usage(self, text: str, is_wavenet: bool = True):
        """
        Add character usage after successful TTS generation
        
        Args:
            text: Text that was synthesized
            is_wavenet: Whether WaveNet voice was used
        """
        self._check_month_reset()
        
        char_count = len(text)
        
        if is_wavenet:
            self.usage_data["wavenet_characters"] += char_count
        else:
            self.usage_data["standard_characters"] += char_count
        
        self._save_usage()
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        self._check_month_reset()
        
        wavenet_used = self.usage_data["wavenet_characters"]
        wavenet_remaining = WAVENET_LIMIT - wavenet_used
        wavenet_percent = (wavenet_used / WAVENET_LIMIT) * 100
        
        standard_used = self.usage_data["standard_characters"]
        standard_remaining = STANDARD_LIMIT - standard_used
        standard_percent = (standard_used / STANDARD_LIMIT) * 100
        
        return {
            "month": self.usage_data["month"],
            "wavenet": {
                "used": wavenet_used,
                "limit": WAVENET_LIMIT,
                "remaining": wavenet_remaining,
                "percent": wavenet_percent
            },
            "standard": {
                "used": standard_used,
                "limit": STANDARD_LIMIT,
                "remaining": standard_remaining,
                "percent": standard_percent
            }
        }
    
    def reset_usage(self):
        """Manually reset usage (admin only)"""
        self.usage_data = self._create_new_usage()
        self._save_usage()
        print("✅ TTS usage manually reset")


# Global usage tracker instance
usage_tracker = TTSUsageTracker()
