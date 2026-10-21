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



def classify_first_alarms(first_alarm_indices, change_point, stream_length):
    """Classify trials by their first alarm, avoiding false-alarm/detection double counting.

    An alarm before the known change point classifies that trial as a false-alarm
    trial. A later alarm in that same trial is not counted as a successful
    detection, because the detector had already alarmed before the change.
    """
    if isinstance(change_point, bool) or not isinstance(change_point, Integral) or change_point < 1:
        raise ValueError("change_point must be a positive integer.")
    if isinstance(stream_length, bool) or not isinstance(stream_length, Integral) or stream_length <= change_point:
        raise ValueError("stream_length must be an integer greater than change_point.")
    if not isinstance(first_alarm_indices, (list, tuple)):
        raise ValueError("first_alarm_indices must be a list or tuple.")
    for index in first_alarm_indices:
        if index is None:
            continue
        if isinstance(index, bool) or not isinstance(index, Integral) or not 0 <= index < stream_length:
            raise ValueError("Each first alarm index must be None or an in-range integer.")

    false_alarm_trials = sum(index is not None and index < change_point for index in first_alarm_indices)
    detection_delays = [
        int(index - change_point)
        for index in first_alarm_indices
        if index is not None and index >= change_point
    ]
    no_alarm_trials = sum(index is None for index in first_alarm_indices)
    return {
        "false_alarm_trials": false_alarm_trials,
        "detection_delays": detection_delays,
        "detected_trials": len(detection_delays),
        "no_alarm_trials": no_alarm_trials,
        "total_trials": len(first_alarm_indices),
    }
