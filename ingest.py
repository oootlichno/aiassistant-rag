import os
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
        print(f"File not found: {file}")