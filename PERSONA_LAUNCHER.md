# 🤖 Bot Persona Launcher

This directory contains launcher scripts that allow you to choose which persona/instruction your Discord AI bot will use when starting up.

## 🎭 Available Personas

Your bot currently has these personas available in the `instructions/` folder:

1. **Albert_Einstein** - Act as the famous theoretical physicist
2. **Albert_Einstein_2025** - Modern version of Einstein persona  
3. **assist** - Default helpful assistant (original)
4. **ivan** - Custom persona
5. **luna** - Custom persona

## 🚀 How to Use

### Method 1: PowerShell Launcher (Recommended for Windows)
```powershell
.\launch_bot.ps1
```

### Method 2: Batch File Launcher (Windows Alternative)
```cmd
launch_bot.bat
```

### Method 3: Python Launcher (Cross-platform)
```cmd
python launch_bot.py
```

## 📋 What the Launcher Does

1. **Shows Available Personas** - Lists all instruction files with descriptions
2. **Displays Current Setting** - Shows which persona is currently active
3. **Lets You Choose** - Interactive selection of persona (1-5)
4. **Updates Config** - Automatically updates `config.yml` with your choice
5. **Starts Bot** - Optionally launches the bot immediately

## 🎯 Example Session

```
🤖 DISCORD AI BOT LAUNCHER
========================================
🎯 Current persona: assist

🎭 AVAILABLE BOT PERSONAS  
============================================================
 1. Albert_Einstein
    📝 From now on, you will act as Albert Einstein.

 2. Albert_Einstein_2025  
    📝 Modern version of Einstein with 2025 knowledge

 3. assist
    📝 I am a helpful AI assistant

 4. ivan
    📝 Custom persona for specific use case
    
 5. luna
    📝 Another custom persona

Please choose a persona (1-5) or press Enter to keep current (assist): 1
✅ Selected persona: Albert_Einstein

🔄 Updating config to use persona: Albert_Einstein
✅ Config updated successfully!

🚀 Ready to start bot with persona: Albert_Einstein
📝 Description: From now on, you will act as Albert Einstein.

Start the bot now? (Y/n): y

🤖 Starting Discord AI Bot...
========================================
```

## ⚙️ Manual Configuration

You can also manually edit `config.yml` and change this line:
```yaml
DEFAULT_INSTRUCTION: Albert_Einstein  # Change this to any persona name
```

## 💭 Adding New Personas

1. Create a new `.txt` file in the `instructions/` folder
2. Write your persona instructions inside
3. The filename (without .txt) becomes the persona name
4. Restart the launcher to see your new persona

## 🛠️ Troubleshooting

- **PowerShell execution policy error**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Python launcher import error**: Use the batch or PowerShell version instead
- **Config not updating**: Make sure `config.yml` exists and is writable

---

Now you can easily switch between different bot personalities! 🎭