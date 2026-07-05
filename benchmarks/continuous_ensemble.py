import numpy as np
from benchmarks.baselines import PersistenceModel, EWMAModel, AR1Model

class LinearModel:
    def predict(self, history):
        if len(history) < 2:
            return history[-1] if len(history) > 0 else 0.0
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * len(history)) + intercept

class MeanRevModel:
    def predict(self, history):
        return np.mean(history) if len(history) > 0 else 0.0

class ContinuousEnsembleRouter:
    def __init__(self, hazard_rate=0.1, process_sigma=0.5):
        self.models = {
            "LINEAR": LinearModel(),
            "MEAN_REV": MeanRevModel(),
            "PERSISTENCE": PersistenceModel(),
            "EWMA": EWMAModel(alpha=0.3),
            "AR1": AR1Model()
        }
        self.alpha = hazard_rate
        self.sigma = process_sigma
        self.model_names = list(self.models.keys())
        # Track the raw recursive belief vector over models
        self.beliefs = np.array([1.0 / len(self.models)] * len(self.models))
        
    def blend_and_forecast(self, history):
        # Calculate raw forecasts from all underlying experts
        preds = {name: mdl.predict(history) for name, mdl in self.models.items()}
        
        if len(history) <= 2:
            w_dict = {name: 1.0 / len(self.models) for name in self.models}
            return sum(preds.values()) / len(self.models), w_dict
            
        actual_last = history[-1]
        prev_window = history[:-1]
        
        # Calculate the recursive internal knowledge step (Predictive Likelihood)
        likelihoods = []
        for name in self.model_names:
            pred_last = self.models[name].predict(prev_window)
            error = actual_last - pred_last
            
            # Evaluate Gaussian error density
            lh = np.exp(-0.5 * (error / self.sigma) ** 2) / (self.sigma * np.sqrt(2 * np.pi))
            likelihoods.append(max(lh, 1e-15))
            
        likelihoods = np.array(likelihoods)
        
        # Evolution Step: Apply hazard matrix transition (Growth vs Collapse)
        growth_component = (1.0 - self.alpha) * self.beliefs
        collapse_component = (self.alpha / len(self.models))
        
        # Resolution Step: Form the unnormalized posterior belief profile
        posterior = likelihoods * (growth_component + collapse_component)
        
        # Integration Step: Normalize safely back to a proper distribution
        total_post = np.sum(posterior)
        if total_post > 0:
            self.beliefs = posterior / total_post
        else:
            self.beliefs = np.array([1.0 / len(self.models)] * len(self.models))
            
        weights = {self.model_names[i]: self.beliefs[i] for i in range(len(self.models))}
        blended_forecast = sum(preds[name] * weights[name] for name in self.models)
        
        return blended_forecast, weights
