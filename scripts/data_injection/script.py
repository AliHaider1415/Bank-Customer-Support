import json

from app.services.embeddings.functions import (
    generate_embeddings,
    upload_embeddings_to_pinecone
)


def load_chunks(path):

    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return chunks


def main():

    print("Loading chunks...")

    chunks = load_chunks("data/preprocessed_chunks.json")

    print("Preparing texts...")

    chunk_texts = [chunk["text"] for chunk in chunks]

    print("Generating embeddings...")

    embeddings = generate_embeddings(chunk_texts)

    print("Uploading to Pinecone...")

    upload_embeddings_to_pinecone(chunks, embeddings)

    print("Upload complete.")


if __name__ == "__main__":
    main()