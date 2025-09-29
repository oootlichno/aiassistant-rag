""" from utils.opensearch import search_index

results = search_index("AI assistant")

print(f"Found results: {len(results)}")

for r in results:
    # Extract the source document
    source = r["_source"]
    title = source.get("title", "Untitled")
    content = source.get("content", "")

    # Print first 200 characters of content
    snippet = content[:200].replace("\n", " ")
    print(f"{title} → {snippet} ...")

 """

import json
import boto3
from utils.opensearch import client, INDEX_NAME

region = "us-east-2"
bedrock = boto3.client("bedrock-runtime", region_name=region)
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

def embed_text(text):
    body = json.dumps({"inputText": text})
    resp = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL,
        contentType="application/json",
        accept="application/json",
        body=body,
    )
    return json.loads(resp["body"].read())["embedding"]

def search_index(query, top_k=3):
    query_vector = embed_text(query)
    body = {
        "size": top_k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_vector,
                    "k": top_k
                }
            }
        }
    }
    res = client.search(index=INDEX_NAME, body=body)
    return res["hits"]["hits"]

if __name__ == "__main__":
    results = search_index("What services do you provide?")
    for r in results:
        print(r["_source"]["title"], "→", r["_source"]["content"][:200], "...")
