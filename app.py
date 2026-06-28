import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from gateway import RealTimeDataGateway
import os

app = FastAPI(
    title="Enterprise Data Guardian", 
    description="Premium Automated Data Stream Integrity Engine."
)

gateway = RealTimeDataGateway()

# Global counters to display live metrics to the client
stats = {
    "total_processed": 0,
    "anomalies_detected": 0,
    "last_value": 0.0,
    "status_message": "Awaiting telemetry stream initialization..."
}

class MetricPayload(BaseModel):
    timestamp: str
    metric: float

@app.post("/validate")
def validate_stream_point(payload: MetricPayload):
    json_data = f'{{"timestamp": "{payload.timestamp}", "metric": {payload.metric}}}'
    response = gateway.process_incoming_metric(json_data)
    
    if response["status"] == "error":
        raise HTTPException(status_code=400, detail=response["message"])
    
    # Update global stats for the UI
    stats["total_processed"] += 1
    stats["last_value"] = response["value_processed"]
    if response["anomaly_detected"]:
        stats["anomalies_detected"] += 1
        stats["status_message"] = f"CRITICAL ANOMALY caught at {response['timestamp']} (Value: {response['value_processed']})!"
    else:
        stats["status_message"] = f"Metric {response['value_processed']} validated successfully at {response['timestamp']}."
        
    return response

@app.post("/manual_submit", response_class=HTMLResponse)
def handle_manual_input(metric_input: str = Form(...)):
    """Handles manual user inputs straight from the web browser dashboard."""
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Send input directly through our secure JSON gate
    json_data = f'{{"timestamp": "{now}", "metric": "{metric_input}"}}'
    response = gateway.process_incoming_metric(json_data)
    
    if response["status"] == "success":
        stats["total_processed"] += 1
        stats["last_value"] = response["value_processed"]
        if response["anomaly_detected"]:
            stats["anomalies_detected"] += 1
            stats["status_message"] = f"CRITICAL ANOMALY BREACH detected via manual injection ({metric_input})!"
        else:
            stats["status_message"] = f"Manual entry '{metric_input}' passed all statistical safety metrics."
    else:
        stats["status_message"] = f"GATEWAY SECURITY REJECTION: {response['message']}"
        
    return client_dashboard_view()

@app.get("/download_log")
def download_audit_trail():
    """Allows client to securely export their compliance audit trail with 1 click."""
    if os.path.exists(gateway.log_filename):
        return FileResponse(gateway.log_filename, media_type="text/csv", filename=gateway.log_filename)
    raise HTTPException(status_code=404, detail="Audit log file empty or not yet generated.")

@app.get("/", response_class=HTMLResponse)
def client_dashboard_view():
    status_color = "#10b981" if "CRITICAL" not in stats["status_message"] and "REJECTION" not in stats["status_message"] else "#ef4444"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Guardian Premium Control Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #0f172a;
                color: #f8fafc;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }}
            .container {{ max-width: 850px; width: 100%; }}
            .header {{ text-align: center; margin-bottom: 35px; }}
            .header h1 {{ font-size: 2.3rem; color: #38bdf8; margin: 0 0 8px 0; font-weight: 800; letter-spacing: -0.025em; }}
            .header p {{ color: #94a3b8; margin: 0; font-size: 1.05rem; }}
            .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 28px; margin-bottom: 24px; }}
            .status-badge {{ background-color: #10b981; color: white; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 24px 0; }}
            .stat-card {{ background: #0f172a; border: 1px solid #334155; padding: 18px; border-radius: 12px; text-align: center; }}
            .stat-label {{ font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }}
            .stat-val {{ font-size: 1.75rem; font-weight: 700; color: #f1f5f9; font-family: monospace; }}
            .console-log {{ background: #020617; border-left: 4px solid {status_color}; font-family: monospace; padding: 16px; border-radius: 8px; color: #e2e8f0; margin-top: 15px; font-size: 0.95rem; }}
            .input-group {{ display: flex; gap: 10px; margin-top: 15px; }}
            input[type="text"] {{ flex: 1; background: #0f172a; border: 1px solid #475569; padding: 12px 16px; border-radius: 8px; color: white; font-size: 1rem; }}
            button {{ background: #0284c7; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem; transition: background 0.2s; }}
            button:hover {{ background: #0369a1; }}
            .btn-secondary {{ background: #334155; margin-top: 10px; display: inline-block; text-decoration: none; color: white; padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; text-align: center; }}
            .btn-secondary:hover {{ background: #475569; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>DATA GUARDIAN CONTROL CENTER</h1>
                <p>Enterprise Statistical Drift & Validation Engine</p>
            </div>
            
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="margin: 0; font-size: 1.35rem; color: #f1f5f9;">Engine Metrics & Live Analytics</h2>
                    <span class="status-badge">System Ready</span>
                </div>
                
                <div class="stat-grid">
                    <div class="stat-card"><div class="stat-label">Total Verified</div><div class="stat-val" style="color: #38bdf8;">{stats["total_processed"]}</div></div>
                    <div class="stat-card"><div class="stat-label">Anomalies Isolated</div><div class="stat-val" style="color: #f43f5e;">{stats["anomalies_detected"]}</div></div>
                    <div class="stat-card"><div class="stat-label">Last Checked Value</div><div class="stat-val">{stats["last_value"]:.2f}</div></div>
                    <div class="stat-card"><div class="stat-label">Current Floor</div><div class="stat-val" style="color: #a855f7;">{gateway.engine.floor:.2f}</div></div>
                </div>

                <div class="stat-label">System Feed Monitor Activity:</div>
                <div class="console-log">&gt;_ {stats["status_message"]}</div>
            </div>

            <div class="card">
                <h3 style="margin: 0 0 10px 0; color: #f1f5f9; font-size: 1.2rem;">Manual Real-Time Processing Gate</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0 0 15px 0;">Inject data points instantly to test structural engine drift or test security validation bypass filters manually.</p>
                <form action="/manual_submit" method="post" class="input-group">
                    <input type="text" name="metric_input" placeholder="e.g., 10.5, 45.2, or 'CORRUPTED_TEXT'" required autocomplete="off">
                    <button type="submit">Process Metric</button>
                </form>
            </div>

            <div style="text-align: center;">
                <a href="/download_log" class="btn-secondary">📥 Export Corporate CSV Audit Trail</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
