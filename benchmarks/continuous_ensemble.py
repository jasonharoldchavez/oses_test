import numpy as np
class LinearModel:
    def predict(self, history):
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * len(history)) + intercept
class MeanRevModel:
    def predict(self, history):
        return np.mean(history)
class ContinuousEnsembleRouter:
    def __init__(self):
        self.linear = LinearModel()
        self.mean_rev = MeanRevModel()
    def blend_and_forecast(self, history):
        lin_pred = self.linear.predict(history)
        mr_pred = self.mean_rev.predict(history)
        if len(history) <= 3:
            return (lin_pred + mr_pred) / 2, 0.5, 0.5, 1.0
        prev_window = history[:-1]
        actual_last = history[-1]
        lin_err = abs(self.linear.predict(prev_window) - actual_last) + 1e-5
        mr_err = abs(self.mean_rev.predict(prev_window) - actual_last) + 1e-5
        inv_lin = 1.0 / lin_err
        inv_mr = 1.0 / mr_err
        total_inv = inv_lin + inv_mr
        w_lin = inv_lin / total_inv
        w_mr = inv_mr / total_inv
        blended_forecast = (w_lin * lin_pred) + (w_mr * mr_pred)
        expected_error = (w_lin * lin_err) + (w_mr * mr_err)
        return blended_forecast, w_lin, w_mr, expected_error
def run_continuous_suite():
    print('=' * 80)
    print('RUNNING CONTINUOUS PERFORMANCE-WEIGHTED ENSEMBLE')
    print('=' * 80)
    router = ContinuousEnsembleRouter()
    test_stream = [10.0, 10.5, 11.0, 11.5, 12.0, 11.0, 10.0, 9.0, 10.0]
    for i in range(4, len(test_stream)):
        window = test_stream[:i]
        target = test_stream[i]
        pred, wl, wmr, exp_err = router.blend_and_forecast(window)
        act_err = abs(pred - target)
        print(f'Step {i} | Forecast: {pred:.2f} (Exp Err: +/-{exp_err:.2f}) | Act Err: {act_err:.2f} | W_Lin: {wl:.2f} | W_MR: {wmr:.2f}')
    print('=' * 80)
if __name__ == '__main__':
    run_continuous_suite()
