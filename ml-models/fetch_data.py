import requests, json, os

# Read .env.local (WSL path)
env_path = "/mnt/d/lotto-ai/.env.local"
url = ""
key = ""
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("NEXT_PUBLIC_SUPABASE_URL="):
            url = line.split("=", 1)[1]
        elif line.startswith("NEXT_PUBLIC_SUPABASE_ANON_KEY="):
            key = line.split("=", 1)[1]

print("URL:", url[:50])

api_url = url + "/rest/v1/lotto_results?select=draw_date,first_prize,two_digit,three_digit_last&order=draw_date.desc&limit=10"

headers = {
    "apikey": key,
    "Authorization": "Bearer " + key
}

resp = requests.get(api_url, headers=headers, timeout=30)
print("Status:", resp.status_code)
print("Response:", resp.text[:500])

if resp.status_code == 200:
    data = resp.json()
    print("\nRows:", len(data))
    if data:
        print("First:", json.dumps(data[0], ensure_ascii=False))
    
    out_path = "/mnt/d/lotto-ai/ml-models/data/lotto_data.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to:", out_path)
