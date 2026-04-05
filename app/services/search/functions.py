import os

from pinecone import Pinecone

from app.services.embeddings.functions import generate_embeddings

INDEX_NAME = "badar-index"

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(INDEX_NAME)

def retrieve_context(query: str):
    print(">>> retrieve_context start")

    query_embedding = generate_embeddings([query])[0]
    print(">>> embedding done")

    results = index.query(
        vector=query_embedding.tolist(),
        top_k=3,
        include_metadata=True
    )
    print(">>> pinecone query done")

    contexts = []

    for match in results["matches"]:
        text = match["metadata"].get("text", "")
        contexts.append(text)

    return contexts