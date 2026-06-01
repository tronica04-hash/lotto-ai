import { supabase } from '@/lib/supabase';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const digits = ['d1','d2','d3','d4','d5','d6'].map(k => (formData.get(k) as string) || '');
    const number = digits.join('');

    if (number.length !== 6 || !/^\d{6}$/.test(number)) {
      return NextResponse.json({ error: 'กรุณากรอกเลข 6 หลักให้ครบ' }, { status: 400 });
    }

    if (!supabase) {
      return NextResponse.json({ error: 'Supabase not configured' }, { status: 500 });
    }

    // ดึงผลล่าสุด
    const { data: latest } = await supabase
      .from('lotto_results')
      .select('*')
      .order('draw_date', { ascending: false })
      .limit(1)
      .single();

    if (!latest) {
      return NextResponse.json({ error: 'ไม่พบข้อมูล' }, { status: 404 });
    }

    const results: string[] = [];
    let won = false;

    // เช็ครางวัลที่ 1
    if (latest.first_prize === number) {
      results.push('🎉 ถูกรางวัลที่ 1! 6,000,000 บาท');
      won = true;
    }

    // เช็คข้างเคียงรางวัลที่ 1
    if (latest.nearby_1st?.includes(number)) {
      results.push('🎉 ถูกรางวัลข้างเคียงรางวัลที่ 1! 100,000 บาท');
      won = true;
    }

    // เช็ครางวัลที่ 2 (5 ตัว)
    if (latest.second_prize?.includes(number)) {
      results.push('🎉 ถูกรางวัลที่ 2! 200,000 บาท');
      won = true;
    }

    // เช็ครางวัลที่ 3 (10 ตัว)
    if (latest.third_prize?.includes(number)) {
      results.push('🎉 ถูกรางวัลที่ 3! 80,000 บาท');
      won = true;
    }

    // เช็คเลขหน้า 3
    const last3front = number.substring(0, 3);
    if (latest.three_digit_first?.includes(last3front)) {
      results.push('🎉 ถูกรางวัลเลขหน้า 3! 4,000 บาท');
      won = true;
    }

    // เช็คเลขท้าย 3
    const last3back = number.substring(3, 6);
    if (latest.three_digit_last?.includes(last3back)) {
      results.push('🎉 ถูกรางวัลเลขท้าย 3! 4,000 บาท');
      won = true;
    }

    // เช็คเลขท้าย 2
    const last2 = number.substring(4, 6);
    if (latest.two_digit === last2) {
      results.push('🎉 ถูกรางวัลเลขท้าย 2! 2,000 บาท');
      won = true;
    }

    if (!won) {
      results.push('❌ ไม่ถูกรางวัลใดเลยงวดนี้');
    }

    return NextResponse.json({
      number,
      drawDate: latest.draw_date,
      won,
      results,
    });
  } catch (e) {
    return NextResponse.json({ error: 'เกิดข้อผิดพลาด' }, { status: 500 });
  }
}
