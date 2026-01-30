"""
CiviNigrani Query Agent
=======================

Conversational AI agent for exploring PRGI and PGSM data.
Uses Gemini for natural language understanding and ArmorIQ for safety.
"""

import os
import os
import json
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.agent.data_tools import DataTools
from src.armoriq_guard import ArmorIQGuard

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class QueryAgent:
    """Conversational agent for data exploration with safety guardrails."""
    
    def __init__(self, data_tools: DataTools, use_gemini: bool = True):
        """
        Initialize the query agent.
        
        Args:
            data_tools: DataTools instance with data access
            use_gemini: Whether to use Gemini API (requires API key)
        """
        self.data_tools = data_tools
        self.armor_guard = ArmorIQGuard()
        self.use_gemini = use_gemini and bool(GEMINI_API_KEY)
        
        # Log which mode we're using
        if self.use_gemini:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model_name = 'gemini-2.0-flash'
            print(f"✅ QueryAgent initialized with {self.model_name} (google-genai SDK)")
        else:
            print("⚠️ QueryAgent using keyword fallback (limited). Set GEMINI_API_KEY for full capability.")
        
        # System context for the agent
        self.system_context = """You are CiviNigrani AI, a helpful assistant for exploring governance data.

You have access to the following tools:
1. get_top_prgi_districts: Find districts with highest Policy Reality Gap Index (PRGI)
2. get_grievance_spikes: Identify months with grievance increases
3. explain_prgi_change: Explain PRGI trends for a district
4. summarize_state_performance: Generate state-level summary
5. update_district_prgi: [ADMIN ONLY] Update PRGI for a district (requires Admin role)

Guidelines:
- Always provide data citations
- Explain metrics in simple terms (PRGI = delivery gap, higher is worse)
- Be concise and factual
- Never make political judgments
- If you don't have data, say so clearly
- For update requests, use update_district_prgi tool

When a user asks a question:
1. Determine which tool to use
2. Extract parameters from the query
3. Return the tool name and parameters as JSON

Example:
User: "Show me top 5 districts with high PRGI"
Response: {"tool": "get_top_prgi_districts", "params": {"n": 5}}

User: "What's happening in Lucknow?"
Response: {"tool": "explain_prgi_change", "params": {"district": "Lucknow"}}

User: "Update Lucknow PRGI to 0.9"
Response: {"tool": "update_district_prgi", "params": {"district": "Lucknow", "prgi": 0.9}}
"""
    
    def query(self, user_query: str, user_role: str = "Analyst") -> Dict[str, Any]:
        """
        Process a user query with safety validation.
        
        Args:
            user_query: Natural language query from user
            user_role: Role of the user (Analyst or Admin)
            
        Returns:
            Dict with response or error
        """
        # Step 1: Validate query with ArmorIQ
        validation = self.armor_guard.validate_query(user_query)
        
        if not validation.get('valid', False):
            return {
                "success": False,
                "error": validation.get('reason', 'Query blocked'),
                "action": validation.get('action', 'BLOCK'),
                "armoriq_verified": True
            }
        
        if not self.use_gemini:
            print("🔄 Using keyword fallback parser (no Gemini API key)")
            # Fallback direct execution for now
            tool_call = self._fallback_parse(user_query)
            if "error" in tool_call:
                return {"success": False, "error": tool_call["error"], "armoriq_verified": False}
            result = self._execute_tool(tool_call["tool"], tool_call.get("params", {}))
            return self._format_response(user_query, tool_call, result)

        # --- ArmorIQ Verified Workflow ---
        
        # 1. Parse Intent (Plan Generation)
        tool_call = self._parse_intent(user_query)
        if "error" in tool_call:
            return {"success": False, "error": tool_call["error"], "armoriq_verified": True}
        
        # 2. Simulate Plan Capture & Local Policy Check
        # (In a real setup, we would call client.capture_plan() and client.get_intent_token())
        # For the hackathon, we simulate policy enforcement based on user_role.
        
        tool_name = tool_call["tool"]
        is_write_op = tool_name == "update_district_prgi"
        
        # Policy: Analyst cannot write
        if user_role == "Analyst" and is_write_op:
            return {
                "success": False,
                "error": "🔒 Action Blocked: 'Analyst' role does not have permission to update data. Contact Admin.",
                "action": "BLOCK",
                "armoriq_verified": True
            }
            
        # 3. Simulate Verified Invocation
        # (Real setup: client.invoke(action, inputs, token, execution_fn))
        # We execute the local tool directly if allowed.
        
        result = self._execute_tool(tool_name, tool_call.get("params", {}))
        
        # 4. Format Response
        response = self._format_response(user_query, tool_call, result)
        
        # 5. Scan Output with ArmorIQ
        scan_result = self.armor_guard.scan(response.get("answer", ""))
        
        if not scan_result.get("safe", True):
             return {
                "success": False,
                "error": f"Response blocked: {scan_result.get('flagged_for')}",
                "armoriq_verified": True
            }
            
        response["armoriq_verified"] = True
        return response

    def _parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse user intent and determine which tool to call."""
        
        if self.use_gemini:
            try:
                system_instruction = self.system_context
                prompt = f"""User Query: "{query}"

