from utils.opensearch import search_index

if __name__ == "__main__":
    results = search_index("AI assistant")
    print("Found results:", len(results))
    for r in results:
        print(r[:200], "...")
