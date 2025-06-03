import requests
import pandas as pd
from datetime import datetime
from SmartApi import SmartConnect
import pyotp
from logzero import logger
import os

# === CONFIGURATION ===
symbols = [
    "NIFTY05JUN2524850PE",
    "NIFTY05JUN2524700CE",
    "NIFTY05JUN2523750PE",
    "NIFTY05JUN2525850CE"
]
output_dir = r"C:\Users\specindia\Desktop\temp\test"
client_code = 'V59629'
password = '6216'
totp_secret = 'DHUT7WRLOD5GTSQZFDAIVE6PHE'
api_key = '4XFfmZ2H'

# === FETCH SYMBOL TOKEN MAPPING ===
print("Fetching symbol-token mapping...")
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = requests.get(url)
data = response.json()

symbol_token_map = {}
for target_symbol in symbols:
    token_found = next((item for item in data if item.get("symbol") == target_symbol), None)
    if token_found:
        symbol_token_map[target_symbol] = token_found.get("token")
    else:
        print(f"{target_symbol} -> Not found")

if not symbol_token_map:
    print("No valid tokens found. Exiting.")
    exit()

# === AUTHENTICATE WITH SMART API ===
print("Authenticating with Angel One SmartAPI...")
smartApi = SmartConnect(api_key)
totp = pyotp.TOTP(totp_secret).now()
session = smartApi.generateSession(client_code, password, totp)

if not session.get("status"):
    logger.error("Session generation failed.")
    exit()

authToken = session['data']['jwtToken']
refreshToken = session['data']['refreshToken']
feedToken = smartApi.getfeedToken()
smartApi.getProfile(refreshToken)
smartApi.generateToken(refreshToken)

# === DOWNLOAD HISTORICAL DATA AND EXPORT ===
today = datetime.now().strftime("%Y-%m-%d %H:%M")
from_date = "2025-05-29 09:15"
to_date = today+1

os.makedirs(output_dir, exist_ok=True)

for symbol, token in symbol_token_map.items():
    print(f"\nFetching data for {symbol} (Token: {token})")
    try:
        historicParam = {
            "exchange": "NFO",  #For index use NSE, for stikes use NFO
            "symboltoken": token,
            "interval": "ONE_MINUTE",
            "fromdate": from_date,
            "todate": to_date
        }
        response = smartApi.getCandleData(historicParam)
        if 'data' in response:
            df = pd.DataFrame(response['data'], columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Time']).dt.date
            df['Time'] = pd.to_datetime(df['Time']).dt.time
            df = df[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

            file_path = os.path.join(output_dir, f"{symbol}.xlsx")
            df.to_excel(file_path, index=False)
            print(f"Saved to: {file_path}")
        else:
            print(f"No data found for {symbol}. Response: {response}")
    except Exception as e:
        logger.exception(f"Failed for symbol {symbol}: {e}")
