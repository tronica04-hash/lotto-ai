import { supabase } from '@/lib/supabase';

async function getAllResults() {
  if (!supabase) return [];
  const { data } = await supabase
    .from('lotto_results')
    .select('draw_date, first_prize, two_digit, three_digit_first, three_digit_last')
    .order('draw_date', { ascending: true });
  return data || [];
}

function predictNumbers(results: any[]) {
  // วิเคราะห์ frequency
  const freq2: Record<string, number> = {};
  const freq3: Record<string, number> = {};
  const lastSeen2: Record<string, number> = {};
  const lastSeen3: Record<string, number> = {};

  results.forEach((r, idx) => {
    if (r.two_digit) {
      freq2[r.two_digit] = (freq2[r.two_digit] || 0) + 1;
      lastSeen2[r.two_digit] = idx;
    }
    if (r.three_digit_first) {
      for (const n of r.three_digit_first) {
        freq3[n] = (freq3[n] || 0) + 1;
        lastSeen3[n] = idx;
      }
    }
    if (r.three_digit_last) {
      for (const n of r.three_digit_last) {
        freq3[n] = (freq3[n] || 0) + 1;
        lastSeen3[n] = idx;
      }
    }
  });

  // คำนวณคะแนน = frequency weight + due weight
  const score2: [string, number][] = Object.keys(freq2).map(num => {
    const freqScore = freq2[num] || 0;
    const dueScore = results.length - (lastSeen2[num] || 0);
    return [num, freqScore * 0.6 + dueScore * 0.4];
  });
  const score3: [string, number][] = Object.keys(freq3).map(num => {
    const freqScore = freq3[num] || 0;
    const dueScore = results.length - (lastSeen3[num] || 0);
    return [num, freqScore * 0.6 + dueScore * 0.4];
  });

  const top2 = score2.sort((a, b) => b[1] - a[1]).slice(0, 5).map(x => x[0]);
  const top3 = score3.sort((a, b) => b[1] - a[1]).slice(0, 6).map(x => x[0]);

  // สร้างคอมโบ = top3(first) + top3(last) + top2
  const combos: string[] = [];
  for (let i = 0; i < Math.min(3, top3.length); i++) {
    for (let j = 0; j < Math.min(2, top2.length); j++) {
      const last3 = top3[(i + 1) % top3.length] || '000';
      const last2 = top2[j];
      combos.push(top3[i] + last3.substring(2) + last2);
      if (combos.length >= 5) break;
    }
    if (combos.length >= 5) break;
  }

  return { top2, top3, combos, total: results.length };
}

export default async function AIPage() {
  const results = await getAllResults();
  const prediction = results.length > 0 ? predictNumbers(results) : null;

  return (
    <>
    <style dangerouslySetInnerHTML={{__html: `
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; }
      .nav { border-bottom: 1px solid rgba(148,163,184,0.2); }
      .nav-inner { max-width: 1200px; margin: 0 auto; padding: 16px; display: flex; align-items: center; justify-content: space-between; }
      .logo { font-size: 22px; font-weight: bold; text-decoration: none; color: #e2e8f0; }
      .nav-links { display: flex; gap: 8px; align-items: center; }
      .nav-links a { text-decoration: none; color: #94a3b8; padding: 8px 16px; }
      .nav-links a:hover { color: #fff; }
      .nav-links a.active { color: #c084fc; font-weight: 600; }
      .btn-primary { padding: 8px 16px; background: #9333ea; color: #fff; border-radius: 8px; font-weight: 600; text-decoration: none; }

      .container { max-width: 900px; margin: 0 auto; padding: 32px 16px; }
      .page-title { font-size: 28px; font-weight: bold; margin-bottom: 8px; }
      .page-subtitle { color: #94a3b8; margin-bottom: 32px; }

      .ai-card { background: linear-gradient(135deg, rgba(147,51,234,0.2), rgba(236,72,153,0.2)); border: 1px solid rgba(168,85,247,0.3); border-radius: 20px; padding: 32px; margin-bottom: 24px; }
      .ai-card h2 { font-size: 20px; font-weight: bold; margin-bottom: 20px; }

      .combo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; }
      .combo-item { background: rgba(30,41,59,0.6); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 20px; text-align: center; }
      .combo-num { font-family: monospace; font-size: 28px; font-weight: bold; background: linear-gradient(90deg, #c084fc, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
      .combo-label { color: #94a3b8; font-size: 12px; margin-top: 4px; }

      .num-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
      .num-chip { background: #1e293b; border: 1px solid #334155; padding: 8px 14px; border-radius: 8px; font-family: monospace; font-size: 16px; font-weight: bold; }
      .num-chip.t2 { border-color: #9333ea; color: #c084fc; }
      .num-chip.t3 { border-color: #ec4899; color: #f472b6; }

      .info-box { background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
      .info-box p { color: #94a3b8; font-size: 14px; line-height: 1.6; }

      .disclaimer { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius: 12px; padding: 16px; margin-top: 24px; }
      .disclaimer p { color: #fca5a5; font-size: 13px; }
    `}} />
    <div>
      <nav className="nav">
        <div className="nav-inner">
          <a href="/" className="logo">🎰 LottoAI</a>
          <div className="nav-links">
            <a href="/results">ผลหวย</a>
            <a href="/stats" className="active">สถิติ</a>
            <a href="/login">เข้าสู่ระบบ</a>
            <a href="/register" className="btn-primary">สมัครฟรี</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <h1 className="page-title">🤖 AI ทำนายเลข</h1>
        <p className="page-subtitle">คำนวณจาก pattern และความถี่ของข้อมูลย้อนหลัง {prediction?.total || 0} งวด</p>

        {prediction && (
          <>
            <div className="ai-card">
              <h2>🎯 เลขคอมโบแนะนำ</h2>
              <div className="combo-grid">
                {prediction.combos.map((combo, i) => (
                  <div key={i} className="combo-item">
                    <div className="combo-num">{combo}</div>
                    <div className="combo-label">คอมโบ #{i + 1}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="info-box">
              <p>เลขเด่น 2 ตัว: </p>
              <div className="num-row" style={{marginTop:8}}>
                {prediction.top2.map(n => (
                  <span key={n} className="num-chip t2">{n}</span>
                ))}
              </div>
              <p style={{marginTop:12}}>เลขเด่น 3 ตัว: </p>
              <div className="num-row" style={{marginTop:8}}>
                {prediction.top3.map(n => (
                  <span key={n} className="num-chip t3">{n}</span>
                ))}
              </div>
            </div>
          </>
        )}

        <div className="disclaimer">
          <p>⚠️ ผลการทำนายเป็นเพียงการคำนวณทางสถิติ ไม่สามารถรับประกันผลลัพธ์ได้ 100% เล่นหวยอย่างมีสติ</p>
        </div>
      </div>
    </div>
    </>
  );
}
