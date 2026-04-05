from app.services.resources import get_resources
import torch

def generate_embeddings(chunks_text):
    resources = get_resources()
    tokenizer = resources.tokenizer
    model = resources.embedding_model

    inputs = tokenizer(
        chunks_text,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)

    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings.cpu().numpy()

def upload_embeddings_to_pinecone(chunks, embeddings):
    resources = get_resources()
    index = resources.index
    vectors = []

    for i, chunk in enumerate(chunks):

        vectors.append({
            "id": chunk["id"],
            "values": embeddings[i].tolist(),
            "metadata": {
                "text": chunk["text"],
                "account": chunk["account"]
            }
        })

    index.upsert(vectors=vectors)

def ingest_documents(chunks):
    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(chunk_texts)
    upload_embeddings_to_pinecone(chunks, embeddings)
    return len(chunks)