# Time to First Token (TTFT) Evaluation Guide for RAG Applications

## What is TTFT?

**Time to First Token (TTFT)** is the latency between:
- **Start**: When the user submits a query
- **End**: When the model generates and outputs the first token

TTFT is critical for user experience because it determines how quickly users perceive that the system is responding.

### Why TTFT Matters:
- **User Perception**: Users perceive responsiveness within the first few hundred milliseconds
- **Streaming Experience**: In streaming scenarios, TTFT is more important than total latency
- **Real-time Applications**: Essential for interactive applications like chatbots

---

## Implementation Overview

### Core Components

#### 1. **TTFTCallbackHandler** - Captures Timing Events
```python
class TTFTCallbackHandler(BaseCallbackHandler):
    - on_llm_start(): Records when LLM processing begins
    - on_llm_new_token(): Captures first token generation time
    - on_llm_end(): Records completion time
    - get_metrics(): Calculates all timing metrics
```

**Key Metrics Collected:**
- `ttft_ms`: Time to first token in milliseconds
- `total_time_ms`: Total response generation time
- `token_count`: Number of tokens generated
- `tokens_per_second`: Throughput metric

#### 2. **PerformanceMetricsCollector** - Aggregates Results
Collects metrics across multiple queries and provides:
- Per-query metrics
- Summary statistics (min, max, average)
- Detailed reporting

---

## Usage Example

### Basic Usage
```python
# Create metrics collector
metrics_collector = PerformanceMetricsCollector()

# Create callback handler
ttft_handler = TTFTCallbackHandler()

# Execute query with callbacks
response = qa_chain.invoke(
    query,
    config={"callbacks": [ttft_handler]}
)

# Retrieve metrics
metrics = ttft_handler.get_metrics()
metrics_collector.add_metrics(metrics, query)

# Print report
metrics_collector.print_detailed_report()
```

### Multiple Queries Evaluation
```python
metrics_collector = PerformanceMetricsCollector()

queries = [
    "Query 1: ...",
    "Query 2: ...",
    "Query 3: ..."
]

for query in queries:
    ttft_handler = TTFTCallbackHandler()
    response = qa_chain.invoke(query, config={"callbacks": [ttft_handler]})
    metrics_collector.add_metrics(ttft_handler.get_metrics(), query)

# Get comprehensive summary
summary = metrics_collector.get_summary()
print(f"Average TTFT: {summary['ttft_ms']['avg']:.2f} ms")
```

---

## Metrics Explained

### Primary Metrics

| Metric | Unit | What It Measures | Good Range |
|--------|------|------------------|------------|
| **TTFT** | ms | Time until first token appears | < 200ms (ideal) |
| **Total Time** | ms | Complete generation time | Depends on content |
| **Token Count** | count | Number of tokens generated | Variable |
| **Tokens/Second** | tokens/s | Generation throughput | > 5 tokens/s (typical) |

### Performance Tiers

**Excellent Performance:**
- TTFT: < 100ms
- Tokens/Second: > 10

**Good Performance:**
- TTFT: 100-500ms
- Tokens/Second: 5-10

**Acceptable Performance:**
- TTFT: 500ms - 2s
- Tokens/Second: 2-5

**Poor Performance:**
- TTFT: > 2s
- Tokens/Second: < 2

---

## Optimization Strategies

### 1. Reduce Retrieval Latency
```python
# Optimize retriever search
retriever = db.as_retriever(
    search_kwargs={
        "k": 3,  # Fewer results = faster
        "fetch_k": 20  # Control internal ranking
    }
)
```

### 2. Optimize Prompt Size
```python
# Shorter context window = faster processing
text_splitter = CharacterTextSplitter(
    chunk_size=300,  # Smaller chunks
    chunk_overlap=30
)
```

### 3. Use Faster Models
```python
# Different Ollama models have different speeds
llm = Ollama(model="mistral:latest")  # Faster than larger models
```

### 4. Enable Streaming
```python
# For streaming responses (if supported)
response = qa_chain.invoke(query, stream=True)
```

### 5. Batch Queries
```python
# Process multiple queries to amortize overhead
for query in batch_queries:
    # Results in better overall throughput
```

---

## Output Examples

### Console Output
```
============================================================
QUERY RESPONSE
============================================================
[Response content here]

IMMEDIATE METRICS:
  Time To First Token (TTFT): 245.32 ms
  Total Response Time: 3456.78 ms
  Tokens Generated: 150
  Tokens Per Second: 4.34

============================================================
DETAILED PERFORMANCE REPORT
============================================================

Query 1:
  Query: You are act as financial analyst...
  TTFT: 245.32 ms
  Total Time: 3456.78 ms
  Tokens Generated: 150
  Tokens/Second: 4.34

------------------------------------------------------------
SUMMARY STATISTICS
------------------------------------------------------------
Total Queries: 1

Time To First Token (TTFT):
  Min: 245.32 ms
  Max: 245.32 ms
  Avg: 245.32 ms

Total Response Time:
  Min: 3456.78 ms
  Max: 3456.78 ms
  Avg: 3456.78 ms

Tokens Per Second:
  Min: 4.34
  Max: 4.34
  Avg: 4.34

Total Tokens Generated: 150
============================================================
```

