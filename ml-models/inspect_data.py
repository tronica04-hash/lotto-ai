import json
with open(r'D:\lotto-ai\ml-models\data\scraped_all.json', 'r') as f:
    data = json.load(f)
print('Type:', type(data))
print('Length:', len(data))
if isinstance(data, list):
    print('First entry keys:', list(data[0].keys()) if isinstance(data[0], dict) else 'not dict')
    print('First entry:', json.dumps(data[0], indent=2)[:2000])
    print('Last entry:', json.dumps(data[-1], indent=2)[:1000])
elif isinstance(data, dict):
    print('Keys:', list(data.keys())[:10])
