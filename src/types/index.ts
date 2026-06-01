// LottoAI Types

export interface LottoResult {
  id?: number;
  draw_date: string;        // YYYY-MM-DD
  draw_number?: string;     // งวดที่ (ถ้ามี)
  first_prize?: string;     // รางวัลที่ 1 (6 หลัก)
  second_prize?: string[];  // รางวัลที่ 2 (5 หลัก x5)
  third_prize?: string[];   // รางวัลที่ 3 (5 หลัก x10)
  two_digit?: string;       // เลขท้าย 2 ตัว
  three_digit_first?: string[];  // รางวัลเลขหน้า 3 ตัว
  three_digit_last?: string[];   // รางวัลเลขท้าย 3 ตัว
  created_at?: string;
  updated_at?: string;
}

export interface FrequencyStat {
  digit: string;
  position: number;         // ตำแหน่งที่ (1-6)
  count: number;
  percentage: number;
  last_seen?: string;       // งวดสุดท้ายที่ออก
  gap: number;              // จำนวนงวดที่ไม่ออก
}

export interface AnalysisResult {
  hot_numbers: { digit: string; count: number; position: number }[];
  cold_numbers: { digit: string; count: number; position: number }[];
  due_numbers: { digit: string; gap: number; position: number }[];
  predictions: { number: string; confidence: number; reason: string }[];
  total_draws: number;
  date_range: { from: string; to: string };
}

export interface UserProfile {
  id: string;
  email: string;
  plan: 'free' | 'premium' | 'vip';
  queries_today: number;
  queries_limit: number;
  created_at: string;
}