Respond with ONLY a JSON object specifying the tool and parameters. No other text."""
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json"
                    )
                )
                
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    return self._fallback_parse(query)
            
            except Exception as e:
                print(f"❌ Gemini API call failed: {str(e)}")
                return self._fallback_parse(query)
        
        else:
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Enhanced fallback parser for when Gemini API is not available."""
        query_lower = query.lower()
        import re
        
        # Extract numbers from query
        numbers = re.findall(r'\d+', query)
        
        # Pattern 1: Top/Worst/Best districts
        if any(word in query_lower for word in ["top", "worst", "best", "highest"]) and \
           ("district" in query_lower or "prgi" in query_lower):
            n = int(numbers[0]) if numbers else 5
            return {"tool": "get_top_prgi_districts", "params": {"n": n}}
        
        # Pattern 2: Average/Mean queries
        if any(word in query_lower for word in ["average", "mean", "avg"]) and \
           any(word in query_lower for word in ["prgi", "pgsm", "state", "performance"]):
            # Extract year if present
            years = re.findall(r'20\d{2}', query)
            year = years[0] if years else None
            params = {"year": year} if year else {}
            return {"tool": "summarize_state_performance", "params": params}
        
        # Pattern 3: Grievance spikes
        if "spike" in query_lower or "increase" in query_lower:
            return {"tool": "get_grievance_spikes", "params": {}}
        
        # Pattern 4: District-specific queries
        if "explain" in query_lower or any(d in query_lower for d in 
            ["lucknow", "agra", "kanpur", "varanasi", "allahabad", "meerut", "gorakhpur"]):
            # Extract district name
            districts = ["lucknow", "agra", "kanpur", "varanasi", "allahabad", 
                        "meerut", "gorakhpur", "mau", "mahoba", "jhansi"]
            for district in districts:
                if district in query_lower:
                    return {"tool": "explain_prgi_change", "params": {"district": district}}
            return {"error": "Could not identify district"}
        
        # Pattern 5: State summary / overview
        if any(word in query_lower for word in ["summary", "state", "overall", "total", "performance"]):
            years = re.findall(r'20\d{2}', query)
            year = years[0] if years else None
            params = {"year": year} if year else {}
            return {"tool": "summarize_state_performance", "params": params}
        
        # No match
        return {
            "error": "Could not understand query. Try: 'Show top 5 districts', 'Average PRGI in state', or 'Explain PRGI in Lucknow'."
        }
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified data tool."""
        
        tool_map = {
            "get_top_prgi_districts": self.data_tools.get_top_prgi_districts,
            "get_grievance_spikes": self.data_tools.get_grievance_spikes,
            "explain_prgi_change": self.data_tools.explain_prgi_change,
            "summarize_state_performance": self.data_tools.summarize_state_performance
        }
        
        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            return tool_func(**params)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _format_response(self, query: str, tool_call: Dict, result: Dict) -> Dict[str, Any]:
        """Format the tool result into a user-friendly response."""
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "query": query
            }
        
        # Build natural language response
        tool_name = tool_call["tool"]
        
        if tool_name == "get_top_prgi_districts":
            districts = result.get("results", [])
            if not districts:
                answer = "No district data available."
            else:
                lines = ["**Top Districts by PRGI (Delivery Gap):**\n"]
                for i, d in enumerate(districts, 1):
                    lines.append(f"{i}. **{d['district']}** - PRGI: {d['prgi']} (Allocated: {d['allocation']:.0f}, Distributed: {d['distribution']:.0f})")
                answer = "\n".join(lines)
        
        elif tool_name == "get_grievance_spikes":
            spikes = result.get("results", [])
            if not spikes:
                answer = "No significant grievance spikes detected."
            else:
                lines = ["**Grievance Spikes Detected:**\n"]
                for spike in spikes:
                    lines.append(f"- **{spike['month']}**: {spike['receipts']} receipts (+{spike['increase_pct']}%)")
                answer = "\n".join(lines)
        
        elif tool_name == "explain_prgi_change":
            exp = result.get("explanation", {})
            if not exp:
                answer = "No trend data available."
            else:
                district = exp['district']
                current = exp['current_prgi']
                trend = exp['trend']
                change = exp['change']
                
                answer = f"**{district} PRGI Trend:**\n\n"
                answer += f"Current PRGI: **{current}** (trend: {trend}, change: {change:+.3f})\n\n"
                answer += "Recent months:\n"
                for month_data in exp.get('recent_months', []):
                    answer += f"- {month_data['month']}: PRGI {month_data['prgi']}\n"
        
        elif tool_name == "summarize_state_performance":
            summary = result.get("summary", {})
            if not summary:
                answer = "No summary data available."
            else:
                answer = f"**Uttar Pradesh PDS Performance:**\n\n"
                answer += f"- Districts: {summary['total_districts']}\n"
                answer += f"- Avg PRGI: {summary['avg_prgi']} (State average)\n"
                answer += f"- Worst: {summary['worst_prgi']} | Best: {summary['best_prgi']}\n"
                answer += f"- Total Allocated: {summary['total_allocation']:.0f}\n"
                answer += f"- Total Distributed: {summary['total_distribution']:.0f}\n\n"
                
                risk = summary.get('risk_classification', {})
                answer += f"**Risk Classification:**\n"
                answer += f"- 🔴 High Risk: {risk.get('high_risk', 0)} districts\n"
                answer += f"- 🟡 Medium Risk: {risk.get('medium_risk', 0)} districts\n"
                answer += f"- 🟢 Low Risk: {risk.get('low_risk', 0)} districts"
        
        elif tool_name == "update_district_prgi":
            if result.get("success"):
                answer = f"✅ **Success**: {result.get('message')}\n"
                answer += f"Updated {result.get('district')} from **{result.get('old_prgi')}** to **{result.get('new_prgi')}**."
            else:
                answer = f"❌ **Update Failed**: {result.get('error', 'Unknown error')}"

        else:
            answer = "Data retrieved. See citation for details."
        
        # Add citation
        citation = result.get("citation", {})
        if citation:
            answer += f"\n\n*Source: {citation.get('source', 'PDS/PGSM Data')}*"
        
        return {
            "success": True,
            "answer": answer,
            "citation": citation,
            "query": query,
            "tool_used": tool_name
        }
