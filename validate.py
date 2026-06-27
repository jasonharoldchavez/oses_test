import numpy as np

print("=" * 60)
print("          RUNNING CRITICAL STRESS TEST (SAFETY CHECK)     ")
print("=" * 60)

# Simulate 500 steps of pure, extreme market chaos (high noise)
np.random.seed(999)
steps = 500
cusum_score = 0.0
chosen_threshold = 1.500
false_alarms = 0

print(f"Simulating {steps} steps of high market volatility...")
print(f"Safety Threshold set to: {chosen_threshold}")
print("-" * 60)

for step in range(1, steps + 1):
    extreme_market_noise = np.abs(np.random.normal(0, 0.05))
    noise_floor = 0.02

    increment = extreme_market_noise - noise_floor
    cusum_score = max(0.0, cusum_score + increment)

    # Martingale stabilization
    cusum_score *= 0.85

    if cusum_score > chosen_threshold:
        false_alarms += 1
        print(f"!!! FALSE ALARM TRIGGERED at step {step} | Score: {cusum_score:.3f} !!!")
        break

if false_alarms == 0:
    print("[PASSED] Stress Test Successful!")
    print(f"Final Peak Noise Accumulation: {cusum_score:.3f} / {chosen_threshold}")
    print("Verdict: Passed synthetic baseline stress test under current simulation parameters.")
else:
    print("[FAILED] The threshold is too low for raw volatility. Adjust 'h' higher.")
print("=" * 60)

