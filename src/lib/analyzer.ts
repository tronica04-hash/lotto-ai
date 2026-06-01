// LottoAI Analysis Engine
// วิเคราะห์สถิติหวยจากข้อมูลย้อนหลัง

import { supabase } from './supabase';
import type { AnalysisResult, FrequencyStat } from '@/types';

// ดึงข้อมูลหวยทั้งหมดจาก DB
export async function getAllResults() {
  if (!supabase) return [];
  const { data, error } = await supabase
    .from('lotto_results')
    .select('*')
    .order('draw_date', { ascending: false });

  if (error) throw error;
  return data || [];
}

// ดึงข้อมูลตามช่วงเวลา
export async function getResultsByRange(from: string, to: string) {
  if (!supabase) return [];
  const { data, error } = await supabase
    .from('lotto_results')
    .select('*')
    .gte('draw_date', from)
    .lte('draw_date', to)
    .order('draw_date', { ascending: true });

  if (error) throw error;
  return data || [];
}

// วิเคราะห์ความถี่ของแต่ละตัวเลขในแต่ละตำแหน่ง
export function analyzeFrequency(results: any[]): FrequencyStat[] {
  const stats: Map<string, FrequencyStat> = new Map();

  for (const result of results) {
    if (!result.first_prize || result.first_prize.length < 6) continue;

    const digits = result.first_prize.split('');
    for (let pos = 0; pos < digits.length; pos++) {
      const key = `${pos}_${digits[pos]}`;
      const existing = stats.get(key);
      if (existing) {
        existing.count++;
        existing.last_seen = result.draw_date;
      } else {
        stats.set(key, {
          digit: digits[pos],
          position: pos,
          count: 1,
          percentage: 0,
          last_seen: result.draw_date,
          gap: 0,
        });
      }
    }
  }

  const totalDraws = results.length;
  for (const stat of stats.values()) {
    stat.percentage = (stat.count / totalDraws) * 100;
  }

  return Array.from(stats.values());
}

// วิเคราะห์ Gap (จำนวนงวดที่ไม่ออก)
export function analyzeGap(results: any[]): FrequencyStat[] {
  const lastSeen: Map<string, { date: string; position: number }> = new Map();

  for (let i = results.length - 1; i >= 0; i--) {
    const result = results[i];
    if (!result.first_prize || result.first_prize.length < 6) continue;

    const digits = result.first_prize.split('');
    for (let pos = 0; pos < digits.length; pos++) {
      const key = `${pos}_${digits[pos]}`;
      if (!lastSeen.has(key)) {
        lastSeen.set(key, { date: result.draw_date, position: pos });
      }
    }
  }

  const gaps: FrequencyStat[] = [];
  const latestDate = results[0]?.draw_date;

  for (const [key, info] of lastSeen) {
    const [, digit] = key.split('_');
    const gapDays = latestDate
      ? Math.floor(
          (new Date(latestDate).getTime() - new Date(info.date).getTime()) /
            (1000 * 60 * 60 * 24)
        )
      : 0;

    gaps.push({
      digit,
      position: info.position,
      count: 0,
      percentage: 0,
      last_seen: info.date,
      gap: gapDays,
    });
  }

  return gaps.sort((a, b) => b.gap - a.gap);
}

// หาเลขร้อน (ออกบ่อย)
export function getHotNumbers(freq: FrequencyStat[], topN = 5) {
  return freq
    .sort((a, b) => b.count - a.count)
    .slice(0, topN)
    .map((f) => ({ digit: f.digit, count: f.count, position: f.position }));
}

// หาเลขเย็น (ออกน้อย)
export function getColdNumbers(freq: FrequencyStat[], topN = 5) {
  return freq
    .sort((a, b) => a.count - b.count)
    .slice(0, topN)
    .map((f) => ({ digit: f.digit, count: f.count, position: f.position }));
}

// หาเลข Due (ไม่ออกนานแล้ว น่าจะออก)
export function getDueNumbers(gaps: FrequencyStat[], topN = 5) {
  return gaps
    .sort((a, b) => b.gap - a.gap)
    .slice(0, topN)
    .map((g) => ({ digit: g.digit, gap: g.gap, position: g.position }));
}

// สร้าง prediction
export function generatePredictions(
  hot: ReturnType<typeof getHotNumbers>,
  due: ReturnType<typeof getDueNumbers>,
  freq: FrequencyStat[]
): { number: string; confidence: number; reason: string }[] {
  const predictions: { number: string; confidence: number; reason: string }[] = [];

  const dueDigits = due.slice(0, 3).map((d) => d.digit);
  const hotDigits = hot.slice(0, 3).map((d) => d.digit);

  if (dueDigits.length >= 3) {
    predictions.push({
      number: dueDigits.join(''),
      confidence: 15,
      reason: 'เลข Due - ไม่ออกนานแล้ว มีแนวโน้มจะกลับมา',
    });
  }

  if (hotDigits.length >= 3) {
    predictions.push({
      number: hotDigits.join(''),
      confidence: 12,
      reason: 'เลขร้อน - ออกบ่อยในช่วงที่ผ่านมา',
    });
  }

  if (dueDigits.length >= 2) {
    predictions.push({
      number: dueDigits.slice(0, 2).join(''),
      confidence: 8,
      reason: 'เลขท้าย 2 ตัว - จากสถิติ Due',
    });
  }

  return predictions;
}

// วิเคราะห์ทั้งหมด (main function)
export async function analyzeAll(): Promise<AnalysisResult> {
  const results = await getAllResults();

  if (results.length === 0) {
    return {
      hot_numbers: [],
      cold_numbers: [],
      due_numbers: [],
      predictions: [],
      total_draws: 0,
      date_range: { from: '', to: '' },
    };
  }

  const freq = analyzeFrequency(results);
  const gaps = analyzeGap(results);
  const hot = getHotNumbers(freq);
  const cold = getColdNumbers(freq);
  const due = getDueNumbers(gaps);
  const predictions = generatePredictions(hot, due, freq);

  return {
    hot_numbers: hot,
    cold_numbers: cold,
    due_numbers: due,
    predictions,
    total_draws: results.length,
    date_range: {
      from: results[results.length - 1]?.draw_date || '',
      to: results[0]?.draw_date || '',
    },
  };
}
