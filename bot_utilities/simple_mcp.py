"""
Simplified MCP utilities that work with current Groq API limitations
"""
import json
import asyncio
import os
import platform
from typing import Dict, List, Any
from bot_utilities.config_loader import config
from duckduckgo_search import AsyncDDGS

class SimpleMCPClient:
    """Simplified MCP client that works without complex tool calling"""
    
    def __init__(self):
        self.enabled = config.get('MCP_ENABLED', False)
        print(f"🔧 SimpleMCP initialized - Enabled: {self.enabled}")
    
    async def process_message_with_mcp(self, user_message: str) -> str:
        """Process a user message and enhance it with MCP capabilities"""
        if not self.enabled:
            return user_message
        
        enhanced_content = user_message
        
        # Check for web search requests
        search_triggers = ["search for", "find information about", "look up", "google", "web search"]
        if any(trigger in user_message.lower() for trigger in search_triggers):
            # Extract search query
            query = await self._extract_search_query(user_message)
            if query:
                search_results = await self._web_search(query)
                enhanced_content += f"\n\n[MCP Web Search Results for '{query}':]:\n{search_results}"
        
        # Check for system info requests
        system_triggers = ["system info", "cpu usage", "memory usage", "disk space", "system specs", "computer specs"]
        if any(trigger in user_message.lower() for trigger in system_triggers):
            system_info = await self._get_system_info()
            enhanced_content += f"\n\n[MCP System Information]:\n{system_info}"
        
        # Check for code analysis requests
        code_triggers = ["analyze this code", "review this code", "check this code", "```"]
        if any(trigger in user_message.lower() for trigger in code_triggers):
            if "```" in user_message:
                code = await self._extract_code_from_message(user_message)
                if code:
                    analysis = await self._analyze_code(code)
                    enhanced_content += f"\n\n[MCP Code Analysis]:\n{analysis}"
        
        return enhanced_content
    
    async def _extract_search_query(self, message: str) -> str:
        """Extract search query from user message"""
        message_lower = message.lower()
        
        # Common patterns for extracting search queries
        patterns = [
            "search for ",
            "find information about ",
            "look up ",
            "google ",
            "web search "
        ]
        
        for pattern in patterns:
            if pattern in message_lower:
                start_idx = message_lower.find(pattern) + len(pattern)
                # Extract until end of sentence or message
                query = message[start_idx:].split('.')[0].split('?')[0].split('!')[0].strip()
                return query[:100]  # Limit query length
        
        # If no specific pattern, use the whole message as query
        return message[:100]
    
    async def _web_search(self, query: str) -> str:
        """Perform web search using DuckDuckGo"""
        try:
            print(f"🌐 MCP Web Search: {query}")
            results = await AsyncDDGS(proxy=None).text(query, max_results=3)
            
            if not results:
                return "No search results found."
            
            formatted_results = ""
            for i, result in enumerate(results[:3], 1):
                formatted_results += f"{i}. **{result['title']}**\n"
                formatted_results += f"   {result['body'][:150]}...\n"
                formatted_results += f"   Source: {result['href']}\n\n"
            
            return formatted_results
            
        except Exception as e:
            return f"Search error: {str(e)}"
    
    async def _get_system_info(self) -> str:
        """Get basic system information"""
        try:
            import psutil
            
            # Get basic system info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Use appropriate disk path for Windows
            try:
                disk = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
            except:
                disk = psutil.disk_usage('/')
            
            info = f"🖥️ **System Information:**\n"
            info += f"• CPU Usage: {cpu_percent}%\n"
            info += f"• Memory: {memory.percent}% used ({memory.available // (1024**3)} GB available)\n"
            info += f"• Disk: {(disk.used/disk.total)*100:.1f}% used ({disk.free // (1024**3)} GB free)\n"
            info += f"• Platform: {platform.system()} {platform.release()}\n"
            
            return info
            
        except ImportError as e:
            return f"System info requires 'psutil' package. Error: {e}"
        except Exception as e:
            return f"System info error: {str(e)}"
    
    async def _extract_code_from_message(self, message: str) -> str:
        """Extract code from message (looking for code blocks)"""
        if "```" in message:
            # Extract code between triple backticks
            parts = message.split("```")
            if len(parts) >= 3:
                # Get the code part (usually the second part)
                code = parts[1]
                # Remove language identifier if present
                lines = code.split('\n')
                if lines and not any(char in lines[0] for char in [' ', '(', ')', '{', '}', ';']):
                    # First line might be language identifier
                    code = '\n'.join(lines[1:])
                return code.strip()
        
        return ""
    
    async def _analyze_code(self, code: str) -> str:
        """Analyze code and provide insights"""
        try:
            lines = code.split('\n')
            non_empty_lines = [l for l in lines if l.strip()]
            
            analysis = f"💻 **Code Analysis:**\n"
            analysis += f"• Lines of code: {len(lines)}\n"
            analysis += f"• Non-empty lines: {len(non_empty_lines)}\n"
            
            # Detect language
            if any(keyword in code for keyword in ['def ', 'import ', 'print(']):
                analysis += f"• Language: Python\n"
            elif any(keyword in code for keyword in ['function ', 'const ', 'let ']):
                analysis += f"• Language: JavaScript\n"
            elif any(keyword in code for keyword in ['public class', 'private ', 'public ']):
                analysis += f"• Language: Java\n"
            else:
                analysis += f"• Language: Unknown\n"
            
            # Simple complexity analysis
            complexity_keywords = ['if', 'for', 'while', 'try', 'catch', 'switch']
            complexity_count = sum(code.lower().count(keyword) for keyword in complexity_keywords)
            analysis += f"• Complexity indicators: {complexity_count}\n"
            
            # Security check for Python
            if 'python' in analysis.lower():
                dangerous_funcs = ['eval', 'exec', 'open', '__import__']
                security_issues = [func for func in dangerous_funcs if func in code]
                if security_issues:
                    analysis += f"• ⚠️ Security concerns: {', '.join(security_issues)}\n"
            
            return analysis
            
        except Exception as e:
            return f"Code analysis error: {str(e)}"

# Global simple MCP client
simple_mcp = SimpleMCPClient()

async def enhance_message_with_mcp(user_message: str) -> str:
    """Enhance user message with MCP capabilities"""
    return await simple_mcp.process_message_with_mcp(user_message)