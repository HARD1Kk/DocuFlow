# Text Embeddings — Complete Notes

---

## 1. Definition

```
Embedding = Converting human-readable text into a list of numbers (vector)
            that captures the MEANING of the text.

"Hello world" → [0.023, -0.156, 0.892, 0.341, ..., 0.045]
                 └──────────── hundreds of numbers ──────────┘
```

---

## 2. Why Do We Need Embeddings?

```
Problem: Computers CANNOT understand text
         They ONLY understand numbers

Solution: Convert text → numbers
          But in a SMART way that preserves MEANING

"King"  → [0.2, 0.8, 0.1, ...]
"Queen" → [0.2, 0.7, 0.1, ...]   ← similar numbers (similar meaning)
"Banana"→ [0.9, 0.1, 0.8, ...]   ← different numbers (different meaning)
```

---

## 3. Simple Analogy

```
Think of GPS coordinates for cities:

New York  → (40.7, -74.0)
New Jersey→ (40.0, -74.4)   ← close numbers = close cities
Tokyo     → (35.6, 139.6)   ← far numbers = far city

Embeddings do the SAME THING but for TEXT MEANING:

"happy"     → [0.9, 0.8, 0.1, ...]
"joyful"    → [0.88, 0.82, 0.12, ...] ← close = similar meaning
"earthquake"→ [0.1, 0.3, 0.95, ...]   ← far = different meaning
```

---

## 4. Types of Embeddings

```
┌────────────────────┬──────────────────────┬──────────────────────┐
│ Type               │ Sparse               │ Dense                │
├────────────────────┼──────────────────────┼──────────────────────┤
│ What it looks like │ [0,0,0,1,0,0,0,1,0] │ [0.23,-0.15,0.89]   │
│                    │ Mostly zeros          │ All meaningful values│
├────────────────────┼──────────────────────┼──────────────────────┤
│ Dimensions         │ 10,000 - 100,000+    │ 384 - 1024           │
├────────────────────┼──────────────────────┼──────────────────────┤
│ Method             │ TF-IDF, BM25         │ BERT, BGE, OpenAI    │
├────────────────────┼──────────────────────┼──────────────────────┤
│ Captures           │ Keyword matching     │ Semantic meaning     │
├────────────────────┼──────────────────────┼──────────────────────┤
│ Example            │ "car" matches "car"  │ "car" matches        │
│                    │ but NOT "automobile"  │ "automobile" too     │
├────────────────────┼──────────────────────┼──────────────────────┤
│ Used in            │ Traditional search   │ Modern AI search     │
└────────────────────┴──────────────────────┴──────────────────────┘
```

---

## 5. How Embeddings Are Created

### Step-by-Step Process

```
Input: "The cat sat on the mat"

Step 1: TOKENIZATION
────────────────────
"The cat sat on the mat"
  → [101, 1996, 4937, 2938, 2006, 1996, 13523, 102]
  (each word/subword gets a number ID)

Step 2: TOKEN EMBEDDINGS (lookup table)
───────────────────────────────────────
Token 101  → [0.1, 0.2, 0.3, ..., 0.5]   (768 numbers)
Token 1996 → [0.4, 0.1, 0.7, ..., 0.2]   (768 numbers)
Token 4937 → [0.3, 0.6, 0.2, ..., 0.8]   (768 numbers)
...

Step 3: TRANSFORMER LAYERS
──────────────────────────
Layer 1:  Learns grammar and syntax
Layer 2:  Learns word relationships
Layer 3:  Learns phrase meaning
...
Layer 12: Learns deep semantic meaning

Each layer refines the understanding.
Words "look at" each other (attention mechanism).

Step 4: POOLING
───────────────
Transformer outputs one vector PER token (word).
We need ONE vector for the ENTIRE text.

Methods:
├── [CLS] token: Use the first special token's vector
├── Mean pooling: Average all token vectors
└── Max pooling: Take maximum across all token vectors

Step 5: NORMALIZATION (optional)
────────────────────────────────
Scale vector to length = 1
This makes cosine similarity = dot product (faster)

Step 6: FINAL OUTPUT
────────────────────
"The cat sat on the mat" → [0.023, -0.156, 0.892, ..., 0.045]
                            └──── 384 or 768 or 1024 numbers ────┘
```

---

## 6. What Each Dimension Means

