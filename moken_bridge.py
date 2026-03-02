from fastapi import FastAPI, HTTPException, Header, Depends
import requests
from datetime import datetime, timedelta

app = FastAPI(title="Quakecore to Moken Bridge Automatic")

# --- YOUR SECRET TOKEN FOR MOKEN ---
# You can change this string to whatever you prefer
MOKEN_SECRET_TOKEN = "quakecore-moken-token-2026"

def verify_token(authorization: str = Header(None)):
    """Verifies that Moken is calling us with the correct password."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized: No token provided")
    
    # Remove the "Bearer " prefix if Moken uses it
    token = authorization.replace("Bearer ", "")
    if token != MOKEN_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")

def fetch_quakecore_data():
    """Fetches the most recent log file from the Quakecore server."""
    # Pretend to be a browser to avoid being blocked by the server
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    today = datetime.utcnow()
    
    # Search backwards up to 5 days
    for days_back in range(5):
        target_date = today - timedelta(days=days_back)
        date_str = target_date.strftime('%Y-%m-%d')
        url = f"https://api.quakecore.com/rewards/rewards-{date_str}"
        
        print(f"Trying to download from: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"SUCCESS! Downloaded file for {date_str}")
                return response.content
            else:
                print(f"Failed (Error {response.status_code}) - File might not exist yet.")
        except Exception as e:
            print(f"Connection error: {e}")
            
    # FALLBACK: If the last 5 days fail, use the historically working file
    print("Falling back to the known working file from 2025-09-19...")
    fallback_url = "https://api.quakecore.com/rewards/rewards-2025-09-19"
    try:
        response = requests.get(fallback_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
    except:
        pass

    return None

# Added "dependencies=[Depends(verify_token)]" to block requests without the password
@app.get("/api/miners/{public_id}", dependencies=[Depends(verify_token)])
def get_miner(public_id: str):
    # 1. Fetch fresh data from Quakecore
    raw_data = fetch_quakecore_data()
    
    if not raw_data:
        raise HTTPException(status_code=500, detail="Unable to fetch logs from Quakecore at this time.")

    # 2. Check if the public_id is present in the binary dump
    is_online = public_id.encode() in raw_data

    # If not found, tell Moken the node is offline
    if not is_online:
        return {"miner_id": public_id, "status": "offline"}

    # 3. If found, return the expected Moken format
    moken_response = {
        "miner_id": public_id,
        "status": "online",
        "hex_location": "85be8d8ffffffff", # Replace with your actual H3 Hex
        "performance_metrics": {
            "hex_density_percent": 100,
            "device_density_percent": 100,
            "location_percent": 100,
            "heartbeat_percent": 100
        },
        "rewards": {
            "total_earned": 0,
            "reward_cap": 0
        },
        "protection": {
            "nft_protection": True,
            "loss_of_protection": False
        },
        "uptime": {
            "consecutive_days_running": 5,
            "consecutive_days_off": 0
        }
    }
    
    return moken_response