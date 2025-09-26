import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

region = "us-east-2"  
service = "es"
INDEX_NAME = "documents"

# Get credentials from EC2 instance role
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()

aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    credentials.token,
    region,
    service
)

OPENSEARCH_ENDPOINT = "search-aiassistant-vectors-dev-d4jiukbmp2erksrnnwtcwvdlcm.us-east-2.es.amazonaws.com"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_ENDPOINT, "port": 443}],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def search_index(query, top_k=3):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "content"]
            }
        }
    }
    res = client.search(index=INDEX_NAME, body=body, size=top_k)
    return res["hits"]["hits"]
