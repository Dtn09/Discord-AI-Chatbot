import aiohttp
import io
import time
import os
import random
import json
import base64
from bot_utilities.config_loader import load_current_language, config
from openai import AsyncOpenAI
from duckduckgo_search import AsyncDDGS
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

current_language = load_current_language()
internet_access = config['INTERNET_ACCESS']

client = AsyncOpenAI(
    base_url=config['API_BASE_URL'],
    api_key=os.environ.get("API_KEY"),
)

async def analyze_image(image_url):
    """Analyze an image using Llama 4 Maverick multimodal vision model"""
    # Check if vision is enabled in config
    if not config.get('VISION_ENABLED', True):
        return "Image analysis is currently disabled in the bot configuration."
    
    try:
        print(f"\033[1;36m(Vision) Analyzing image with Llama 4 Maverick: {image_url}\033[0m")
        
        # Download the image
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Convert to base64 for the API
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    # Get vision model from config
                    vision_model = config.get('VISION_MODEL', 'meta-llama/llama-4-maverick-17b-128e-instruct')
                    
                    # List of vision models to try (Llama 4 Maverick first, then fallbacks)
                    vision_models = [
                        vision_model,
                        "meta-llama/llama-4-maverick-17b-128e-instruct",  # Primary multimodal model
                        "gpt-4-vision-preview",        # OpenAI fallback
                        "gpt-4o",                      # OpenAI fallback
                        "gpt-4o-mini"                  # OpenAI fallback
                    ]
                    
                    # Remove duplicates while preserving order
                    vision_models = list(dict.fromkeys(vision_models))
                    
                    for model in vision_models:
                        try:
                            print(f"\033[1;33m(Vision) Trying model: {model}\033[0m")
                            
                            # Create vision request for Llama 4 Maverick multimodal model
                            # Use direct URL for Llama 4 Maverick (base64 not supported)
                            if model == "meta-llama/llama-4-maverick-17b-128e-instruct":
                                vision_response = await client.chat.completions.create(
                                    model=model,
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Please analyze this image in detail. Describe what you see, including objects, people, colors, text, settings, emotions, and any other relevant visual elements. Be comprehensive and descriptive."
                                                },
                                                {
                                                    "type": "image_url",
                                                    "image_url": {
                                                        "url": image_url  # Use direct URL for Maverick
                                                    }
                                                }
                                            ]
                                        }
                                    ],
                                    max_tokens=500,
                                    temperature=0.7
                                )
                            else:
                                # Use base64 for other models (OpenAI, etc.)
                                vision_response = await client.chat.completions.create(
                                    model=model,
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Please analyze this image in detail. Describe what you see, including objects, people, colors, text, settings, emotions, and any other relevant visual elements. Be comprehensive and descriptive."
                                                },
                                                {
                                                    "type": "image_url",
                                                    "image_url": {
                                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                                    }
                                                }
                                            ]
                                        }
                                    ],
                                    max_tokens=500,
                                    temperature=0.7
                                )
                            
                            result = vision_response.choices[0].message.content
                            print(f"\033[1;32m(Vision) Successfully analyzed image with {model}\033[0m")
                            return result
                            
                        except Exception as model_error:
                            print(f"\033[1;31m(Vision) Model {model} failed: {str(model_error)[:100]}...\033[0m")
                            continue
                    
                    # If all vision models fail, provide fallback with image metadata
                    print(f"\033[1;33m(Vision) All vision models failed, providing metadata fallback\033[0m")
                    try:
                        from PIL import Image
                        import io
                        
                        img = Image.open(io.BytesIO(image_data))
                        width, height = img.size
                        format_name = img.format or "Unknown"
                        file_size = len(image_data)
                        size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
                        
                        fallback_response = f"I can see an image has been shared! While I'm having trouble with detailed visual analysis right now, here's what I can tell you:\n\n"
                        fallback_response += f"📐 **Dimensions:** {width} × {height} pixels\n"
                        fallback_response += f"📁 **Format:** {format_name}\n"
                        fallback_response += f"📦 **Size:** {size_str}\n\n"
                        fallback_response += "Feel free to describe what's in the image and I'll be happy to discuss it with you! 🖼️"
                        
                        return fallback_response
                        
                    except Exception:
                        return "I can see there's an image attached, but I'm having trouble analyzing it right now. Please describe what's in the image and I'll be happy to discuss it with you!"
                        
                else:
                    return "I couldn't access the image. Please make sure it's a valid image URL."
                    
    except Exception as e:
        print(f"\033[1;31m(Vision) Error analyzing image: {e}\033[0m")
        return "I encountered an error while trying to analyze the image. However, I can see that an image was shared in the chat. Please describe what's in it and I'll discuss it with you!"

async def generate_response(instructions, history):
    messages = [
            {"role": "system", "name": "instructions", "content": instructions},
            *history,
        ]

    tools = [
        {
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
        }
    ]
    response = await client.chat.completions.create(
        model=config['MODEL_ID'],
        messages=messages,        
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "searchtool": duckduckgotool,
        }
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = await function_to_call(
                query=function_args.get("query")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = await client.chat.completions.create(
            model=config['MODEL_ID'],
            messages=messages
        ) 
        return second_response.choices[0].message.content
    return response_message.content

async def duckduckgotool(query) -> str:
    if not config['INTERNET_ACCESS']:
        return "internet access has been disabled by user"
    blob = ''
    results = await AsyncDDGS(proxy=None).text(query, max_results=6)
    try:
        for index, result in enumerate(results[:6]):  # Limiting to 6 results
            blob += f'[{index}] Title : {result["title"]}\nSnippet : {result["body"]}\n\n\n Provide a cohesive response base on provided Search results'
    except Exception as e:
        blob += f"Search error: {e}\n"
    return blob


