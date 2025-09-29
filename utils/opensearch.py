import json
import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

region = "us-east-2"
service = "es"
INDEX_NAME = "ai-assistant-docs"
embedding_model_id = "amazon.titan-embed-text-v2:0"

# ===== Auth =====
session = boto3.Session()
credentials = session.get_credentials()
aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# ===== OpenSearch client =====
OPENSEARCH_ENDPOINT = "search-aiassistant-vectors-dev-d4jiukbmp2erksrnnwtcwvdlcm.us-east-2.es.amazonaws.com"
client = OpenSearch(
    hosts=[{"host": OPENSEARCH_ENDPOINT, "port": 443}],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# ===== Bedrock client =====
bedrock = boto3.client("bedrock-runtime", region_name=region)

def get_embedding(text: str):
    """Generate Titan embeddings for text"""
    response = bedrock.invoke_model(
        modelId=embedding_model_id,
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

def search_index(query: str, top_k: int = 3):
    """Vector search in OpenSearch"""
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
    return [hit["_source"] for hit in res["hits"]["hits"]]
