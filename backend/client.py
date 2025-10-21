import urllib.request
import json

url = 'http://127.0.0.1:5000/parse'
data = json.dumps({"input": "your string to parse"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=5) as resp:
    print("Status Code:", resp.status)
    print("Response:", resp.read().decode())