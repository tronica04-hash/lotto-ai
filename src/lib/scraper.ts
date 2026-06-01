// LottoAI Scraper - ดึงข้อมูลหวยรัฐบาลไทย
// ใช้กับเว็บไซต์สลก (สำนักงานสลก)

import * as cheerio from 'cheerio';

export interface RawLottoResult {
  drawDate: string;
  drawNumber: string;
  firstPrize: string;
  secondPrize: string[];
  thirdPrize: string[];
  twoDigit: string;
  threeDigitFirst: string[];
  threeDigitLast: string[];
}

// ดึงข้อมูลจาก lotto.th (ตัวอย่าง - ต้องปรับตามโครงสร้างเว็บจริง)
export async function scrapeLottoPage(url: string): Promise<RawLottoResult[]> {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const html = await response.text();
    const $ = cheerio.load(html);
    const results: RawLottoResult[] = [];

    // TODO: ปรับ selector ตามโครงสร้างเว็บจริง
    // ตัวอย่างโครงสร้างทั่วไป
    $('table.lotto-results tr').each((i, row) => {
      const cells = $(row).find('td');
      if (cells.length >= 4) {
        results.push({
          drawDate: $(cells[0]).text().trim(),
          drawNumber: $(cells[1]).text().trim(),
          firstPrize: $(cells[2]).text().trim(),
          secondPrize: $(cells[3]).text().trim().split(/\s+/),
          thirdPrize: [],
          twoDigit: '',
          threeDigitFirst: [],
          threeDigitLast: [],
        });
      }
    });

    return results;
  } catch (error) {
    console.error('Scrape error:', error);
    throw error;
  }
}

// ดึงข้อมูลจาก API ถ้ามี
export async function fetchLottoAPI(date: string): Promise<RawLottoResult | null> {
  try {
    // ตัวอย่าง API endpoint (ต้องหา API จริง)
    const response = await fetch(`https://www.lotto.th/api/results?date=${date}`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
    });

    if (!response.ok) return null;

    const data = await response.json();
    return {
      drawDate: data.date || date,
      drawNumber: data.drawNumber || '',
      firstPrize: data.firstPrize || '',
      secondPrize: data.secondPrize || [],
      thirdPrize: data.thirdPrize || [],
      twoDigit: data.twoDigit || '',
      threeDigitFirst: data.threeDigitFirst || [],
      threeDigitLast: data.threeDigitLast || [],
    };
  } catch {
    return null;
  }
}

// แปลงข้อมูลดิบเป็น format ที่เก็บใน DB
export function normalizeResult(raw: RawLottoResult) {
  return {
    draw_date: raw.drawDate,
    draw_number: raw.drawNumber || null,
    first_prize: raw.firstPrize || null,
    second_prize: JSON.stringify(raw.secondPrize),
    third_prize: JSON.stringify(raw.thirdPrize),
    two_digit: raw.twoDigit || null,
    three_digit_first: JSON.stringify(raw.threeDigitFirst),
    three_digit_last: JSON.stringify(raw.threeDigitLast),
  };
}
