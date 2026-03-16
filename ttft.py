# Example: Multiple TTFT Measurement Scenarios

import time
from typing import Any, List
from datetime import datetime
import json
import statistics

# Simulated TTFTCallbackHandler (replace with actual from main code)
class TTFTCallbackHandler:
    """Simulated callback for demonstration"""
    def __init__(self):
        self.start_time = None
        self.first_token_time = None
        self.end_time = None
        self.token_count = 0
        
    def get_metrics(self) -> dict:
        return {
            "start_time": self.start_time,
            "first_token_time": self.first_token_time,
            "end_time": self.end_time,
            "ttft_ms": (self.first_token_time - self.start_time) * 1000 if self.first_token_time and self.start_time else None,
            "total_time_ms": (self.end_time - self.start_time) * 1000 if self.end_time and self.start_time else None,
            "token_count": self.token_count,
            "tokens_per_second": self.token_count / (self.end_time - self.start_time) if self.end_time and self.start_time else None
        }


# ============================================================
# SCENARIO 1: Single Query Measurement
# ============================================================
def scenario_1_single_query():
    """Measure TTFT for a single query"""
    print("\n" + "="*60)
    print("SCENARIO 1: Single Query Measurement")
    print("="*60)
    
    query = "Analyze merchant M-9921 performance"
    
    # Simulate metrics (replace with actual qa_chain.invoke)
    ttft_handler = TTFTCallbackHandler()
    ttft_handler.start_time = time.time()
    time.sleep(0.2)  # Simulate retrieval
    ttft_handler.first_token_time = time.time()
    time.sleep(2.5)  # Simulate generation
    ttft_handler.end_time = time.time()
    ttft_handler.token_count = 150
    
    metrics = ttft_handler.get_metrics()
    
    print(f"\nQuery: {query}")
    print(f"TTFT: {metrics['ttft_ms']:.2f} ms")
    print(f"Total Time: {metrics['total_time_ms']:.2f} ms")
    print(f"Tokens: {metrics['token_count']}")
    print(f"Tokens/Second: {metrics['tokens_per_second']:.2f}")


# ============================================================
# SCENARIO 2: Multiple Queries with Comparison
# ============================================================
def scenario_2_multiple_queries():
    """Compare TTFT across multiple different queries"""
    print("\n" + "="*60)
    print("SCENARIO 2: Multiple Queries Comparison")
    print("="*60)
    
    queries = [
        "What is the total revenue?",
        "Analyze transaction trends",
        "List top performers",
        "Generate quarterly report"
    ]
    
    all_metrics = []
    
    for i, query in enumerate(queries, 1):
        handler = TTFTCallbackHandler()
        handler.start_time = time.time()
        time.sleep(0.15 + (i * 0.05))  # Variable delays
        handler.first_token_time = time.time()
        time.sleep(1.5 + (i * 0.3))  # Variable generation times
        handler.end_time = time.time()
        handler.token_count = 100 + (i * 20)
        
        metrics = handler.get_metrics()
        all_metrics.append(metrics)
        
        print(f"\nQuery {i}: {query[:40]}...")
        print(f"  TTFT: {metrics['ttft_ms']:.2f} ms")
        print(f"  Total: {metrics['total_time_ms']:.2f} ms")
        print(f"  TPS: {metrics['tokens_per_second']:.2f}")
    
    # Calculate statistics
    ttft_values = [m['ttft_ms'] for m in all_metrics]
    print("\n" + "-"*60)
    print("SUMMARY:")
    print(f"  Min TTFT: {min(ttft_values):.2f} ms")
    print(f"  Max TTFT: {max(ttft_values):.2f} ms")
    print(f"  Avg TTFT: {statistics.mean(ttft_values):.2f} ms")
    print(f"  Median TTFT: {statistics.median(ttft_values):.2f} ms")
    print(f"  Std Dev: {statistics.stdev(ttft_values):.2f} ms")


