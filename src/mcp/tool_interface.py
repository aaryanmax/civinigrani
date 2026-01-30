"""
CiviNigrani MCP-Style Tool Interface
=====================================

Simplified MCP-style interface for data tool invocation.
For hackathon demo: provides standardized tool interface without full MCP async complexity.
"""

import json
from typing import Dict, Any
import pandas as pd


class MCPStyleToolInterface:
    """MCP-style interface for CiviNigrani data tools."""
    
    def __init__(self, data_tools):
        """Initialize with DataTools instance."""
        self.data_tools = data_tools
        self.tools = [
            {
                "name": "prgi_top_districts",
                "description": "Get top N districts with highest PRGI (worst delivery gap)",
                "parameters": ["n", "time_period"]
            },
            {
                "name": "prgi_explain",
                "description": "Explain PRGI trends for a specific district",
                "parameters": ["district", "month"]
            },
            {
                "name": "pgsm_spikes",
                "description": "Identify months with grievance spikes",
                "parameters": ["threshold_pct"]
            },
            {
                "name": "state_summary",
                "description": "Generate state-level performance summary",
                "parameters": ["year"]
            }
        ]
    
    def list_tools(self) -> list:
        """List available tools."""
        return self.tools
    
    def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool with parameters.
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            
        Returns:
            Tool result with data and citation
        """
        tool_map = {
            "prgi_top_districts": lambda args: self.data_tools.get_top_prgi_districts(**args),
            "prgi_explain": lambda args: self.data_tools.explain_prgi_change(**args),
            "pgsm_spikes": lambda args: self.data_tools.get_grievance_spikes(**args),
            "state_summary": lambda args: self.data_tools.summarize_state_performance(**args)
        }
        
        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            # Filter out None values from parameters
            filtered_params = {k: v for k, v in parameters.items() if v is not None}
            result = tool_map[tool_name](filtered_params)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


# Singleton instance
_mcp_interface: Any = None

def get_mcp_interface(data_tools=None):
    """Get or create the MCP interface."""
    global _mcp_interface
    
    if _mcp_interface is None:
        if data_tools is None:
            # Lazy load data tools
            from src.loaders import load_pds_data, load_grievance_data
            from src.prgi import compute_prgi
            from src.agent.data_tools import DataTools
            
            pds_data = load_pds_data()
            prgi_data = compute_prgi(pds_data)
            grievance_data = load_grievance_data()
            data_tools = DataTools(prgi_data, grievance_data)
        
        _mcp_interface = MCPStyleToolInterface(data_tools)
        print("✅ MCP-style tool interface initialized")
    
    return _mcp_interface


def test_mcp_interface():
    """Test the MCP interface."""
    print("🧪 Testing MCP-Style Tool Interface...")
    
    interface = get_mcp_interface()
    
    # List tools
    tools = interface.list_tools()
    print(f"📋 Available tools: {[t['name'] for t in tools]}")
    
    # Test state summary
    result = interface.invoke_tool("state_summary", {})
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        summary = result.get("summary", {})
        print(f"✅ State Summary: {summary.get('total_districts')} districts, Avg PRGI: {summary.get('avg_prgi')}")
    
    # Test top districts
    result = interface.invoke_tool("prgi_top_districts", {"n": 3})
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        districts = result.get("results", [])
        print(f"✅ Top 3 Districts: {[d['district'] for d in districts]}")


if __name__ == "__main__":
    test_mcp_interface()
