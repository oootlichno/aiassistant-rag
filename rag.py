from utils.opensearch import search_index
from utils.bedrock import ask_bedrock

def rag_answer(query: str):
    # Retrieve top chunks
    docs = search_index(query, top_k=3)
    context = "\n\n".join([doc["content"] for doc in docs])

    # Build prompt
    prompt = f"""You are a helpful assistant. 
Answer the question based only on the context below.

Context:
{context}

Question: {query}
"""

    # Ask LLM
    answer = ask_bedrock(prompt)
    print("Q:", query)
    print("A:", answer)

if __name__ == "__main__":
    rag_answer("What services does AI Solutions Agency provide?")
