import os
import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from pypdf import PdfReader

# ===== Settings =====
INDEX_NAME = "ai-assistant-docs"
region = "us-east-2"
service = "es"
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
        body=json.dumps({"inputText": text}),   # ✅ JSON string
        contentType="application/json",        # ✅ tell Bedrock it's JSON
        accept="application/json"
    )
    result = json.loads(response["body"].read())  # ✅ parse Bedrock response
    return result["embedding"]

# ===== PDF loader =====
def pdf_to_chunks(filepath, chunk_size=300):
    reader = PdfReader(filepath)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

# ===== Ensure index exists with knn_vector =====
if client.indices.exists(index=INDEX_NAME):
    client.indices.delete(index=INDEX_NAME)  # start fresh

client.indices.create(
    index=INDEX_NAME,
    body={
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "embedding": {"type": "knn_vector", "dimension": 1024}
            }
        }
    }
)

# ===== Ingest PDFs =====
docs = [
    ("AI Solutions Agency.pdf", "AI Solutions Agency"),
    ("Frequently Asked Questions.pdf", "FAQ"),
]

for file, title in docs:
    if os.path.exists(file):
        for chunk in pdf_to_chunks(file):
            emb = get_embedding(chunk)
            client.index(
                index=INDEX_NAME,
                body={"title": title, "content": chunk, "embedding": emb}
            )
        print(f"Indexed: {file}")
    else:
        print(f"File not found: {file}")