```
Short answer: We don't know exactly.

Each number represents some ABSTRACT FEATURE learned during training.

Dimension 1:   might capture "formality"
Dimension 2:   might capture "topic: science vs arts"
Dimension 3:   might capture "sentiment: positive vs negative"
Dimension 47:  might capture "about animals vs not"
Dimension 200: might capture something humans can't name

These features are learned automatically from billions of text examples.
Humans don't choose them — the neural network discovers them.
```

---

## 7. Embedding Dimensions

```
┌──────────────────────┬────────────┬──────────┬───────────┐
│ Model                │ Dimensions │ Size     │ Quality   │
├──────────────────────┼────────────┼──────────┼───────────┤
│ bge-small-en-v1.5    │ 384        │ ~130 MB  │ Good      │
│ bge-base-en-v1.5     │ 768        │ ~440 MB  │ Better    │
│ bge-large-en-v1.5    │ 1024       │ ~1.3 GB  │ Best      │
│ OpenAI text-ada-002  │ 1536       │ API only │ Very Good │
│ OpenAI text-3-large  │ 3072       │ API only │ Excellent │
└──────────────────────┴────────────┴──────────┴───────────┘

More dimensions = more detail = more memory = slower
Fewer dimensions = less detail = less memory = faster
```

---

## 8. How Similarity Works

### Cosine Similarity

```
Measures the ANGLE between two vectors.

Range: -1 to +1
├── +1.0  = identical meaning
├──  0.0  = completely unrelated
└── -1.0  = opposite meaning

Example:
"I love dogs"      → [0.9, 0.8, 0.1]
"I adore puppies"  → [0.88, 0.82, 0.12]  → similarity = 0.99 (almost same)
"Stock market fell" → [0.1, 0.2, 0.95]    → similarity = 0.15 (very different)
```

### Formula

```
                    A · B           a1×b1 + a2×b2 + ... + an×bn
cosine(A, B) = ─────────── = ─────────────────────────────────────
                |A| × |B|     √(a1²+a2²+...+an²) × √(b1²+b2²+...+bn²)
```

### Code

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example
emb1 = embed_texts(["I love dogs"])[0]
emb2 = embed_texts(["I adore puppies"])[0]
emb3 = embed_texts(["Stock market crashed"])[0]

print(cosine_similarity(emb1, emb2))  # ~0.92 (similar)
print(cosine_similarity(emb1, emb3))  # ~0.15 (different)
```

---

## 9. Embedding Models

### Local Models (Run on Your Machine)

```
┌────────────────────────┬───────────┬─────────────────────┐
│ Model                  │ Provider  │ Notes               │
├────────────────────────┼───────────┼─────────────────────┤
│ bge-small-en-v1.5      │ BAAI      │ Fast, good quality  │
│ bge-base-en-v1.5       │ BAAI      │ Balanced            │
│ bge-large-en-v1.5      │ BAAI      │ Best quality, slow  │
│ all-MiniLM-L6-v2       │ Microsoft │ Very fast, decent   │
│ e5-large-v2            │ Microsoft │ High quality        │
│ nomic-embed-text-v1.5  │ Nomic     │ Good all-around     │
└────────────────────────┴───────────┴─────────────────────┘

Pros: Free, private, no internet needed
Cons: Uses your CPU/GPU, slower on CPU
```

### API Models (Cloud-Based)

```
┌────────────────────────┬───────────┬─────────────────────┐
│ Model                  │ Provider  │ Notes               │
├────────────────────────┼───────────┼─────────────────────┤
│ text-embedding-3-small │ OpenAI    │ Cheap, fast         │
│ text-embedding-3-large │ OpenAI    │ Best quality        │
│ embed-v3               │ Cohere    │ Multilingual        │
│ Gemini embedding       │ Google    │ Good quality        │
└────────────────────────┴───────────┴─────────────────────┘

Pros: Fast, no local compute needed
Cons: Costs money, needs internet, data leaves your machine
```

---

## 10. Use Cases

### Use Case 1: Semantic Search

```
Traditional search:
Query: "How to fix broken pipe"
Finds: documents containing "fix" AND "broken" AND "pipe"
Misses: "plumbing repair guide" (no matching keywords)

