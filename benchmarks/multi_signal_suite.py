import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter, LinearModel, MeanRevModel
def generate_scenarios():
    np.random.seed(42)
    scenarios = {}
    t = np.linspace(0, 10, 50)
    scenarios['pure_trend'] = (t * 1.5 + 10.0 + np.random.normal(0, 0.1, 50)).tolist()
    scenarios['step_change'] = ([10.0]*25 + [20.0]*25 + np.random.normal(0, 0.1, 50)).tolist()
    scenarios['random_walk'] = np.cumsum(np.random.normal(0, 0.5, 50) + 0.1).tolist()
    return scenarios
def run_macro_assessment():
    scenarios = generate_scenarios()
    router = ContinuousEnsembleRouter()
    lin_model = LinearModel()
    mr_model = MeanRevModel()
    print('=' * 75)
    print('MACRO-LEVEL MULTI-SIGNAL EVALUATION SUITE')
    print('=' * 75)
    for name, stream in scenarios.items():
        router_errors, lin_errors, mr_errors = [], [], []
        for i in range(10, len(stream)):
            window = stream[:i]
            target = stream[i]
            r_pred, _, _, _ = router.blend_and_forecast(window)
            l_pred = lin_model.predict(window)
            m_pred = mr_model.predict(window)
            router_errors.append(abs(r_pred - target))
            lin_errors.append(abs(l_pred - target))
            mr_errors.append(abs(m_pred - target))
        print(f'{name:<15} | Router MAE: {np.mean(router_errors):.3f} | Linear MAE: {np.mean(lin_errors):.3f} | Mean-Rev MAE: {np.mean(mr_errors):.3f}')
    print('=' * 75)
if __name__ == '__main__':
    run_macro_assessment()
