from utils.opensearch import search_index

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
