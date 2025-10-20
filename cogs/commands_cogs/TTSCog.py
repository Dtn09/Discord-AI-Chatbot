"""
Text-to-Speech Cog
Provides TTS commands for the Discord bot
"""

import discord
from discord import app_commands
from discord.ext import commands
import io
from bot_utilities.tts_utils import tts_manager, VOICE_PRESETS
from bot_utilities.tts_usage_tracker import usage_tracker
from bot_utilities.smart_tts_detector import smart_tts_detector


class TTSCog(commands.Cog):
    """Text-to-Speech commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="tts", description="Convert text to speech")
    @app_commands.describe(
        text="Text to convert to speech",
        voice="Voice preset (default, male, female, british, aussie, etc.)"
    )
    async def tts(
        self,
        interaction: discord.Interaction,
        text: str,
        voice: str = "default"
    ):
        """Convert text to speech and send as audio file"""
        
        # Check if TTS is available
        if not tts_manager.client:
            await interaction.response.send_message(
                "❌ TTS is not configured. Please set up Google Cloud credentials.",
                ephemeral=True
            )
            return
        
        # Get voice preset
        voice_config = VOICE_PRESETS.get(voice.lower(), VOICE_PRESETS["default"])
        is_wavenet = voice_config.get("is_wavenet", True)
        
        # Check usage limits BEFORE generating
        can_use, reason = usage_tracker.can_use_tts(text, is_wavenet)
        if not can_use:
            await interaction.response.send_message(reason, ephemeral=True)
            return
        
        # Defer response as TTS might take a moment
        await interaction.response.defer()
        
        try:
            # Generate speech
            audio_content = tts_manager.text_to_speech(
                text=text,
                language_code=voice_config["language_code"],
                voice_name=voice_config["voice_name"]
            )
            
            if not audio_content:
                await interaction.followup.send("❌ Failed to generate speech. Please try again.")
                return
            
            # Track usage AFTER successful generation
            usage_tracker.add_usage(text, is_wavenet)
            
            # Create Discord file from audio bytes
            audio_file = discord.File(
                io.BytesIO(audio_content),
                filename=f"tts_{voice}.mp3"
            )
            
            # Get usage stats for footer
            stats = usage_tracker.get_usage_stats()
            usage_info = f"WaveNet: {stats['wavenet']['used']:,}/{stats['wavenet']['limit']:,} chars"
            
            # Send the audio file
            embed = discord.Embed(
                title="🔊 Text-to-Speech",
                description=f"**Text:** {text[:100]}{'...' if len(text) > 100 else ''}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Voice", value=voice.capitalize(), inline=True)
            embed.add_field(name="Characters", value=str(len(text)), inline=True)
            embed.set_footer(text=f"Requested by {interaction.user.display_name} • {usage_info}")
            
            await interaction.followup.send(embed=embed, file=audio_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")
            print(f"TTS Error: {e}")
    
    @app_commands.command(name="tts-voices", description="List available voice presets")
    async def tts_voices(self, interaction: discord.Interaction):
        """Show available TTS voice presets"""
        
        embed = discord.Embed(
            title="🎤 Available TTS Voices",
            description="Use these voice presets with the `/tts` command\n**All using WaveNet (high quality)**",
            color=discord.Color.green()
        )
        
        voices_info = {
            "English": ["default", "male", "female"],
            "Accents": ["british", "aussie"],
            "Languages": ["french", "german", "spanish", "japanese", "korean"],
            "Standard (Fallback)": ["standard"]
        }
        
        for category, voices in voices_info.items():
            embed.add_field(
                name=category,
                value=", ".join(f"`{v}`" for v in voices),
                inline=False
            )
        
        # Add usage stats
        stats = usage_tracker.get_usage_stats()
        usage_text = (
            f"**Monthly Usage ({stats['month']}):**\n"
            f"WaveNet: {stats['wavenet']['used']:,}/{stats['wavenet']['limit']:,} chars "
            f"({stats['wavenet']['percent']:.1f}%)\n"
            f"Standard: {stats['standard']['used']:,}/{stats['standard']['limit']:,} chars "
            f"({stats['standard']['percent']:.1f}%)"
        )
        embed.add_field(name="📊 Free Tier Status", value=usage_text, inline=False)
        
        embed.set_footer(text="Example: /tts text:Hello World voice:british")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="tts-usage", description="Check TTS usage statistics")
    async def tts_usage(self, interaction: discord.Interaction):
        """Display detailed TTS usage statistics"""
        
        stats = usage_tracker.get_usage_stats()
        
        embed = discord.Embed(
            title="📊 TTS Usage Statistics",
            description=f"**Month:** {stats['month']}",
            color=discord.Color.blue()
        )
        
        # WaveNet stats
        wavenet = stats['wavenet']
        wavenet_bar = self._create_progress_bar(wavenet['percent'])
        embed.add_field(
            name="🔊 WaveNet Voices (High Quality)",
            value=(
                f"Used: **{wavenet['used']:,}** / {wavenet['limit']:,} characters\n"
                f"Remaining: **{wavenet['remaining']:,}** characters\n"
                f"{wavenet_bar} {wavenet['percent']:.1f}%"
            ),
            inline=False
        )
        
        # Standard stats
        standard = stats['standard']
        standard_bar = self._create_progress_bar(standard['percent'])
        embed.add_field(
            name="📢 Standard Voices",
            value=(
                f"Used: **{standard['used']:,}** / {standard['limit']:,} characters\n"
                f"Remaining: **{standard['remaining']:,}** characters\n"
                f"{standard_bar} {standard['percent']:.1f}%"
            ),
            inline=False
        )
        
        # Warnings
        if wavenet['percent'] > 80:
            embed.add_field(
                name="⚠️ Warning",
                value="You've used over 80% of your WaveNet free tier!",
                inline=False
            )
        
        embed.set_footer(text="Usage resets on the 1st of each month")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _create_progress_bar(self, percent: float, length: int = 10) -> str:
        """Create a text progress bar"""
        filled = int((percent / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"`{bar}`"
    
    @app_commands.command(name="tts-custom", description="Convert text to speech with custom settings")
    @app_commands.describe(
        text="Text to convert to speech",
        language="Language code (en-US, en-GB, fr-FR, etc.)",
        speed="Speaking speed (0.5 to 2.0, default 1.0)",
        pitch="Voice pitch (-10 to 10, default 0)"
    )
    async def tts_custom(
        self,
        interaction: discord.Interaction,
        text: str,
        language: str = "en-US",
        speed: float = 1.0,
        pitch: float = 0.0
    ):
        """Convert text to speech with custom voice parameters"""
        
        # Check if TTS is available
        if not tts_manager.client:
            await interaction.response.send_message(
                "❌ TTS is not configured. Please set up Google Cloud credentials.",
                ephemeral=True
            )
            return
        
        # Validate parameters
        if not (0.25 <= speed <= 4.0):
            await interaction.response.send_message(
                "❌ Speed must be between 0.25 and 4.0",
                ephemeral=True
            )
            return
        
        if not (-20.0 <= pitch <= 20.0):
            await interaction.response.send_message(
                "❌ Pitch must be between -20 and 20",
                ephemeral=True
            )
            return
        
        # Defer response
        await interaction.response.defer()
        
        try:
            # Generate speech
            audio_content = tts_manager.text_to_speech(
                text=text,
                language_code=language,
                speaking_rate=speed,
                pitch=pitch
            )
            
            if not audio_content:
                await interaction.followup.send("❌ Failed to generate speech. Check your language code.")
                return
            
            # Create Discord file
            audio_file = discord.File(
                io.BytesIO(audio_content),
                filename="tts_custom.mp3"
            )
            
            # Send the audio file
            embed = discord.Embed(
                title="🔊 Custom Text-to-Speech",
                description=f"**Text:** {text[:100]}{'...' if len(text) > 100 else ''}",
                color=discord.Color.purple()
            )
            embed.add_field(name="Language", value=language, inline=True)
            embed.add_field(name="Speed", value=f"{speed}x", inline=True)
            embed.add_field(name="Pitch", value=f"{pitch:+.1f}", inline=True)
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed, file=audio_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")
            print(f"TTS Custom Error: {e}")
    
    @app_commands.command(name="tts-auto", description="Toggle automatic TTS for bot responses in this channel")
    async def tts_auto(self, interaction: discord.Interaction):
        """Toggle automatic TTS generation for bot responses"""
        
        channel_id = interaction.channel.id
        new_state = smart_tts_detector.toggle_channel(channel_id)
        
        embed = discord.Embed(
            title="🤖 Auto-TTS Settings",
            color=discord.Color.green() if new_state else discord.Color.red()
        )
        
        if new_state:
            embed.description = (
                "✅ **Auto-TTS Enabled** for this channel!\n\n"
                "The bot will now automatically add voice messages when:\n"
                "• You ask questions (What, How, Why, etc.)\n"
                "• You use words like 'read', 'speak', 'tell me'\n"
                "• The response is conversational\n"
                "• Response is short enough (under 500 characters)\n\n"
                "Auto-TTS will **NOT** activate for:\n"
                "• Code blocks or technical content\n"
                "• Very long responses\n"
                "• Lists or tables"
            )
        else:
            embed.description = (
                "❌ **Auto-TTS Disabled** for this channel.\n\n"
                "The bot will only generate TTS when you use `/tts` commands."
            )
        
        embed.set_footer(text=f"Channel: {interaction.channel.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(TTSCog(bot))
