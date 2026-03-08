import os

from huggingface_hub import InferenceClient
from app.services.resources import resources

client = InferenceClient(
    api_key=os.getenv('HUGGINGFACE_API_KEY'),
)

def llm_call(context_chunks, query):
    print(">>> llm_call start")
    context = "\n\n".join(context_chunks)

    prompt = f"""
    You are a helpful banking assistant.

    Use ONLY the context below to answer the question.
    If the answer is not present, say you cannot find it.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """
    completion = client.chat.completions.create(
        model=os.getenv('LLM_MODEL_NAME'),
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=2048,
    )
    print(">>> llm_call done")
    return (completion.choices[0].message.content)
