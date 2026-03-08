"""
Bank Customer Support Chatbot — Streamlit UI.
RAG runs in-process (no API): retrieve_context + llm_call.
"""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def load_resources():
    """Load embedding model and set resources once (used by retrieve_context)."""
    from app.services import resources as res_module
    res_module.resources = res_module.Resources()
    return res_module.resources


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

query = st.text_input(
    "Your question",
    placeholder="e.g. How do I reset my password?",
    label_visibility="collapsed",
)

if not query.strip():
    st.info("Enter a question above to get an answer.")
    st.stop()

if st.button("Ask", type="primary"):
    with st.spinner("Searching and generating answer…"):
        try:
            answer, context_chunks = answer_query(query.strip())
            st.markdown("### Answer")
            st.markdown(answer)
            with st.expander("View retrieved context"):
                for i, c in enumerate(context_chunks, 1):
                    st.text(c)
        except Exception as e:
            st.error(f"Error: {e}")
