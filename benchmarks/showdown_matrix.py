import numpy as np
class LinearEngine:
    def forecast(self, history, horizon):
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * (len(history) + horizon)) + intercept
class MeanReversionEngine:
    def forecast(self, history, horizon):
        return np.mean(history)
class AdaptiveRouter:
    def __init__(self):
        self.linear = LinearEngine()
        self.mean_rev = MeanReversionEngine()
    def select_and_forecast(self, history, horizon):
        y = np.array(history)
        mean = np.mean(y)
        zero_crossings = np.diff(y > mean).sum()
        if zero_crossings >= 2:
            return self.mean_rev.forecast(history, horizon), 'OSCILLATORY'
        else:
            return self.linear.forecast(history, horizon), 'TRENDING'
def run_showdown():
    print('=' * 80)
    print('RUNNING COMPARATIVE PERFORMANCE SHOWDOWN')
    print('=' * 80)
    trend_data = [10.0, 10.4, 10.8, 11.2, 11.6, 12.0, 12.4, 12.8]
    trend_actual = 13.2
    wave_data = [10.0, 13.0, 9.0, 12.5, 9.5, 12.0, 9.0, 11.5]
    wave_actual = 10.5
    linear_eng = LinearEngine()
    mean_eng = MeanReversionEngine()
    router = AdaptiveRouter()
    err_linear_trend = abs(linear_eng.forecast(trend_data, 1) - trend_actual)
    err_linear_wave  = abs(linear_eng.forecast(wave_data, 1) - wave_actual)
    err_mean_trend   = abs(mean_eng.forecast(trend_data, 1) - trend_actual)
    err_mean_wave    = abs(mean_eng.forecast(wave_data, 1) - wave_actual)
    rout_trend_val, _ = router.select_and_forecast(trend_data, 1)
    rout_wave_val, _  = router.select_and_forecast(wave_data, 1)
    err_rout_trend   = abs(rout_trend_val - trend_actual)
    err_rout_wave    = abs(rout_wave_val - wave_actual)
    print(f'| Steady Trend | Linear Err: {err_linear_trend:.2f} | Mean-Rev Err: {err_mean_trend:.2f} | Router Err: {err_rout_trend:.2f} |')
    print(f'| Volatile Wave| Linear Err: {err_linear_wave:.2f} | Mean-Rev Err: {err_mean_wave:.2f} | Router Err: {err_rout_wave:.2f} |')
    print('=' * 80)
if __name__ == '__main__':
    run_showdown()
