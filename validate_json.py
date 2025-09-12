import json

try:
    with open("data/pricing_results.json") as f:
        data = json.load(f)
    print(f"records: {len(data)}")
    if data:
        print(f"sample keys: {list(data[0].keys())}")
        print(f"First record user_id: {data[0]['user_id']}")
        print("JSON file is valid!")
    else:
        print("JSON file is empty")
except Exception as e:
    print(f"Error reading JSON: {e}")