import json
import boto3
from utils.opensearch import client, INDEX_NAME

region = "us-east-2"
embedding_model_id = "amazon.titan-embed-text-v2:0"
bedrock = boto3.client("bedrock-runtime", region_name=region)

def get_embedding(text: str):
    """Generate Titan embeddings for text"""
    response = bedrock.invoke_model(
        modelId=embedding_model_id,
        body=json.dumps({"inputText": text}),   
        contentType="application/json",       
        accept="application/json"
    )
    result = json.loads(response["body"].read())  
    return result["embedding"]

def search_index(query, top_k=3):
    vector = get_embedding(query)
    body = {
        "size": top_k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": vector,
                    "k": top_k
                }
            }
        }
    }
    res = client.search(index=INDEX_NAME, body=body)
    return [
        (hit["_source"]["title"], hit["_source"]["content"])
        for hit in res["hits"]["hits"]
    ]

if __name__ == "__main__":
    results = search_index("What services do you provide?")
    for title, content in results:
        print(f"{title} → {content[:200]}...")
