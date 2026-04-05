"""
Bank Customer Support Chatbot — Streamlit UI.
RAG runs in-process (no API): retrieve_context + llm_call.
"""
import csv
import io
import json
import uuid

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def load_resources():
    """Load embedding model and set resources once (used by retrieve_context)."""
    from app.services.resources import get_resources
    return get_resources()


def answer_query(query: str):
    """Run RAG in-process: retrieve context, then LLM."""
    from app.services.search.functions import retrieve_context
    from app.services.llm.functions import llm_call
    context_chunks = retrieve_context(query)
    return llm_call(context_chunks, query), context_chunks


st.set_page_config(
    page_title="Bank Customer Support",
    page_icon="🏦",
    layout="centered",
)

st.title("🏦 Bank Customer Support")
st.caption("Ask a question. Answers are based on bank support content (RAG).")

# Ensure resources are loaded before any query (for embeddings)
try:
    load_resources()
except Exception as e:
    st.error(f"Failed to load model: {e}")
    st.stop()

# ── Custom CSS: fuse the + button, text input, and Ask button into one bar ──
st.markdown("""
<style>
/* Remove vertical gaps inside the input row */
div[data-testid="column"] { padding: 0 2px; }

/* Make the popover trigger look like a rounded-left icon button */
div[data-testid="column"]:first-child button[kind="secondary"] {
    border-radius: 12px 0 0 12px;
    height: 42px;
    width: 42px;
    padding: 0;
    font-size: 1.3rem;
    margin-top: 0px;
}

/* Remove rounded corners from the text input sides */
div[data-testid="column"]:nth-child(2) input {
    border-radius: 0;
    height: 42px;
}

/* Make the Ask button rounded on the right */
div[data-testid="column"]:last-child button {
    border-radius: 0 12px 12px 0;
    height: 42px;
    margin-top: 0px;
}

/* Hide file-uploader drag text & instructions inside popover */
section[data-testid="stFileUploader"] > div:first-child { min-height: 0; }
</style>
""", unsafe_allow_html=True)

# ── Input row: [+] [ query ...             ] [Ask] ──
col_plus, col_input, col_ask = st.columns([0.06, 0.82, 0.12])

with col_plus:
    upload_pop = st.popover("➕")
    with upload_pop:
        st.markdown("**Upload a document** (JSON / CSV / TXT)")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["json", "csv", "txt"],
            label_visibility="collapsed",
        )

with col_input:
    query = st.text_input(
        "Your question",
        placeholder="e.g. How do I reset my password?",
        label_visibility="collapsed",
    )

with col_ask:
    ask_clicked = st.button("Ask", type="primary", use_container_width=True)

# ── Handle file upload (real-time indexing) ───────────────────────────
if uploaded_file is not None:
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        with st.status("Uploading & indexing document…", expanded=True) as status:
            try:
                raw = uploaded_file.read().decode("utf-8")
                name = uploaded_file.name.lower()
                chunks = []

                if name.endswith(".json"):
                    st.write("Parsing JSON…")
                    data = json.loads(raw)
                    if not isinstance(data, list):
                        data = [data]
                    for item in data:
                        chunks.append({
                            "id": item.get("id", str(uuid.uuid4())),
                            "text": item["text"],
                            "account": item.get("account", "unknown"),
                        })

                elif name.endswith(".csv"):
                    st.write("Parsing CSV…")
                    reader = csv.DictReader(io.StringIO(raw))
                    for row in reader:
                        if "text" not in row or not row["text"].strip():
                            continue
                        chunks.append({
                            "id": row.get("id") or str(uuid.uuid4()),
                            "text": row["text"].strip(),
                            "account": row.get("account", "unknown").strip(),
                        })

                elif name.endswith(".txt"):
                    st.write("Parsing TXT…")
                    for line in raw.splitlines():
                        line = line.strip()
                        if line:
                            chunks.append({
                                "id": str(uuid.uuid4()),
                                "text": line,
                                "account": "unknown",
                            })

                if not chunks:
                    st.warning("No valid chunks found in the file.")
                else:
                    st.write(f"Embedding & indexing {len(chunks)} chunks…")
                    from app.services.embeddings.functions import ingest_documents
                    count = ingest_documents(chunks)
                    status.update(label="Done!", state="complete", expanded=False)
                    st.success(f"✅ Indexed {count} chunks from **{uploaded_file.name}**. They are now queryable.")
                    st.session_state.last_uploaded = uploaded_file.name

            except KeyError as e:
                st.error(f"Missing required field in file: {e}")
            except Exception as e:
                st.error(f"Upload failed: {e}")

# ── Handle query ──────────────────────────────────────────────────────
if not query.strip():
    st.info("Enter a question above to get an answer.")
    st.stop()

if ask_clicked:
    from app.services.guardrails.functions import validate_input, sanitize_input, validate_output

    safe_query = sanitize_input(query.strip())
    is_safe, refusal_msg = validate_input(safe_query)

    if not is_safe:
        st.warning(refusal_msg)
    else:
        with st.spinner("Searching and generating answer…"):
            try:
                answer, context_chunks = answer_query(safe_query)
                output_ok, cleaned_answer = validate_output(answer)
                st.markdown("### Answer")
                if output_ok:
                    st.markdown(cleaned_answer)
                else:
                    st.warning(cleaned_answer)
                with st.expander("View retrieved context"):
                    for i, c in enumerate(context_chunks, 1):
                        st.text(c)
            except Exception as e:
                st.error(f"Error: {e}")
