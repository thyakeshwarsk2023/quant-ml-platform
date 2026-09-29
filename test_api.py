import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("1. Testing GET /")
r = client.get("/")
print("Status:", r.status_code, r.json())

print("\n2. Testing GET /health")
r = client.get("/health")
print("Status:", r.status_code, r.json())

print("\n3. Testing GET /rankings")
r = client.get("/rankings?top_k=5")
print("Status:", r.status_code, "Results count:", len(r.json().get("results", [])))

print("\n4. Testing GET /portfolio")
r = client.get("/portfolio?top_k=5")
print("Status:", r.status_code, "Status:", r.json().get("status"), "Selected count:", len(r.json().get("selected_stocks", [])))

print("\n5. Testing GET /analytics?symbol=AAPL&period=1mo")
try:
    r = client.get("/analytics?symbol=AAPL&period=1mo")
    print("Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Symbol:", data.get("symbol"))
        bars = data.get("bars", [])
        print("Bars count:", len(bars))
        if bars:
            print("Sample bar keys:", list(bars[0].keys()))
            print("First bar:", bars[0])
            print("Last bar:", bars[-1])
    else:
        print("Error:", r.text)
except Exception as e:
    print("Analytics exception:", e)

print("\n6. Testing GET /forecast?symbol=AAPL&period=1mo")
try:
    r = client.get("/forecast?symbol=AAPL&period=1mo")
    print("Status:", r.status_code)
    if r.status_code == 200:
        print("Forecast:", r.json().get("forecast"))
    else:
        print("Error:", r.text)
except Exception as e:
    print("Forecast exception:", e)

print("\n7. Testing GET /equity/1")
r = client.get("/equity/1")
print("Status:", r.status_code, "Equity points:", r.json())
