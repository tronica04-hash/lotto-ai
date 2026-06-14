import json, sys, os

filepath = r'D:\lotto-ai\ml-models\data\scraped_all.json'
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== สรุปข้อมูลหวย ===')
print('จำนวนงวดทั้งหมด: ' + str(len(data)) + ' งวด')
print('งวดแรก: ' + data[0]['draw_date'])
print('งวดสุดท้าย: ' + data[-1]['draw_date'])
print()

# Check all fields in latest draw
latest = data[-1]
print('=== งวดสุดท้าย (' + latest['draw_date'] + ') ===')
for key, value in latest.items():
    if isinstance(value, list):
        print('  ' + key + ': ' + str(len(value)) + ' รายการ -> ' + str(value[:5]) + '...' if len(value) > 5 else '  ' + key + ': ' + str(value))
    else:
        print('  ' + key + ': "' + str(value) + '"')

print()

# Check for missing/empty fields across all draws
expected_fields = ['draw_date', 'first_prize', 'two_digit', 'three_digit_last', 'three_digit_first', 'nearby_1st', 'second_prize', 'third_prize', 'prize_4', 'prize_5']
print('=== ตรวจสอบข้อมูล 10 งวดสุดท้าย ===')
for draw in data[-10:]:
    missing = []
    for field in expected_fields:
        val = draw.get(field)
        if val is None or val == '' or val == []:
            missing.append(field)
    status = 'OK' if not missing else 'MISSING: ' + str(missing)
    print('  ' + draw['draw_date'] + ': ' + status)

print()

# Count draws with any missing field across ALL data
problematic = 0
for draw in data:
    for field in expected_fields:
        val = draw.get(field)
        if val is None or val == '' or val == []:
            problematic += 1
            break
print('งวดที่มีข้อมูลขาดหาย: ' + str(problematic) + ' จาก ' + str(len(data)) + ' งวด')

print()
print('=== สรุปข้อมูลขาดหายตามฟิลด์ (ทั้งหมด ' + str(len(data)) + ' งวด) ===')
for field in expected_fields:
    count = sum(1 for d in data if d.get(field) is None or d.get(field) == '' or d.get(field) == [])
    if count > 0:
        pct = round(count * 100.0 / len(data), 1)
        print('  ' + field + ': ขาด ' + str(count) + ' งวด (' + str(pct) + '%)')
    else:
        print('  ' + field + ': OK (ครบทุกงวด)')
