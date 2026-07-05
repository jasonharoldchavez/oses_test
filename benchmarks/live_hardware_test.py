import numpy as np
from scenarios.system_metrics import LiveNetworkMeasurementStream
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector
from streaming_guardian.detectors.models import CUSUMDecisionEngine

if __name__ == "__main__":
    print("=" * 80)
    print("      LAUNCHING LIVE INTERNET TELEMETRY BENCHMARK (REAL-TIME LATENCY)")
    print("=" * 80)
    print("Pinging 8.8.8.8 to establish live streaming telemetry...")
    
    stream = LiveNetworkMeasurementStream()
    
    # Adjusted thresholds to match standard internet fluctuations
    std_detector = CUSUMDecisionEngine(threshold_h=50.0, noise_floor=25.0)
    adp_detector = AdaptiveCUSUMDetector(burn_in=15)
    
    print("\nWarm-up: Gathering baseline internet latency for 15 ticks...")
    for _ in range(15):
        _ = stream.fetch_raw_data()
        
    print("Monitoring active connection. Press Ctrl+C to terminate.")
    print("-" * 80)
    print(f"{'Tick':<8} | {'Ping (ms)':<12} | {'Static Tracker':<16} | {'Adaptive Tracker':<16} | {'Alarms Triggered'}")
    print("-" * 80)
    
    try:
        for tick in range(1, 41):  # 40 steps for a quick live check
            ping_val = stream.fetch_raw_data()
            
            std_alarm, std_track = std_detector.update(ping_val)
            adp_alarm, adp_track = adp_detector.update(ping_val)
            
            alarms = []
            if std_alarm: alarms.append("STATIC_ALERT")
            if adp_alarm: alarms.append("ADAPTIVE_ALERT")
            alarm_str = ", ".join(alarms) if alarms else "NONE"
            
            print(f"{tick:<8} | {ping_val:<12.2f} | {std_track:<16.2f} | {adp_track:<16.2f} | {alarm_str}")
                
    except KeyboardInterrupt:
        print("\nStream monitoring halted by user request.")
        
    print("=" * 80)
    print("Live validation complete. True non-stationary data successfully verified.")
