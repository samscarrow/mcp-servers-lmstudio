# 🚀 LM Studio MCP Servers

One-click installers for Model Context Protocol (MCP) servers that enable LM Studio models to collaborate, query each other, and work together through async operations.

## 🎯 Quick Install

Click any button below to install MCP servers directly into LM Studio:

### Production Servers

| Server | Description | Install | Docs |
|--------|-------------|---------|------|
| **Concurrent Multi-Agent** | Query multiple models simultaneously with connection pooling | [**🚀 Install**](https://samscarrow.github.io/mcp-servers-lmstudio/installers/concurrent.html) | [📖 Docs](docs/concurrent.md) |
| **Code Reviewer** | Automated code review using 30B+ models | [**🚀 Install**](https://samscarrow.github.io/mcp-servers-lmstudio/installers/code-reviewer.html) | [📖 Docs](docs/code-reviewer.md) |
| **Oracle Database** | Connect LM Studio to Oracle databases | [**🚀 Install**](https://samscarrow.github.io/mcp-servers-lmstudio/installers/oracle.html) | [📖 Docs](docs/oracle.md) |
| **MongoDB** | MongoDB operations from LM Studio | [**🚀 Install**](https://samscarrow.github.io/mcp-servers-lmstudio/installers/mongodb.html) | [📖 Docs](docs/mongodb.md) |

### Experimental Servers

| Server | Description | Install | Status |
|--------|-------------|---------|--------|
| **Agent Orchestrator** | Coordinate multiple specialized agents | [**🧪 Install**](https://samscarrow.github.io/mcp-servers-lmstudio/installers/orchestrator.html) | Beta |
| **VRAM Manager** | Auto-manage model loading within VRAM limits | [**🧪 Install**](https://samscarrow.github.io/mcp-servers-lmstudio/installers/vram-manager.html) | Alpha |

## 💡 What is MCP?

Model Context Protocol (MCP) allows LM Studio models to:
- 🔄 **Query other models** - One model can ask another for help
- 🚀 **Run concurrently** - Multiple models working in parallel
- 🛠️ **Use tools** - Connect to databases, APIs, and services
- 🤖 **Self-referential AI** - Models can improve their own responses

## 📊 Model Requirements

Based on extensive testing, here are the minimum model requirements for effective tool use:

| Task Complexity | Minimum Model | VRAM | Use Cases |
|-----------------|---------------|------|-----------|
| **Simple** | qwen2.5-coder-14b | 8.5GB | Basic function calls, single tools |
| **Medium** | codestral-22b | 13.5GB | Multi-step workflows, sequential logic |
| **Complex** | qwen3-coder-30b | 18GB | Nested workflows, dynamic selection |
| **Expert** | qwen3-32b | 19.5GB | Error handling, production systems |

## 🔧 Installation Methods

### Method 1: One-Click Web Installer (Recommended)
1. Click any install button above
2. Your browser will open the installer page
3. Click "Install in LM Studio"
4. LM Studio will prompt to add the server

### Method 2: Direct Deeplink
Copy and paste these links into your browser:

```
# Concurrent Multi-Agent Server
lmstudio://add_mcp?name=lmstudio-concurrent&config=eyJjb21tYW5kIjoicHl0aG9uMyIsImFyZ3MiOlsiL3BhdGgvdG8vbG1zdHVkaW9fYnJpZGdlLnB5Il0sImVudiI6eyJMTVNUVURJT19BUElfQkFTRSI6Imh0dHA6Ly9sb2NhbGhvc3Q6MTIzNC92MSJ9fQ==
```

### Method 3: Manual Configuration
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

### Method 4: CLI Installation
```bash
# Using the installer generator
python3 generate_installer.py --preset concurrent --open

# Or directly with LM Studio CLI
lmstudio mcp add-json 'lmstudio-concurrent' '{"command":"python3","args":["/path/to/server.py"]}'
```

## 🎨 Create Your Own MCP Server

### Quick Start Template

```python
# my_mcp_server.py
from mcp import server
import asyncio

@server.tool()
async def my_tool(param: str) -> str:
    """Your tool description"""
    return f"Processed: {param}"

if __name__ == "__main__":
    server.run()
```

### Generate Installer

```bash
# Clone this repo
git clone https://github.com/samscarrow/mcp-servers-lmstudio.git
cd mcp-servers-lmstudio

# Generate installer for your server
python3 scripts/generate_installer.py \
  --name "my-server" \
  --script "/path/to/my_mcp_server.py" \
  --output installers/my-server.html \
  --open
```

## 📈 Performance Benchmarks

| Configuration | Response Time | Throughput | VRAM Usage |
|---------------|--------------|------------|------------|
| Single 14B Model | 2.3s | 26 tokens/s | 8.5GB |
| 2x 14B Concurrent | 2.4s | 52 tokens/s | 17GB |
| 4x 14B Concurrent | 2.8s | 95 tokens/s | 33GB* |
| 1x 30B Model | 4.1s | 18 tokens/s | 18GB |

*Using JIT loading with auto-unload

## 🛡️ Security

⚠️ **Important**: MCP servers can execute code on your system. Only install servers from trusted sources.

Each installer shows:
- Full configuration before installation
- File paths and permissions required
- Environment variables used
- Network endpoints accessed

## 🤝 Contributing

We welcome contributions! To add your MCP server:

1. Fork this repository
2. Add your server to `installers/`
3. Create documentation in `docs/`
4. Submit a pull request

### Server Requirements
- [ ] Async/await support for concurrent operations
- [ ] Proper error handling
- [ ] Documentation with examples
- [ ] Security considerations documented
- [ ] Tested with LM Studio v0.3.0+

## 📚 Resources

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [MCP Specification](https://github.com/modelcontextprotocol/spec)
- [Example MCP Servers](https://github.com/modelcontextprotocol/servers)
- [LM Studio Discord](https://discord.gg/lmstudio)

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LM Studio team for the amazing local LLM platform
- Anthropic for the Model Context Protocol specification
- Contributors who've shared their MCP servers

---

**Made with ❤️ by the LM Studio community**

*Last updated: 2025-01-30*