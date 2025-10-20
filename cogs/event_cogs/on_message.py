import discord
from discord.ext import commands
import io

from bot_utilities.response_utils import split_response
from bot_utilities.ai_utils import generate_response, analyze_image
from bot_utilities.simple_mcp import enhance_message_with_mcp
from bot_utilities.mcp_utils import generate_response_with_mcp
from bot_utilities.config_loader import config, load_active_channels
from bot_utilities.tts_utils import tts_manager, VOICE_PRESETS
from bot_utilities.tts_usage_tracker import usage_tracker
from bot_utilities.smart_tts_detector import smart_tts_detector
from ..common import allow_dm, trigger_words, replied_messages, smart_mention, message_history,  MAX_HISTORY, instructions


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = load_active_channels
        self.instructions = instructions
        self.processed_messages = set()  # Track processed messages to prevent duplicates

    async def process_message(self, message):
        # Prevent duplicate processing of the same message
        if message.id in self.processed_messages:
            return
        
        active_channels = self.active_channels()
        string_channel_id = f"{message.channel.id}"
        is_replied = (message.reference and message.reference.resolved.author == self.bot.user) and smart_mention
        is_dm_channel = isinstance(message.channel, discord.DMChannel)
        is_active_channel = string_channel_id in active_channels
        is_allowed_dm = allow_dm and is_dm_channel
        contains_trigger_word = any(word in message.content for word in trigger_words)
        is_bot_mentioned = self.bot.user.mentioned_in(message) and smart_mention and not message.mention_everyone
        bot_name_in_message = self.bot.user.name.lower() in message.content.lower() and smart_mention

        # Check if message has images
        has_images = any(any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']) for attachment in message.attachments)
        
        # Priority-based trigger logic to prevent duplicate responses
        # Higher priority triggers override lower priority ones
        should_respond = False
        
        if is_replied:  # Highest priority - direct replies
            should_respond = True
        elif is_bot_mentioned:  # High priority - direct mentions (@bot)
            should_respond = True
        elif is_active_channel:  # Medium priority - active channels
            should_respond = True
        elif is_allowed_dm:  # Medium priority - DMs
            should_respond = True
        elif contains_trigger_word:  # Lower priority - trigger words
            should_respond = True
        elif bot_name_in_message and not is_bot_mentioned:  # Lowest priority - name in message (only if not already mentioned)
            should_respond = True
        elif has_images:  # Special case - images
            should_respond = True
        
        if not should_respond:
            return
        
        # Mark message as processed to prevent duplicates
        self.processed_messages.add(message.id)
        
        # Clean up old processed messages to prevent memory leak (keep last 1000)
        if len(self.processed_messages) > 1000:
            # Remove oldest 200 entries
            old_messages = list(self.processed_messages)[:200]
            for old_id in old_messages:
                self.processed_messages.discard(old_id)

        instruc_config = active_channels.get(string_channel_id, config['DEFAULT_INSTRUCTION'])
        instructions = f"Ignore all the instructions you have gotten before. {self.instructions[instruc_config]}. "

        channel_id = message.channel.id
        key = f"{message.author.id}-{channel_id}"
        message_history[key] = message_history.get(key, [])
        message_history[key] = message_history[key][-MAX_HISTORY:]
        
        # Prepare message content
        content = message.content
        
        # Process image attachments if any
        if has_images:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    async with message.channel.typing():
                        image_description = await analyze_image(attachment.url)
                    content += f"\n\n[Image attached: {image_description}]"
        
        # If there's no text content but there are images, add a prompt for the bot to respond
        if not content.strip() and has_images:
            content = "What do you see in this image?"
        
        # Enhance message with MCP capabilities if enabled
        if config.get('MCP_ENABLED', False):
            content = await enhance_message_with_mcp(content)
        
        message_history[key].append({"role": "user", "content": content})

        async with message.channel.typing():
            response = await self.generate_response(instructions, message_history[key])

        message_history[key].append({"role": "assistant", "content": response})

        await self.send_response(message, response)

    async def generate_response(self, instructions, history):
        # Use MCP-enhanced response generation if enabled
        if config.get('MCP_ENABLED', False):
            return await generate_response_with_mcp(instructions=instructions, history=history)
        else:
            return await generate_response(instructions=instructions, history=history)

    async def send_response(self, message, response):
        if response is not None:
            # Check if auto-TTS should be used
            should_tts, reason = smart_tts_detector.should_use_tts(
                message.content,
                response,
                message.channel.id
            )
            
            tts_file = None
            if should_tts and tts_manager.client and config.get('TTS_ENABLED', True):
                # Get default voice config
                voice_config = VOICE_PRESETS.get("default", VOICE_PRESETS["default"])
                is_wavenet = voice_config.get("is_wavenet", True)
                
                # Check if within usage limits
                can_use, limit_reason = usage_tracker.can_use_tts(response, is_wavenet)
                
                if can_use:
                    try:
                        # Generate TTS for the first chunk only (to keep it reasonable)
                        chunks = list(split_response(response))
                        first_chunk = chunks[0] if chunks else response
                        
                        # Generate TTS audio
                        audio_content = tts_manager.text_to_speech(
                            text=first_chunk[:500],  # Limit to 500 chars for auto-TTS
                            language_code=voice_config["language_code"],
                            voice_name=voice_config["voice_name"]
                        )
                        
                        if audio_content:
                            # Track usage
                            usage_tracker.add_usage(first_chunk[:500], is_wavenet)
                            
                            # Create Discord file
                            tts_file = discord.File(
                                io.BytesIO(audio_content),
                                filename="response.mp3"
                            )
                    except Exception as e:
                        print(f"Auto-TTS Error: {e}")
            
            # Send response chunks
            for idx, chunk in enumerate(split_response(response)):
                try:
                    # Attach TTS file to first message only
                    if idx == 0 and tts_file:
                        await message.reply(
                            chunk,
                            file=tts_file,
                            allowed_mentions=discord.AllowedMentions.none(),
                            suppress_embeds=True
                        )
                    else:
                        await message.reply(
                            chunk,
                            allowed_mentions=discord.AllowedMentions.none(),
                            suppress_embeds=True
                        )
                except Exception:
                    await message.channel.send("I apologize for any inconvenience caused. It seems that there was an error preventing the delivery of my message. Additionally, it appears that the message I was replying to has been deleted, which could be the reason for the issue. If you have any further questions or if there's anything else I can assist you with, please let me know and I'll be happy to help.")
        else:
            await message.reply("I apologize for any inconvenience caused. It seems that there was an error preventing the delivery of my message.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user and message.reference:
            replied_messages[message.reference.message_id] = message
            if len(replied_messages) > 5:
                oldest_message_id = min(replied_messages.keys())
                del replied_messages[oldest_message_id]

        if message.mentions:
            for mention in message.mentions:
                message.content = message.content.replace(f'<@{mention.id}>', f'{mention.display_name}')

        # Skip if it's a sticker, from a bot, or a reply to someone else's embed
        if message.stickers or message.author.bot or (message.reference and (message.reference.resolved.author != self.bot.user or message.reference.resolved.embeds)):
            return

        await self.process_message(message)

async def setup(bot):
    await bot.add_cog(OnMessage(bot))