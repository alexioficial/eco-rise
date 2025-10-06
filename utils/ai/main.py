from os import getenv
from typing import List, Dict, Optional
from enum import Enum
import logging

from ddgs import DDGS
from dotenv import load_dotenv
from google import genai
from google.genai import types


# Basic logging for diagnostics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load env and init Gemini client
load_dotenv()
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in your environment/.env. Please set it to use Gemini."
    )

client = genai.Client(api_key=GEMINI_API_KEY)


class Tool(Enum):
    """Enumeration of available tools for Gemini."""

    SEARCH_INTERNET = {
        "function_declarations": [
            {
                "name": "search_internet",
                "description": "Search for information on the internet using DuckDuckGo. Returns relevant results with titles, URLs and snippets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find information on the internet",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            }
        ]
    }


def search_internet(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Implementation of internet search using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in results
            ]
    except Exception as e:
        logger.error(f"Error searching internet: {e}")
        return []


def prompt(
    prompt_param: str,
    files: Optional[List[str]] = None,
    tools: Optional[str] = None,
    system_prompt: Optional[str] = None,
):
    """
    Generate a response using Gemini with optional file uploads and tools.

    Args:
        prompt: The user prompt/query
        files: List of file paths to upload to the client
        tools: Tool configuration (str or callable)
        system_prompt: System instructions for the model

    Returns:
        The generated response from Gemini
    """
    # Upload files if provided
    uploaded_files = []
    if files:
        for file_path in files:
            try:
                uploaded_file = client.files.upload(file=file_path)
                uploaded_files.append(uploaded_file)
                logger.info(f"Uploaded file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")

    # Prepare the content parts
    content_parts = []

    # Add uploaded files to content
    for uploaded_file in uploaded_files:
        content_parts.append(uploaded_file)

    # Add the text prompt
    content_parts.append(prompt_param)

    # Prepare generation config
    config_params = {}

    if system_prompt:
        config_params["system_instruction"] = system_prompt

    # Add tools if provided
    if tools:
        if isinstance(tools, dict):
            # Tools is a dict with function_declarations
            tool_obj = types.Tool(**tools)
            config_params["tools"] = [tool_obj]
        elif callable(tools):
            config_params["tools"] = [tools]
        else:
            config_params["tools"] = tools

    # Create config object
    config = types.GenerateContentConfig(**config_params) if config_params else None

    # Generate response
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=content_parts, config=config
        )
        
        # Check if response contains function calls
        function_calls = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)
        
        # If there are function calls, execute them
        if function_calls:
            logger.info(f"Detected {len(function_calls)} function call(s)")
            
            # Add model's response with function calls to conversation
            content_parts.append(response.candidates[0].content)
            
            # Execute each function call and create response parts
            for function_call in function_calls:
                logger.info(f"Executing function: {function_call.name}")
                
                if function_call.name == "search_internet":
                    query = function_call.args.get("query", "")
                    max_results = function_call.args.get("max_results", 5)
                    function_result = search_internet(query, max_results)
                    
                    # Create function response
                    function_response_part = types.Part(
                        function_response=types.FunctionResponse(
                            name=function_call.name,
                            response={"result": function_result}
                        )
                    )
                    content_parts.append(function_response_part)
            
            # Get final response from model with function results
            final_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=content_parts,
                config=config
            )
            
            # Debug logging
            logger.info(f"Final response text: {final_response.text}")
            logger.info(f"Final response candidates: {len(final_response.candidates) if final_response.candidates else 0}")
            
            if final_response.text:
                return final_response.text
            
            # If still no text, try to extract from parts
            if final_response.candidates and final_response.candidates[0].content.parts:
                text_parts = []
                for part in final_response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                if text_parts:
                    return ''.join(text_parts)
            
            return "Could not generate a response"
        
        # If no function calls, return text directly
        return response.text if response.text else "Could not generate a response"
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise
