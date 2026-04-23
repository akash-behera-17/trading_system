import requests

URL = "https://trading-system-ma0a.onrender.com/api/stocks/market-movers"
headers = {
    "Origin": "https://neurotrade-ai.netlify.app",
    "Access-Control-Request-Method": "GET"
}

try:
    print("Testing OPTIONS request...")
    res_options = requests.options(URL, headers=headers)
    print("OPTIONS STATUS:", res_options.status_code)
    print("OPTIONS HEADERS:", res_options.headers)
    
    print("\nTesting GET request...")
    res_get = requests.get(URL, headers=headers)
    print("GET STATUS:", res_get.status_code)
    print("GET HEADERS:", res_get.headers)
    
except Exception as e:
    print('Error:', e)
