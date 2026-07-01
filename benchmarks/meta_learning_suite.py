import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter, LinearModel, MeanRevModel
def generate_stress_signals():
    np.random.seed(1337)
    signals = {}
    t = np.linspace(0, 20, 100)
    signals['seasonal_wave'] = (np.sin(t) * 5 + 15 + np.random.normal(0, 0.2, 100)).tolist()
    signals['exp_decay'] = (50 * np.exp(-0.2 * t) + np.random.normal(0, 0.1, 100)).tolist()
    signals['missing_data'] = (t * 0.8 + 10.0).tolist()
    for idx in [20, 21, 22, 50, 51, 52]: signals['missing_data'][idx] = np.nan
    return signals
def run_meta_learning_suite():
    signals = generate_stress_signals()
    router = ContinuousEnsembleRouter()
    lin_model = LinearModel()
    mr_model = MeanRevModel()
    confusion_matrix = {'TREND': {'TREND': 0, 'OSC': 0}, 'OSC': {'TREND': 0, 'OSC': 0}}
    print('=' * 85)
    print('ADVANCED STRESS-TESTING SUITE & REGIME CONFUSION MATRIX')
    print('=' * 85)
    for name, stream in signals.items():
        router_errors, lin_errors, mr_errors = [], [], []
        actual_regime = 'OSC' if 'wave' in name else 'TREND'
        for i in range(10, len(stream)):
            window = stream[:i]
            target = stream[i]
            if np.isnan(target) or np.any(np.isnan(window[-3:])):
                continue
            clean_window = [x for x in window if not np.isnan(x)]
            r_pred, wl, wmr, _ = router.blend_and_forecast(clean_window)
            l_pred = lin_model.predict(clean_window)
            m_pred = mr_model.predict(clean_window)
            router_errors.append(abs(r_pred - target))
            lin_errors.append(abs(l_pred - target))
            mr_errors.append(abs(m_pred - target))
            predicted_regime = 'TREND' if wl >= wmr else 'OSC'
            confusion_matrix[actual_regime][predicted_regime] += 1
        print(f'{name:<15} | Router MAE: {np.mean(router_errors):.3f} | Linear MAE: {np.mean(lin_errors):.3f} | Mean-Rev MAE: {np.mean(mr_errors):.3f}')
    print('-' * 85)
    print('REGIME CLASSIFICATION CONFUSION MATRIX:')
    print(f"  Actual TREND -> Predicted TREND: {confusion_matrix['TREND']['TREND']:<3} | Predicted OSC: {confusion_matrix['TREND']['OSC']}")
    print(f"  Actual OSC   -> Predicted TREND: {confusion_matrix['OSC']['TREND']:<3} | Predicted OSC: {confusion_matrix['OSC']['OSC']}")
    print('=' * 85)
if __name__ == '__main__':
    run_meta_learning_suite()
