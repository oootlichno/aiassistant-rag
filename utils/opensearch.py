import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

region = "us-east-2"
service = "es"
INDEX_NAME = "documents"

def get_opensearch_client():
    session = boto3.Session(region_name=region)
    credentials = session.get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        credentials.token,
        region,
        service
    )

    OPENSEARCH_ENDPOINT = "search-aiassistant-vectors-dev-d4jiukbmp2erksrnnwtcwvdlcm.us-east-2.es.amazonaws.com"

    return OpenSearch(
        hosts=[{"host": OPENSEARCH_ENDPOINT, "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

def search_index(query, top_k=2):
    client = get_opensearch_client()
    body = {"query": {"match": {"content": query}}}
    res = client.search(index=INDEX_NAME, body=body, size=top_k)
    return [hit["_source"]["content"] for hit in res["hits"]["hits"]]