### JSON Output (evaluation_metrics.json)
```json
{
  "metrics_history": [
    {
      "timestamp": "2024-03-16T10:30:45.123456",
      "query": "You are act as financial analyst...",
      "start_time": 1710678645.123,
      "first_token_time": 1710678645.368,
      "end_time": 1710678648.580,
      "ttft_seconds": 0.245,
      "ttft_ms": 245.32,
      "total_time_seconds": 3.457,
      "total_time_ms": 3456.78,
      "token_count": 150,
      "tokens_per_second": 4.34
    }
  ],
  "summary": {
    "total_queries": 1,
    "ttft_ms": {
      "min": 245.32,
      "max": 245.32,
      "avg": 245.32
    },
    "total_time_ms": {
      "min": 3456.78,
      "max": 3456.78,
      "avg": 3456.78
    },
    "tokens_per_second": {
      "min": 4.34,
      "max": 4.34,
      "avg": 4.34
    },
    "total_tokens": 150
  }
}
```

---

## Advanced Usage Patterns

### Pattern 1: Continuous Monitoring
```python
from collections import deque

class MetricsMonitor:
    def __init__(self, window_size=10):
        self.ttft_window = deque(maxlen=window_size)
        self.collector = PerformanceMetricsCollector()
    
    def process_query(self, query):
        handler = TTFTCallbackHandler()
        response = qa_chain.invoke(query, config={"callbacks": [handler]})
        metrics = handler.get_metrics()
        
        self.ttft_window.append(metrics['ttft_ms'])
        self.collector.add_metrics(metrics, query)
        
        avg_ttft = sum(self.ttft_window) / len(self.ttft_window)
        return response, avg_ttft
```

### Pattern 2: Performance Regression Detection
```python
class PerformanceBaseline:
    def __init__(self, baseline_ttft_ms):
        self.baseline = baseline_ttft_ms
        self.threshold = 0.2  # 20% increase triggers alert
    
    def check(self, current_ttft_ms):
        increase = (current_ttft_ms - self.baseline) / self.baseline
        if increase > self.threshold:
            return f"⚠️ PERFORMANCE REGRESSION: +{increase*100:.1f}%"
        return "✓ Performance OK"
```

### Pattern 3: Load Testing
```python
import concurrent.futures

def load_test(num_requests=100):
    collector = PerformanceMetricsCollector()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(num_requests):
            future = executor.submit(process_query, collector)
            futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            future.result()
    
    summary = collector.get_summary()
    print(f"P50 TTFT: {percentile(50)} ms")
    print(f"P95 TTFT: {percentile(95)} ms")
    print(f"P99 TTFT: {percentile(99)} ms")
```

---

## Troubleshooting

### Issue: TTFT Always None
**Cause**: Model doesn't support streaming or callback not triggered
**Solution**: Check if Ollama supports `on_llm_new_token` callback

### Issue: High TTFT (> 2 seconds)
**Causes**:
- Large retrieval results
- Complex prompt/context
- Slow model
**Solutions**:
- Reduce chunk size
- Use faster model
- Optimize prompt

### Issue: Metrics Not Saving
**Solution**:
```python
import os
os.makedirs('./metrics', exist_ok=True)
# Adjust file path to existing directory
with open("./metrics/evaluation_metrics.json", "w") as f:
    json.dump(data, f)
```

---

## Best Practices

1. **Run Multiple Trials**: Single measurements can be noisy
   ```python
   metrics_list = []
   for _ in range(10):
       metrics = measure_single_query(query)
       metrics_list.append(metrics)
   avg = statistics.mean([m['ttft_ms'] for m in metrics_list])
   ```

2. **Warm Up**: First invocation might be slower
   ```python
   # Warm-up call
   qa_chain.invoke("dummy query")
   # Then measure
   ```

3. **Control Variables**: Test one change at a time

4. **Log Trends**: Track performance over time
   ```python
   # Save metrics with timestamp
   metrics['date'] = datetime.now().isoformat()
   ```

5. **Profile Bottlenecks**: Measure each component
   ```python
   t1 = time.time()
   retriever_results = retriever.get_relevant_documents(query)
   t2 = time.time()
   # retrieval time = t2 - t1
   ```
