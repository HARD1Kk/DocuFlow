In basic RAG:

User Query → Embedding → Vector Search

But real queries are often:

vague

poorly structured

requiring multiple pieces of information

Therefore additional retrieval techniques are required.




# Hybrid Search

Production systems combine two search techniques.

Vector Search

Good for understanding meaning.

Keyword Search

Good for exact matches like:

product names

error codes

specific terminology

The results from both searches are combined and reranked to find the most relevant chunks.


# Handling Complex Queries

Some queries require reasoning across multiple sources.

Example:

Compare Q3 performance in Europe and Asia and recommend which region to focus on next quarter.

To answer this question, the system must:

retrieve Europe data

retrieve Asia data

analyze historical trends

perform reasoning

This cannot be solved by a single retrieval step.



# Reasoning Engine

Production systems introduce a reasoning engine.

The reasoning engine includes:

### Planner

The planner determines:

what information is required

which steps must be executed

which tools should be used

### Tool Execution Layer

The system performs actions such as:

multiple retrievals

API calls

calculations


# Multi-Agent Systems

Some advanced systems use multiple specialized agents.

Examples of agents:

financial data retrieval agent

summarization agent

calculation agent

Each agent performs a specific task and contributes to the final answer.

This architecture is often called:

Agentic RAG.

The planner creates a plan and then the tool execution layer carries it out. Maybe it
runs multiple retrievalss, maybe it calls an external API for market data and maybe it does some calculations. And in more advanced setups, you have a multi- aent system. Different agents specializing in different things. One agent might be good at retrieving financial data. Another might be good at summarization. Another might handle calculations. These agents work on the process database, fetch information relevant to their part of the journey. And then output gets combined into a final response. And this is what people