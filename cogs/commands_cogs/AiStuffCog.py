import discord
from discord.ext import commands

from bot_utilities.ai_utils import analyze_image


class AiStuffCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot





    @commands.hybrid_command(name="analyze-image", description="Analyze an image by URL or attachment")
    @discord.app_commands.describe(url="URL of the image to analyze")
    async def analyze_image_command(self, ctx, url: str = None):
        await ctx.defer()
        
        image_url = None
        
        # Check if there's an attachment
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    image_url = attachment.url
                    break
        
        # Use provided URL if no attachment
        if not image_url and url:
            image_url = url
        
        if not image_url:
            await ctx.send("❌ Please provide an image URL or attach an image to analyze!")
            return
        
        try:
            analysis = await analyze_image(image_url)
            
            embed = discord.Embed(
                title="🔍 Image Analysis",
                description=analysis,
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=image_url)
            embed.set_footer(text=f"Analyzed by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error analyzing image: {str(e)}")

    @commands.hybrid_command(name="mcp-tools", description="Show available MCP (Model Context Protocol) tools")
    async def mcp_tools_command(self, ctx):
        """Display available MCP tools and capabilities"""
        await ctx.defer()
        
        try:
            from bot_utilities.mcp_utils import mcp_client
            from bot_utilities.config_loader import config
            
            # Initialize MCP if not already done
            if not mcp_client.initialized:
                await mcp_client.initialize()
            
            embed = discord.Embed(
                title="🔧 Model Context Protocol (MCP) Tools",
                description="Available external system integrations",
                color=discord.Color.green() if config.get('MCP_ENABLED', False) else discord.Color.red()
            )
            
            if not config.get('MCP_ENABLED', False):
                embed.add_field(
                    name="❌ MCP Disabled",
                    value="Enable MCP in config.yml to access external tools",
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ MCP Status",
                    value=f"Enabled with {len(mcp_client.available_tools)} tools",
                    inline=False
                )
                
                # Group tools by category
                tool_categories = {
                    "📁 Filesystem": ["read_file_mcp"],
                    "🌐 Web Search": ["web_search_mcp"],
                    "💻 Code Analysis": ["analyze_code_mcp"],
                    "🖥️ System Info": ["get_system_info_mcp"]
                }
                
                for category, tool_names in tool_categories.items():
                    available_tools = []
                    for tool in mcp_client.available_tools:
                        if tool["function"]["name"] in tool_names:
                            available_tools.append(f"• `{tool['function']['name']}`")
                    
                    if available_tools:
                        embed.add_field(
                            name=category,
                            value="\n".join(available_tools),
                            inline=True
                        )
                
                embed.add_field(
                    name="💡 Usage",
                    value="MCP tools are automatically available when chatting with the bot. Just ask for file contents, web searches, code analysis, or system information!",
                    inline=False
                )
            
            embed.set_footer(text=f"MCP enables AI to connect with external systems securely")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error displaying MCP tools: {str(e)}")

    @commands.hybrid_command(name="mcp-test", description="Test MCP functionality with a simple tool")
    @discord.app_commands.describe(tool="Tool to test", query="Query or parameter for the tool")
    async def mcp_test_command(self, ctx, tool: str = "web_search_mcp", query: str = "Discord bot development"):
        """Test MCP tool functionality"""
        await ctx.defer()
        
        try:
            from bot_utilities.mcp_utils import mcp_client
            from bot_utilities.config_loader import config
            
            if not config.get('MCP_ENABLED', False):
                await ctx.send("❌ MCP is disabled. Enable it in config.yml first.")
                return
            
            # Initialize MCP if not already done
            if not mcp_client.initialized:
                await mcp_client.initialize()
            
            # Test the specified tool
            if tool == "web_search_mcp":
                result = await mcp_client.execute_tool("web_search_mcp", {"query": query, "max_results": 3})
            elif tool == "get_system_info_mcp":
                result = await mcp_client.execute_tool("get_system_info_mcp", {"info_type": "cpu"})
            elif tool == "analyze_code_mcp":
                sample_code = "def hello_world():\n    print('Hello, World!')\n    return True"
                result = await mcp_client.execute_tool("analyze_code_mcp", {"code": sample_code, "language": "python"})
            else:
                result = f"Unknown tool: {tool}. Available tools: web_search_mcp, get_system_info_mcp, analyze_code_mcp"
            
            # Create response embed
            embed = discord.Embed(
                title=f"🧪 MCP Tool Test: {tool}",
                description=f"Query: `{query}`",
                color=discord.Color.blue()
            )
            
            # Truncate result if too long
            if len(result) > 1000:
                result = result[:1000] + "...\n\n*[Result truncated]*"
            
            embed.add_field(
                name="📋 Result",
                value=f"```\n{result}\n```",
                inline=False
            )
            
            embed.set_footer(text=f"Test completed by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error testing MCP tool: {str(e)}")




async def setup(bot):
    await bot.add_cog(AiStuffCog(bot))
