import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter, LinearModel, MeanRevModel
from benchmarks.baselines import PersistenceModel, EWMAModel

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
    pers_model = PersistenceModel()
    ewma_model = EWMAModel(alpha=0.3)
    
    print('=' * 115)
    print('DYNAMIC ORACLE REGRET ANALYSIS & FORECASTING EFFICIENCY MATRIX')
    print('=' * 115)
    for name, stream in scenarios.items():
        router_loss = 0.0
        dynamic_oracle_loss = 0.0
        
        for i in range(10, len(stream)):
            window = stream[:i]
            target = stream[i]
            
            r_pred, _ = router.blend_and_forecast(window)
            
            l_err = abs(lin_model.predict(window) - target)
            m_err = abs(mr_model.predict(window) - target)
            p_err = abs(pers_model.predict(window) - target)
            e_err = abs(ewma_model.predict(window) - target)
            r_err = abs(r_pred - target)
            
            router_loss += r_err
            # Dynamic Oracle: Always selects the single absolute best error at step t
            dynamic_oracle_loss += min(l_err, m_err, p_err, e_err)
            
        n_steps = len(stream) - 10
        router_mae = router_loss / n_steps
        
        # Calculate dynamic regret and efficiency metric
        dynamic_regret = router_loss - dynamic_oracle_loss
        oracle_efficiency = dynamic_oracle_loss / (router_loss + 1e-5)
        
        print(f'{name:<15} | Router MAE: {router_mae:.3f} | Dynamic Oracle Regret: {dynamic_regret:+.3f} | Oracle Efficiency (eta): {oracle_efficiency:.3f}')
    print('=' * 115)

if __name__ == '__main__':
    run_macro_assessment()
