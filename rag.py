from utils.opensearch import search_index
from utils.bedrock import generate_with_bedrock

def rag_pipeline(question):
    docs = search_index(question)
    context = "\n\n".join(docs)

    prompt = f"""You are an AI assistant.
Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

    return generate_with_bedrock(prompt)

if __name__ == "__main__":
    q = "What services does AI Solutions Agency provide?"
    print("Q:", q)
    print("A:", rag_pipeline(q))
