#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import aiohttp
import asyncio
import json
import sys
from typing import List, Dict, Any, Optional

# Initialize FastMCP server
mcp = FastMCP("lmstudio-bridge")

# LM Studio settings - configurable via environment variable
import os
LMSTUDIO_API_BASE = os.getenv("LMSTUDIO_API_BASE", "http://192.168.50.136:1234/v1")
DEFAULT_MODEL = "default"  # Will be replaced with whatever model is currently loaded

# Global session for connection pooling
_session: Optional[aiohttp.ClientSession] = None

async def get_session() -> aiohttp.ClientSession:
    """Get or create aiohttp session with connection pooling"""
    global _session
    if _session is None or _session.closed:
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection limit
            limit_per_host=20,  # Per-host connection limit
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=300, connect=10)
        _session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
    return _session

def log_error(message: str):
    """Log error messages to stderr for debugging"""
    print(f"ERROR: {message}", file=sys.stderr)

def log_info(message: str):
    """Log informational messages to stderr for debugging"""
    print(f"INFO: {message}", file=sys.stderr)

@mcp.tool()
async def health_check() -> str:
    """Check if LM Studio API is accessible.
    
    Returns:
        A message indicating whether the LM Studio API is running.
    """
    try:
        session = await get_session()
        async with session.get(f"{LMSTUDIO_API_BASE}/models") as response:
            if response.status == 200:
                return "LM Studio API is running and accessible."
            else:
                return f"LM Studio API returned status code {response.status}."
    except Exception as e:
        return f"Error connecting to LM Studio API: {str(e)}"

@mcp.tool()
async def list_models() -> str:
    """List all available models in LM Studio.
    
    Returns:
        A formatted list of available models.
    """
    try:
        session = await get_session()
        async with session.get(f"{LMSTUDIO_API_BASE}/models") as response:
            if response.status != 200:
                return f"Failed to fetch models. Status code: {response.status}"
            
            data = await response.json()
            models = data.get("data", [])
            if not models:
                return "No models found in LM Studio."
            
            result = "Available models in LM Studio:\n\n"
            for model in models:
                result += f"- {model['id']}\n"
            
            return result
    except Exception as e:
        log_error(f"Error in list_models: {str(e)}")
        return f"Error listing models: {str(e)}"

@mcp.tool()
async def get_current_model() -> str:
    """Get the currently loaded model in LM Studio.
    
    Returns:
        The name of the currently loaded model.
    """
    try:
        session = await get_session()
        payload = {
            "messages": [{"role": "system", "content": "What model are you?"}],
            "temperature": 0.7,
            "max_tokens": 10
        }
        
        async with session.post(f"{LMSTUDIO_API_BASE}/chat/completions", json=payload) as response:
            if response.status != 200:
                return f"Failed to identify current model. Status code: {response.status}"
            
            data = await response.json()
            model_info = data.get("model", "Unknown")
            return f"Currently loaded model: {model_info}"
    except Exception as e:
        log_error(f"Error in get_current_model: {str(e)}")
        return f"Error identifying current model: {str(e)}"

@mcp.tool()
async def chat_completion(prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 1024, model: str = "") -> str:
    """Generate a completion from the current LM Studio model.
    
    Args:
        prompt: The user's prompt to send to the model
        system_prompt: Optional system instructions for the model
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        model: Optional specific model to use (e.g., "qwen/qwen2.5-coder-14b")
        
    Returns:
        The model's response to the prompt
    """
    try:
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        log_info(f"Sending async request to LM Studio with {len(messages)} messages, model: {model or 'default'}")
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add model specification if provided
        if model:
            payload["model"] = model
        
        session = await get_session()
        async with session.post(f"{LMSTUDIO_API_BASE}/chat/completions", json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                log_error(f"LM Studio API error: {response.status}")
                return f"Error: LM Studio returned status code {response.status}: {error_text[:200]}"
            
            response_json = await response.json()
            log_info(f"Received async response from LM Studio")
            
            # Extract the assistant's message
            choices = response_json.get("choices", [])
            if not choices:
                return "Error: No response generated"
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            
            if not content:
                return "Error: Empty response from model"
            
            return content
            
    except Exception as e:
        log_error(f"Error in chat_completion: {str(e)}")
        return f"Error generating completion: {str(e)}"

@mcp.tool()
async def multi_agent_query(prompt: str, models: List[str], system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """Query multiple models concurrently with the same prompt.
    
    Args:
        prompt: The user's prompt to send to all models
        models: List of model IDs to query (e.g., ["qwen/qwen2.5-coder-14b", "mistralai/devstral-small-2507"])
        system_prompt: Optional system instructions for all models
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        JSON string with results from all models
    """
    try:
        if not models:
            return json.dumps({"error": "No models specified"})
        
        log_info(f"Sending concurrent requests to {len(models)} models")
        
        # Create async tasks for true concurrent execution
        session = await get_session()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async def query_single_model(model: str) -> tuple:
            """Query a single model and return (model, result)"""
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                async with session.post(f"{LMSTUDIO_API_BASE}/chat/completions", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return model, {
                            "success": True,
                            "content": content,
                            "tokens": data.get("usage", {}).get("total_tokens", 0)
                        }
                    else:
                        error_text = await response.text()
                        return model, {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text[:200]}"
                        }
            except Exception as e:
                return model, {
                    "success": False,
                    "error": str(e)
                }
        
        # Execute all requests concurrently using asyncio.gather
        tasks = [query_single_model(model) for model in models]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        results = {}
        for task_result in task_results:
            if isinstance(task_result, Exception):
                results["unknown"] = {
                    "success": False,
                    "error": str(task_result)
                }
            else:
                model, result = task_result
                results[model] = result
        
        log_info(f"Completed concurrent requests, {len([r for r in results.values() if r.get('success')])} successful")
        return json.dumps(results, indent=2)
        
    except Exception as e:
        log_error(f"Error in multi_agent_query: {str(e)}")
        return json.dumps({"error": f"Multi-agent query failed: {str(e)}"})

async def cleanup_session():
    """Clean up the aiohttp session"""
    global _session
    if _session and not _session.closed:
        await _session.close()

def main():
    """Entry point for the package when installed via pip"""
    import atexit
    
    # Register cleanup function
    atexit.register(lambda: asyncio.run(cleanup_session()) if _session else None)
    
    log_info("Starting LM Studio Bridge MCP Server with async support")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # Initialize and run the server
    main()