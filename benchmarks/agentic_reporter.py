import json
import time
import os
from scenarios.system_metrics import LiveNetworkMeasurementStream
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector

if __name__ == "__main__":
    print("=" * 80)
    print("        LAUNCHING AUTOMATED TELEMETRY LOGGING LAYER (AGENTIC PREP)")
    print("=" * 80)
    
    stream = LiveNetworkMeasurementStream()
    adp_detector = AdaptiveCUSUMDetector(burn_in=15)
    
    log_file = "benchmarks/telemetry_incidents.json"
    print(f"Streaming data live. Anomalies will be saved automatically to: {log_file}")
    print("-" * 80)
    
    try:
        # Quick 20-tick operational run to capture live events
        for tick in range(1, 21):
            ping_val = stream.fetch_raw_data()
            is_anomaly, tracker_val = adp_detector.update(ping_val)
            
            # Determine the status
            status = "CRITICAL_SPIKE" if is_anomaly else "STABLE"
            
            # Formulate the automated record
            record = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tick": tick,
                "metric_ms": round(ping_val, 2),
                "detector_score": round(tracker_val, 2),
                "status": status
            }
            
            # Print operational status to screen
            print(f"Tick {tick:<2} | Ping: {ping_val:<6.2f} ms | Score: {tracker_val:<6.2f} | Status: {status}")
            
            # If an anomaly occurs, write it to the persistent JSON storage
            if is_anomaly or ping_val > 100.0:
                # Append to existing file or create a new one
                data = []
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            data = []
                            
                data.append(record)
                with open(log_file, "w") as f:
                    json.dump(data, f, indent=4)
                    
    except KeyboardInterrupt:
        print("\nLogging stream stopped.")
        
    print("=" * 80)
    print("Persistence pass complete. Historical records successfully secured.")