# ============================================================
# SCENARIO 3: Warm-up and Cold Start Comparison
# ============================================================
def scenario_3_warmup_comparison():
    """Compare cold start vs warm start performance"""
    print("\n" + "="*60)
    print("SCENARIO 3: Cold Start vs Warm Start")
    print("="*60)
    
    query = "Analyze payment patterns"
    
    print("\nCold Start (First Invocation):")
    cold_handler = TTFTCallbackHandler()
    cold_handler.start_time = time.time()
    time.sleep(0.8)  # Cold start is slower
    cold_handler.first_token_time = time.time()
    time.sleep(2.0)
    cold_handler.end_time = time.time()
    cold_handler.token_count = 120
    
    cold_metrics = cold_handler.get_metrics()
    print(f"  TTFT: {cold_metrics['ttft_ms']:.2f} ms")
    print(f"  Total: {cold_metrics['total_time_ms']:.2f} ms")
    
    print("\nWarm Start (Subsequent Invocation):")
    warm_handler = TTFTCallbackHandler()
    warm_handler.start_time = time.time()
    time.sleep(0.15)  # Warm start is faster
    warm_handler.first_token_time = time.time()
    time.sleep(2.0)
    warm_handler.end_time = time.time()
    warm_handler.token_count = 120
    
    warm_metrics = warm_handler.get_metrics()
    print(f"  TTFT: {warm_metrics['ttft_ms']:.2f} ms")
    print(f"  Total: {warm_metrics['total_time_ms']:.2f} ms")
    
    # Calculate improvement
    improvement = (cold_metrics['ttft_ms'] - warm_metrics['ttft_ms']) / cold_metrics['ttft_ms'] * 100
    print(f"\nImprovement: {improvement:.1f}%")


# ============================================================
# SCENARIO 4: Percentile Analysis (Load Testing)
# ============================================================
def scenario_4_percentile_analysis():
    """Analyze TTFT distribution using percentiles"""
    print("\n" + "="*60)
    print("SCENARIO 4: Percentile Analysis (Load Testing)")
    print("="*60)
    
    # Simulate 100 requests
    ttft_values = []
    for i in range(100):
        handler = TTFTCallbackHandler()
        handler.start_time = time.time()
        # Add some randomness to simulate real-world variance
        import random
        delay = random.gauss(0.2, 0.05)  # Normal distribution
        time.sleep(max(0.05, delay))
        handler.first_token_time = time.time()
        time.sleep(2.0)
        handler.end_time = time.time()
        handler.token_count = 150
        
        metrics = handler.get_metrics()
        ttft_values.append(metrics['ttft_ms'])
    
    # Sort for percentile calculation
    ttft_values.sort()
    
    print(f"\n100 Requests Distribution:")
    print(f"  P0 (Min): {ttft_values[0]:.2f} ms")
    print(f"  P25: {ttft_values[24]:.2f} ms")
    print(f"  P50 (Median): {ttft_values[49]:.2f} ms")
    print(f"  P75: {ttft_values[74]:.2f} ms")
    print(f"  P95: {ttft_values[94]:.2f} ms")
    print(f"  P99: {ttft_values[98]:.2f} ms")
    print(f"  P100 (Max): {ttft_values[99]:.2f} ms")
    
    print(f"\nMean: {statistics.mean(ttft_values):.2f} ms")
    print(f"Std Dev: {statistics.stdev(ttft_values):.2f} ms")


# ============================================================
# SCENARIO 5: Different Model Comparison
# ============================================================
def scenario_5_model_comparison():
    """Compare TTFT across different models"""
    print("\n" + "="*60)
    print("SCENARIO 5: Model Comparison")
    print("="*60)
    
    models = {
        "gemma3:latest": {"ttft": 245, "tps": 4.34},
        "mistral:latest": {"ttft": 180, "tps": 5.12},
        "neural-chat:latest": {"ttft": 320, "tps": 3.85},
        "orca-mini:latest": {"ttft": 150, "tps": 5.89}
    }
    
    print("\nModel Performance Comparison:")
    print(f"{'Model':<25} {'TTFT (ms)':<15} {'Tokens/Sec':<15} {'Rank'}")
    print("-" * 60)
    
    sorted_models = sorted(models.items(), key=lambda x: x[1]['ttft'])
    for rank, (model, metrics) in enumerate(sorted_models, 1):
        print(f"{model:<25} {metrics['ttft']:<15.0f} {metrics['tps']:<15.2f} #{rank}")
    
    # Recommendation
    best_model = sorted_models[0][0]
    best_ttft = sorted_models[0][1]['ttft']
    worst_model = sorted_models[-1][0]
    worst_ttft = sorted_models[-1][1]['ttft']
    
    print(f"\n✓ Best: {best_model} ({best_ttft:.0f} ms)")
    print(f"✗ Worst: {worst_model} ({worst_ttft:.0f} ms)")
    print(f"Difference: {(worst_ttft/best_ttft - 1)*100:.1f}% slower")


