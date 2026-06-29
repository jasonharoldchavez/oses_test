import numpy as np
import time
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector

def run_million_test():
    total_samples = 5000000
    print("=" * 70)
    print(f"🚀 SPINNING UP THE ULTRA-HIGH THROUGHPUT TEST ({total_samples:,} SAMPLES)")
    print("=" * 70)
    print("Generating synthetic telemetry stream in memory...")
    
    # Pre-allocate 5 million points to isolate algorithm performance from random generation speed
    np.random.seed(42)
    stream = np.random.normal(10.0, 1.0, total_samples).astype(np.float32)
    
    detector = AdaptiveCUSUMDetector(burn_in=200)
    
    print("Starting engine. Processing stream...")
    start_time = time.time()
    
    # Stream the data live
    for i in range(total_samples):
        detector.update(stream[i])
        
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate performance metrics
    throughput = total_samples / total_time
    avg_latency_ns = (total_time / total_samples) * 1e9
    
    print("\n" + "📊 PERFORMANCE BENCHMARK RESULTS")
    print("-" * 70)
    print(f"Total Points Processed : {total_samples:,}")
    print(f"Total Execution Time   : {total_time:.4f} seconds")
    print(f"Engine Throughput      : {throughput:,.2f} samples/sec")
    print(f"Average Latency        : {avg_latency_ns:.2f} nanoseconds per sample")
    print("=" * 70)

if __name__ == "__main__":
    run_million_test()
