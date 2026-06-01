#!/usr/bin/env node
/**
 * LottoAI Data Importer
 * 
 * สคริปต์สำหรับ import ข้อมูลหวยรัฐบาลไทยเข้า database
 * 
 * วิธีใช้:
 * 1. ติดตั้ง dependencies: npm install
 * 2. ตั้งค่า .env.local
 * 3. รัน: npx tsx scripts/import-lotto.ts
 * 
 * หรือ import จาก CSV:
 *   npx tsx scripts/import-lotto.ts --csv path/to/file.csv
 */

import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';

// Load env
const envPath = path.join(process.cwd(), '.env.local');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  for (const line of envContent.split('\n')) {
    const [key, ...rest] = line.split('=');
    if (key && rest.length > 0) {
      process.env[key.trim()] = rest.join('=').trim();
    }
  }
}

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

if (!supabaseUrl || !supabaseKey) {
  console.error('Error: Missing Supabase credentials in .env.local');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

interface LottoRow {
  draw_date: string;
  draw_number?: string;
  first_prize?: string;
  second_prize?: string;
  third_prize?: string;
  two_digit?: string;
  three_digit_first?: string;
  three_digit_last?: string;
}

// Import จาก CSV
async function importFromCSV(filePath: string) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(l => l.trim());
  const headers = lines[0].split(',').map(h => h.trim());
  
  const rows: LottoRow[] = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    const row: any = {};
    
    headers.forEach((h, idx) => {
      row[h] = values[idx] || null;
    });
    
    if (row.draw_date) {
      rows.push(row);
    }
  }
  
  console.log(`Found ${rows.length} rows to import`);
  
  // Insert in batches of 100
  const batchSize = 100;
  let inserted = 0;
  
  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);
    const { data, error } = await supabase
      .from('lotto_results')
      .upsert(batch, { onConflict: 'draw_date' })
      .select();
    
    if (error) {
      console.error(`Batch ${i / batchSize + 1} error:`, error.message);
    } else {
      inserted += data?.length || 0;
      console.log(`Batch ${i / batchSize + 1}: inserted ${data?.length || 0} rows`);
    }
  }
  
  console.log(`\nDone! Total inserted: ${inserted}/${rows.length}`);
}

// Import จาก JSON
async function importFromJSON(filePath: string) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  
  const rows = Array.isArray(data) ? data : data.results || [];
  console.log(`Found ${rows.length} results to import`);
  
  const batchSize = 100;
  let inserted = 0;
  
  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);
    const { data: result, error } = await supabase
      .from('lotto_results')
      .upsert(batch, { onConflict: 'draw_date' })
      .select();
    
    if (error) {
      console.error(`Batch ${i / batchSize + 1} error:`, error.message);
    } else {
      inserted += result?.length || 0;
      console.log(`Batch ${i / batchSize + 1}: inserted ${result?.length || 0} rows`);
    }
  }
  
  console.log(`\nDone! Total inserted: ${inserted}/${rows.length}`);
}

// Main
async function main() {
  const args = process.argv.slice(2);
  const fileArg = args.find(a => a.startsWith('--csv=') || a.startsWith('--json='));
  
  if (!fileArg) {
    console.log('Usage:');
    console.log('  npx tsx scripts/import-lotto.ts --csv=data.csv');
    console.log('  npx tsx scripts/import-lotto.ts --json=data.json');
    console.log('\nCSV format: draw_date, draw_number, first_prize, two_digit, ...');
    console.log('Date format: YYYY-MM-DD');
    process.exit(0);
  }
  
  if (fileArg.startsWith('--csv=')) {
    const filePath = fileArg.replace('--csv=', '');
    await importFromCSV(filePath);
  } else if (fileArg.startsWith('--json=')) {
    const filePath = fileArg.replace('--json=', '');
    await importFromJSON(filePath);
  }
}

main().catch(console.error);
