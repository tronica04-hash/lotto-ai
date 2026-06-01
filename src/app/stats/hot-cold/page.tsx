import { supabase } from '@/lib/supabase';

async function getStats() {
  if (!supabase) return null;
  const { data } = await supabase
    .from('lotto_results')
    .select('draw_date, first_prize, two_digit, three_digit_first, three_digit_last, nearby_1st')
    .order('draw_date', { ascending: false });
  return data || [];
}

function computeHotCold(results: any[]) {
  // Frequency maps
  const freq2: Record<string, number> = {};
  const freq3First: Record<string, number> = {};
  const freq3Last: Record<string, number> = {};
  const freq6: Record<string, number> = {};
  const lastSeen: Record<string, number> = {}; // key -> index of last appearance

  results.forEach((r, idx) => {
    // 2-digit
    if (r.two_digit) {
      freq2[r.two_digit] = (freq2[r.two_digit] || 0) + 1;
      if (!(r.two_digit in lastSeen)) lastSeen[r.two_digit] = idx;
    }
    // 3-digit first
    if (r.three_digit_first) {
      for (const n of r.three_digit_first) {
        freq3First[n] = (freq3First[n] || 0) + 1;
        if (!(n in lastSeen)) lastSeen[n] = idx;
      }
    }
    // 3-digit last
    if (r.three_digit_last) {
      for (const n of r.three_digit_last) {
        freq3Last[n] = (freq3Last[n] || 0) + 1;
        if (!(n in lastSeen)) lastSeen[n] = idx;
      }
    }
    // 6-digit (first prize)
    if (r.first_prize) {
      freq6[r.first_prize] = (freq6[r.first_prize] || 0) + 1;
    }
  });

  // Hot = highest frequency
  const hot2 = Object.entries(freq2).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const cold2 = Object.entries(freq2).sort((a, b) => a[1] - b[1]).slice(0, 10);
  const hot3First = Object.entries(freq3First).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const hot3Last = Object.entries(freq3Last).sort((a, b) => b[1] - a[1]).slice(0, 10);

  // Due = hasn't appeared for longest (among top frequency numbers)
  const due2 = Object.entries(freq2)
    .filter(([k]) => freq2[k] >= 2)
    .sort((a, b) => (lastSeen[b[0]] || 0) - (lastSeen[a[0]] || 0))
    .slice(0, 10);

  return { hot2, cold2, hot3First, hot3Last, due2, total: results.length };
}

