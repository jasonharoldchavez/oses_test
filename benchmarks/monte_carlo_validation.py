import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter, LinearModel, MeanRevModel
def run_monte_carlo(iterations=100):
    router = ContinuousEnsembleRouter()
    lin_model = LinearModel()
    mr_model = MeanRevModel()
    results = {'decay_router': [], 'decay_linear': [], 'decay_mr': []}
    print('=' * 80)
    print(f'RUNNING MONTE CARLO VALIDATION ({iterations} RANDOM SEEDS)')
    print('=' * 80)
    for seed in range(iterations):
        np.random.seed(seed)
        t = np.linspace(0, 20, 50)
        noise = np.random.normal(0, 0.5, 50)
        decay_stream = (50 * np.exp(-0.2 * t) + noise).tolist()
        r_errs, l_errs, m_errs = [], [], []
        for i in range(15, len(decay_stream)):
            window = decay_stream[:i]
            target = decay_stream[i]
            r_pred, _, _, _ = router.blend_and_forecast(window)
            l_pred = lin_model.predict(window)
            m_pred = mr_model.predict(window)
            r_errs.append(abs(r_pred - target))
            l_errs.append(abs(l_pred - target))
            m_errs.append(abs(m_pred - target))
        results['decay_router'].append(np.mean(r_errs))
        results['decay_linear'].append(np.mean(l_errs))
        results['decay_mr'].append(np.mean(m_errs))
    print('EXPONENTIAL DECAY AGGREGATE METRICS:')
    print(f"  Router MAE:   {np.mean(results['decay_router']):.3f} (sigma: +/-{np.std(results['decay_router']):.3f})")
    print(f"  Linear MAE:   {np.mean(results['decay_linear']):.3f} (sigma: +/-{np.std(results['decay_linear']):.3f})")
    print(f"  Mean-Rev MAE: {np.mean(results['decay_mr']):.3f} (sigma: +/-{np.std(results['decay_mr']):.3f})")
    print('=' * 80)
if __name__ == '__main__':
    run_monte_carlo(100)
