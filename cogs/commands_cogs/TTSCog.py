"""
Text-to-Speech Cog
Provides TTS commands for the Discord bot
"""

import discord
from discord import app_commands
from discord.ext import commands
import io
from bot_utilities.tts_utils import tts_manager, VOICE_PRESETS


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
        
        # Defer response as TTS might take a moment
        await interaction.response.defer()
        
        try:
            # Get voice preset
            voice_config = VOICE_PRESETS.get(voice.lower(), VOICE_PRESETS["default"])
            
            # Generate speech
            audio_content = tts_manager.text_to_speech(
                text=text,
                language_code=voice_config["language_code"],
                voice_name=voice_config["voice_name"]
            )
            
            if not audio_content:
                await interaction.followup.send("❌ Failed to generate speech. Please try again.")
                return
            
            # Create Discord file from audio bytes
            audio_file = discord.File(
                io.BytesIO(audio_content),
                filename=f"tts_{voice}.mp3"
            )
            
            # Send the audio file
            embed = discord.Embed(
                title="🔊 Text-to-Speech",
                description=f"**Text:** {text[:100]}{'...' if len(text) > 100 else ''}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Voice", value=voice.capitalize(), inline=True)
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed, file=audio_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")
            print(f"TTS Error: {e}")
    
    @app_commands.command(name="tts-voices", description="List available voice presets")
    async def tts_voices(self, interaction: discord.Interaction):
        """Show available TTS voice presets"""
        
        embed = discord.Embed(
            title="🎤 Available TTS Voices",
            description="Use these voice presets with the `/tts` command",
            color=discord.Color.green()
        )
        
        voices_info = {
            "English": ["default", "male", "female"],
            "Accents": ["british", "aussie"],
            "Languages": ["french", "german", "spanish", "japanese"]
        }
        
        for category, voices in voices_info.items():
            embed.add_field(
                name=category,
                value=", ".join(f"`{v}`" for v in voices),
                inline=False
            )
        
        embed.set_footer(text="Example: /tts text:Hello World voice:british")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
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


async def setup(bot):
    await bot.add_cog(TTSCog(bot))
