import json
import csv
import os
import time
import numpy as np
from framework_core import AdaptiveCUSUMDetector

class RealTimeDataGateway:
    """
    The production-ready intake station. Handles live streaming data points,
    updates a persistent CSV audit log, and renders a real-time monitor dashboard.
    """
    def __init__(self, log_filename="anomaly_audit_log.csv"):
        self.engine = AdaptiveCUSUMDetector(burn_in=30)
        self.log_filename = log_filename
        
        # Initialize the persistent CSV file with corporate headers if it doesn't exist
        if not os.path.exists(self.log_filename):
            with open(self.log_filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Raw_Metric", "Calibrated_Floor", "Tracker_Level", "Anomaly_Status"])
        
        print("[GATEWAY ON] Self-Correcting Data Guardian and Audit Engine is online.")

    def process_incoming_metric(self, json_payload):
        try:
            data = json.loads(json_payload)
            metric_value = float(data.get("metric", 0.0))
            timestamp = data.get("timestamp", "UNKNOWN")
            
            # Process data through the self-correcting mathematical engine
            is_anomaly, tracker_score = self.engine.update(metric_value)
            status_string = "ANOMALY_CONFIRMED" if is_anomaly else "NORMAL"
            
            # 1. THE AUDIT LOG LAYER: Append the row to persistent storage
            with open(self.log_filename, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, metric_value, self.engine.floor, tracker_score, status_string])
            
            return {
                "status": "success",
                "timestamp": timestamp,
                "value_processed": metric_value,
                "current_floor": round(self.engine.floor, 4),
                "tracker_level": round(tracker_score, 4),
                "anomaly_detected": is_anomaly
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def render_dashboard_ui(self, step, resp):
        """Renders a clean visual monitor dashboard straight to the terminal frame."""
        floor = resp["current_floor"]
        tracker = resp["tracker_level"]
        val = resp["value_processed"]
        
        # Build a dynamic visual alert banner
        if resp["anomaly_detected"]:
            alert_banner = " [!!! ANOMALY BREACH !!!] "
            status_color = "CRITICAL ALERT"
        elif floor == 0.0:
            alert_banner = " [LEARNING/CALIBRATING] "
            status_color = "CALIBRATING"
        else:
            alert_banner = " [SYSTEM NOMINAL]       "
            status_color = "TRACKING"

        # Create a tiny text-based sparkline graph representing the tracker level
        bar_length = min(30, int(tracker * 2))
        graph_bar = "█" * bar_length + "░" * (30 - bar_length)

        print(f"│ Step {step:02d} │ {alert_banner} │ Val: {val:6.2f} │ Floor: {floor:7.4f} │ Score: {tracker:7.4f} │ {graph_bar} │")

if __name__ == "__main__":
    gateway = RealTimeDataGateway()
    
    print("┌" + "─" * 111 + "┐")
    print(f"│ {'LIVE DATACENTER RESOURCE MONITOR & DATA DRIFT DASHBOARD':^111} │")
    print("├" + "─" * 111 + "┤")
    
    # Stream 35 data points live with a tiny artificial delay to simulate a real data pipeline
    for i in range(1, 36):
        if i <= 30:
            # Safe training baseline signals
            metric_val = np.random.normal(10.0, 0.2)
        else:
            # Active creeping attack/leak drift signals
            metric_val = 10.0 + (i - 30) * 1.6
            
        payload = f'{{"timestamp": "16:05:{i:02d}", "metric": {metric_val}}}'
        response = gateway.process_incoming_metric(payload)
        
        gateway.render_dashboard_ui(i, response)
        time.sleep(0.08)  # Mimics real-time streaming ingestion speeds
        
    print("└" + "─" * 111 + "┘")
    print(f"\n[SUCCESS] Execution complete. Audit trail secured in: '{gateway.log_filename}'")
