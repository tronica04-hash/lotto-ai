-- ============================================
-- LottoAI: Complete Import Script
-- Run ทั้ง script นี้ใน Supabase SQL Editor
-- ============================================

-- 1. เพิ่ม columns ที่ยังขาดใน lotto_results
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='lotto_results' AND column_name='nearby_1st') THEN
    ALTER TABLE lotto_results ADD COLUMN nearby_1st JSONB DEFAULT '[]';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='lotto_results' AND column_name='prize_4') THEN
    ALTER TABLE lotto_results ADD COLUMN prize_4 JSONB DEFAULT '[]';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='lotto_results' AND column_name='prize_5') THEN
    ALTER TABLE lotto_results ADD COLUMN prize_5 JSONB DEFAULT '[]';
  END IF;
END
$$;

-- 2. สร้าง function import ข้อมูลจาก JSON
-- วิธีใช้: ส่ง JSON array ของข้อมูลหวยเป็น parameter
-- ตัวอย่าง format:
-- [
--   {"draw_date":"2026-06-01","draw_number":"20260601","first_prize":"173770","two_digit":"95","nearby_1st":["173769","173771"],"three_digit_first":["415","848"],"three_digit_last":["410","938"],"second_prize":["494547","536050","791562","798580","998762"],"third_prize":["...","..."]}
-- ]

CREATE OR REPLACE FUNCTION import_lotto_data(data_json JSONB)
RETURNS TABLE(imported_count INT, errors TEXT[]) AS $$
DECLARE
  row_data JSONB;
  counter INT := 0;
  error_list TEXT[] := '{}';
  upsert_result INT;
BEGIN
  FOR row_data IN SELECT * FROM jsonb_array_elements(data_json)
  LOOP
    BEGIN
      INSERT INTO lotto_results (
        draw_date, draw_number, first_prize,
        two_digit, nearby_1st,
        three_digit_first, three_digit_last,
        second_prize, third_prize,
        prize_4, prize_5
      ) VALUES (
        (row_data->>'draw_date')::DATE,
        row_data->>'draw_number',
        row_data->>'first_prize',
        row_data->>'two_digit',
        COALESCE(row_data->'nearby_1st', '[]'::jsonb),
        COALESCE(row_data->'three_digit_first', '[]'::jsonb),
        COALESCE(row_data->'three_digit_last', '[]'::jsonb),
        COALESCE(row_data->'second_prize', '[]'::jsonb),
        COALESCE(row_data->'third_prize', '[]'::jsonb),
        COALESCE(row_data->'prize_4', '[]'::jsonb),
        COALESCE(row_data->'prize_5', '[]'::jsonb)
      )
      ON CONFLICT (draw_date) DO UPDATE SET
        draw_number = EXCLUDED.draw_number,
        first_prize = EXCLUDED.first_prize,
        two_digit = EXCLUDED.two_digit,
        nearby_1st = EXCLUDED.nearby_1st,
        three_digit_first = EXCLUDED.three_digit_first,
        three_digit_last = EXCLUDED.three_digit_last,
        second_prize = EXCLUDED.second_prize,
        third_prize = EXCLUDED.third_prize,
        prize_4 = EXCLUDED.prize_4,
        prize_5 = EXCLUDED.prize_5,
        updated_at = NOW();

      counter := counter + 1;
    EXCEPTION WHEN OTHERS THEN
      error_list := array_append(error_list, (row_data->>'draw_date') || ': ' || SQLERRM);
    END;
  END LOOP;

  RETURN QUERY SELECT counter, error_list;
END;
$$ LANGUAGE plpgsql;

-- 3. สร้าง view สำหรับสถิติ (ใช้ในหน้าสถิติ)

