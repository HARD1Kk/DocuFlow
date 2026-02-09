# Batch Size — Complete Notes

---

## 1. Definition

```
Batch Size = The number of items processed together in ONE operation
             before moving to the next group.
```

---

## 2. Simple Analogy

```
You are a teacher grading 100 exam papers.

batch_size = 1:
├── Pick 1 paper → grade it → put away
├── Pick 1 paper → grade it → put away
├── Repeat 100 times
└── Slow (too much picking up and putting down)

batch_size = 10:
├── Pick 10 papers → grade all 10 → put away
├── Pick 10 papers → grade all 10 → put away
├── Repeat 10 times
└── Efficient ✅

batch_size = 100:
├── Pick ALL 100 papers at once
├── Your desk overflows → papers fall → mess
└── Crashed (out of space) ❌
```

---

## 3. How It Works in Code

### Without Batching

```python
texts = ["t1", "t2", "t3", ..., "t1000"]  # 1000 texts

# ALL at once — risky
embeddings = model.encode(texts)  # loads all 1000 into memory
```

### With Batching

```python
texts = ["t1", "t2", "t3", ..., "t1000"]
batch_size = 64

results = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]       # take 64 at a time
    embeddings = model.encode(batch)       # process only 64
    results.extend(embeddings.tolist())    # store results
```

---

## 4. Step-by-Step Trace

```
10 texts, batch_size = 3

texts = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

range(0, 10, 3) → [0, 3, 6, 9]

Step 1: i=0 → texts[0:3]  = ["a","b","c"] → encode → 3 embeddings
Step 2: i=3 → texts[3:6]  = ["d","e","f"] → encode → 3 embeddings
Step 3: i=6 → texts[6:9]  = ["g","h","i"] → encode → 3 embeddings
Step 4: i=9 → texts[9:12] = ["j"]         → encode → 1 embedding

Total: 3 + 3 + 3 + 1 = 10 embeddings ✅
```

---

## 5. How `range(start, stop, step)` Works

```python
range(0, 10, 3)

start = 0   → begin at index 0
stop  = 10  → stop before index 10
step  = 3   → jump by 3

produces → [0, 3, 6, 9]
```

---

## 6. Why Batching Is Needed

### Problem 1: Out of Memory

```
Without batching:
1,000,000 texts × 4 KB each = 4 GB input
+ model weights             = 1.3 GB
+ intermediate computations = 8 GB
= 13+ GB total

Your RAM = 8 GB → 💥 CRASH
```

### Problem 2: Overhead Per Call

```
Each model.encode() call has fixed costs:

├── Tokenizer setup         ~2ms
├── Computation graph setup  ~3ms
├── Memory allocation        ~1ms
├── Actual computation       varies
└── Total overhead:          ~6ms per call

batch_size=1,  1000 texts → 1000 calls → 6000ms overhead
batch_size=64, 1000 texts → 16 calls   → 96ms overhead
```

---

## 7. Batch Size Tradeoffs

```
┌────────────────────┬────────────────┬──────────────────┐
│                    │   Too Small    │    Too Large     │
│                    │  (1 or 2)      │  (100,000+)      │
├────────────────────┼────────────────┼──────────────────┤
│ Speed              │ Slow           │ Fast             │
│ Memory Usage       │ Very Low       │ Very High        │
│ Overhead           │ High           │ Low              │
│ Crash Risk         │ None           │ High             │
│ Verdict            │ Safe but slow  │ Fast but risky   │
└────────────────────┴────────────────┴──────────────────┘

             Sweet Spot = somewhere in the MIDDLE
```

---

## 8. Choosing the Right Batch Size

### Based on Hardware

```
┌─────────────────────────┬────────────────────┐
│ Hardware                │ Recommended        │
├─────────────────────────┼────────────────────┤
│ CPU + 4 GB RAM          │ batch_size = 16    │
│ CPU + 8 GB RAM          │ batch_size = 32    │
│ CPU + 16 GB RAM         │ batch_size = 64    │
│ CPU + 32 GB RAM         │ batch_size = 128   │
│ GPU + 4 GB VRAM         │ batch_size = 64    │
│ GPU + 8 GB VRAM         │ batch_size = 256   │
│ GPU + 16 GB VRAM        │ batch_size = 512   │
│ GPU + 24 GB VRAM        │ batch_size = 1024  │
└─────────────────────────┴────────────────────┘
```

### Based on Text Length

```
Short texts ("hello world"):
└── Can use larger batch_size (128-256)

Long texts (full paragraphs/documents):
└── Use smaller batch_size (16-32)
    (each text uses more memory)
```

