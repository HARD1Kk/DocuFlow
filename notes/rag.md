
# Notes: Building a Scalable RAG System for AI Apps

## 1. What is RAG (Retrieval Augmented Generation)

Large Language Models (LLMs) do not know private or internal data because they are trained on public internet data.

**RAG solves this problem** by retrieving relevant information from internal documents before generating an answer.

### RAG Workflow

1. **Retrieve** – Search relevant information from documents.
2. **Augment** – Combine retrieved information with the user query.
3. **Generate** – Send this combined prompt to the LLM to generate an answer.

So the pipeline is:

**Retrieve → Augment → Generate** 

Advantages:

* No need to retrain the model
* No huge compute costs
* Just requires document search + context injection into the LLM 

---

# 2. Problem with Basic RAG

A study showed that **bad retrieval is worse than no retrieval**.

If incorrect context is retrieved:

* The LLM becomes **more confident**
* It may **hallucinate incorrect answers**

Example issues:

* Retrieved policy document may be **outdated**
* Chunk may contain **incomplete sentences**
* Tables may become **messy text after extraction**

Even if retrieval appears relevant, the context might be:

* incomplete
* outdated
* incorrect

This causes the system to produce **confident but wrong answers**. 

---

# 3. Difference Between Demo RAG and Production RAG

### Demo RAG

* Clean documents
* Predictable queries
* Simple architecture

### Production RAG

Real-world challenges:

* messy documents
* tables, images, headers, footers
* multiple document versions
* vague user queries

Therefore production systems require **more advanced architecture**. 

---

# 4. Production RAG Architecture

Production RAG consists of several components:

1. Data Sources
2. Data Processing
3. Database Layer
4. Retrieval System
5. Reasoning Engine
6. Validation Layer
7. Evaluation System
8. Stress Testing

---

# 5. Data Sources

Organizations contain different types of data:

* Documents
* Code
* Images
* Spreadsheets
* Structured and unstructured data

These must first go through a **data processing pipeline**. 

---

# 6. Data Processing Pipeline (Data Ingestion)

### 1. Restructuring Layer

Raw documents are parsed to understand structure such as:

* headings
* paragraphs
* tables
* code blocks

Structure must be preserved because it carries meaning. 

---

### 2. Structure-Aware Chunking

Instead of splitting blindly every fixed token size, chunks respect document structure.

Examples:

* heading stays with its paragraph
* tables remain intact
* functions are not cut in half

Typical chunk size:

**256 – 512 tokens with overlap**

Exact size is less important than respecting structure. 

---

### 3. Metadata Creation

For each chunk additional metadata is generated:

* summary of the chunk
* keywords
* hypothetical questions the chunk could answer

Why hypothetical questions?

Because matching **question-to-question works better than question-to-paragraph** during retrieval. 

---

# 7. Database Layer

Basic RAG tutorials use only a **vector database**.

Production systems require both:

* **Embeddings (vector search)**
* **Relational metadata**

Reasons:

* filtering by date
* filtering by department
* joining chunks with original documents
* tracking document versions

Therefore many systems combine **vector search + relational database**. 

---

# 8. Query Processing

In basic RAG:

User Query → Embedding → Vector Search

But real queries are often:

* vague
* multi-step
* requiring multiple information sources

So production systems add **additional reasoning layers**. 

---

# 9. Hybrid Retrieval

Production retrieval combines:

1. **Vector Search**
2. **Keyword Search**

### Vector Search

Good for semantic similarity.

### Keyword Search

Good for:

* product names
* error codes
* exact terms

Results from both are then **reranked to find the most relevant chunks**. 

---

# 10. Reasoning Engine

Complex queries may require multiple steps.

Example query:

Compare Q3 performance in Europe vs Asia and suggest focus for next quarter.

Required steps:

* retrieve Europe data
* retrieve Asia data
* analyze trends
* perform reasoning

A **planner** breaks the query into steps and executes them. 

---

# 11. Multi-Agent System

Advanced RAG systems may use multiple agents.

Each agent specializes in tasks such as:

* retrieving financial data
* summarization
* performing calculations

Agents coordinate to produce the final answer.

This approach is known as **Agentic RAG**. 

---

# 12. Validation Layer

Because complex systems can produce incorrect results, validation nodes are used before returning the answer.

Types of validators:

### Gatekeeper

Checks whether the response actually answers the user’s question.

### Auditor

Verifies that the response is grounded in retrieved context.

### Strategist

Evaluates whether the response logically makes sense.

These steps help reduce hallucinations. 

---

# 13. Evaluation System

Production systems require evaluation metrics.

### 1. Qualitative Evaluation

Uses LLM judges to evaluate:

* faithfulness
* relevance
* depth

### 2. Quantitative Evaluation

Measures:

* retrieval precision
* retrieval recall

### 3. Performance Evaluation

Measures:

* latency
* cost
* token usage

Without evaluation, system quality cannot be monitored. 

---

# 14. Stress Testing (Red Teaming)

Before deployment systems must be tested for weaknesses.

Testing includes:

* prompt injection attacks
* information leakage
* biased responses
* harmful outputs

This helps identify vulnerabilities before users encounter them. 

---

# 15. Complete Production RAG Pipeline

A production-ready RAG system includes:

1. Structured data ingestion
2. Structure-aware chunking
3. Metadata generation
4. Vector + relational database
5. Hybrid retrieval
6. Reasoning engine
7. Multi-agent processing
8. Validation nodes
9. Evaluation metrics
10. Stress testing

This architecture goes far beyond the simple:

**Chunk → Embed → Retrieve → Generate**

and is necessary for building reliable AI applications in production. 

