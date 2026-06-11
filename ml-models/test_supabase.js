const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Read .env.local
const envContent = fs.readFileSync('D:\\lotto-ai\\.env.local', 'utf8');
let url = '', key = '';
for (const line of envContent.split('\n')) {
  if (line.startsWith('NEXT_PUBLIC_SUPABASE_URL=')) url = line.split('=', 1)[1] || line.substring('NEXT_PUBLIC_SUPABASE_URL='.length);
  if (line.startsWith('NEXT_PUBLIC_SUPABASE_ANON_KEY=')) key = line.split('=', 1)[1] || line.substring('NEXT_PUBLIC_SUPABASE_ANON_KEY='.length);
}

console.log('URL:', url);
console.log('Key length:', key.length);
console.log('Key preview:', key.substring(0, 30));

const supabase = createClient(url, key);

async function main() {
  const { data, error } = await supabase
    .from('lotto_results')
    .select('*')
    .order('draw_date', { ascending: false })
    .limit(5);
  
  if (error) {
    console.log('Error:', JSON.stringify(error, null, 2));
  } else {
    console.log('Rows:', data.length);
    if (data.length > 0) {
      console.log('Columns:', Object.keys(data[0]));
      console.log('First row:', JSON.stringify(data[0], null, 2));
    }
  }
}

main();
