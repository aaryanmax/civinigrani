import pandas as pd
import numpy as np
import os

# Create 5 test districts
districts = ["Test-Lucknow", "Test-Varanasi", "Test-Agra", "Test-Kanpur", "Test-Meerut"]

# Generate data for the last 12 months
months = pd.date_range(start="2024-01-01", periods=12, freq="MS").strftime("%Y-%m").tolist()

data = []

for district in districts:
    base_alloc = np.random.randint(50000, 100000)
    
    for month in months:
        # Add some monthly variability
        alloc = base_alloc + np.random.randint(-5000, 5000)
        
        # Determine distribution with a variable gap (0-30%)
        gap_pct = np.random.uniform(0.05, 0.35) 
        dist = alloc * (1 - gap_pct)
        
        # Calculate PRGI in the data itself (or agent will do it)
        # But our loader logic usually calculates it.
        # Let's save Allocation and Distribution so PRGI is computed.
        
        data.append({
            "state_name": "Uttar Pradesh",
            "district_name": district,
            "month": month,
            "commodity": "Wheat",  # Standard commodity
            "year": month.split("-")[0],
            "allocation": alloc,
            "distribution": dist
        })

df = pd.DataFrame(data)

# Ensure directory exists
os.makedirs("data/test", exist_ok=True)

# Save to CSV
df.to_csv("data/test/pds_test.csv", index=False)

print(f"✅ Generated {len(df)} records for {len(districts)} test districts in data/test/pds_test.csv")
