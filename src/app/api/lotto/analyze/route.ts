import { NextRequest, NextResponse } from 'next/server';
import { analyzeAll } from '@/lib/analyzer';

export async function GET() {
  try {
    const result = await analyzeAll();
    return NextResponse.json(result);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Analysis failed' },
      { status: 500 }
    );
  }
}
