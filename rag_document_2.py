import time
from typing import Any, List
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
import json
from datetime import datetime


# ============ CUSTOM CALLBACK FOR METRICS ============
class TTFTCallbackHandler(BaseCallbackHandler):
    """Custom callback to measure Time To First Token (TTFT) and other metrics"""
    
    def __init__(self):
        self.start_time = None
        self.first_token_time = None
        self.end_time = None
        self.token_count = 0
        self.first_token_received = False
        
    def on_llm_start(self, serialized: dict, prompts: List[str], **kwargs: Any) -> None:
        """Called when LLM starts processing"""
        self.start_time = time.time()
        self.first_token_received = False
        self.token_count = 0
        
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called when a new token is generated"""
        if not self.first_token_received:
            self.first_token_time = time.time()
            self.first_token_received = True
        self.token_count += 1
        
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Called when LLM finishes"""
        self.end_time = time.time()
        
    def get_metrics(self) -> dict:
        """Calculate and return all metrics"""
        metrics = {
            "start_time": self.start_time,
            "first_token_time": self.first_token_time,
            "end_time": self.end_time,
        }
        
        if self.start_time and self.first_token_time:
            metrics["ttft_seconds"] = self.first_token_time - self.start_time
            metrics["ttft_ms"] = (self.first_token_time - self.start_time) * 1000
            
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            metrics["total_time_seconds"] = total_time
            metrics["total_time_ms"] = total_time * 1000
            
        metrics["token_count"] = self.token_count
        
        if self.start_time and self.end_time and self.token_count > 0:
            total_time = self.end_time - self.start_time
            metrics["tokens_per_second"] = self.token_count / total_time if total_time > 0 else 0
            
        return metrics


class PerformanceMetricsCollector:
    """Collects and aggregates performance metrics across multiple queries"""
    
    def __init__(self):
        self.metrics_history = []
        
    def add_metrics(self, metrics: dict, query: str = None) -> None:
        """Add metrics from a single query"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            **metrics
        }
        self.metrics_history.append(entry)
        
    def get_summary(self) -> dict:
        """Get summary statistics across all queries"""
        if not self.metrics_history:
            return {}
            
        ttft_values = [m["ttft_ms"] for m in self.metrics_history if "ttft_ms" in m]
        total_time_values = [m["total_time_ms"] for m in self.metrics_history if "total_time_ms" in m]
        token_values = [m["token_count"] for m in self.metrics_history if "token_count" in m]
        tps_values = [m["tokens_per_second"] for m in self.metrics_history if "tokens_per_second" in m]
        
        return {
            "total_queries": len(self.metrics_history),
            "ttft_ms": {
                "min": min(ttft_values) if ttft_values else None,
                "max": max(ttft_values) if ttft_values else None,
                "avg": sum(ttft_values) / len(ttft_values) if ttft_values else None,
            },
            "total_time_ms": {
                "min": min(total_time_values) if total_time_values else None,
                "max": max(total_time_values) if total_time_values else None,
                "avg": sum(total_time_values) / len(total_time_values) if total_time_values else None,
            },
            "tokens_per_second": {
                "min": min(tps_values) if tps_values else None,
                "max": max(tps_values) if tps_values else None,
                "avg": sum(tps_values) / len(tps_values) if tps_values else None,
            },
            "total_tokens": sum(token_values) if token_values else 0,
        }
        
    def print_detailed_report(self) -> None:
        """Print a detailed report of all metrics"""
        print("\n" + "="*60)
        print("DETAILED PERFORMANCE REPORT")
        print("="*60)
        
        for i, metrics in enumerate(self.metrics_history, 1):
            print(f"\nQuery {i}:")
            if metrics.get("query"):
                print(f"  Query: {metrics['query'][:80]}...")
            print(f"  TTFT: {metrics.get('ttft_ms', 'N/A'):.2f} ms")
            print(f"  Total Time: {metrics.get('total_time_ms', 'N/A'):.2f} ms")
            print(f"  Tokens Generated: {metrics.get('token_count', 0)}")
            print(f"  Tokens/Second: {metrics.get('tokens_per_second', 'N/A'):.2f}")
            
        summary = self.get_summary()
        print("\n" + "-"*60)
        print("SUMMARY STATISTICS")
        print("-"*60)
        print(f"Total Queries: {summary.get('total_queries', 0)}")
        print(f"\nTime To First Token (TTFT):")
        print(f"  Min: {summary['ttft_ms']['min']:.2f} ms")
        print(f"  Max: {summary['ttft_ms']['max']:.2f} ms")
        print(f"  Avg: {summary['ttft_ms']['avg']:.2f} ms")
        print(f"\nTotal Response Time:")
        print(f"  Min: {summary['total_time_ms']['min']:.2f} ms")
        print(f"  Max: {summary['total_time_ms']['max']:.2f} ms")
        print(f"  Avg: {summary['total_time_ms']['avg']:.2f} ms")
        print(f"\nTokens Per Second:")
        print(f"  Min: {summary['tokens_per_second']['min']:.2f}")
        print(f"  Max: {summary['tokens_per_second']['max']:.2f}")
        print(f"  Avg: {summary['tokens_per_second']['avg']:.2f}")
        print(f"\nTotal Tokens Generated: {summary['total_tokens']}")
        print("="*60)


# ============ MAIN CODE ============

# Load document
loader = TextLoader("./sample.csv")
documents = loader.load()

# Split documents
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# Print chunks
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}:\n{chunk.page_content}\n")

# Use Ollama to generate embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Store in ChromaDB locally
db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

# Initialize Gemma model
llm = Ollama(model="gemma3:latest")

# Create retriever
retriever = db.as_retriever(search_kwargs={"k": 3})

# Create the chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# ============ EXECUTE QUERY WITH METRICS ============
metrics_collector = PerformanceMetricsCollector()

query = """You are act as financial analyst,
            please create 4 list how is the performance of 
            the merchant M-9921?"""

# Create callback handler for this query
ttft_handler = TTFTCallbackHandler()

# Invoke with callbacks
response = qa_chain.invoke(
    query,
    config={"callbacks": [ttft_handler]}
)

# Get metrics
metrics = ttft_handler.get_metrics()
metrics_collector.add_metrics(metrics, query)

# Print response
print("\n" + "="*60)
print("QUERY RESPONSE")
print("="*60)
print(response['result'])

# Print metrics
print("\nIMMEDIATE METRICS:")
print(f"  Time To First Token (TTFT): {metrics.get('ttft_ms', 'N/A'):.2f} ms")
print(f"  Total Response Time: {metrics.get('total_time_ms', 'N/A'):.2f} ms")
print(f"  Tokens Generated: {metrics.get('token_count', 0)}")
print(f"  Tokens Per Second: {metrics.get('tokens_per_second', 'N/A'):.2f}")

# Print detailed report
metrics_collector.print_detailed_report()

# Optional: Save metrics to JSON
with open("./evaluation_metrics.json", "w") as f:
    json.dump({
        "metrics_history": metrics_collector.metrics_history,
        "summary": metrics_collector.get_summary()
    }, f, indent=2)
print("\nMetrics saved to ./evaluation_metrics.json")