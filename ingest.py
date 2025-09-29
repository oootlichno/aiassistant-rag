""" import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from pypdf import PdfReader

# Index name
INDEX_NAME = "ai-assistant-docs"

# Region and service
region = "us-east-2"
service = "es"

# Get credentials from IAM role attached to EC2
session = boto3.Session()
credentials = session.get_credentials()
aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# OpenSearch endpoint (replace with your domain endpoint if different)
OPENSEARCH_ENDPOINT = "search-aiassistant-vectors-dev-d4jiukbmp2erksrnnwtcwvdlcm.us-east-2.es.amazonaws.com"

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{"host": OPENSEARCH_ENDPOINT, "port": 443}],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Ensure index exists
if not client.indices.exists(index=INDEX_NAME):
    client.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {"number_of_shards": 1},
            "mappings": {"properties": {"content": {"type": "text"}}}
        }
    )

# PDF loader
def pdf_to_text(filepath):
    reader = PdfReader(filepath)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# Documents to ingest
docs = [
    ("AI Solutions Agency.pdf", "AI Solutions Agency"),
    ("Frequently Asked Questions.pdf", "FAQ"),
]

# Ingest PDFs
for file, title in docs:
    if os.path.exists(file):
        text = pdf_to_text(file)
        client.index(index=INDEX_NAME, body={"title": title, "content": text})
        print(f"Indexed: {file}")
    else:
        print(f"File not found: {file}") """


import os
import json
import boto3
from pypdf import PdfReader
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

region = "us-east-2"
service = "es"
INDEX_NAME = "ai-assistant-docs"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

# --- Bedrock + OpenSearch clients ---
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()

aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    credentials.token,
    region,
    service
)

opensearch = OpenSearch(
    hosts=[{
        "host": "search-aiassistant-vectors-dev-d4jiukbmp2erksrnnwtcwvdlcm.us-east-2.es.amazonaws.com",
        "port": 443
    }],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

bedrock = boto3.client("bedrock-runtime", region_name=region)

# --- Ensure index with vector mapping ---
if not opensearch.indices.exists(index=INDEX_NAME):
    index_body = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "embedding": {"type": "knn_vector", "dimension": 1024}
            }
        }
    }
    opensearch.indices.create(index=INDEX_NAME, body=index_body)

# --- Helpers ---
def pdf_to_text(filepath):
    reader = PdfReader(filepath)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def embed_text(text):
    body = json.dumps({"inputText": text})
    resp = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL,
        contentType="application/json",
        accept="application/json",
        body=body,
    )
    return json.loads(resp["body"].read())["embedding"]

# --- Documents to ingest ---
docs = [
    ("AI Solutions Agency.pdf", "AI Solutions Agency"),
    ("Frequently Asked Questions.pdf", "FAQ"),
]

# --- Ingest PDFs ---
for file, title in docs:
    if os.path.exists(file):
        text = pdf_to_text(file)
        embedding = embed_text(text[:2000])  # limit size for demo
        doc = {"title": title, "content": text, "embedding": embedding}
        opensearch.index(index=INDEX_NAME, body=doc)
        print(f"Indexed with embeddings: {file}")
    else:
        print(f"File not found: {file}")
