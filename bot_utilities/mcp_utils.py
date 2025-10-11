"""
Model Context Protocol (MCP) utilities for Discord AI Chatbot
Provides standardized interface for AI to interact with external systems
"""
import json
import aiohttp
import asyncio
import os
from typing import Dict, List, Any, Optional
from bot_utilities.config_loader import config
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    """Model Context Protocol client for managing external tool integrations"""
    
    def __init__(self):
        self.enabled = config.get('MCP_ENABLED', False)
        self.servers = config.get('MCP_SERVERS', [])
        self.client = AsyncOpenAI(
            base_url=config['API_BASE_URL'],
            api_key=os.environ.get("API_KEY"),
        )
        self.available_tools = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize MCP servers and discover available tools"""
        if not self.enabled:
            print("🔧 MCP is disabled in configuration")
            return
        
        print("🚀 Initializing Model Context Protocol (MCP)...")
        
        # Initialize available tools
        await self._discover_tools()
        self.initialized = True
        
        print(f"✅ MCP initialized with {len(self.available_tools)} tools available")
    
    async def _discover_tools(self):
        """Discover available MCP tools from configured servers"""
        self.available_tools = [
            # Filesystem tools
            {
                "type": "function",
                "function": {
                    "name": "read_file_mcp",
                    "description": "Read contents of a file using MCP filesystem access",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            # Web search tools
            {
                "type": "function", 
                "function": {
                    "name": "web_search_mcp",
                    "description": "Search the web for information using MCP web search capabilities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            # Code analysis tools
            {
                "type": "function",
                "function": {
                    "name": "analyze_code_mcp",
                    "description": "Analyze code structure and provide insights using MCP",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to analyze"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language"
                            }
                        },
                        "required": ["code"]
                    }
                }
            },
            # System information tools
            {
                "type": "function",
                "function": {
                    "name": "get_system_info_mcp",
                    "description": "Get system information using MCP system access",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "info_type": {
                                "type": "string",
                                "description": "Type of system info: 'memory', 'disk', 'cpu', 'network'",
                                "enum": ["memory", "disk", "cpu", "network", "all"]
                            }
                        },
                        "required": ["info_type"]
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute an MCP tool with given parameters"""
        try:
            print(f"🔧 Executing MCP tool: {tool_name} with params: {parameters}")
            
            if tool_name == "read_file_mcp":
                return await self._read_file_mcp(parameters.get("file_path"))
            elif tool_name == "web_search_mcp":
                return await self._web_search_mcp(
                    parameters.get("query"), 
                    parameters.get("max_results", 5)
                )
            elif tool_name == "analyze_code_mcp":
                return await self._analyze_code_mcp(
                    parameters.get("code"),
                    parameters.get("language", "unknown")
                )
            elif tool_name == "get_system_info_mcp":
                return await self._get_system_info_mcp(parameters.get("info_type"))
            else:
                return f"Unknown MCP tool: {tool_name}"
                
        except Exception as e:
            error_msg = f"Error executing MCP tool {tool_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    async def _read_file_mcp(self, file_path: str) -> str:
        """MCP filesystem access to read files"""
        try:
            # Security check - only allow certain directories
            allowed_dirs = [".", "./instructions", "./lang", "./cogs"]
            if not any(file_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
                return "Access denied: File path not in allowed directories"
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"File content from {file_path}:\n\n{content}"
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    async def _web_search_mcp(self, query: str, max_results: int = 5) -> str:
        """Enhanced web search using MCP"""
        try:
            from duckduckgo_search import AsyncDDGS
            
            results = await AsyncDDGS(proxy=None).text(query, max_results=max_results)
            
            if not results:
                return f"No search results found for: {query}"
            
            formatted_results = f"Web search results for '{query}':\n\n"
            for i, result in enumerate(results[:max_results], 1):
                formatted_results += f"{i}. **{result['title']}**\n"
                formatted_results += f"   URL: {result['href']}\n"
                formatted_results += f"   Summary: {result['body'][:200]}...\n\n"
            
            return formatted_results
            
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    async def _analyze_code_mcp(self, code: str, language: str) -> str:
        """Analyze code using MCP code analysis tools"""
        try:
            analysis = f"Code analysis for {language}:\n\n"
            
            # Basic code metrics
            lines = code.split('\n')
            analysis += f"📊 **Metrics:**\n"
            analysis += f"• Lines of code: {len(lines)}\n"
            analysis += f"• Non-empty lines: {len([l for l in lines if l.strip()])}\n"
            analysis += f"• Language: {language}\n\n"
            
            # Simple complexity analysis
            complexity_indicators = ['if', 'for', 'while', 'try', 'except', 'def', 'class']
            complexity_count = sum(code.lower().count(indicator) for indicator in complexity_indicators)
            analysis += f"🔍 **Complexity Indicators:** {complexity_count}\n\n"
            
            # Security checks for Python
            if language.lower() in ['python', 'py']:
                security_issues = []
                dangerous_funcs = ['eval', 'exec', 'open', 'input', '__import__']
                for func in dangerous_funcs:
                    if func in code:
                        security_issues.append(f"Found potentially dangerous function: {func}")
                
                if security_issues:
                    analysis += f"⚠️ **Security Considerations:**\n"
                    for issue in security_issues:
                        analysis += f"• {issue}\n"
                    analysis += "\n"
            
            analysis += "✅ **Analysis complete**"
            return analysis
            
        except Exception as e:
            return f"Code analysis error: {str(e)}"
    
    async def _get_system_info_mcp(self, info_type: str) -> str:
        """Get system information using MCP"""
        try:
            import psutil
            import platform
            
            info = f"System Information ({info_type}):\n\n"
            
            if info_type in ["cpu", "all"]:
                info += f"🖥️ **CPU:**\n"
                info += f"• CPU Count: {psutil.cpu_count()}\n"
                info += f"• CPU Usage: {psutil.cpu_percent()}%\n\n"
            
            if info_type in ["memory", "all"]:
                memory = psutil.virtual_memory()
                info += f"💾 **Memory:**\n"
                info += f"• Total: {memory.total // (1024**3)} GB\n"
                info += f"• Available: {memory.available // (1024**3)} GB\n"
                info += f"• Usage: {memory.percent}%\n\n"
            
            if info_type in ["disk", "all"]:
                disk = psutil.disk_usage('/')
                info += f"💿 **Disk:**\n"
                info += f"• Total: {disk.total // (1024**3)} GB\n"
                info += f"• Free: {disk.free // (1024**3)} GB\n"
                info += f"• Usage: {(disk.used/disk.total)*100:.1f}%\n\n"
            
            if info_type in ["network", "all"]:
                info += f"🌐 **Platform:**\n"
                info += f"• OS: {platform.system()}\n"
                info += f"• Version: {platform.version()}\n"
                info += f"• Architecture: {platform.architecture()[0]}\n\n"
            
            return info
            
        except ImportError:
            return "System info requires 'psutil' package. Install with: pip install psutil"
        except Exception as e:
            return f"System info error: {str(e)}"

# Global MCP client instance
mcp_client = MCPClient()

async def generate_response_with_mcp(instructions: str, history: List[Dict[str, Any]]) -> str:
    """Generate response using MCP-enhanced capabilities"""
    
    # Initialize MCP if not already done
    if not mcp_client.initialized:
        await mcp_client.initialize()
    
    if not mcp_client.enabled:
        # Fallback to regular generation without MCP
        from bot_utilities.ai_utils import generate_response
        return await generate_response(instructions, history)
    
    # Prepare messages with MCP tools available
    messages = [
        {"role": "system", "name": "instructions", "content": instructions},
        *history,
    ]
    
    # Combine MCP tools with existing tools
    all_tools = mcp_client.available_tools.copy()
    
    # Add existing search tool
    all_tools.append({
        "type": "function",
        "function": {
            "name": "searchtool",
            "description": "Searches the internet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query for search engine",
                    }
                },
                "required": ["query"],
            },
        },
    })
    
    try:
        # Use MCP-compatible model
        model = config.get('MODEL_ID', 'meta-llama/llama-4-maverick-17b-128e-instruct')
        
        # Use standard completion without tools for Groq compatibility
        # Groq models don't support tool calling properly, so we use simple approach
        response = await mcp_client.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        
        response_message = response.choices[0].message
        return response_message.content
        
    except Exception as e:
        print(f"❌ MCP generation error: {e}")
        # Fallback to regular generation
        from bot_utilities.ai_utils import generate_response
        return await generate_response(instructions, history)