-- Hot 2-digit numbers (สุ่ม 10 อันดับแรก)
CREATE OR REPLACE VIEW v_hot_2digit AS
WITH all_2digit AS (
  SELECT two_digit AS num, COUNT(*) AS freq
  FROM lotto_results
  WHERE two_digit IS NOT NULL AND two_digit != ''
  GROUP BY two_digit
)
SELECT num, freq, RANK() OVER (ORDER BY freq DESC) AS rank
FROM all_2digit
ORDER BY freq DESC
LIMIT 10;

-- Hot 3-digit first numbers
CREATE OR REPLACE VIEW v_hot_3digit_first AS
WITH expanded AS (
  SELECT jsonb_array_text AS num
  FROM lotto_results, jsonb_array_elements_text(three_digit_first) AS jsonb_array_text
  WHERE three_digit_first IS NOT NULL AND jsonb_array_length(three_digit_first) > 0
)
SELECT num, COUNT(*) AS freq, RANK() OVER (ORDER BY freq DESC) AS rank
FROM expanded
GROUP BY num
ORDER BY freq DESC
LIMIT 10;

-- Hot 3-digit last numbers
CREATE OR REPLACE VIEW v_hot_3digit_last AS
WITH expanded AS (
  SELECT jsonb_array_text AS num
  FROM lotto_results, jsonb_array_elements_text(three_digit_last) AS jsonb_array_text
  WHERE three_digit_last IS NOT NULL AND jsonb_array_length(three_digit_last) > 0
)
SELECT num, COUNT(*) AS freq, RANK() OVER (ORDER BY freq DESC) AS rank
FROM expanded
GROUP BY num
ORDER BY freq DESC
LIMIT 10;

-- Due 2-digit (ไม่ออกนานที่สุด)
CREATE OR REPLACE VIEW v_due_2digit AS
WITH last_seen AS (
  SELECT two_digit AS num, MAX(draw_date) AS last_date
  FROM lotto_results
  WHERE two_digit IS NOT NULL AND two_digit != ''
  GROUP BY two_digit
)
SELECT num, last_date, (CURRENT_DATE - last_date) AS days_since
FROM last_seen
ORDER BY last_date ASC
LIMIT 10;

-- Overall stats summary
CREATE OR REPLACE VIEW v_lotto_stats AS
SELECT
  COUNT(*) AS total_draws,
  MIN(draw_date) AS first_draw,
  MAX(draw_date) AS last_draw,
  COUNT(CASE WHEN first_prize IS NOT NULL AND first_prize != '' THEN 1 END) AS has_first_prize,
  COUNT(CASE WHEN two_digit IS NOT NULL AND two_digit != '' THEN 1 END) AS has_two_digit,
  COUNT(CASE WHEN jsonb_array_length(three_digit_first) > 0 THEN 1 END) AS has_three_digit_first,
  COUNT(CASE WHEN jsonb_array_length(three_digit_last) > 0 THEN 1 END) AS has_three_digit_last
FROM lotto_results;

-- 4. Grant permissions
GRANT SELECT ON v_hot_2digit, v_hot_3digit_first, v_hot_3digit_last, v_due_2digit, v_lotto_stats TO anon, authenticated;
GRANT EXECUTE ON FUNCTION import_lotto_data TO anon, authenticated;

-- ============================================
-- วิธี Import ข้อมูล:
-- ============================================
-- 1. รัน import ผ่าน REST API (จาก Python script):
--    POST https://YOUR_SUPABASE_URL/rest/v1/rpc/import_lotto_data
--    Headers: apikey=YOUR_ANON_KEY
--    Body: {"data_json": [...]}
--
-- 2. หรือ import ทีละชุดผ่าน SQL:
--    SELECT * FROM import_lotto_data('[
--      {"draw_date":"2026-06-01","first_prize":"173770","two_digit":"95",...}
--    ]'::jsonb);
--
-- 3. ตรวจสอบข้อมูล:
--    SELECT (v_lotto_stats).* FROM v_lotto_stats;
--    SELECT * FROM v_hot_2digit;
--    SELECT * FROM v_due_2digit;