---

## 9. Memory Calculation

```
Memory per batch ≈ batch_size × max_tokens × hidden_size × 4 bytes

Example with bge-large:
├── batch_size   = 64
├── max_tokens   = 512
├── hidden_size  = 1024
├── bytes        = 4 (float32)
│
└── 64 × 512 × 1024 × 4 = 134 MB per batch

Example with batch_size = 1000:
└── 1000 × 512 × 1024 × 4 = 2 GB per batch ⚠️
```

---

## 10. What Happens Inside Each Batch

```
Batch = ["How are you?", "Good morning", "Hello world"]

Step 1: TOKENIZATION
├── "How are you?"  → [101, 2129, 2024, 2017, 102, 0, 0]
├── "Good morning"  → [101, 3342, 2851, 102, 0, 0, 0]
├── "Hello world"   → [101, 7592, 2088, 102, 0, 0, 0]
│                                              ↑
│                                         padding (all same length)
└── Result: 2D array of shape (3, 7)

Step 2: MODEL PROCESSING
├── Input shape:  (3, 7)      → 3 texts, 7 tokens each
├── Through transformer layers
└── Output shape: (3, 1024)   → 3 texts, 1024-dim embedding each

Step 3: RESULT
├── "How are you?"  → [0.23, -0.45, 0.78, ..., 0.12]
├── "Good morning"  → [0.31, -0.22, 0.65, ..., 0.09]
└── "Hello world"   → [0.18, -0.56, 0.82, ..., 0.15]
```

---

## 11. Batch Size in Different Contexts

```
┌─────────────────────────┬────────────────────────────────────┐
│ Context                 │ What Batch Size Means              │
├─────────────────────────┼────────────────────────────────────┤
│ Text Embedding          │ Number of texts encoded together   │
│ (our case)              │                                    │
├─────────────────────────┼────────────────────────────────────┤
│ Deep Learning Training  │ Number of training samples per     │
│                         │ gradient update                    │
├─────────────────────────┼────────────────────────────────────┤
│ Database Operations     │ Number of rows inserted/updated    │
│                         │ per transaction                    │
├─────────────────────────┼────────────────────────────────────┤
│ API Calls               │ Number of requests sent together   │
│                         │ in one API call                    │
├─────────────────────────┼────────────────────────────────────┤
│ File Processing         │ Number of files read/processed     │
│                         │ before writing results             │
└─────────────────────────┴────────────────────────────────────┘
```

---

## 12. Common Errors Related to Batch Size

### Error 1: Out of Memory

```python
# Cause: batch_size too large
torch.cuda.OutOfMemoryError  # GPU
MemoryError                  # CPU

# Fix: reduce batch_size
batch_size = 32  # try smaller
```

### Error 2: Too Slow

```python
# Cause: batch_size too small (usually 1)
# Each call has overhead

# Fix: increase batch_size
batch_size = 64  # try larger
```

### Error 3: Last Batch Smaller

```python
# 10 texts, batch_size = 3
# Last batch has only 1 text — is this a problem?

texts[9:12] = ["j"]  # only 1 element, NOT 3

# Answer: NO problem
# Python slicing handles this gracefully
# model.encode(["j"]) works fine with 1 text
```

---

## 13. Complete Template

```python
from typing import List
import numpy as np

def process_in_batches(
    items: List[str],
    batch_size: int = 64
) -> List[List[float]]:
    """
    Process items in batches to avoid memory issues.

    Args:
        items: All items to process.
        batch_size: How many items per batch.

    Returns:
        All results combined.
    """
    if not items:
        return []

    all_results = []

    total_batches = (len(items) + batch_size - 1) // batch_size

    for i in range(0, len(items), batch_size):
        batch_num = i // batch_size + 1
        batch = items[i:i + batch_size]

        print(f"Processing batch {batch_num}/{total_batches} "
              f"({len(batch)} items)")

        results = model.encode(batch)

        if isinstance(results, np.ndarray):
            all_results.extend(results.tolist())
        else:
            all_results.extend(results)

    print(f"Done! Processed {len(items)} items total")
    return all_results
```

---

## 14. Quick Reference

```
BATCH SIZE = items processed at once

Small (1-8):     Safe     + Slow    + High overhead
Medium (32-128): Safe     + Fast    + Low overhead    ← BEST
Large (512+):    Risky    + Fastest + May crash

Formula:
total_batches = ceil(total_items / batch_size)

CPU recommended:  32-64
GPU recommended:  128-512

Key rule: If you get memory errors → REDUCE batch_size
          If processing is too slow → INCREASE batch_size
```