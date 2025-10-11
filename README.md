# Discord AI Chatbot 🤖
#### An Intelligent Discord AI Assistant with Personality!

Created and maintained by **Tommy** - A powerful Discord bot that brings AI conversation to your server with multiple personalities and advanced features.

## 🌟 Key Features

- **🎭 Multiple AI Personalities**: Choose from Albert Einstein, Luna, Ivan, or create your own custom personas
- **⚡ Smart Response System**: Priority-based message handling prevents duplicate responses
- **🔧 Interactive Launcher**: Easy persona selection with PowerShell/Batch launchers
- **🌐 Multi-language Support**: 16+ languages supported including English, Vietnamese, Chinese, and more
- **🔍 Image Analysis**: Advanced image recognition and analysis capabilities
- **🧠 Context Awareness**: Maintains conversation history for coherent discussions
- **⚙️ Hybrid Commands**: Both slash commands and natural language processing
- **🔒 Secure Configuration**: Environment variables for API keys and tokens
- **📊 MCP Integration**: Model Context Protocol support for extended capabilities
- **🎯 Channel Management**: Per-channel activation/deactivation controls

## 🚀 Quick Start

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

### 🎭 Available Personas

- **Albert Einstein** - The famous theoretical physicist persona
- **Albert Einstein 2025** - Modern casual Einstein with contemporary knowledge
- **Luna** - Caring and empathetic friend for meaningful conversations
- **Ivan** - Direct and concise responses, perfect for quick interactions
- **assist** - Default helpful assistant without specific personality

## 🛠️ Configuration

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
| `/toggleactive` | Enable/disable bot in current channel | `/toggleactive` |
| `/mcp-tools` | Show available MCP tools | `/mcp-tools` |
| `/mcp-test` | Test MCP functionality | `/mcp-test` |

## 🎮 Usage Examples

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

## � Development Features

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

## 🐳 Docker Support

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🛠️ Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your setup and the issue

## ⭐ Acknowledgments

- Thanks to the open-source community for inspiration and tools
- Groq for providing the AI API
- Discord.py developers for the excellent library

---

**Created with ❤️ by Tommy** | 
