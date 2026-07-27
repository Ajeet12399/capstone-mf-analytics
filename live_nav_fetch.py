import requests
import pandas as pd
import os

def fetch_nav(scheme_code):
    """Fetch full NAV history for a scheme from mfapi.in"""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# HDFC Top 100 Direct — required as the standalone live fetch
hdfc_code = 125497

# 5 key schemes for cross-checking
key_schemes = {
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_Large_Cap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841,
}

os.makedirs("data/raw", exist_ok=True)

# Fetch HDFC Top 100 first
print("Fetching HDFC Top 100 Direct...")
hdfc_data = fetch_nav(hdfc_code)
print("Scheme:", hdfc_data["meta"]["scheme_name"])
print("Fund house:", hdfc_data["meta"]["fund_house"])

hdfc_df = pd.DataFrame(hdfc_data["data"])
hdfc_df.to_csv("data/raw/live_HDFC_Top_100_nav.csv", index=False)
print(f"Saved {len(hdfc_df)} rows for HDFC Top 100\n")

# Fetch the 5 key schemes
for name, code in key_schemes.items():
    print(f"Fetching {name} ({code})...")
    data = fetch_nav(code)
    df = pd.DataFrame(data["data"])
    df.to_csv(f"data/raw/live_{name}_nav.csv", index=False)
    print(f"Saved {len(df)} rows for {name}\n")

print("Live NAV fetch complete for all 6 schemes.")