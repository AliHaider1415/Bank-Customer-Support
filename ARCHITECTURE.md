# Bank Customer Support Chatbot — Architecture

This document describes the high-level architecture and request flow. Diagrams use [Mermaid](https://mermaid.js.org/); they render on GitHub, GitLab, and in many Markdown viewers.

---

## 1. Component overview

All components run in a **single process**. There is no separate API server; the Streamlit app drives the UI and calls the RAG pipeline directly.

```mermaid
flowchart TB
    subgraph User
        U[User / Browser]
    end

    subgraph App["Bank Customer Support Chatbot (single process)"]
        ST[Streamlit UI\napp_streamlit.py]
        RES[Resources\nembedding model, Pinecone client, HF client]
        EMB[Embeddings\ngenerate_embeddings]
        SRC[Search\nretrieve_context]
        LLM[LLM\nllm_call]
    end

    subgraph External["External services"]
        PC[(Pinecone\nvector index)]
        HF[Hugging Face\nInference API]
    end

    U <-->|"questions / answers"| ST
    ST --> SRC
    ST --> LLM
    RES --> EMB
    RES --> SRC
    RES --> LLM
    SRC --> EMB
    SRC -->|"query vectors"| PC
    PC -->|"context chunks"| SRC
    LLM -->|"prompt + context"| HF
    HF -->|"generated answer"| LLM
```

**In words:**

- **Streamlit UI** — Renders the page, captures the user question, calls the RAG pipeline, and displays the answer (and optional context).
- **Resources** — Loaded once at startup: embedding model (e.g. Gemma), Pinecone client, and Hugging Face inference client.
- **Embeddings** — Turns text (query or chunks) into vectors using the shared embedding model.
- **Search** — Embeds the query, queries Pinecone for similar chunks, returns context strings.
- **LLM** — Builds a prompt from context + question and calls Hugging Face to generate the answer.

---

## 2. Request flow (sequence)

When the user clicks **Ask**, the following sequence runs in-process.

```mermaid
sequenceDiagram
    participant U as User
    participant ST as Streamlit
    participant SRC as Search
    participant EMB as Embeddings
    participant RES as Resources
    participant PC as Pinecone
    participant LLM as LLM
    participant HF as Hugging Face

    U->>ST: Enter question + click Ask
    ST->>RES: Ensure resources loaded (embedding model, clients)
    RES-->>ST: OK

    ST->>SRC: retrieve_context(query)
    SRC->>EMB: generate_embeddings([query])
    EMB->>RES: tokenizer + embedding_model
    RES-->>EMB: model
    EMB-->>SRC: query_embedding

    SRC->>PC: index.query(vector=query_embedding, top_k=3)
    PC-->>SRC: matches (metadata.text)
    SRC-->>ST: context_chunks

    ST->>LLM: llm_call(context_chunks, query)
    LLM->>LLM: Build prompt (context + question)
    LLM->>HF: chat.completions.create(...)
    HF-->>LLM: completion.choices[0].message.content
    LLM-->>ST: answer

    ST->>U: Show answer + optional "View retrieved context"
```

---

## 3. Data flow (simplified)

```mermaid
flowchart LR
    A[User question] --> B[Embed query]
    B --> C[Pinecone: top_k similar chunks]
    C --> D[Context text]
    D --> E[Prompt: context + question]
    E --> F[LLM]
    F --> G[Answer]
    G --> H[Streamlit UI]
```

---

## 4. File-to-component mapping

| Layer        | File(s)                          | Role |
|-------------|-----------------------------------|------|
| Entry       | `main.py`, `app_streamlit.py`     | Launcher and Streamlit app; loads resources and wires UI to RAG. |
| Resources   | `app/services/resources.py`       | Singleton: embedding model, Pinecone index, Hugging Face client. |
| Embeddings  | `app/services/embeddings/functions.py` | `generate_embeddings()`; used by search and (for ingestion) `upload_embeddings_to_pinecone()`. |
| Search      | `app/services/search/functions.py`   | `retrieve_context(query)` → embed → Pinecone query → return context chunks. |
| LLM         | `app/services/llm/functions.py`      | `llm_call(context_chunks, query)` → prompt → Hugging Face → return answer. |

---

## 5. Deployment view (single host)

```mermaid
flowchart LR
    subgraph Host["Your machine or server"]
        APP[Python process\nStreamlit + RAG]
    end

    subgraph Cloud["Cloud services"]
        PC[(Pinecone)]
        HF[Hugging Face]
    end

    Browser[Browser] <--> APP
    APP <--> PC
    APP <--> HF
```

No API gateway or separate backend is required; a single `streamlit run app_streamlit.py` (or `python main.py`) process serves the UI and runs the full RAG pipeline.
