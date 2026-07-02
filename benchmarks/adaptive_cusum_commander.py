import numpy as np
from benchmarks.regime_models import PersistenceModel, EWMAModel, AR1Model, LinearModel

class AdaptiveCUSUMCommander:
    def __init__(self, target_mean=0.0, target_std=1.0, k_threshold=1.5, h_decision=4.5):
        self.experts = {
            "PERSISTENCE": PersistenceModel(),
            "EWMA": EWMAModel(alpha=0.4),
            "AR1": AR1Model(),
            "LINEAR": LinearModel()
        }
        # Core Statistical State Engine
        self.mu = target_mean
        self.sigma = target_std
        self.k = k_threshold  
        self.h = h_decision   
        self.g_pos = 0.0
        self.g_neg = 0.0
        
        # Formalized Belief State Scorecard S_t
        self.scorecard = {
            "cusum_stat": 0.0,
            "confidence": 1.0,
            "momentum": 0.0,
            "adaptation_speed": 0.1,
            "active_regime": "STABLE_NORMAL"
        }
        
        # Learned Playbook Parameter Weights (Initialized Uniformly)
        self.expert_losses = {name: 0.0 for name in self.experts}

    def inspect_environment(self, history):
        if len(history) < 3:
            return
        
        latest_val = history[-1]
        z = (latest_val - self.mu) / (self.sigma + 1e-9)
        
        # Track drift metrics
        self.g_pos = max(0.0, self.g_pos + z - self.k)
        self.g_neg = max(0.0, self.g_neg - z - self.k)
        
        cusum_stat = max(self.g_pos, self.g_neg)
        self.scorecard["cusum_stat"] = cusum_stat
        
        # Calculate systemic metrics inside the belief state
        self.scorecard["confidence"] = max(0.0, 1.0 - (cusum_stat / (self.h * 1.5)))
        self.scorecard["momentum"] = self.g_pos - self.g_neg
        
        # Adaptation speed acts as a dynamic learning rate parameter \eta_t
        self.scorecard["adaptation_speed"] = 0.1 + 0.85 * (cusum_stat / (self.h + 1e-9))
        self.scorecard["adaptation_speed"] = min(0.95, self.scorecard["adaptation_speed"])

        # Operational Regime Boundary Evaluation
        if self.g_pos > self.h:
            self.scorecard["active_regime"] = "BREAKOUT_UP"
            self.g_pos = 0.0  # State engine clear/reset
        elif self.g_neg > self.h:
            self.scorecard["active_regime"] = "BREAKOUT_DOWN"
            self.g_neg = 0.0
        elif cusum_stat > (self.h * 0.4):
            self.scorecard["active_regime"] = "WARNING_ZONE"
        else:
            self.scorecard["active_regime"] = "STABLE_NORMAL"

    def route_and_predict(self, history):
        if len(history) <= 2:
            return (history[-1] if len(history) > 0 else 0.0), {n: 0.25 for n in self.experts}
            
        self.inspect_environment(history)
        regime = self.scorecard["active_regime"]
        eta = self.scorecard["adaptation_speed"]
        
        # Get raw candidate predictions
        preds = {name: exp.predict(history) for name, exp in self.experts.items()}
        
        # Online Learning Update Step (Stochastic Gradient Feedback)
        actual_latest = history[-1]
        prev_history = history[:-1]
        
        for name, exp in self.experts.items():
            try:
                # Estimate what the expert *would* have calculated last step
                prior_pred = exp.predict(prev_history)
                instant_loss = abs(prior_pred - actual_latest)
            except Exception:
                instant_loss = 2.0
            
            # Blend tracking loss using the dynamic adaptation step rate
            self.expert_losses[name] = ((1.0 - eta) * self.expert_losses[name]) + (eta * instant_loss)

        # Exponentiated Gradient allocation math (Hedge Framework)
        min_loss = min(self.expert_losses.values())
        raw_w = {}
        for name in self.experts:
            # Scale mathematical risk allocations via dynamic regime parameters
            regime_multiplier = 2.5 if regime in ["BREAKOUT_UP", "BREAKOUT_DOWN"] else 1.2
            scaled_loss = self.expert_losses[name] - min_loss
            raw_w[name] = np.exp(-regime_multiplier * scaled_loss)
            
        total_w = sum(raw_w.values()) + 1e-12
        weights = {n: w / total_w for n, w in raw_w.items()}
        
        # Compute optimized, blended projection
        final_pred = sum(preds[n] * weights[n] for n in self.experts)
        return final_pred, weights