# ============================================================
# SCENARIO 6: Parameter Tuning Impact
# ============================================================
def scenario_6_parameter_tuning():
    """Show impact of different parameter settings on TTFT"""
    print("\n" + "="*60)
    print("SCENARIO 6: Parameter Tuning Impact")
    print("="*60)
    
    configurations = {
        "Default": {"chunk_size": 500, "k": 3, "ttft_ms": 245},
        "Smaller Chunks": {"chunk_size": 300, "k": 3, "ttft_ms": 195},
        "Fewer Results": {"chunk_size": 500, "k": 1, "ttft_ms": 165},
        "Aggressive": {"chunk_size": 300, "k": 1, "ttft_ms": 125},
        "Verbose": {"chunk_size": 1000, "k": 5, "ttft_ms": 385}
    }
    
    print("\nConfiguration Impact on TTFT:")
    print(f"{'Configuration':<20} {'Chunk Size':<15} {'K':<5} {'TTFT (ms)':<15} {'vs Baseline'}")
    print("-" * 65)
    
    baseline_ttft = configurations["Default"]["ttft_ms"]
    
    for config_name, params in configurations.items():
        vs_baseline = ((params['ttft_ms'] - baseline_ttft) / baseline_ttft * 100)
        vs_str = f"{vs_baseline:+.1f}%" if config_name != "Default" else "baseline"
        
        print(f"{config_name:<20} {params['chunk_size']:<15} {params['k']:<5} {params['ttft_ms']:<15.0f} {vs_str}")
    
    print("\n✓ Recommendation: Use 'Fewer Results' configuration for best balance")


# ============================================================
# SCENARIO 7: Export Metrics to JSON
# ============================================================
def scenario_7_export_metrics():
    """Export comprehensive metrics to JSON"""
    print("\n" + "="*60)
    print("SCENARIO 7: Export to JSON")
    print("="*60)
    
    query = "Sample financial analysis query"
    
    handler = TTFTCallbackHandler()
    handler.start_time = time.time()
    time.sleep(0.25)
    handler.first_token_time = time.time()
    time.sleep(2.5)
    handler.end_time = time.time()
    handler.token_count = 150
    
    metrics = handler.get_metrics()
    
    # Create comprehensive report
    report = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "metrics": metrics,
        "analysis": {
            "ttft_category": "good" if metrics['ttft_ms'] < 500 else "acceptable" if metrics['ttft_ms'] < 2000 else "poor",
            "throughput_category": "good" if metrics['tokens_per_second'] > 5 else "acceptable" if metrics['tokens_per_second'] > 2 else "poor",
            "total_time_seconds": metrics['total_time_ms'] / 1000
        }
    }
    
    # Save to JSON
    filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nMetrics exported to: {filename}")
    print("\nJSON Content:")
    print(json.dumps(report, indent=2))


# ============================================================
# Run All Scenarios
# ============================================================
if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# TTFT Measurement Scenarios - Complete Examples")
    print("#"*60)
    
    scenario_1_single_query()
    scenario_2_multiple_queries()
    scenario_3_warmup_comparison()
    scenario_4_percentile_analysis()
    scenario_5_model_comparison()
    scenario_6_parameter_tuning()
    scenario_7_export_metrics()
    
    print("\n" + "#"*60)
    print("# All Scenarios Completed")
    print("#"*60)