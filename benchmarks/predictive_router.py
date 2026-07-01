import numpy as np
import time

class AdaptiveStrategyRouter:
    def __init__(self):
        self.history = []
        print("[SYSTEM COUPE] Adaptive Strategy Router Online.")

    def extract_features(self):
        if len(self.history) < 5:
            return None
        
        y = np.array(self.history)
        # Feature Vector F mapping
        mean = np.mean(y)
        variance = np.var(y)
        
        # Calculate a basic directional drift velocity
        drift_rate = y[-1] - y[0]
        
        # Calculate a basic oscillation metric (mean crossing frequency)
        zero_crossings = np.diff(y > mean).sum()
        
        return {
            "variance": variance,
            "drift_rate": drift_rate,
            "crossings": zero_crossings
        }

    def route_and_forecast(self, current_val):
        self.history.append(current_val)
        if len(self.history) > 30:
            self.history.pop(0)
            
        features = self.extract_features()
        if not features:
            return "INITIALIZING", 5, current_val

        # 1. DYNAMIC STRATEGY SELECTION
        # High crossing frequencies imply oscillatory behavior; high variance with low crossings implies a regime drift.
        if features["crossings"] >= 2:
            strategy = "OSCILLATORY (Fourier/Mean-Reversion)"
            # Horizon adapts: compress prediction horizon because oscillatory data shifts quickly
            horizon = 4 
            # Forecast matches local mean historical bounds
            forecasted_val = np.mean(self.history)
        else:
            strategy = "TRENDING (Linear/Regression)"
            # Horizon adapts: extend horizon because steady trends are highly predictable
            horizon = 12 
            x = np.arange(len(self.history))
            slope, intercept = np.polyfit(x, self.history, 1)
            forecasted_val = (slope * (len(self.history) + horizon)) + intercept

        return strategy, horizon, forecasted_val

def run_strategy_arena():
    print("=" * 75)
    print("🧠 DEPLOYING ADAPTIVE STRATEGY ROUTER (VERSION 2)")
    print("=" * 75)
    
    router = AdaptiveStrategyRouter()
    
    # Dataset A: A clean, steady upward industrial trend
    industrial_stream = [10.0, 10.3, 10.5, 10.8, 11.1, 11.4, 11.7, 12.0]
    # Dataset B: A volatile, fluctuating sensor wave (sine pattern)
    wave_stream = [10.0, 12.0, 9.0, 11.5, 9.5, 12.0, 9.0, 11.0]
    
    print("\n📈 TESTING SCENARIO 1: Steady Directional Trend")
    for val in industrial_stream:
        strat, hor, fc = router.route_and_forecast(val)
        print(f"Input: {val:<4} | Selected Engine: {strat:<35} | Horizon: +{hor:<2} | Est: {fc:.2f}")
        
    print("\n🔄 TESTING SCENARIO 2: Sudden Oscillatory Signal Burst")
    router.history = [] # Reset pipeline history for test block
    for val in wave_stream:
        strat, hor, fc = router.route_and_forecast(val)
        print(f"Input: {val:<4} | Selected Engine: {strat:<35} | Horizon: +{hor:<2} | Est: {fc:.2f}")
    print("=" * 75)

if __name__ == "__main__":
    run_strategy_arena()
