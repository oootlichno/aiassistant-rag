""" import boto3
from utils.opensearch import search_index

# Step 1: Connect to Bedrock
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

def rag_answer(query):
    # Step 2: Retrieve from OpenSearch
    results = search_index(query, top_k=2)

    # Extract content (make sure they're strings)
    docs = [doc.get("content", "") for doc in results]
    context = "\n\n".join(docs)

    # Step 3: Build Bedrock prompt
    prompt = f"""
"""     You are an AI assistant for our AI Solutions Agency.
    Use the context below to answer the user’s question.

    Context:
    {context}

    Question: {query}
    Answer: """
    """

    # Step 4: Call Bedrock model (Claude example)
    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",  # can switch to Titan/Llama later
        body=(
            '{"prompt": ' + f'"{prompt}"' + ', "max_tokens_to_sample": 300, "temperature": 0.2}'
        ),
        contentType="application/json",
        accept="application/json"
    )

    output = response["body"].read().decode("utf-8")
    print(output)

if __name__ == "__main__":
    rag_answer("What services does AI Solutions Agency provide?")

 """

from utils.opensearch import search_index
from utils.bedrock import ask_bedrock

def rag_answer(query: str):
    docs = search_index(query, top_k=3)
    context = "\n\n".join([d["_source"]["content"] for d in docs])
    prompt = f"""You are a helpful assistant. 
    Answer the question based only on the context below.

    Context:
    {context}

    Question: {query}
    """

    answer = ask_bedrock(prompt)
    print("Q:", query)
    print("A:", answer)


if __name__ == "__main__":
    rag_answer("What services does AI Solutions Agency provide?")
