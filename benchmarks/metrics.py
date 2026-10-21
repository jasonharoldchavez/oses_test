"""Metric helpers that keep trial-level and sample-level denominators distinct."""
import math
from numbers import Integral


def summarize_trials(num_trials, change_point, false_alarm_counts, detection_delays):
    """Summarize one scenario.

    false_alarm_counts has one non-negative integer count per trial for alarms
    observed strictly before the known change point. detection_delays contains
    one non-negative delay for each trial that had a post-change detection.
    """
    if isinstance(num_trials, bool) or not isinstance(num_trials, Integral) or num_trials < 1:
        raise ValueError("num_trials must be a positive integer.")
    if isinstance(change_point, bool) or not isinstance(change_point, Integral) or change_point < 1:
        raise ValueError("change_point must be a positive integer.")
    if len(false_alarm_counts) != num_trials:
        raise ValueError("false_alarm_counts must contain one entry per trial.")
    if any(isinstance(n, bool) or not isinstance(n, Integral) or n < 0 for n in false_alarm_counts):
        raise ValueError("false-alarm counts must be non-negative integers.")
    if any(isinstance(d, bool) or not isinstance(d, Integral) or d < 0 for d in detection_delays):
        raise ValueError("detection delays must be non-negative integers.")
    if len(detection_delays) > num_trials:
        raise ValueError("detection delays cannot exceed the number of trials.")

    false_alarm_trials = sum(n > 0 for n in false_alarm_counts)
    false_alarm_samples = sum(false_alarm_counts)
    detected_trials = len(detection_delays)
    return {
        "false_alarm_trial_probability": false_alarm_trials / num_trials,
        "false_alarm_sample_rate": false_alarm_samples / (num_trials * change_point),
        "detection_probability": detected_trials / num_trials,
        "mean_delay_given_detection": (
            sum(detection_delays) / detected_trials if detected_trials else math.nan
        ),
        "false_alarm_trials": false_alarm_trials,
        "false_alarm_samples": false_alarm_samples,
        "detected_trials": detected_trials,
        "total_trials": int(num_trials),
        "pre_change_samples": int(num_trials * change_point),
    }



def wilson_interval(successes, total, z=1.96):
    """Return a two-sided Wilson score interval for a binomial proportion."""
    import math
    from numbers import Real

    if isinstance(successes, bool) or not isinstance(successes, Integral):
        raise ValueError("successes must be an integer.")
    if isinstance(total, bool) or not isinstance(total, Integral) or total < 1:
        raise ValueError("total must be a positive integer.")
    if successes < 0 or successes > total:
        raise ValueError("successes must be between zero and total.")
    if isinstance(z, bool) or not isinstance(z, Real) or not math.isfinite(float(z)) or z <= 0:
        raise ValueError("z must be a positive finite real number.")

    n = float(total)
    p = successes / n
    z2 = float(z) ** 2
    denominator = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denominator
    margin = (float(z) * math.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * n * n)))) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)
