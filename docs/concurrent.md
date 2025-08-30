# Concurrent Multi-Agent MCP Server

## Overview

The Concurrent Multi-Agent MCP server enables LM Studio models to query multiple models simultaneously with true async operations and connection pooling. This is the most powerful MCP server for parallel model execution.

## Features

- **Concurrent Queries**: Query up to 10 models at once
- **Connection Pooling**: Reuse HTTP connections for efficiency
- **Async Operations**: True async/await pattern implementation
- **Auto-retry Logic**: Automatic retry on transient failures
- **Performance**: 1.18x faster than sequential execution

## Installation

### One-Click Install
[**🚀 Install Now**](../installers/concurrent.html)

### Manual Installation
Add to `~/.lmstudio/mcp.json`:

```json
{
  "mcpServers": {
    "lmstudio-concurrent": {
      "command": "python3",
      "args": ["/path/to/lmstudio_bridge.py"],
      "env": {
        "LMSTUDIO_API_BASE": "http://localhost:1234/v1"
      }
    }
  }
}
```

## Available Functions

### health_check()
Check if LM Studio API is accessible.

```python
result = await health_check()
# Returns: "LM Studio API is running"
```

### list_models()
List all available models in LM Studio.

```python
models = await list_models()
# Returns formatted list of available models
```

### get_current_model()
Get the currently loaded model.

```python
current = await get_current_model()
# Returns: "qwen/qwen2.5-coder-14b"
```

### chat_completion()
Query a specific model.

```python
response = await chat_completion(
    prompt="Explain quantum computing",
    model="qwen/qwen2.5-coder-14b",
    temperature=0.7,
    max_tokens=1024
)
```

### multi_agent_query()
Query multiple models concurrently.

```python
results = await multi_agent_query(
    prompt="Write a sorting algorithm",
    models=[
        "qwen/qwen2.5-coder-14b",
        "mistralai/codestral-22b"
    ],
    temperature=0.7,
    max_tokens=1024
)
```

## Configuration

### Environment Variables

- `LMSTUDIO_API_BASE`: LM Studio API endpoint (default: `http://localhost:1234/v1`)
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests (default: 10)
- `CONNECTION_TIMEOUT`: Connection timeout in seconds (default: 30)
- `READ_TIMEOUT`: Read timeout in seconds (default: 120)

### Network Configuration

If LM Studio is running on a different machine:

```bash
export LMSTUDIO_API_BASE="http://192.168.1.100:1234/v1"
```

## Performance Benchmarks

| Configuration | Response Time | Throughput | VRAM |
|--------------|---------------|------------|------|
| 1x 14B Model | 2.3s | 26 tok/s | 8.5GB |
| 2x 14B Concurrent | 2.4s | 52 tok/s | 17GB |
| 4x 14B Concurrent | 2.8s | 95 tok/s | 33GB |

## Use Cases

### Comparing Model Responses
```python
# Get perspectives from different models
results = await multi_agent_query(
    prompt="What are the implications of AGI?",
    models=["qwen/qwen2.5-coder-14b", "mistralai/codestral-22b"]
)
```

### Ensemble Decision Making
```python
# Use multiple models for critical decisions
results = await multi_agent_query(
    prompt="Should we deploy this code to production?",
    models=["model1", "model2", "model3"]
)
# Aggregate responses for consensus
```

### Specialized Task Routing
```python
# Route to best model for task
if "code" in prompt:
    model = "qwen/qwen2.5-coder-14b"
elif "creative" in prompt:
    model = "mistralai/codestral-22b"
    
response = await chat_completion(prompt, model=model)
```

## Troubleshooting

### Connection Refused
- Ensure LM Studio is running
- Check API server is enabled in LM Studio settings
- Verify IP address and port

### Timeout Errors
- Increase timeout values in environment variables
- Check model loading status in LM Studio
- Ensure sufficient VRAM available

### Model Not Found
- Verify model is loaded in LM Studio
- Use `list_models()` to see available models
- Check model ID spelling

## Requirements

- Python 3.8+
- aiohttp
- mcp[cli]
- LM Studio v0.3.0+

## License

MIT License - See LICENSE file for details.