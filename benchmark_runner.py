import numpy as np
import time
# Importing your exact class name from framework_core.py
from framework_core import AdaptiveCUSUMDetector

def run_auditable_benchmark():
    print("==========================================================")
    print("      REGULATED BENCHMARK: ANTI-ENTROPY ENGINE EVAL       ")
    print("==========================================================")

    np.random.seed(42)
    stream_length = 200                                             
    change_point = 100

    clean_signal = np.random.normal(loc=10.0, scale=1.0, size=stream_length)
    drift = np.zeros(stream_length)
    for i in range(change_point, stream_length):                        
        drift[i] = (i - change_point) * 0.15

    test_stream = clean_signal + drift

    # Initializing using your exact class blueprint
    detector = AdaptiveCUSUMDetector(burn_in=30)

    false_positives = 0
    true_positives = 0
    detection_index = None

    start_time = time.perf_counter()
    for idx, val in enumerate(test_stream):
        # Calling your exact method signature: update(signal) -> returns (is_alarm, tracker)
        is_anomaly, tracker = detector.update(val)

        if is_anomaly:
            if idx < change_point:
                false_positives += 1
            else:
                true_positives += 1
                if detection_index is None:
                    detection_index = idx

    execution_time = (time.perf_counter() - start_time) * 1000

    detection_delay = (detection_index - change_point) if detection_index else -1
    fpr = (false_positives / change_point) * 100

    print(f"\n[METRIC SUMMARY]")
    print(f"• Total Processed Packets : {stream_length}")
    print(f"• Math Engine Compute Time : {execution_time:.3f} ms")
    print(f"• False Positive Rate (FPR): {fpr:.2f}%")
    print(f"• True Anomaly Injected    : Packet index {change_point}")
    print(f"• Engine Alert Triggered   : Packet index {detection_index}")
    print(f"• Strict Detection Delay   : {detection_delay} packets")
    print("\n✅ Evaluation complete. Data is locked and reproducible.")

if __name__ == "__main__":
    run_auditable_benchmark()
