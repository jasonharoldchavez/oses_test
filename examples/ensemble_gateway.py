"""
Streaming Guardian - Enterprise Multi-Model Ensemble Gateway
Demonstrates how to route telemetry through a weighted ensemble of compatible detectors.
"""
import json
import random
import time
from streaming_guardian import AdaptiveCUSUMDetector
from streaming_guardian.detectors.models import EWMADetector, SimpleMovingAverageDetector

print("Initializing Enterprise Ensemble Gateway...")

# Initialize three fully compatible detectors
cusum_detector = AdaptiveCUSUMDetector(burn_in=30)
ewma_detector = EWMADetector()
sma_detector = SimpleMovingAverageDetector(window_size=15)

def process_multi_sensor_payload(payload_json):
    try:
        data = json.loads(payload_json)
        timestamp = data.get("timestamp")
        temp = data.get("temperature")
        
        # 1. Update individual models (all return: is_anomaly, score)
        is_cusum_anomaly, cusum_score = cusum_detector.update(temp)
        is_ewma_anomaly, ewma_score = ewma_detector.update(temp)
        is_sma_anomaly, sma_score = sma_detector.update(temp)
        
        # 2. Weighted consensus of their anomaly scores
        ensemble_score = (0.4 * float(cusum_score)) + (0.3 * float(ewma_score)) + (0.3 * float(sma_score))
        
        # 3. Decision logic: Trigger alarm if 2+ models agree, or score is too high
        active_alarms = sum([is_cusum_anomaly, is_ewma_anomaly, is_sma_anomaly])
        is_ensemble_anomaly = (active_alarms >= 2) or (ensemble_score > 2.0)
        
        if is_ensemble_anomaly:
            print(f"🚨 [ENSEMBLE ALARM] Time: {timestamp:.2f} | Score: {ensemble_score:.3f} | [CUSUM: {is_cusum_anomaly} | EWMA: {is_ewma_anomaly} | SMA: {is_sma_anomaly}]")
        else:
            print(f"  [Healthy] Time: {timestamp:.2f} | Score: {ensemble_score:.3f}")
            
    except Exception as e:
        print(f"Gateway ingestion error: {e}")

if __name__ == "__main__":
    print("\nStarting 100-step Industrial Telemetry Stream simulation...")
    for step in range(100):
        current_time = time.time()
        
        # Standard baseline values
        base_temp = 65.0 + random.normalvariate(0.0, 1.0)
        
        # Inject structural fault (simulated boiler overheating) starting at step 70
        if step >= 70:
            base_temp += (step - 70) * 1.5
            
        mock_packet = json.dumps({
            "timestamp": current_time,
            "temperature": base_temp
        })
        
        process_multi_sensor_payload(mock_packet)
        time.sleep(0.05)
