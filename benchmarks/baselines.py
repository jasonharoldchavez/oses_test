import numpy as np

class PersistenceModel:
    def predict(self, history):
        if len(history) == 0:
            return 0.0
        return history[-1]

class EWMAModel:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
    def predict(self, history):
        if len(history) == 0:
            return 0.0
        ewma = history[0]
        for val in history[1:]:
            ewma = self.alpha * val + (1.0 - self.alpha) * ewma
        return ewma

class AR1Model:
    def predict(self, history):
        if len(history) < 5:
            return history[-1] if len(history) > 0 else 0.0
        # Fit y_t = c + phi * y_{t-1} using basic least squares
        y = np.array(history[1:])
        x = np.array(history[:-1])
        A = np.vstack([x, np.ones(len(x))]).T
        try:
            phi, c = np.polyfit(x, y, 1)
            return c + phi * history[-1]
        except:
            return history[-1]
