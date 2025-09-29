""" from utils.opensearch import search_index
from utils.bedrock import ask_bedrock

def rag_answer(query: str):
    # Retrieve top chunks
    docs = search_index(query, top_k=3)
    context = "\n\n".join([doc["content"] for doc in docs])

    # Build prompt
    prompt = f"""""" You are a helpful assistant. 
Answer the question based only on the context below.

Context:
{context}

Question: {query} """
"""

    # Ask LLM
    answer = ask_bedrock(prompt)
    print("Q:", query)
    print("A:", answer)

if __name__ == "__main__":
    rag_answer("What services does AI Solutions Agency provide?") """


import json
import boto3
from utils.opensearch import search_index

# ===== Settings =====
region = "us-east-2"
model_id = "arn:aws:bedrock:us-east-2:338220915419:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0"

# ===== Bedrock client =====
bedrock = boto3.client("bedrock-runtime", region_name=region)

def rag_answer(query: str, top_k: int = 3):
    # 1. Retrieve top-k documents from OpenSearch
    docs = search_index(query, top_k=top_k)
    context = "\n\n".join(d["content"] for d in docs)

    # 2. Build prompt for Claude
    prompt = f"""You are a helpful AI assistant. 
Answer the following question based ONLY on the context below. 
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {query}
"""

    # 3. Send to Bedrock Claude
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.2
        })
    )

    # 4. Parse response
    result = json.loads(response["body"].read())
    answer = result["output"]["message"]["content"][0]["text"]

    print("Q:", query)
    print("A:", answer)


if __name__ == "__main__":
    rag_answer("What services does AI Solutions Agency provide?")
