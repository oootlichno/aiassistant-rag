import boto3
from utils.opensearch import search_index

# Step 1: Connect to Bedrock
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

def rag_answer(query):
    # Step 2: Retrieve from OpenSearch
    results = search_index(query, top_k=2)
    context = "\n".join(results)

    # Step 3: Build Bedrock prompt
    prompt = f"""
    You are an AI assistant for our AI Solutions Agency.
    Use the context below to answer the user’s question.

    Context:
    {context}

    Question: {query}
    Answer:
    """

    # Step 4: Call Bedrock model (Claude example)
    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",  # we can change this later
        body={
            "prompt": prompt,
            "max_tokens_to_sample": 300,
            "temperature": 0.2
        },
        contentType="application/json",
        accept="application/json"
    )

    output = response["body"].read().decode("utf-8")
    print(output)

if __name__ == "__main__":
    rag_answer("What services do you provide?")
