import pandas as pd
import json
import random

def fetch_and_build_tariffs():
    print("📡 Fetching global HS codes from open-source data stream...")
    
    # Corrected active URL for the harmonized-system dataset
    raw_url = "https://raw.githubusercontent.com/datasets/harmonized-system/main/data/harmonized-system.csv"
    
    try:
        # Load the remote CSV directly into memory via Pandas
        df = pd.read_csv(raw_url)
        
        # Filter down specifically to 6-digit detailed entries
        df_6digit = df[df['level'] == 6].dropna(subset=['hscode', 'description'])
        
        mock_tariffs = {}
        print(f"📦 Processing {len(df_6digit)} international product lines...")
        
        for _, row in df_6digit.iterrows():
            # Clean up the code structure string
            hs_code = str(row['hscode']).strip().replace('.', '')
            description = str(row['description']).strip()
            
            # Generate realistic variant mock duty rates for the regional UI components
            ca_rate = round(random.choice([0.0, 0.0, 0.0, 0.025, 0.05, 0.065]), 3)
            us_rate = round(random.choice([0.0, 0.0, 0.0, 0.015, 0.03, 0.045]), 3)
            eu_rate = round(random.choice([0.0, 0.0, 0.0, 0.02, 0.04, 0.055]), 3)
            
            mock_tariffs[hs_code] = {
                "description": description,
                "rates": {
                    "CA": ca_rate,
                    "US": us_rate,
                    "EU": eu_rate
                }
            }
            
        # Write clean dictionary to file
        output_path = "data/mock_tariffs.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(mock_tariffs, f, indent=2, ensure_ascii=False)
            
        print(f"🚀 Success! Local database seeded with authentic data at: {output_path}")
        
    except Exception as e:
        print(f"❌ Automation build failure: {e}")

if __name__ == "__main__":
    fetch_and_build_tariffs()