# Discord AI Chatbot 
#### An Intelligent Discord AI Assistant with Personality!

Created and maintained by **Tommy** - A powerful Discord bot that brings AI conversation to your server with multiple personalities and advanced features.

## Features

- **Multiple AI Personalities**: Choose from Albert Einstein, Luna, Ivan, or create your own custom personas
- **Smart Response System**: Priority-based message handling prevents duplicate responses
- **Interactive Launcher**: Easy persona selection with PowerShell/Batch launchers
- **Multi-language Support**: 16+ languages supported including English, Vietnamese, Chinese, and more
- **Image Analysis**: Advanced image recognition and analysis capabilities
- **Context Awareness**: Maintains conversation history for coherent discussions
- **Hybrid Commands**: Both slash commands and natural language processing
- **Secure Configuration**: Environment variables for API keys and tokens
- **MCP Integration**: Model Context Protocol support for extended capabilities
- **Channel Management**: Per-channel activation/deactivation controls

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Discord Bot Token
- Groq API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Discord-AI-Chatbot
   cd Discord-AI-Chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install DuckDuckGo Search (specific version)**
   
   Install version 5.3.1, which is a modern version that works correctly with this bot:
   ```bash
   python -m pip install duckduckgo-search==5.3.1
   ```

4. **Configure environment**
   - Rename `example.env` to `.env`
   - Add your Discord token and Groq API key:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   API_KEY=your_groq_api_key_here
   ```

5. **Launch with persona selection**
   ```powershell
   # Windows PowerShell (Recommended)
   .\launch_bot.ps1
   
   # Windows Command Prompt
   launch_bot.bat
   
   # Direct launch
   python main.py
   ```

## Configuration

### Language Support
Set your preferred language in `config.yml`:
```yaml
LANGUAGE: en  # English (default)
# Supported: en, vn, cn, fr, es, de, ru, ar, tr, pl, pt, ua
```

### Custom Personalities
1. Create a `.txt` file in the `instructions/` folder
2. Write your persona instructions
3. Update `config.yml`:
   ```yaml
   DEFAULT_INSTRUCTION: your_persona_name
   ```
4. Use the launcher or restart the bot

### 🔊 Text-to-Speech (TTS) Setup

This bot includes Google Cloud Text-to-Speech with **4 million free characters/month**!

#### Step 1: Create Google Cloud Account
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the **Text-to-Speech API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Cloud Text-to-Speech API"
   - Click "Enable"

#### Step 2: Create Service Account
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name it `discord-bot-tts` (or any name)
4. Grant role: **"Cloud Text-to-Speech User"**
5. Click "Done"

#### Step 3: Generate Credentials
1. Click on your new service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose **JSON** format
5. Download the JSON file

#### Step 4: Configure Bot

**For Local/PC:**
1. Save the JSON file in your project folder
2. Add to `.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your-credentials.json
   ```

**For Replit/Cloud:**
1. Open the JSON file in a text editor
2. Copy the entire JSON content
3. Add to Secrets :
   - **Key:** `GOOGLE_CLOUD_CREDENTIALS_JSON`
   - **Value:** Paste the entire JSON content (as one line)

#### Step 5: Test TTS
Run your bot and try:
```
/tts text:Hello World voice:default
/tts-voices
```

#### Available Voices
**WaveNet Voices (High Quality - 1M free characters/month):**

- `default` / `male` / `female` - English WaveNet voices
- `british` / `aussie` - English accents
- `french` / `german` / `spanish` / `japanese` / `korean` - International languages
- `standard` - Fallback standard voice (4M free characters/month)

**Usage Tracking:**
- Built-in usage tracker ensures you never exceed free tier
- Check usage with `/tts-usage` command
- Automatic monthly reset
- Warning alerts at 80% usage

**Free Tier Limits:**
- WaveNet voices: **1 million characters/month** (better quality)
- Standard voices: **4 million characters/month** (basic quality)

#### Intelligent Auto-TTS
The bot can automatically add voice messages to responses when appropriate!

**How to Enable:**
1. Use `/tts-auto` in any channel to toggle automatic TTS
2. The bot will intelligently detect when to generate speech

**Auto-TTS Activates When:**
- You ask questions (What, How, Why, When, Where, etc.)
- You use trigger words like "read", "speak", "tell me", "say", "explain"
- The response is conversational and friendly
- Response is concise (under 500 characters for voice quality)

**Auto-TTS Automatically Skips:**
- Code blocks or technical content with backticks
- Very long responses (keeps voice messages manageable)
- Lists, tables, or structured data
- Messages with anti-trigger words like "don't read", "no audio"

**Toggle Controls:**
- `/tts-auto` - Enable/disable for current channel
- Settings are per-channel (each channel has independent control)
- Uses the default voice configured (German Chirp 3 HD Alnilam)

#### TTS Commands
- `/tts text voice` - Generate speech with voice presets
- `/tts-voices` - List all available voices and view usage
- `/tts-usage` - Check detailed usage statistics
- `/tts-custom` - Advanced TTS with custom speed/pitch

### Advanced Settings
```yaml
# Core Configuration
MAX_HISTORY: 8              # Conversation memory length
SMART_MENTION: true         # Enhanced mention detection
ALLOW_DM: true             # Enable direct messages
INTERNET_ACCESS: true       # Web search capabilities
MCP_ENABLED: true          # Model Context Protocol features
```

## 📋 Commands

| Command | Description | Usage |
|---------|-------------|--------|
| `/help` | Display all available commands | `/help` |
| `/analyze-image` | Analyze uploaded images or URLs | `/analyze-image [url]` |
| `/tts` | Convert text to speech | `/tts text:Hello voice:default` |
| `/tts-voices` | List available TTS voice presets | `/tts-voices` |
| `/tts-usage` | Check TTS usage statistics | `/tts-usage` |
| `/tts-custom` | Custom TTS with speed/pitch control | `/tts-custom text:Hello language:en-US` |
| `/tts-auto` | Toggle automatic TTS for bot responses | `/tts-auto` |
| `/toggleactive` | Enable/disable bot in current channel | `/toggleactive` |
| `/mcp-tools` | Show available MCP tools | `/mcp-tools` |
| `/mcp-test` | Test MCP functionality | `/mcp-test` |

## Usage Examples

### Basic Conversation
```
@YourBot Hello! How are you today?
```

### Image Analysis
Upload an image and use:
```
/analyze-image
```

### Einstein Persona Example
When using Albert Einstein persona:
```
User: Can you explain relativity?
Einstein Bot: Ah, relativity! It's quite fascinating actually. Imagine you're on a train...
```

## Development Features

### Duplicate Response Prevention
- Priority-based trigger system prevents multiple responses
- Message tracking ensures single response per message
- Clean, non-repetitive conversation flow

### Smart Launcher System
- Interactive persona selection
- Automatic config updates
- Immediate bot launch capability

### MCP Integration
- File system access
- Web search capabilities
- Code analysis tools
- System information gathering

## Docker Support

### Using Docker Compose
1. Ensure you have your `.env` file configured
2. Run the container:
   ```bash
   docker-compose up --build
   ```

### Manual Docker Build
```bash
# Build the image
docker build -t discord-ai-chatbot .

