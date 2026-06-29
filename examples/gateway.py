import json
import csv
import os
import time
import sys
import numpy as np
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector

class RealTimeDataGateway:
    """
    The enterprise-ready intake station. Handles live streaming data points,
    filters malformed payloads via an input validation layer, updates a 
    persistent CSV audit log, and renders a real-time monitor dashboard.
    """
    def __init__(self, log_filename="anomaly_audit_log.csv"):
        self.engine = AdaptiveCUSUMDetector(burn_in=30)
        self.log_filename = log_filename

        # Initialize the persistent CSV file with corporate headers if it doesn't exist
        if not os.path.exists(self.log_filename):
            with open(self.log_filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Raw_Metric", "Calibrated_Floor", "Tracker_Level", "Anomaly_Status"])

        print("[GATEWAY ON] Hardened Data Guardian and Audit Engine is online.")

    def process_incoming_metric(self, json_payload):
        timestamp = "UNKNOWN"
        try:
            # Safe JSON parsing
            try:
                data = json.loads(json_payload)
            except (json.JSONDecodeError, TypeError):
                return {"status": "error", "message": "Malformed JSON payload rejected."}

            timestamp = str(data.get("timestamp", "UNKNOWN"))
            raw_metric = data.get("metric")

            # ENTERPRISE INPUT SANITIZATION LAYER
            # Rejects None, strings that aren't numeric, booleans, infinite loops, and NaN anomalies
            if raw_metric is None or isinstance(raw_metric, bool):
                return {"status": "error", "message": "Invalid metric type detected: Numeric value required."}
            
            try:
                metric_value = float(raw_metric)
                if np.isnan(metric_value) or np.isinf(metric_value):
                    raise ValueError()
            except (ValueError, TypeError):
                return {"status": "error", "message": f"Rejected unsafe metric format: Received '{raw_metric}'"}

            # Process data through the self-correcting mathematical engine safely
            is_anomaly, tracker_score = self.engine.update(metric_value)
            status_string = "ANOMALY_CONFIRMED" if is_anomaly else "NORMAL"

            # THE AUDIT LOG LAYER: Append the row to persistent storage
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
            return {"status": "error", "message": f"Critical stream processing exception: {str(e)}"}

    def render_dashboard_ui(self, step, resp):
        """Renders a clean visual monitor dashboard straight to the terminal frame."""
        if resp["status"] == "error":
            print(f"│ Step {step:02d} │ [!] FILTER REJECTION │ {resp['message']:<82} │")
            return

        floor = resp["current_floor"]
        tracker = resp["tracker_level"]
        val = resp["value_processed"]

        # Build a dynamic visual alert banner
        if resp["anomaly_detected"]:
            alert_banner = " [!!! ANOMALY BREACH !!!] "
        elif floor == 0.0:
            alert_banner = " [LEARNING/CALIBRATING] "
        else:
            alert_banner = " [SYSTEM NOMINAL]       "

        # Create a text-based sparkline graph representing the tracker level
        bar_length = min(30, int(tracker * 2))
        graph_bar = "█" * bar_length + "░" * (30 - bar_length)

        print(f"│ Step {step:02d} │ {alert_banner} │ Val: {val:6.2f} │ Floor: {floor:7.4f} │ Score: {tracker:7.4f} │ {graph_bar} │")

if __name__ == "__main__":
    gateway = RealTimeDataGateway()

    print("┌" + "─" * 111 + "┐")
    print(f"│ {'LIVE DATACENTER RESOURCE MONITOR & DATA DRIFT DASHBOARD':^111} │")
    print("├" + "─" * 111 + "┤")

    # Stream 38 data points live (35 valid ones, plus 3 corrupted enterprise edge cases injected at the end)
    for i in range(1, 39):
        if i <= 30:
            # Safe training baseline signals
            metric_val = np.random.normal(10.0, 0.2)
            payload = f'{{"timestamp": "16:05:{i:02d}", "metric": {metric_val}}}'
        elif i <= 35:
            # Active creeping attack/leak drift signals
            metric_val = 10.0 + (i - 30) * 1.6
            payload = f'{{"timestamp": "16:05:{i:02d}", "metric": {metric_val}}}'
        elif i == 36:
            # Edge Case 1: Corrupted String Payload Injection
            payload = '{"timestamp": "16:05:36", "metric": "MALICIOUS_STRING"}'
        elif i == 37:
            # Edge Case 2: Missing Key / Null Parameter Payload Injection
            payload = '{"timestamp": "16:05:37"}'
        elif i == 38:
            # Edge Case 3: Completely Broken/Malformed Data Stream Packet
            payload = '{"timestamp": "16:05:38", "metric":'

        response = gateway.process_incoming_metric(payload)
        gateway.render_dashboard_ui(i, response)
        time.sleep(0.08)  # Mimics real-time streaming ingestion speeds

    print("└" + "─" * 111 + "┘")
    print(f"\n[SUCCESS] Execution complete. Audit trail secured in: '{gateway.log_filename}'")
