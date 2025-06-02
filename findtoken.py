import requests

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = requests.get(url)
data = response.json()

# List of symbols you're searching for
symbols = [
    "NIFTY05JUN2524400PE",
    "NIFTY05JUN2524500CE",
    "NIFTY05JUN2525000PE"
]

# Search and print token for each symbol
for target_symbol in symbols:
    found = False
    for item in data:
        if item.get("symbol") == target_symbol:
            print(f"{target_symbol} -> Token: {item.get('token')}")
            found = True
            break
    if not found:
        print(f"{target_symbol} -> Not found")
