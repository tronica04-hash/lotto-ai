import requests, json, os

url = ""
key = ""
with open(r"D:\lotto-ai\.env.local") as f:
    for line in f:
        line = line.strip()
        if line.startswith("NEXT_PUBLIC_SUPABASE_URL="):
            url = line.split("=", 1)[1]
        elif line.startswith("NEXT_PUBLIC_SUPABASE_ANON_KEY="):
            key = line.split("=", 1)[1]

api_url = url + "/rest/v1/lotto_results?select=draw_date,first_prize,two_digit,three_digit_last,nearby_1st,second_prize,third_prize&order=draw_date.asc&limit=1000"
headers = {"apikey": key, "Authorization": "Bearer " + key}
resp = requests.get(api_url, headers=headers, timeout=30)
data = resp.json()

out_dir = r"D:\lotto-ai\ml-models\data"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "lotto_all.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Fetched", len(data), "draws")
print("Saved to", out_path)
