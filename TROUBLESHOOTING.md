# 🔧 Bot Troubleshooting Guide

## Common Issues After Deployment

### 1. Bot Not Responding
**Problem:** Bot is online but doesn't respond to messages
**Solutions:**
- Check if bot has proper permissions in the server
- Verify the bot is added to channels where you're testing
- Make sure `INTERNET_ACCESS: true` in config.yml
- Test with direct mention: `@YourBot hello`

### 2. Web Search Not Working  
**Problem:** Bot says "internet access has been disabled"
**Solution:** 
- Fixed logic error in `duckduckgotool` function
- Ensure `INTERNET_ACCESS: true` in config.yml

### 3. API/Model Issues
**Problem:** API errors or model not found
**Solutions:**
- Updated MODEL_ID to `llama-3.1-8b-instant` (Groq compatible)
- Verify your GROQ_API_KEY is set correctly
- Check API quota/limits on Groq console

### 4. MCP Functions Not Working
**Problem:** MCP tools causing errors
**Solutions:**
- Simplified MCP implementation for Groq compatibility
- MCP now works without complex tool calling
- System info, web search, and code analysis work through simple triggers

### 5. Replit-Specific Issues
**Problem:** Bot works locally but not on Replit
**Solutions:**
- Use Secrets instead of .env file on Replit
- Set `DISCORD_TOKEN` and `API_KEY` in Replit Secrets
- Make sure all requirements are installed
- Check Replit console for error messages

## Quick Fixes Applied:
✅ Fixed internet access logic error
✅ Updated model to Groq-compatible version
✅ Simplified MCP for better compatibility  
✅ Maintained all core functionality

## Test Commands:
- `@YourBot hello` - Basic response
- `@YourBot search for python tutorials` - Web search
- `@YourBot system info` - System information
- Upload an image - Image analysis