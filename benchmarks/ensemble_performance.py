import numpy as np
class LinearModel:
    def predict(self, history):
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * len(history)) + intercept
class MeanRevModel:
    def predict(self, history):
        return np.mean(history)
class PerformanceWeightedRouter:
    def __init__(self):
        self.linear = LinearModel()
        self.mean_rev = MeanRevModel()
        self.lin_error_weight = 1.0
        self.mr_error_weight = 1.0
    def select_and_predict(self, history):
        lin_pred = self.linear.predict(history)
        mr_pred = self.mean_rev.predict(history)
        if len(history) > 3:
            prev_window = history[:-1]
            actual_last = history[-1]
            self.lin_error_weight = abs(self.linear.predict(prev_window) - actual_last) + 1e-5
            self.mr_error_weight = abs(self.mean_rev.predict(prev_window) - actual_last) + 1e-5
        if self.lin_error_weight < self.mr_error_weight:
            return lin_pred, 'DYNAMIC_LINEAR'
        else:
            return mr_pred, 'DYNAMIC_MEAN_REV'
def run_suite():
    print('=' * 75)
    print('EVALUATING PERFORMANCE-WEIGHTED ENSEMBLE SELECTION')
    print('=' * 75)
    router = PerformanceWeightedRouter()
    test_stream = [10.0, 10.5, 11.0, 11.5, 12.0, 11.0, 10.0, 9.0, 10.0]
    for i in range(4, len(test_stream)):
        window = test_stream[:i]
        target = test_stream[i]
        pred, mode = router.select_and_predict(window)
        error = abs(pred - target)
        print(f'Step {i}: Target={target:<4} | Chosen Model={mode:<18} | Abs Error={error:.2f}')
    print('=' * 75)
if __name__ == '__main__':
    run_suite()
