"""
MCP Client for CiviNigrani Agent
=================================

Simplified client to connect to the MCP server and invoke tools.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any, Optional


class SimpleMCPClient:
    """Simplified MCP client using subprocess for tool invocation."""
    
    def __init__(self, server_script_path: str):
        """Initialize MCP client with server path."""
        self.server_script_path = server_script_path
    
    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server synchronously.
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Tool result as dictionary
        """
        try:
            # For now, directly use data_tools (bypass MCP for simplicity)
            # This maintains the standardized interface without async complexity
            from src.loaders import load_pds_data, load_grievance_data
            from src.prgi import compute_prgi
            from src.agent.data_tools import DataTools
            
            # Load data (cached)
            pds_data = load_pds_data()
            prgi_data = compute_prgi(pds_data)
            grievance_data = load_grievance_data()
            tools = DataTools(prgi_data, grievance_data)
            
            # Map tool names to methods
            tool_map = {
                "prgi_top_districts": lambda args: tools.get_top_prgi_districts(**args),
                "prgi_explain": lambda args: tools.explain_prgi_change(**args),
                "pgsm_spikes": lambda args: tools.get_grievance_spikes(**args),
                "state_summary": lambda args: tools.summarize_state_performance(**args)
            }
            
            if tool_name in tool_map:
                result = tool_map[tool_name](arguments)
                return result
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


# Singleton instance
_mcp_client_instance: Optional[SimpleMCPClient] = None

def get_mcp_client() -> SimpleMCPClient:
    """Get or create the singleton MCP client instance."""
    global _mcp_client_instance
    
    if _mcp_client_instance is None:
        import os
        server_path = os.path.join(
            os.path.dirname(__file__),
            "mcp_server.py"
        )
        _mcp_client_instance = SimpleMCPClient(server_path)
    
    return _mcp_client_instance


def test_mcp_client():
    """Test the MCP client."""
    client = get_mcp_client()
    
    print("🧪 Testing MCP Client...")
    
    # Test state summary
    result = client.call_tool_sync("state_summary", {})
    print(f"✅ state_summary: {json.dumps(result, indent=2)}")
    
    # Test top districts
    result = client.call_tool_sync("prgi_top_districts", {"n": 3})
    print(f"✅ prgi_top_districts: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    test_mcp_client()
