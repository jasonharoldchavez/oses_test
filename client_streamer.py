import time
import requests
import random
import datetime

# The endpoint pointing directly to your live app server
URL = "http://127.0.0.1:8000/validate"

print("🚀 Starting Enterprise Data Stream Simulation...")
print("Streaming live telemetry packets to the Data Guardian Core...\n")

# Stream 40 data points automatically
for i in range(1, 41):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    if i <= 25:
        # Generate safe, normal baseline decimal numbers around 10.0
        metric_value = round(random.normalvariate(10.0, 0.2), 2)
    else:
        # Simulate a dangerous creeping system drift or attack signal spiking upwards
        metric_value = round(10.0 + (i - 25) * 2.5, 2)
        
    payload = {
        "timestamp": now,
        "metric": metric_value
    }
    
    try:
        # Fire the data across the local network to your app
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            print(f"[PACKET {i:02d} SENT] Time: {now} | Value: {metric_value:<6} | Status: Delivered")
        else:
            print(f"[WARN] Ingestion layer rejected packet {i:02d}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the app server. Make sure 'python app.py' is running in another window!")
        break
        
    time.sleep(0.5) # Half-second intervals so they can watch it update live

print("\n✅ Simulation stream complete. Check your web dashboard to review the metrics and download the audit log!")