Embedding search:
Query: "How to fix broken pipe" → [0.2, 0.8, ...]
Finds: "plumbing repair guide"  → [0.21, 0.79, ...] (similar vector!)
```

### Use Case 2: RAG (Retrieval-Augmented Generation)

```
┌──────────┐    ┌──────────┐    ┌────────────────┐
│Documents │───▶│ Embed    │───▶│Vector Database │
│          │    │          │    │(store vectors) │
└──────────┘    └──────────┘    └───────┬────────┘
                                        │
┌──────────┐    ┌──────────┐    Search  │
│User Query│───▶│ Embed    │───▶(find   │
│          │    │          │    nearest)│
└──────────┘    └──────────┘       │
                                   ▼
                          ┌─────────────────┐
                          │ Retrieved Docs   │
                          │ + User Query     │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   LLM Answer     │
                          └─────────────────┘
```

### Use Case 3: Duplicate Detection

```python
docs = [
    "The project deadline is Friday",
    "Friday is the due date for the project",  # duplicate meaning
    "We need more office supplies"              # different
]

embeddings = embed_texts(docs)

sim_0_1 = cosine_similarity(embeddings[0], embeddings[1])  # ~0.93 duplicate!
sim_0_2 = cosine_similarity(embeddings[0], embeddings[2])  # ~0.12 different
```

### Use Case 4: Clustering

```
Group similar documents automatically:

Cluster 1 (Sports):
├── "The team won the championship"
├── "Soccer match ended in a draw"
└── "Athletes trained for Olympics"

Cluster 2 (Technology):
├── "New smartphone released today"
├── "AI breakthrough in research"
└── "Software update available"

Cluster 3 (Weather):
├── "Heavy rain expected tomorrow"
├── "Sunny skies all week"
└── "Temperature dropping tonight"
```

### Use Case 5: Recommendation

```
User liked:     "Introduction to Machine Learning"
                    → embedding: [0.5, 0.8, 0.3, ...]

Recommendations (nearest vectors):
├── "Deep Learning Basics"          → similarity: 0.92
├── "Neural Networks Explained"     → similarity: 0.89
├── "Statistics for Data Science"   → similarity: 0.78
└── "Cooking Italian Food"          → similarity: 0.05 (skip!)
```

---

## 11. Query vs Document Embedding

```
Some models (like BGE) treat queries and documents DIFFERENTLY.

Query (short question):
├── Needs instruction prefix
├── "Represent this sentence for searching: What is AI?"
└── Optimized for FINDING relevant documents

Document (long passage):
├── No prefix needed
├── "Artificial intelligence is a branch of computer science..."
└── Optimized for BEING FOUND

┌──────────────────┬───────────────────┬──────────────────┐
│ Method           │ Prefix Added?     │ Used For         │
├──────────────────┼───────────────────┼──────────────────┤
│ model.encode()        │ No           │ Documents        │
│ model.encode_queries()│ Yes          │ Search queries   │
└──────────────────┴───────────────────┴──────────────────┘
```

---

## 12. Vector Databases (Where Embeddings Are Stored)

```
Regular Database:
├── Stores text, numbers, dates
├── Search by: exact match, range, keywords
└── SELECT * FROM docs WHERE title = "AI"

Vector Database:
├── Stores embedding vectors
├── Search by: nearest neighbors (similarity)
└── "Find 10 vectors closest to this query vector"

Popular Vector Databases:
┌──────────────┬────────────┬─────────────────────┐
│ Database     │ Type       │ Notes               │
├──────────────┼────────────┼─────────────────────┤
│ ChromaDB     │ Local      │ Simple, good start  │
│ FAISS        │ Local      │ Facebook, very fast │
│ Qdrant       │ Both       │ Rust-based, fast    │
│ Pinecone     │ Cloud      │ Managed, easy       │
│ Weaviate     │ Both       │ Feature-rich        │
│ Milvus       │ Both       │ Scalable            │
│ pgvector     │ Local      │ PostgreSQL extension│
└──────────────┴────────────┴─────────────────────┘
```

---

## 13. Embedding Storage Size

```
How much space do embeddings take?

Formula: num_documents × dimensions × 4 bytes (float32)

Example with bge-large (1024 dimensions):

