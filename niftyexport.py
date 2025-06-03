from SmartApi import SmartConnect
import pyotp
from logzero import logger
import pandas as pd
from datetime import datetime

# Initialize the API connection
smartApi = SmartConnect('4XFfmZ2H')

# Generate TOTP for authentication
try:
    totp = pyotp.TOTP('DHUT7WRLOD5GTSQZFDAIVE6PHE').now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

# Generate session and authenticate
correlation_id = "abcde"
data = smartApi.generateSession('V59629', '6216', totp)

if data['status'] == False:
    logger.error(data)
else:
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    feedToken = smartApi.getfeedToken()
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    
# Get today's date and time
today = datetime.now().strftime("%Y-%m-%d %H:%M")

# Historical data request from 1st October 2024 till now
try:
    historicParam = {
        "exchange": "NSE",
        "symboltoken": "99926000",  # Ensure this token is for the correct symbol
        "interval": "ONE_MINUTE",
        "fromdate": "2025-01-01 09:15",  # Start from 1st October 2024
        "todate": today  # Till the current date and time
    }
    candeldata = smartApi.getCandleData(historicParam)
    
    # Check if the 'data' key exists
    if 'data' in candeldata:
        columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        candeldata_df = pd.DataFrame(candeldata['data'], columns=columns)
        
        # Split the 'Time' column into 'Date' and 'Time' columns
        candeldata_df['Date'] = pd.to_datetime(candeldata_df['Time']).dt.date
        candeldata_df['Time'] = pd.to_datetime(candeldata_df['Time']).dt.time

        # Reorder the columns to have 'Date' and 'Time' first
        candeldata_df = candeldata_df[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # Save DataFrame to the specified Excel file
        excel_filename = r"D:\VSCode\Nifty_Historical.xlsx"
        candeldata_df.to_excel(excel_filename, index=False)

        print(f"Data has been successfully saved to {excel_filename}")
    else:
        print("No 'data' key found in the response. Check the API response.")
except Exception as e:
    logger.exception(f"Historic Api failed: {e}")
