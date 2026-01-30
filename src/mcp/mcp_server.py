"""
CiviNigrani MCP Server
======================

Model Context Protocol server exposing PRGI and PGSM data tools.
"""

import asyncio
import json
from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import data tools
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.loaders import load_pds_data, load_grievance_data
from src.prgi import compute_prgi
from src.agent.data_tools import DataTools

# Initialize data
print("📊 Loading CiviNigrani data...")
pds_data = load_pds_data()
prgi_data = compute_prgi(pds_data)
grievance_data = load_grievance_data()
data_tools = DataTools(prgi_data, grievance_data)
print("✅ Data loaded successfully")

# Create MCP server
server = Server("civinigrani-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available data tools."""
    return [
        Tool(
            name="prgi_top_districts",
            description="Get top N districts with highest PRGI (worst delivery gap). PRGI > 0.3 = high risk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of top districts to return",
                        "default": 5
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Optional time period filter (e.g., '2024-Q4', '2024-10')",
                        "default": None
                    }
                }
            }
        ),
        Tool(
            name="prgi_explain",
            description="Explain PRGI trends and changes for a specific district over time.",
            inputSchema={
                "type": "object",
                "properties": {
                    "district": {
                        "type": "string",
                        "description": "District name (e.g., 'Lucknow', 'Agra')"
                    },
                    "month": {
                        "type": "string",
                        "description": "Optional month to focus on",
                        "default": None
                    }
                },
                "required": ["district"]
            }
        ),
        Tool(
            name="pgsm_spikes",
            description="Identify months with significant grievance increases above threshold.",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold_pct": {
                        "type": "number",
                        "description": "Percentage increase threshold to flag as spike",
                        "default": 30.0
                    }
                }
            }
        ),
        Tool(
            name="state_summary",
            description="Generate comprehensive state-level PDS performance summary with risk classification.",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "string",
                        "description": "Optional year filter (e.g., '2024')",
                        "default": None
                    }
                }
            }
        ),
        Tool(
            name="update_district_prgi",
            description="[ADMIN ONLY] Update the PRGI (Delivery Gap) for a specific district. High PRGI = Poor delivery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "district": {
                        "type": "string",
                        "description": "District name"
                    },
                    "prgi": {
                        "type": "number",
                        "description": "New PRGI value (0.0 to 1.0)"
                    }
                },
                "required": ["district", "prgi"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a data tool and return results."""
    
    try:
        if name == "prgi_top_districts":
            result = data_tools.get_top_prgi_districts(
                n=arguments.get("n", 5),
                time_period=arguments.get("time_period")
            )
        
        elif name == "prgi_explain":
            result = data_tools.explain_prgi_change(
                district=arguments["district"],
                month=arguments.get("month")
            )
        
        elif name == "pgsm_spikes":
            result = data_tools.get_grievance_spikes(
                threshold_pct=arguments.get("threshold_pct", 30.0)
            )
        
        elif name == "state_summary":
            result = data_tools.summarize_state_performance(
                year=arguments.get("year")
            )

        elif name == "update_district_prgi":
            result = data_tools.update_district_prgi(
                district=arguments["district"],
                prgi=float(arguments["prgi"])
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        # Return as TextContent
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        error_result = {"error": str(e)}
        return [TextContent(
            type="text",
            text=json.dumps(error_result, indent=2)
        )]

async def main():
    """Run the MCP server."""
    print("🚀 Starting CiviNigrani MCP Server...")
    print("📡 Tools available: prgi_top_districts, prgi_explain, pgsm_spikes, state_summary")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
