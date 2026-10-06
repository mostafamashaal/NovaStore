# Database

This directory contains database-related files for NovaStore.

Planned areas include:
- Database schema
- Migrations
- Seed data
- Database scripts# Database

This directory contains database-related files for NovaStore.

Planned areas include:
- Database schema
- Migrations
- Seed data
- Database scripts

## M1.2 — Database Creation

### Overview

This phase verifies that the PostgreSQL database for NovaStore was successfully created and is ready for schema implementation.

### Database Configuration

| Item               | Value       |
| ------------------ | ----------- |
| Database           | `novastore` |
| PostgreSQL User    | `novastore` |
| PostgreSQL Version | `18.6       |
| Default Schema     | `public`    |
| Vector Extension   | `pgvector`  |
| pgvector Version   | `0.8.7`     |

### Verification

The database connection was verified successfully using PostgreSQL's interactive terminal.

The following checks were performed:

* Verified the current database name.
* Verified the current PostgreSQL user.
* Verified the PostgreSQL version.
* Confirmed that the database initially contained no application tables.
* Confirmed that the default `public` schema exists.
* Verified the PostgreSQL user and its development permissions.
* Verified that the `vector` extension is available.
* Enabled the `vector` extension inside the `novastore` database.
* Confirmed that the `vector` extension is installed successfully.

### pgvector

NovaStore uses PostgreSQL with the `pgvector` extension to support AI-related vector operations.

The extension enables PostgreSQL to store vector embeddings that will later be used for:

* Semantic search
* Retrieval-Augmented Generation (RAG)
* Document similarity search
* AI-powered knowledge retrieval

The extension was enabled with:

```
CREATE EXTENSION vector;
```

The installed version is:

```
0.8.7
```

### Current Database State

At the end of M1.2:

* The `novastore` database is operational.
* PostgreSQL is running through Docker.
* The database connection is working.
* The default `public` schema is available.
* `pgvector` is enabled.
* No NovaStore application tables have been created yet.

### Next Phase

The next phase is:

**M1.3 — Schema Implementation**

This phase will implement the NovaStore database design by creating the required tables, relationships, data types, primary keys, and foreign keys based on:

`docs/database-design.md`
