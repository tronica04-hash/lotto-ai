import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

const LOCAL_DATA_PATH = path.join(process.cwd(), '..', 'ml-models', 'data', 'scraped_all.json');

export async function GET() {
  try {
    const raw = fs.readFileSync(LOCAL_DATA_PATH, 'utf-8');
    const data = JSON.parse(raw);
    return NextResponse.json({ source: 'local', count: data.length, data });
  } catch (e) {
    return NextResponse.json({ source: 'local', error: String(e), count: 0, data: [] }, { status: 500 });
  }
}
