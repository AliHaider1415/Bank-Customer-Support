# Bank Customer Support Chatbot — Architecture

This document describes the high-level architecture and request flow. Diagrams use [Mermaid](https://mermaid.js.org/); they render on GitHub, GitLab, and in many Markdown viewers.

---

## 1. Component overview

All components run in a **single process**. There is no separate API server; the Streamlit app drives the UI, applies guardrails, and calls the RAG pipeline directly.

```mermaid
flowchart TB
    subgraph User
        U[User / Browser]
    end

    subgraph App["Bank Customer Support Chatbot (single process)"]
        ST[Streamlit UI\napp_streamlit.py]
        GR[Guardrails\ninput validation, output filtering]
        RES[Resources\nembedding model, Pinecone client, HF client]
        EMB[Embeddings\ngenerate_embeddings, ingest_documents]
        SRC[Search\nretrieve_context]
        LLM[LLM\nllm_call + system prompt]
    end

    subgraph Offline["Offline pipeline"]
        PP[Preprocessing\npreprocess.py]
        DI[Data Injection\nscript.py]
    end

    subgraph External["External services"]
        PC[(Pinecone\nbadar-index, 1024-dim)]
        HF[Hugging Face\nInference API]
    end

    U <-->|"questions / answers / uploads"| ST
    ST --> GR
    GR --> SRC
    GR --> LLM
    RES --> EMB
    RES --> SRC
    RES --> LLM
    SRC --> EMB
    SRC -->|"query vectors"| PC
    PC -->|"context chunks"| SRC
    LLM -->|"system prompt + context + query"| HF
    HF -->|"generated answer"| LLM
    LLM --> GR
    ST -->|"file upload"| EMB
    EMB -->|"upsert vectors"| PC
    PP -->|"preprocessed_chunks.json"| DI
    DI --> EMB
```

**In words:**

- **Streamlit UI** — Renders the page, captures user questions and file uploads, calls the RAG pipeline, and displays answers with expandable retrieved context.
- **Guardrails** — Three-layer safety: input sanitization & validation (prompt injection, harmful content, off-topic detection), system prompt enforcement, and output validation (PII redaction, harmful content filtering).
- **Resources** — Loaded once at startup via lazy singleton (`get_resources()`): BGE-large embedding model (1024-dim), Pinecone client, and Hugging Face inference client.
- **Embeddings** — Turns text (query or chunks) into 1024-dim vectors using `BAAI/bge-large-en-v1.5`. Also handles real-time ingestion via `ingest_documents()`.
- **Search** — Embeds the query, queries Pinecone for top-3 similar chunks, returns context strings.
- **LLM** — Sends a safety-hardened system prompt + context + question to `meta-llama/Llama-3.2-1B-Instruct` via HuggingFace Inference API.
- **Preprocessing** (offline) — Reads raw Excel, cleans text, anonymizes PII, outputs chunked JSON.
- **Data Injection** (offline) — Loads preprocessed chunks, generates embeddings, upserts to Pinecone.

---

## 2. Request flow (sequence)

When the user clicks **Ask**, the following sequence runs in-process.

```mermaid
sequenceDiagram
    participant U as User
    participant ST as Streamlit
    participant GR as Guardrails
    participant SRC as Search
    participant EMB as Embeddings
    participant RES as Resources
    participant PC as Pinecone
    participant LLM as LLM
    participant HF as Hugging Face

    U->>ST: Enter question + click Ask
    ST->>RES: Ensure resources loaded (embedding model, clients)
    RES-->>ST: OK

    ST->>GR: sanitize_input(query)
    GR-->>ST: sanitized query
    ST->>GR: validate_input(query)
    GR-->>ST: (is_safe, refusal_msg)
    alt Input blocked
        ST->>U: Show refusal message
    end

    ST->>SRC: retrieve_context(query)
    SRC->>EMB: generate_embeddings([query])
    EMB->>RES: tokenizer + embedding_model (BAAI/bge-large-en-v1.5)
    RES-->>EMB: model
    EMB-->>SRC: query_embedding (1024-dim)

    SRC->>PC: index.query(vector=query_embedding, top_k=3)
    PC-->>SRC: matches (metadata.text)
    SRC-->>ST: context_chunks

    ST->>LLM: llm_call(context_chunks, query)
    LLM->>LLM: Build messages (system prompt + context + question)
    LLM->>HF: chat.completions.create(model=Llama-3.2-1B-Instruct)
    HF-->>LLM: completion.choices[0].message.content
    LLM-->>ST: answer

    ST->>GR: validate_output(answer)
    GR-->>ST: (is_safe, cleaned_answer)

    ST->>U: Show cleaned answer + expandable "View retrieved context"
```

---

## 3. Data flow (simplified)

**Query flow (runtime):**

```mermaid
flowchart LR
    A[User question] --> B[Sanitize + Validate input]
    B -->|blocked| Z[Refusal message]
    B -->|safe| C[Embed query\nBGE-large 1024-dim]
    C --> D[Pinecone: top-3 similar chunks]
    D --> E[Context text]
    E --> F[System prompt + context + question]
    F --> G[LLM\nLlama-3.2-1B-Instruct]
    G --> H[Validate output + redact PII]
    H --> I[Streamlit UI]
```

**Upload flow (real-time):**

```mermaid
flowchart LR
    A[User uploads file\nJSON / CSV / TXT] --> B[Parse into chunks]
    B --> C[Embed chunks\nBGE-large 1024-dim]
    C --> D[Upsert to Pinecone]
    D --> E[Immediately queryable]
```

**Offline preprocessing flow:**

```mermaid
flowchart LR
    A[Excel file\n33 product sheets] --> B[Preprocess\nclean + anonymize + chunk]
    B --> C[preprocessed_chunks.json\n726 chunks]
    C --> D[Data injection\nembed + upsert]
    D --> E[Pinecone index]
```

---

## 4. File-to-component mapping

| Layer          | File(s)                                    | Role |
|---------------|---------------------------------------------|------|
| Entry          | `main.py`, `app_streamlit.py`              | Launcher and Streamlit app; loads resources, applies guardrails, handles uploads, and wires UI to RAG. |
| Resources      | `app/services/resources.py`                | Lazy singleton via `get_resources()`: `BAAI/bge-large-en-v1.5` embedding model (1024-dim), Pinecone index (`badar-index`), HuggingFace inference client. |
| Guardrails     | `app/services/guardrails/functions.py`     | `sanitize_input()`, `validate_input()` (prompt injection, harmful, off-topic detection), `validate_output()` (PII redaction, harmful content filtering). |
| Embeddings     | `app/services/embeddings/functions.py`     | `generate_embeddings()`, `upload_embeddings_to_pinecone()`, `ingest_documents()` for real-time upload indexing. |
| Search         | `app/services/search/functions.py`         | `retrieve_context(query)` → embed → Pinecone top-3 query → return context chunks. |
| LLM            | `app/services/llm/functions.py`            | `llm_call(context_chunks, query)` → system prompt + context + question → `Llama-3.2-1B-Instruct` via HuggingFace → return answer. |
| Preprocessing  | `scripts/preprocessing/preprocess.py`      | Reads Excel, cleans text, anonymizes PII, Q&A pairing, outputs `preprocessed_chunks.json` (726 chunks). |
| Data Injection | `scripts/data_injection/script.py`         | Loads preprocessed chunks, generates embeddings, batch upserts to Pinecone. |

---

## 5. Deployment view (single host)

```mermaid
flowchart LR
    subgraph Host["Your machine or server"]
        APP[Python process\nStreamlit + RAG + Guardrails]
        MDL[BAAI/bge-large-en-v1.5\nlocal embedding model]
    end

    subgraph Cloud["Cloud services"]
        PC[(Pinecone\nbadar-index, 1024-dim)]
        HF[Hugging Face Inference API\nLlama-3.2-1B-Instruct]
    end

    Browser[Browser] <-->|"queries, uploads,\nanswers"| APP
    APP --- MDL
    APP <-->|"vector upsert / search"| PC
    APP <-->|"LLM chat completion"| HF
```

No API gateway or separate backend is required; a single `streamlit run app_streamlit.py` (or `python main.py`) process serves the UI, runs the full RAG pipeline, and applies guardrails. The embedding model runs locally; the LLM and vector DB are cloud services.
