import os
from dotenv import load_dotenv
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

load_dotenv()

class Resources:

    def __init__(self):

        # HuggingFace embedding model
        MODEL_NAME = "google/embeddinggemma-300m"

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=os.getenv("HF_TOKEN"))
        self.embedding_model = AutoModel.from_pretrained(MODEL_NAME)

        # HuggingFace LLM client
        self.llm_client = InferenceClient(
            api_key=os.getenv("HF_TOKEN")
        )

        # Pinecone
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pinecone.Index("bank-customer-support")


resources = None