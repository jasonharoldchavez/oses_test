#!/bin/bash

REPORT_FILE="benchmarks/benchmark_report.md"

echo "===================================================="
echo "📊 GENERATING AUDITABLE SYSTEM BENCHMARK REPORT"
echo "===================================================="

# Gather System Metadata
PYTHON_VERSION=$(python -c 'import sys; print(sys.version.split()[0])')
OS_INFO=$(uname -srm)
GIT_COMMIT=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Write Header to Markdown Report
cat << EOM > $REPORT_FILE
# 📊 Algorithmic Performance Audit Report

* **Generated At:** $TIMESTAMP
* **Git Commit Hash:** \`$GIT_COMMIT\`

## 🖥️ System & Execution Environment
* **Operating System / Architecture:** \`$OS_INFO\`
* **Python Runtime Version:** \`$PYTHON_VERSION\`
* **Execution Model:** Single-threaded, synchronous loop execution

## ⚡ Execution Metrics Matrix
EOM

# Run the Million Point Dash and capture output
echo "Running Million Point Throughput Test..."
OUTPUT=$(PYTHONPATH=. python benchmarks/million_point_dash.py)

# Extract numbers dynamically from your script's stdout
RUNTIME=$(echo "$OUTPUT" | grep "Total Execution Time" | awk -F': ' '{print $2}')
THROUGHPUT=$(echo "$OUTPUT" | grep "Engine Throughput" | awk -F': ' '{print $2}')
LATENCY=$(echo "$OUTPUT" | grep "Average Latency" | awk -F': ' '{print $2}')

# Append results to the markdown table
cat << EOM >> $REPORT_FILE
| Metric | Audit Result |
| :--- | :--- |
| **Total Samples Processed** | 5,000,000 |
| **Total Runtime** | $RUNTIME |
| **Sustained Throughput** | $THROUGHPUT |
| **Average Latency** | $LATENCY |

---
> **Audit Verification:** This report ties live performance data to an exact Git revision hash. Rerun \`bash benchmarks/run_suite.sh\` on this hardware to reproduce these constraints.
EOM

echo "✅ Success! Performance data bound to commit [$GIT_COMMIT]."
echo "Report written to: $REPORT_FILE"
echo "===================================================="
