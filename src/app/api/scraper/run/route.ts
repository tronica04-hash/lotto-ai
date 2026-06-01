import { NextRequest, NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { results } = body;

    if (!results || !Array.isArray(results)) {
      return NextResponse.json({ error: 'Invalid data' }, { status: 400 });
    }

    if (!supabaseAdmin) {
      return NextResponse.json({ error: 'Service role not configured' }, { status: 500 });
    }

    const { data, error } = await supabaseAdmin
      .from('lotto_results')
      .upsert(results, { onConflict: 'draw_date' })
      .select();

    if (error) throw error;

    return NextResponse.json({
      success: true,
      inserted: data?.length || 0,
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Scraper failed' },
      { status: 500 }
    );
  }
}
