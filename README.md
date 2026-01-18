# Project Chat Bot

A small Retrieval-Augmented Generation (RAG) document chatbot built with Flask. The bot searches uploaded documents using a vector store (OpenAI/Gemini), then streams concise, source-grounded answers to the browser.

## Overview

- Purpose: Provide a web UI for asking questions about project documents and receive retrieval-grounded answers streamed in real time.
- Core idea: User queries are sent to a retrieval agent which uses a vector store to retrieve relevant document content and returns answers strictly based on retrieved text.

## Key Features

- Streaming responses to the browser for a live chat experience.
- Retrieval-first answers using a `FileSearchTool` and strict instructions to avoid hallucination.
- Helper scripts to create and ingest documents into a vector store.
- Minimal dark-themed web UI built with Flask.

## Requirements

- Python 3.13+
- See `pyproject.toml` for declared dependencies (Flask, openai-agents, python-dotenv).

## Quick Setup

1. Install dependencies:

```bash
python -m pip install flask openai-agents python-dotenv
```

2. Create or upload documents into a vector store (one of):

```bash
python create_vector_store.py
# or
python ingest.py
```

3. Create a `.env` file in the project root with your API keys and the vector store id (example below).

4. Run the app:

```bash
python main.py
# Open http://127.0.0.1:5000/
```

## `.env` example

Create a `.env` file and set the following variables (or use your environment manager of choice):

```
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
VECTOR_STORE_ID=your_vector_store_id_here
```

Notes:
- `GEMINI_API_KEY` is used by `config.py` when using Gemini through the custom client.
- `OPENAI_API_KEY` is used by the ingestion scripts (`create_vector_store.py` / `ingest.py`).
- After uploading documents, copy the resulting vector store ID into `VECTOR_STORE_ID` so the agent can query it.

## File map

- [pyproject.toml](pyproject.toml) — project metadata & dependencies
- [config.py](config.py) — environment loading and model/client wrapper
- [main.py](main.py) — Flask app and streaming `/chat` endpoint
- [my_agent.py](my_agent.py) — agent setup, retrieval instructions, and streaming helper
- [create_vector_store.py](create_vector_store.py) — helper to create and upload files to a vector store
- [ingest.py](ingest.py) — alternate ingestion flow using OpenAI client
- [templates/index.html](templates/index.html) — frontend UI and streaming client code
- [static/styles.css](static/styles.css) — UI styling
- [data/docs.txt](data/docs.txt) — example document used for retrieval

## How it works (high level)

- The Flask UI posts user questions to `/chat`.
- `main.py` uses `stream_agent_response()` from `my_agent.py` to stream incrementally produced text deltas.
- `my_agent.py` configures an `Agent` with `FileSearchTool` and a `SQLiteSession` for chat state; retrieval queries the configured vector store.

## Usage notes & caveats

- The agent is intentionally strict: it will answer only from retrieved document content and will say when information is not available.
- Ensure relevant documents are uploaded to the configured vector store; otherwise the agent will report missing information.
- Streaming depends on the client handling chunked responses — the included frontend (`templates/index.html`) already implements a streaming reader.

---

If you want, I can also add a `.env.example` file to the repo and/or create a short `requirements.txt`. Would you like me to add either of those now?

