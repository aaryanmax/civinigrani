import random
import time

class MockAIEngine:
    """
    Mock AI Engine for Policy RAG (Retrieval Augmented Generation).
    Simulates fetching context and generating a narrative response.
    """
    
    def __init__(self):
        self.df = None
        
    def update_data(self, df):
        """Update the knowledge base with the latest dataframe."""
        self.df = df
        
    def query(self, user_question: str) -> str:
        """
        Simulates an LLM response based on the question.
        Dynamically analyzes the PDS dataframe if available.
        """
        time.sleep(1.0)  # Simulate latency
        user_question = user_question.lower()
        
        # If no data is loaded yet
        if self.df is None or self.df.empty:
            return "I don't have access to the latest PDS data yet. Please ensure the dashboard has loaded correctly."
            
        # ----------------------------------------
        # DYNAMIC ANALYSIS LOGIC
        # ----------------------------------------
        
        # Calculate key metrics per district (using the latest month available for each)
        latest_df = self.df.sort_values("month").groupby("district").last().reset_index()
        latest_df['gap_pct'] = (1 - (latest_df['distribution'] / latest_df['allocation'])) * 100
        latest_df['gap_pct'] = latest_df['gap_pct'].fillna(0) # Handle divide by zero
        
        if "highest gap" in user_question or "worst" in user_question or "poor" in user_question:
            worst = latest_df.sort_values("gap_pct", ascending=False).head(2)
            d1 = worst.iloc[0]
            d2 = worst.iloc[1]
            
            warning = ""
            if d1['gap_pct'] >= 99.9 or d2['gap_pct'] >= 99.9:
                warning = " ⚠️ **Note:** Some districts show 100% gap (0 distribution), which may indicate data reporting delays or data corruption rather than actual leakage."
                
            return (f"Based on the latest real-time data, **{d1['district']}** has the highest delivery gap of **{d1['gap_pct']:.1f}%**, "
                    f"followed by **{d2['district']}** at {d2['gap_pct']:.1f}%.{warning}")
        
        elif "best" in user_question or "lowest gap" in user_question or "good" in user_question:
            best = latest_df[latest_df['allocation'] > 1000].sort_values("gap_pct", ascending=True).head(1)
            if not best.empty:
                d = best.iloc[0]
                return (f"**{d['district']}** is performing exceptionally well with a delivery gap of only **{d['gap_pct']:.1f}%**, "
                        f"ensuring efficient food grain distribution.")
            else:
                return "All districts are showing some gaps, but performance varies."
            
        elif "trend" in user_question:
            # Simple trend analysis (compare last 2 months of state avg)
            monthly_avg = self.df.groupby("month")['prgi'].mean().sort_index()
            if len(monthly_avg) >= 2:
                curr = monthly_avg.iloc[-1]
                prev = monthly_avg.iloc[-2]
                diff = (prev - curr) * 100 # Decrease in PRGI is improvement? 
                # PRGI is Gap Index (Lower is better). So (Prev - Curr) > 0 means improvement.
                direction = "improvement" if diff > 0 else "decline"
                return (f"The state-wide PRGI trend shows a **{abs(diff):.1f}% {direction}** in efficiency "
                        f"compared to last month (Current Avg PRGI: {curr:.2f}).")
            else:
                return "Insufficient historical data to calculate a trend."
            
        else:
            return (f"I have analyzed data for {len(latest_df)} districts. "
                    "You can ask me about 'worst performing districts', 'best districts', or 'overall trends'.")
