import subprocess
import re
from streaming_guardian.detectors.framework_core import AbstractMeasurementLayer

class LiveNetworkMeasurementStream(AbstractMeasurementLayer):
    """
    Real-world Network Latency Harvester. Sends a live network ping 
    to extract actual, messy, non-stationary network telemetry.
    """
    def __init__(self):
        # Google's public DNS is highly reliable for latency testing
        self.target = "8.8.8.8" 
        
    def fetch_raw_data(self):
        try:
            # Run a standard shell ping command: 1 packet, 1-second timeout
            cmd = ["ping", "-c", "1", "-W", "1", self.target]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            
            # Extract the actual milliseconds response using regex
            match = re.search(r"time=([\d\.]+)\s+ms", output)
            if match:
                return float(match.group(1))
        except Exception:
            # If the network drops a packet completely, return a high penalty value
            return 150.0
            
        return 20.0
