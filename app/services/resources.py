import os
from dotenv import load_dotenv
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel

from huggingface_hub import InferenceClient

load_dotenv()

class Resources:

    def __init__(self):

        # HuggingFace embedding model
        MODEL_NAME = "BAAI/bge-large-en-v1.5"

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=os.getenv("HF_TOKEN"))
        self.embedding_model = AutoModel.from_pretrained(MODEL_NAME)

        # HuggingFace LLM client
        self.llm_client = InferenceClient(
            api_key=os.getenv("HF_TOKEN")
        )

        # Pinecone
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pinecone.Index("badar-index")


resources = None

def get_resources() -> Resources:
    global resources
    if resources is None:
        resources = Resources()
    return resources