import requests

url = 'http://127.0.0.1:5000/parse'
data = {"input": "your string to parse"}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())