┌──────────────┬────────────────┬───────────────┐
│ Documents    │ Calculation    │ Storage       │
├──────────────┼────────────────┼───────────────┤
│ 1,000        │ 1K × 1024 × 4 │ ~4 MB         │
│ 10,000       │ 10K × 1024 × 4│ ~40 MB        │
│ 100,000      │ 100K×1024 × 4 │ ~400 MB       │
│ 1,000,000    │ 1M × 1024 × 4 │ ~4 GB         │
│ 10,000,000   │ 10M× 1024 × 4 │ ~40 GB        │
└──────────────┴────────────────┴───────────────┘
```

---

## 14. Complete Working Example

```python
from typing import List
import numpy as np
from FlagEmbedding import FlagModel

# ─── Load Model (once) ───
model = FlagModel(
    'BAAI/bge-small-en-v1.5',
    query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
    use_fp16=False
)

# ─── Embed Documents ───
def embed_texts(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    if not texts:
        return []

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = model.encode(batch)
        if isinstance(embeddings, np.ndarray):
            all_embeddings.extend(embeddings.tolist())
        else:
            all_embeddings.extend(embeddings)
    return all_embeddings

# ─── Embed Queries ───
def embed_queries(queries: List[str]) -> List[List[float]]:
    if not queries:
        return []
    embeddings = model.encode_queries(queries)
    if isinstance(embeddings, np.ndarray):
        return embeddings.tolist()
    return embeddings

# ─── Similarity Function ───
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ─── Usage ───
documents = [
    "Python is a programming language",
    "Java is used for enterprise software",
    "Cats are adorable pets",
    "Dogs are loyal companions"
]

query = "What programming languages exist?"

# Embed everything
doc_embeddings = embed_texts(documents)
query_embedding = embed_queries([query])[0]

# Find most similar document
for i, doc in enumerate(documents):
    sim = cosine_similarity(query_embedding, doc_embeddings[i])
    print(f"Similarity: {sim:.4f} | {doc}")

# Output:
# Similarity: 0.8234 | Python is a programming language    ← MOST SIMILAR
# Similarity: 0.7891 | Java is used for enterprise software ← SIMILAR
# Similarity: 0.1234 | Cats are adorable pets               ← NOT SIMILAR
# Similarity: 0.1567 | Dogs are loyal companions            ← NOT SIMILAR
```

---

## 15. Key Terminology

```
┌─────────────────────┬──────────────────────────────────────────┐
│ Term                │ Meaning                                  │
├─────────────────────┼──────────────────────────────────────────┤
│ Embedding           │ Numerical vector representing text       │
│ Vector              │ A list of numbers [0.1, 0.2, ...]       │
│ Dimension           │ How many numbers in the vector (384/768) │
│ Dense Embedding     │ All values are meaningful (not zeros)    │
│ Sparse Embedding    │ Mostly zeros (keyword-based)             │
│ Tokenization        │ Splitting text into small pieces         │
│ Cosine Similarity   │ Measure of angle between two vectors     │
│ Dot Product         │ Quick similarity when vectors normalized │
│ Nearest Neighbor    │ Finding the closest vector to a query    │
│ Pooling             │ Combining token vectors into one vector  │
│ Normalization       │ Scaling vector to length 1               │
│ Semantic            │ Related to meaning (not just keywords)   │
│ Vector Database     │ Database optimized for storing vectors   │
│ Retrieval           │ Finding relevant documents               │
│ Encoding            │ Converting text to embedding             │
│ fp16 / fp32         │ Precision of numbers (16-bit / 32-bit)   │
│ Batch Size          │ Number of texts processed at once        │
│ MTEB Benchmark      │ Standard test for embedding quality      │
└─────────────────────┴──────────────────────────────────────────┘
```

---

## 16. Quick Reference Card

```
EMBEDDING = Text → Numbers that capture meaning

WHY:    Computers need numbers, not text
HOW:    Neural network (transformer) converts text
WHAT:   List of 384-3072 floating point numbers
WHERE:  Stored in vector databases
WHEN:   Before search, during indexing, for similarity

SIMILAR meaning → SIMILAR numbers → HIGH cosine similarity
DIFFERENT meaning → DIFFERENT numbers → LOW cosine similarity

Model choices:
├── bge-small (fast, good)
├── bge-base (balanced)
├── bge-large (slow, best)
└── OpenAI API (easy, costs money)

Key functions:
├── model.encode(texts)          → embed documents
├── model.encode_queries(queries)→ embed search queries
└── cosine_similarity(a, b)      → compare two embeddings
```