export default async function HotColdPage() {
  const results = await getStats();
  const stats = results ? computeHotCold(results) : null;

  if (!stats) {
    return <div style={{color:'#e2e8f0', padding:40, textAlign:'center'}}>ไม่สามารถโหลดข้อมูลได้</div>;
  }

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

      .container { max-width: 1200px; margin: 0 auto; padding: 32px 16px; }
      .page-title { font-size: 28px; font-weight: bold; margin-bottom: 8px; }
      .page-subtitle { color: #94a3b8; margin-bottom: 32px; }

      .tabs { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
      .tab { padding: 10px 20px; background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 8px; color: #94a3b8; cursor: pointer; font-size: 14px; }
      .tab.active { background: #9333ea; border-color: #9333ea; color: #fff; font-weight: 600; }

      .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
      .stat-card { background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 16px; padding: 24px; }
      .stat-card h3 { font-size: 18px; font-weight: bold; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
      .stat-list { list-style: none; }
      .stat-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(148,163,184,0.1); }
      .stat-item:last-child { border-bottom: none; }
      .stat-num { font-family: monospace; font-size: 16px; font-weight: bold; }
      .stat-count { color: #94a3b8; font-size: 13px; }
      .stat-bar { height: 4px; background: #1e293b; border-radius: 2px; margin-top: 4px; }
      .stat-bar-fill { height: 100%; border-radius: 2px; }

      .hot-color { color: #ef4444; }
      .cold-color { color: #3b82f6; }
      .due-color { color: #f59e0b; }
      .hot-bg { background: #ef4444; }
      .cold-bg { background: #3b82f6; }
      .due-bg { background: #f59e0b; }

      .info-box { background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 16px; margin-bottom: 24px; }
      .info-box p { color: #94a3b8; font-size: 14px; line-height: 1.6; }
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
        <h1 className="page-title">🔥 เลขร้อน / ❄️ เลขเย็น / ⏰ เลขนาย</h1>
        <p className="page-subtitle">วิเคราะห์จากข้อมูล {stats.total} งวดย้อนหลัง</p>

        <div className="info-box">
          <p>
            <strong>เลขร้อน (Hot):</strong> ตัวเลขที่ออกบ่อยที่สุด — มีแนวโน้มจะออกซ้ำ<br/>
            <strong>เลขเย็น (Cold):</strong> ตัวเลขที่ออกน้อยที่สุด — อาจถึงเวลาออก<br/>
            <strong>เลขนาย (Due):</strong> ตัวเลขที่ไม่ได้ออกมานานที่สุด — ใกล้จะออก
          </p>
        </div>

        <div className="stats-grid">
          {/* Hot 2-digit */}
          <div className="stat-card">
            <h3><span className="hot-color">🔥</span> เลขร้อน 2 ตัว</h3>
            <ul className="stat-list">
              {stats.hot2.map(([num, count], i) => (
                <li key={num} className="stat-item">
                  <div>
                    <span className="stat-num hot-color">{num}</span>
                    <div className="stat-bar"><div className="stat-bar-fill hot-bg" style={{width:`${Math.min(100, count * 10)}%`}} /></div>
                  </div>
                  <span className="stat-count">{count} ครั้ง</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Cold 2-digit */}
          <div className="stat-card">
            <h3><span className="cold-color">❄️</span> เลขเย็น 2 ตัว</h3>
            <ul className="stat-list">
              {stats.cold2.map(([num, count], i) => (
                <li key={num} className="stat-item">
                  <div>
                    <span className="stat-num cold-color">{num}</span>
                    <div className="stat-bar"><div className="stat-bar-fill cold-bg" style={{width:`${Math.min(100, count * 20)}%`}} /></div>
                  </div>
                  <span className="stat-count">{count} ครั้ง</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Due 2-digit */}
          <div className="stat-card">
            <h3><span className="due-color">⏰</span> เลขนาย 2 ตัว</h3>
            <ul className="stat-list">
              {stats.due2.map(([num, count], i) => (
                <li key={num} className="stat-item">
                  <div>
                    <span className="stat-num due-color">{num}</span>
                    <div className="stat-bar"><div className="stat-bar-fill due-bg" style={{width:`${Math.min(100, count * 10)}%`}} /></div>
                  </div>
                  <span className="stat-count">{count} ครั้ง</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Hot 3-digit first */}
          <div className="stat-card">
            <h3><span className="hot-color">🔥</span> เลขร้อน 3 ตัวหน้า</h3>
            <ul className="stat-list">
              {stats.hot3First.map(([num, count], i) => (
                <li key={num} className="stat-item">
                  <div>
                    <span className="stat-num hot-color">{num}</span>
                    <div className="stat-bar"><div className="stat-bar-fill hot-bg" style={{width:`${Math.min(100, count * 15)}%`}} /></div>
                  </div>
                  <span className="stat-count">{count} ครั้ง</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Hot 3-digit last */}
          <div className="stat-card">
            <h3><span className="hot-color">🔥</span> เลขร้อน 3 ตัวท้าย</h3>
            <ul className="stat-list">
              {stats.hot3Last.map(([num, count], i) => (
                <li key={num} className="stat-item">
                  <div>
                    <span className="stat-num hot-color">{num}</span>
                    <div className="stat-bar"><div className="stat-bar-fill hot-bg" style={{width:`${Math.min(100, count * 15)}%`}} /></div>
                  </div>
                  <span className="stat-count">{count} ครั้ง</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