# Run the container
docker run -d --env-file .env discord-ai-chatbot
```

## Free 24/7 Hosting on Replit

### Setup Guide (No Credit Card Required!)

#### Step 1: Import to Replit

1. **Go to [Replit.com](https://replit.com)** and sign up (free)
2. Click **"Create Repl"**
3. Select **"Import from GitHub"**
4. Paste your repository URL: `https://github.com/Dtn09/Discord-AI-Chatbot`
5. Click **"Import from GitHub"**

#### Step 2: Configure Secrets (Environment Variables)

1. In your Repl, click the **Lock icon** (Secrets) in the left sidebar
2. Add these secrets:
   - **Key:** `DISCORD_TOKEN` → **Value:** `your_discord_bot_token`
   - **Key:** `API_KEY` → **Value:** `your_groq_api_key`
3. Click **"Add secret"** for each

#### Step 3: Install Dependencies

Replit should auto-install from `requirements.txt`. If not, click **"Shell"** and run:
```bash
pip install -r requirements.txt
python -m pip install duckduckgo-search==5.3.1
```

#### Step 4: Run Your Bot

1. Click the big **"Run"** button at the top
2. Your bot should start and connect to Discord! 🎉
3. You'll see a web view showing "Bot is alive!"

#### Step 5: Keep Bot Online 24/7 with UptimeRobot

Replit free tier sleeps after inactivity. Use UptimeRobot to keep it awake:

1. **Copy your Repl URL** (from the webview, looks like `https://yourproject.yourname.repl.co`)
2. **Go to [UptimeRobot.com](https://uptimerobot.com)** and sign up (free)
3. Click **"Add New Monitor"**
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Discord AI Chatbot
   - **URL:** Your Repl URL
   - **Monitoring Interval:** 5 minutes
4. Click **"Create Monitor"**

Your bot will now stay online 24/7! 

---

### Troubleshooting

**Bot keeps sleeping:**
- Make sure UptimeRobot is pinging your Repl URL every 5 minutes
- Verify the URL is correct (should show "Bot is alive!")

**Bot won't start:**
- Check Secrets are set correctly (DISCORD_TOKEN, API_KEY)
- Look at the Console tab for error messages
- Make sure all dependencies installed

**Import errors:**
- Click "Shell" and run: `pip install -r requirements.txt`

---

### Alternative Free Hosting Options

<details>
<summary>Click to see other free options</summary>

#### Railway.app
- $5 free credit/month (~500 hours)
- GitHub integration
- One-click deploy

#### Glitch.com
- No credit card needed
- GitHub import
- Simple interface

#### Oracle Cloud Free Tier (Most Powerful)
- Always free (not trial)
- 2 VMs with 1GB RAM each
- Requires credit card for verification

</details>

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your setup and the issue

## Acknowledgments

- Thanks to the open-source community for inspiration and tools
- Groq for providing the AI API
- Discord.py developers for the excellent library

---

**Created with love by Tommy** 
