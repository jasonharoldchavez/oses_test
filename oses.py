import numpy as np
import time
import os

class OptimalStoppingScheduler:
    def __init__(self, channels=1, alpha_fa=0.01):
        self.threshold_h = np.log(1.0 / alpha_fa)  # h ≈ 4.605
        self.cusum_tracker = 0.0

    def update(self, empirical_signal, noise_floor):
        # Joint evidence accumulation
        increment = empirical_signal - noise_floor
        self.cusum_tracker = max(0.0, self.cusum_tracker + increment)
        return self.cusum_tracker > self.threshold_h, self.cusum_tracker

class JointKernelBridge:
    """Monitors the joint behavior of CPU usage and context switching."""
    def __init__(self):
        self.last_work = 0
        self.last_total = 0
        self.last_ctxt = 0
        self.refresh()

    def refresh(self):
        try:
            with open("/proc/stat", "r") as f:
                lines = f.readlines()
            
            # Parse CPU
            cpu_parts = lines[0].split()[1:5]
            fields = [float(x) for x in cpu_parts]
            work = sum(fields[:3])
            total = sum(fields)
            
            # Parse Context Switches
            ctxt = 0
            for line in lines:
                if line.startswith("ctxt"):
                    ctxt = float(line.split()[1])
                    break
                    
            diff_work = work - self.last_work
            diff_total = total - self.last_total
            diff_ctxt = ctxt - self.last_ctxt
            
            self.last_work = work
            self.last_total = total
            self.last_ctxt = ctxt
            
            cpu_pct = (diff_work / diff_total) * 100.0 if diff_total > 0 else 0.0
            return cpu_pct, diff_ctxt
        except Exception:
            return 5.0, 100.0

    def get_joint_metric(self):
        cpu_pct, ctxt_delt = self.refresh()
        # Vector Magnitude: Treating joint features as an orthogonal space
        # This protects against one signal flattening out
        return np.sqrt((cpu_pct ** 2) + ((ctxt_delt / 1000.0) ** 2))

if __name__ == "__main__":
    print("=" * 60)
    print("        JOINT BEHAVIOR ANOMALY DETECTION ENGINE         ")
    print("=" * 60)
    
    bridge = JointKernelBridge()
    detector = OptimalStoppingScheduler(alpha_fa=0.01)
    
    # Restricting baseline contamination: Using clean historical constraints
    # instead of a hyper-volatile initialization window
    clean_historical_noise_floor = 12.0
    print(f"Operational Multi-Dimensional Noise Floor: {clean_historical_noise_floor:.2f}")
    print(f"Safety Threshold (h):                     {detector.threshold_h:.3f}")
    print("-" * 60)
    
    anomaly_triggered = False
    
    for step in range(1, 40):
        time.sleep(0.1)
        
        # Pull the multi-dimensional joint feature
        joint_signal = bridge.get_joint_metric()
        
        # At step 20, we simulate a heavy multi-threaded application shift 
        # by passing an unmitigated joint system state change
        if step >= 20:
            observed_signal = joint_signal + 15.0
        else:
            observed_signal = joint_signal
            
        alarm, score = detector.update(observed_signal, clean_historical_noise_floor)
        
        if step % 5 == 0 or alarm:
            print(f"Step {step:02d} | Joint Signal Vector: {observed_signal:.2f} | CUSUM: {score:.3f}")
            
        if alarm:
            print(f"\n[ALERT] Joint behavioral deviation verified at Step {step}!")
            anomaly_triggered = True
            break
            
    print("-" * 60)
    print("=" * 60)

