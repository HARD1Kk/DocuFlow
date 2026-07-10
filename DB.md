
## 1. The Core Problem: Why Not Just ChromaDB?

Vector databases like ChromaDB are highly specialized mathematical engines. They are incredible at finding patterns ("Find me text that *means* something similar to X"), but they are terrible at traditional data management.

If you only use ChromaDB, you eventually hit a wall:

* **The Auditing Problem:** If you run the pipeline twice, ChromaDB happily creates duplicate chunks. Checking if a 100-page PDF has already been processed using semantic search is slow and inaccurate.
* **The Versioning Problem:** If a user updates page 5 of a PDF, ChromaDB doesn't know what "page 5" is. You'd have to delete all chunks related to that PDF and re-embed everything, or risk serving outdated chunks.
* **The Join Problem:** If a user says, *"Summarize this topic, but only using documents from the HR department from 2023,"* filtering that strictly inside a vector database is often inefficient or impossible.

**The Solution:** You split the brain. SQLite acts as the "source of truth" for the files and their metadata, while ChromaDB acts purely as a mathematical index for the text.

## 2. Deep Dive: The Data Models

The SQLAlchemy code establishes a strict **One-to-Many** relationship. One `Document` contains many `ChunkRecords`.

### The `Document` Table (The Parent)

This table represents the actual file on your hard drive.

* `file_hash`: This is the most critical column. By hashing the raw file (using SHA-256), you create a unique fingerprint. If someone changes even a single comma in a 50MB PDF, the hash completely changes.
* `version`: Allows you to keep historical data. If the hash changes, you can either overwrite the row or increment the version.

### The `ChunkRecord` Table (The Child & The Bridge)

This table acts as the bridge between your SQL world and your Vector world.

* `chunk_id = Column(String, unique=True)`: This is the magic key. The value stored here will be the **exact same ID** used as the primary key for that specific vector in ChromaDB.
* `document_id = ForeignKey(...)`: Links the chunk back to its parent file.
* `ondelete="CASCADE"`: This is a powerful SQLAlchemy feature. If you delete a `Document` from the database, SQLite will automatically delete all associated `ChunkRecord` rows instantly.

## 3. The New Ingestion Flow

By introducing SQLite, your ingestion pipeline becomes stateful and intelligent. Here is exactly what happens when a file enters the system.

1. **Fingerprint the File:** Hash generation.
The system reads the raw binary of the PDF/document and calculates its SHA-256 hash.


2. **Check the Registry:** SQLite Lookup.
The system queries SQLite: `SELECT * FROM documents WHERE file_hash = ?`. If a match is found, the system halts — this exact file is already in the database. No tokens or compute time are wasted.


3. **Process and Split:** Document Parsing.
If the hash is new, the document is parsed, cleaned, and split into smaller text chunks (e.g., 500 tokens each).


4. **The Dual Write:** ChromaDB + SQLite.
The system generates embeddings for the chunks and stores them in ChromaDB. Simultaneously, it creates a `Document` record and multiple `ChunkRecord` rows in SQLite, ensuring the `chunk_id` matches exactly across both systems.


## 4. The Hidden Danger: The "Dual-Write" Problem

The open question in your plan regarding **Delete Cascading** touches on the most difficult part of this architecture: keeping the two databases synchronized.

Because you are writing to two different systems (SQLite and ChromaDB), you risk **orphaned data**.

**Scenario:**

1. You insert chunks into ChromaDB (Success).
2. You try to insert the metadata into SQLite, but your code throws an error (Failure).
3. **Result:** You now have vectors in ChromaDB that do not exist in SQLite. They are "orphans" and will cause errors during retrieval.

**How to solve this (The Helper Method):**
Whenever you modify data, you must wrap it in a transaction-like pattern. If the SQLite insertion fails, your code must catch the exception and actively issue a `delete` command to ChromaDB to rollback the vectors you just inserted.

Likewise, for deletion, deleting the parent document in SQLite will cascade and delete the SQL chunks, but **it will not automatically delete the vectors in ChromaDB**. Your custom helper method must explicitly grab all the `chunk_id`s from SQLite first, send a delete request to ChromaDB, and *then* delete the SQLite parent document.