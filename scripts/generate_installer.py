#!/usr/bin/env python3
"""
Generate one-click installer links for LM Studio MCP servers
Supports both stdio and SSE server configurations
"""

import json
import base64
import urllib.parse
from typing import Dict, Any, Optional
import webbrowser
import argparse

class LMStudioMCPInstaller:
    """Generate installation deeplinks for LM Studio MCP servers"""
    
    def __init__(self):
        self.deeplink_base = "lmstudio://add_mcp"
        
    def create_stdio_config(
        self,
        command: str,
        script_path: str,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create configuration for stdio-based MCP server"""
        config = {
            "command": command,
            "args": [script_path]
        }
        
        if env_vars:
            config["env"] = env_vars
            
        return config
    
    def create_sse_config(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create configuration for SSE-based MCP server"""
        config = {"url": url}
        
        if headers:
            config["headers"] = headers
            
        return config
    
    def generate_deeplink(self, server_name: str, config: Dict[str, Any]) -> str:
        """Generate the deeplink URL for one-click installation"""
        
        # Convert config to JSON and encode to base64
        config_json = json.dumps(config)
        config_base64 = base64.b64encode(config_json.encode()).decode()
        
        # Build the deeplink
        params = {
            "name": server_name,
            "config": config_base64
        }
        
        query_string = urllib.parse.urlencode(params)
        deeplink = f"{self.deeplink_base}?{query_string}"
        
        return deeplink
    
    def generate_html_installer(
        self,
        server_name: str,
        config: Dict[str, Any],
        description: str = "",
        output_file: str = "installer.html"
    ):
        """Generate a standalone HTML installer page"""
        
        deeplink = self.generate_deeplink(server_name, config)
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Install {server_name} - LM Studio MCP</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }}
        .card {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .description {{
            color: #666;
            margin-bottom: 20px;
        }}
        .install-btn {{
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: 600;
            margin: 20px 0;
            transition: transform 0.3s;
        }}
        .install-btn:hover {{
            transform: translateY(-2px);
        }}
        .config {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: left;
        }}
        .config pre {{
            margin: 0;
            font-size: 0.9em;
            overflow-x: auto;
        }}
        .warning {{
            background: #fff5f5;
            border: 1px solid #feb2b2;
            color: #c53030;
            padding: 10px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 {server_name}</h1>
        <p class="description">{description or 'MCP Server for LM Studio'}</p>
        
        <a href="{deeplink}" class="install-btn">
            Install in LM Studio
        </a>
        
        <div class="config">
            <strong>Configuration:</strong>
            <pre>{json.dumps(config, indent=2)}</pre>
        </div>
        
        <div class="warning">
            ⚠️ Only install MCP servers from trusted sources
        </div>
    </div>
</body>
</html>"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML installer saved to: {output_file}")
        return output_file

# Preset configurations
PRESETS = {
    "concurrent": {
        "name": "lmstudio-concurrent",
        "description": "Concurrent multi-agent MCP server with async support",
        "config": {
            "command": "/Users/samscarrow/miniconda3/bin/python3",
            "args": ["/Users/samscarrow/claude-workspace/sandbox/lmstudio-mcp-consolidated/lmstudio_bridge.py"],
            "env": {
                "LMSTUDIO_API_BASE": "http://192.168.50.136:1234/v1"
            }
        }
    },
    "local": {
        "name": "lmstudio-local",
        "description": "Local LM Studio MCP server",
        "config": {
            "command": "python3",
            "args": ["./lmstudio_bridge.py"],
            "env": {
                "LMSTUDIO_API_BASE": "http://localhost:1234/v1"
            }
        }
    },
    "docker": {
        "name": "lmstudio-docker",
        "description": "Dockerized LM Studio MCP server",
        "config": {
            "command": "docker",
            "args": ["run", "-i", "--rm", "--network=host", "lmstudio-mcp:latest"]
        }
    }
}

def main():
    parser = argparse.ArgumentParser(description="Generate LM Studio MCP installer")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Use a preset configuration")
    parser.add_argument("--name", help="Server name")
    parser.add_argument("--command", help="Command to run")
    parser.add_argument("--script", help="Script path")
    parser.add_argument("--env", help="Environment variables as JSON")
    parser.add_argument("--url", help="SSE server URL (for remote servers)")
    parser.add_argument("--headers", help="Headers as JSON (for remote servers)")
    parser.add_argument("--output", default="installer.html", help="Output HTML file")
    parser.add_argument("--open", action="store_true", help="Open installer in browser")
    parser.add_argument("--print-link", action="store_true", help="Print deeplink URL")
    
    args = parser.parse_args()
    
    installer = LMStudioMCPInstaller()
    
    if args.preset:
        # Use preset configuration
        preset = PRESETS[args.preset]
        server_name = preset["name"]
        config = preset["config"]
        description = preset["description"]
    elif args.url:
        # SSE server configuration
        server_name = args.name or "remote-mcp"
        headers = json.loads(args.headers) if args.headers else None
        config = installer.create_sse_config(args.url, headers)
        description = "Remote MCP server via SSE"
    else:
        # Custom stdio configuration
        server_name = args.name or "custom-mcp"
        command = args.command or "python3"
        script = args.script or "mcp_server.py"
        env_vars = json.loads(args.env) if args.env else None
        config = installer.create_stdio_config(command, script, env_vars)
        description = "Custom MCP server"
    
    if args.print_link:
        # Just print the deeplink
        deeplink = installer.generate_deeplink(server_name, config)
        print(f"Deeplink: {deeplink}")
    else:
        # Generate HTML installer
        html_file = installer.generate_html_installer(
            server_name,
            config,
            description,
            args.output
        )
        
        if args.open:
            webbrowser.open(f"file://{html_file}")
            print(f"🌐 Opened installer in browser")
    
    # Also print the manual installation command
    print(f"\n📋 Manual installation command:")
    print(f"lmstudio mcp add-json '{server_name}' '{json.dumps(config)}'")

if __name__ == "__main__":
    main()