import csv

from streaming_guardian.detectors import AdaptiveCUSUMDetector

detector = AdaptiveCUSUMDetector(burn_in=30)

alarms = 0
in_alarm = False

with open("datasets/nab/ec2_request_latency_system_failure.csv") as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, start=1):
        value = float(row["value"])
        alarm, score = detector.update(value)

        # Only count a new alarm event
        if alarm and not in_alarm:
            alarms += 1
            print(
                f"ALARM EVENT at sample {i:4d} | "
                f"time={row['timestamp']} | "
                f"value={value:.3f} | "
                f"score={score:.3f}"
            )

        in_alarm = alarm

print()
print(f"Total alarm events: {alarms}")
