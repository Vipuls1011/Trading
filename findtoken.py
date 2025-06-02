import requests
import json

# URL of the JSON file
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

# Desired symbol
target_symbol = "NIFTY05JUN2524400PE"

# Fetch and parse JSON data
response = requests.get(url)
data = response.json()

# Search for the symbol and print its token
for item in data:
    if item.get("symbol") == target_symbol:
        print(item.get("token"))
        break
else:
    print("Symbol not found.")
