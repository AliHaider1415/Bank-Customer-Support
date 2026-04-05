# Bank Customer Support Chatbot

A **Retrieval-Augmented Generation (RAG)** chatbot for bank customer support. Users ask questions in natural language; the app retrieves relevant content from a vector store (Pinecone) and generates answers using a large language model (Hugging Face). The UI is built with **Streamlit** and all RAG logic runs in-process no separate API server.

---

## Features

- **Streamlit UI** — Simple, single-page chat interface.
- **RAG pipeline** — Query → embed → retrieve from Pinecone → generate answer with LLM.
- **In-process execution** — No API; embedding, retrieval, and LLM run inside the same process.
- **Optional context view** — Expand to see the retrieved chunks used for the answer.

---

## Prerequisites

- **Python 3.10+**
- **Pinecone** account and API key
- **Hugging Face** account and API key (for embeddings and LLM)
- A Pinecone index named `bank-customer-support` with embedded support content (see [Project structure](#project-structure))

---

## Project structure

```
Bank Customer Support Chatbot/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # Launcher: run this or streamlit run app_streamlit.py
├── app_streamlit.py         # Streamlit app entry point (UI + RAG in-process)
├── .env                     # Your secrets (create from .env.example; do not commit)
└── app/
    ├── services/
    │   ├── resources.py           # Shared resources: embedding model, Pinecone, HF client
    │   ├── embeddings/
    │   │   └── functions.py       # generate_embeddings, upload_embeddings_to_pinecone
    │   ├── search/
    │   │   └── functions.py       # retrieve_context (embed query → Pinecone → chunks)
    │   └── llm/
    │       └── functions.py       # llm_call (context + query → LLM response)
    └── routes/                    # (Legacy; not used by Streamlit app)
```

**Data flow:** User question → `retrieve_context()` (embed + Pinecone) → `llm_call()` (prompt + LLM) → Answer shown in UI.

---

## Setup

### 1. Clone and enter the project

```bash
cd "Bank Customer Support Chatbot"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root with:

| Variable | Description | Required |
|----------|-------------|----------|
| `PINECONE_API_KEY` | Your Pinecone API key | Yes |
| `HF_TOKEN` | Hugging Face token (embeddings + optional LLM) | Yes |
| `HUGGINGFACE_API_KEY` | Hugging Face API key (used by LLM service) | Yes |
| `LLM_MODEL_NAME` | Hugging Face chat model (e.g. `meta-llama/Llama-3.2-1B-Instruct`) | Yes |

Example `.env`:

```env
PINECONE_API_KEY=your-pinecone-key
HF_TOKEN=your-hf-token
HUGGINGFACE_API_KEY=your-hf-api-key
LLM_MODEL_NAME=meta-llama/Llama-3.2-3B-Instruct
```

**Important:** Do not commit `.env`. Add it to `.gitignore` if you use Git.

---

## How to run

From the project root (with the virtual environment activated):

**Option A — Streamlit directly**

```bash
streamlit run app_streamlit.py
```

**Option B — Via launcher**

```bash
python main.py
```

The app opens in your browser (typically `http://localhost:8501`). The first run may take a moment while the embedding model loads.

---

## How to use the app

1. Open the URL shown in the terminal (e.g. `http://localhost:8501`).
2. Enter a customer-support question in the text box (e.g. *How do I reset my password?*).
3. Click **Ask**.
4. Read the generated answer. Use **View retrieved context** to see the chunks that were used.

---

## Tech stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| Embeddings | Hugging Face (e.g. `google/embeddinggemma-300m`) via `transformers` |
| Vector store | Pinecone |
| LLM | Hugging Face Inference API (`huggingface_hub.InferenceClient`) |
| Config | `python-dotenv` + `.env` |

---

## Troubleshooting

- **“Failed to load model”** — Check `HF_TOKEN` and network access to Hugging Face. Ensure the embedding model name in `app/services/resources.py` is valid and accessible.
- **Empty or irrelevant answers** — Confirm the Pinecone index `bank-customer-support` exists, has vectors with a `text` (and optionally `account`) metadata field, and was embedded with the same model used in `resources.py`.
- **LLM errors** — Verify `HUGGINGFACE_API_KEY` and `LLM_MODEL_NAME` in `.env`. Ensure the model supports chat completions and your account has access.
- **Port already in use** — Run with a different port: `streamlit run app_streamlit.py --server.port 8502`.

---

## License

Use and modify as needed for your organization. Ensure compliance with Hugging Face and Pinecone terms when using their services.
