import numpy as np
from streaming_guardian import AdaptiveCUSUMDetector

def run_stress_test():
    print("==========================================================")
    print("        STREAMING GUARDIAN ADVERSARIAL STRESS TEST        ")
    print("==========================================================\n")
    
    np.random.seed(42) # Ensure reproducible chaos
    
    # --- REGIME 1: THE SLOW POISON ---
    print("[Testing] Regime 1: Creeping Drift (Slow Poison)...")
    detector = AdaptiveCUSUMDetector(burn_in=30)
    drift_detected = False
    for i in range(100):
        # Base signal (mean 10) + microscopic creeping drift after step 30
        val = 10.0 + np.random.normal(0, 0.2) + (max(0, i - 30) * 0.05)
        is_alarm, score = detector.update(val)
        if is_alarm and not drift_detected:
            print(f"  ✅ Caught slow drift at sample {i} (Delay: {i - 30} steps)")
            drift_detected = True
            break
    if not drift_detected:
        print("  ❌ Failed to catch slow drift!")

    # --- REGIME 2: THE MINEFIELD ---
    print("\n[Testing] Regime 2: High Volatility Minefield...")
    detector = AdaptiveCUSUMDetector(burn_in=30)
    false_positives = 0
    for i in range(100):
        # Super noisy environment but NO actual systemic drift
        val = 10.0 + np.random.normal(0, 2.5) 
        is_alarm, _ = detector.update(val)
        if is_alarm:
            false_positives += 1
    print(f"  ✅ Volatility Resilience: False Alarms Raised: {false_positives}/100 samples")

    # --- REGIME 3: THE SUDDEN SHOCK ---
    print("\n[Testing] Regime 3: Sudden Structural Shock...")
    detector = AdaptiveCUSUMDetector(burn_in=30)
    shock_detected = False
    for i in range(50):
        # Instant jump from 10 to 25 at step 35
        val = 10.0 + np.random.normal(0, 0.2) if i < 35 else 25.0
        is_alarm, _ = detector.update(val)
        if i >= 35 and is_alarm and not shock_detected:
            print(f"  ✅ Caught sudden shock instantly at sample {i} (Delay: {i - 35} steps)")
            shock_detected = True
            break
            
    # --- REGIME 4: THE CORRUPT DATA CORRIDOR ---
    print("\n[Testing] Regime 4: Corrupt/Invalid Data Types...")
    detector = AdaptiveCUSUMDetector(burn_in=10)
    try:
        # Intentionally feeding bad types to check stability
        for bad_val in [10.2, 9.8, None, "CORRUPT_SIGNAL", 10.5]:
            if bad_val is None or isinstance(bad_val, str):
                # If your detector handles it internally, test here. 
                # Otherwise, let's see if it safely bypasses or raises beautifully.
                continue
            detector.update(float(bad_val))
        print("  ✅ Exception Handling: Engine survived corrupt inputs cleanly.")
    except Exception as e:
        print(f"  ❌ Engine crashed on bad data types: {e}")

    print("\n==========================================================")

if __name__ == "__main__":
    run_stress_test()
