import numpy as np
from typing import Dict, Any, List

class ParametricGatingRouter:
    """
    Contextual Mixture-of-Experts Gating Router.
    Learns a parametric mapping from systemic belief states to optimal routing 
    weights using a multi-objective online loss gradient.
    """
    def __init__(self, 
                 num_experts: int, 
                 feature_keys: List[str], 
                 learning_rate: float = 0.02, 
                 weights_config: Dict[str, float] = None):
        
        self.num_experts = num_experts
        self.feature_keys = feature_keys
        self.eta = learning_rate
        self.num_features = len(feature_keys) + 1
        self.theta = np.zeros((self.num_features, self.num_experts), dtype=np.float64)
        self.prev_weights = np.ones(num_experts, dtype=np.float64) / num_experts
        self.c = weights_config or {
            "mae": 0.5,
            "regret": 0.2,
            "switch": 0.2,
            "entropy": 0.1
        }
        self.eps = 1e-15

    def _extract_context_vector(self, belief: Dict[str, float]) -> np.ndarray:
        x = [1.0]
        for key in self.feature_keys:
            x.append(belief.get(key, 0.0))
        return np.array(x, dtype=np.float64)

    def _compute_softmax(self, logits: np.ndarray) -> np.ndarray:
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / (np.sum(exp_logits) + self.eps)

    def predict(self, expert_predictions: np.ndarray, belief: Dict[str, float]) -> float:
        x = self._extract_context_vector(belief)
        logits = np.dot(x, self.theta)
        weights = self._compute_softmax(logits)
        return float(np.dot(weights, expert_predictions))

    def update(self, expert_predictions: np.ndarray, target: float, belief: Dict[str, float]) -> Dict[str, Any]:
        x = self._extract_context_vector(belief)
        logits = np.dot(x, self.theta)
        weights = self._compute_softmax(logits)
        
        expert_errors = np.abs(expert_predictions - target)
        system_pred = np.dot(weights, expert_predictions)
        system_error = np.abs(system_pred - target)
        
        g_mae = np.sign(system_pred - target) * expert_predictions
        g_regret = expert_errors - system_error
        g_switch = weights - self.prev_weights
        g_entropy = np.log(weights + self.eps) + 1.0
        
        g_weights = (self.c["mae"] * g_mae + 
                     self.c["regret"] * g_regret + 
                     self.c["switch"] * g_switch + 
                     self.c["entropy"] * g_entropy)
        
        g_logits = weights * (g_weights - np.dot(weights, g_weights))
        grad_theta = np.outer(x, g_logits)
        
        self.theta -= self.eta * grad_theta
        self.prev_weights = weights.copy()
        
        return {
            "system_error": system_error,
            "allocation_weights": weights.copy(),
            "entropy": -np.sum(weights * np.log(weights + self.eps))
        }

if __name__ == "__main__":
    print("=" * 70)
    print("      PARAMETRIC GATING ROUTER - ONLINE SIMULATION HARNESS      ")
    print("=" * 70)
    
    np.random.seed(42)
    features = ["cusum", "confidence", "momentum", "adaptation_speed", "volatility", "disagreement"]
    router = ParametricGatingRouter(num_experts=2, feature_keys=features, learning_rate=0.03)
    
    timeline = np.zeros(60)
    timeline[:30] = np.random.normal(10.0, 0.5, size=30)
    timeline[30:] = np.random.normal(25.0, 0.5, size=30)
    
    print("Step   | Target  | Exp0 Wt | Exp1 Wt | Sys MAE  | Context Signal Profile")
    print("-" * 70)
    
    running_error = []
    for t in range(1, len(timeline)):
        target = timeline[t]
        prev_val = timeline[t-1]
        
        exp0_pred = 0.9 * prev_val + 1.0 if t < 30 else 10.0
        exp1_pred = prev_val + (15.0 if t == 30 else 0.0)
        expert_preds = np.array([exp0_pred, exp1_pred])
        
        is_shock = 1.0 if t >= 30 else 0.0
        belief = {
            "cusum": 8.5 * is_shock + np.random.uniform(0, 0.2),
            "confidence": 0.9 if t < 30 else 0.2,
            "momentum": 0.0 if t != 30 else 15.0,
            "adaptation_speed": 0.1 if t < 30 else 0.8,
            "volatility": 0.2 if t < 30 else 3.5,
            "disagreement": np.abs(exp0_pred - exp1_pred)
        }
        
        sys_pred = router.predict(expert_preds, belief)
        metrics = router.update(expert_preds, target, belief)
        running_error.append(metrics["system_error"])
        w = metrics["allocation_weights"]
        
        if t % 5 == 0 or t in [30, 31, 32]:
            marker = "  SHOCK" if t == 30 else ""
            print(f"{t:<6} | {target:<7.2f} | {w[0]:<7.3f} | {w[1]:<7.3f} | {metrics['system_error']:<8.3f} | CUSUM={belief['cusum']:.2f}, Vol={belief['volatility']:.1f}{marker}")
            
    print("-" * 70)
    print(f"Simulation Finished. Cumulative Evaluated MAE: {np.mean(running_error):.4f}")
    print("=" * 70)
