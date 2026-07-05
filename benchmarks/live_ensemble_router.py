import numpy as np
import time
from scenarios.system_metrics import LiveNetworkMeasurementStream
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter
from benchmarks.gating_router import ParametricGatingRouter
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector

if __name__ == "__main__":
    print("=" * 95)
    print("   LAUNCHING PRODUCTION-GRADE LIVE ENSEMBLE ROUTER (REAL-TIME NETWORK SUITE)")
    print("=" * 95)
    
    stream = LiveNetworkMeasurementStream()
    
    # Initialize the continuous Bayesian ensemble
    ensemble = ContinuousEnsembleRouter(hazard_rate=0.05, process_sigma=1.5)
    
    # Initialize the parametric context-aware gating router
    features = ["cusum", "volatility", "raw_ping"]
    gating_router = ParametricGatingRouter(num_experts=2, feature_keys=features, learning_rate=0.04)
    
    # Track baseline state using our adaptive engine
    adp_detector = AdaptiveCUSUMDetector(burn_in=15)
    
    print("Gathering live network statistics to prime the routing engine...")
    history = []
    for _ in range(15):
        ping = stream.fetch_raw_data()
        history.append(ping)
        _, _ = adp_detector.update(ping)
        
    print("\nMonitoring live environment. Routing engine fully armed. Press Ctrl+C to halt.")
    print("-" * 95)
    print(f"{'Tick':<6} | {'Ping (ms)':<10} | {'Blended Forecast':<18} | {'Top Model Allocation':<28} | {'Gating State'}")
    print("-" * 95)
    
    try:
        for tick in range(1, 31):
            ping_val = stream.fetch_raw_data()
            history.append(ping_val)
            
            # 1. Update the Adaptive Detection layer to extract context signals
            _, cusum_track = adp_detector.update(ping_val)
            rolling_vol = float(np.std(history[-10:]))
            
            # 2. Compute the Bayesian Blended Forecast
            blended_pred, weights = ensemble.blend_and_forecast(history)
            
            # Find the current strongest model chosen by the Bayesian engine
            top_model = max(weights, key=weights.get)
            top_weight = weights[top_model]
            
            # 3. Feed the current environmental context into the Parametric Gating Router
            context_belief = {
                "cusum": cusum_track,
                "volatility": rolling_vol,
                "raw_ping": ping_val
            }
            
            # Simulate a 2-expert prediction vector for the gating router to choose from
            expert_preds = np.array([blended_pred, np.mean(history[-5:])])
            gated_output = gating_router.predict(expert_preds, context_belief)
            metrics = gating_router.update(expert_preds, ping_val, context_belief)
            
            # Display real-time operational routing status
            print(f"{tick:<6} | {ping_val:<10.2f} | {blended_pred:<18.2f} | {top_model:<12} ({top_weight*100:.1f}%) | Entropy: {metrics['entropy']:.3f}")
            
    except KeyboardInterrupt:
        print("\nProduction router terminated by user deployment check.")
        
    print("=" * 95)
