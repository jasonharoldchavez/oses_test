import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter, LinearModel, MeanRevModel

def monte_carlo_permutation_p_value(a, b, num_permutations=5000):
    a, b = np.array(a), np.array(b)
    observed_diff = np.mean(a - b)
    paired_diffs = a - b
    n = len(paired_diffs)
    extreme_count = 0
    np.random.seed(42)
    for _ in range(num_permutations):
        signs = np.random.choice([-1, 1], size=n)
        perm_diff = np.mean(paired_diffs * signs)
        if np.abs(perm_diff) >= np.abs(observed_diff):
            extreme_count += 1
    p_val = extreme_count / num_permutations
    return p_val

def run_rigorous_matrix(trials=50):
    router = ContinuousEnsembleRouter()
    lin = LinearModel()
    mr = MeanRevModel()
    scenarios = ['exp_decay', 'seasonal_wave']
    print('=' * 95)
    print(f'RUNNING RIGOROUS STATISTICAL MATRIX ({trials} TRIALS WITH 95% CI & MC PERMUTATION TEST)')
    print('=' * 95)
    for scn in scenarios:
        r_maes, l_maes, m_maes = [], [], []
        r_rmses, l_rmses, m_rmses = [], [], []
        for seed in range(trials):
            np.random.seed(seed)
            t = np.linspace(0, 15, 40)
            noise = np.random.normal(0, 0.4, 40)
            if scn == 'exp_decay':
                stream = (40 * np.exp(-0.25 * t) + noise).tolist()
            else:
                stream = (np.sin(t) * 4 + 12 + noise).tolist()
            r_errs, l_errs, m_errs = [], [], []
            for i in range(12, len(stream)):
                w = stream[:i]; target = stream[i]
                rp, _, _, _ = router.blend_and_forecast(w)
                r_errs.append(abs(rp - target))
                l_errs.append(abs(lin.predict(w) - target))
                m_errs.append(abs(mr.predict(w) - target))
            r_maes.append(np.mean(r_errs)); r_rmses.append(np.sqrt(np.mean(np.array(r_errs)**2)))
            l_maes.append(np.mean(l_errs)); l_rmses.append(np.sqrt(np.mean(np.array(l_errs)**2)))
            m_maes.append(np.mean(m_errs)); m_rmses.append(np.sqrt(np.mean(np.array(m_errs)**2)))
        best_baseline = l_maes if np.mean(l_maes) < np.mean(m_maes) else m_maes
        p_val = monte_carlo_permutation_p_value(r_maes, best_baseline, 5000)
        p_str = f"p < {1/5000:.4f}" if p_val == 0 else f"p = {p_val:.4f}"
        def calc_ci(data):
            return 1.96 * (np.std(data) / np.sqrt(len(data)))
        print(f'Scenario: {scn.upper()}')
        print(f'  Router MAE: {np.mean(r_maes):.3f} (+/-{calc_ci(r_maes):.3f}) | RMSE: {np.mean(r_rmses):.3f}')
        print(f'  Linear MAE: {np.mean(l_maes):.3f} (+/-{calc_ci(l_maes):.3f}) | RMSE: {np.mean(l_rmses):.3f}')
        print(f'  Mean-R MAE: {np.mean(m_maes):.3f} (+/-{calc_ci(m_maes):.3f}) | RMSE: {np.mean(m_rmses):.3f}')
        print(f'  Monte Carlo Permutation Significance (Router vs Best Baseline): {p_str} ' + ('(SIGNIFICANT)' if p_val < 0.05 else '(NOT SIGNIFICANT)'))
        print('-' * 95)

if __name__ == '__main__':
    run_rigorous_matrix(50)
