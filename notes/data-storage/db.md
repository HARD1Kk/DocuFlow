7. Database Layer

Most tutorials mention only vector databases.

However production systems require more.

They must support:

embeddings

metadata

relational queries

This allows filtering by:

document date

department

document type

Systems also need to:

join chunks with parent documents

track document versions

Therefore production systems use databases supporting both vectors and relational data.