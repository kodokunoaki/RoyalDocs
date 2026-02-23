# <p align="center"> RoyalDocs </p>

[![CI](https://github.com/kodokunoaki/RoyalDocs/actions/workflows/pylint.yml/badge.svg)](https://github.com/kodokunoaki/RoyalDocs/actions)

A service for managing JSON documents ("scrolls" and "parchments") across the kingdom. Built with FastAPI and PostgreSQL, it supports JWT-authenticated CRUD, nested path navigation, document diffing, and periodic background data ingestion.

---

## Overview

After the Conjunction of the Spheres, knowledge takes the form of JSON. Documentarium is the royal archive - a REST microservice that stores, retrieves, and compares JSON documents of two kinds:

- **Scrolls** (`scroll`) — structured documents conforming to a strict JSON schema, authored by scholars.
- **Parchments** (`parchment`) — arbitrary valid JSON, submitted by common folk.

All endpoints require JWT authentication. The service also runs a background task that periodically fetches data from a configured URL and merges the response into every document's root.

---

## Service Dependencies

| Dependency | Role |
|---|---|
| **PostgreSQL** | Primary document and user storage |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12 |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Database driver | asyncpg |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Containerisation | Docker + Docker Compose |

---

## Prerequisites

- Docker and Docker Compose
- No local Python installation required

---

## Routes

### Auth — `/auth`

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth` | Obtain a JWT access token (OAuth2 password flow) |

### Documents — `/docs`

All routes below require a valid `Authorization: Bearer <token>` header.

#### Core CRUD

| Method | Path | Description |
|---|---|---|
| `POST` | `/docs` | Create a new document; owner is set to the authenticated user |
| `GET` | `/docs` | List own documents with pagination (`limit`, `offset`) |
| `GET` | `/docs/{id}` | Retrieve a full document by ID |
| `PATCH` | `/docs/{id}` | Partially update `title` and/or `content` of a document |
| `DELETE` | `/docs/{id}` | Permanently delete a document |

#### Nested path navigation

Paths follow document nesting: `keyA/keyB/keyC` maps to `content["keyA"]["keyB"]["keyC"]`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/docs/{id}/path/{path}` | Read a nested block at the given key path |
| `PATCH` | `/docs/{id}/path/{path}` | Replace a nested block at the given key path |
| `DELETE` | `/docs/{id}/path/{path}` | Remove a nested block at the given key path |

#### Diff

| Method | Path | Description |
|---|---|---|
| `GET` | `/docs/diff?a={id}&b={id}` | Compare two documents; returns added, removed, and changed keys with old/new values |

### Health — `/health`

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check; returns service status |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kodokunoaki/amicon-test.git
cd documentarium
```

### 2. Configure environment

Copy the example env file and fill in the values:

```bash
cp .env.example .env
```

### 3. Start the stack

```bash
docker compose up --build
```

### Stopping

```bash
docker compose down
docker compose down -v
```

---

## Notes on Project Decisions

**Simple authentication.** Simple JWT authentication with single user was chosen because scalable microservice authentication in my opinion requires separate service for authentication and role-based access control model. It would be overkill for this task to implement that.

**Single `content` JSON column.** The entire document is stored as a single `JSON` column in PostgreSQL. Navigating nested keys (`keyA/keyB/keyC`) is handled in application code rather than with generated columns or JSONB operators. This keeps the schema simple and avoids coupling the API contract to the database query language.

**Explicit dict copy for JSON mutation.** SQLAlchemy 2's async session does not track in-place mutations to JSON fields. Every path write operation copies `doc.content` into a new `dict`, mutates it, and reassigns it so the ORM registers the change and emits an `UPDATE`.

**PUT intentionally omitted.** A full replacement of a document can have destructive consequences. `PATCH` on the root or a specific path is a safer default. PUT can be added later behind a flag or a specific `force=true` query parameter.

**AI Usage.** AI was used for boilerplate generation and README realisation via requested template. I prefer to use modern instruments so I can save time and use it for key features.