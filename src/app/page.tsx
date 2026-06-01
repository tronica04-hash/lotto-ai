import { supabase } from '@/lib/supabase';

async function getLatestResult() {
  if (!supabase) return null;
  const { data } = await supabase.from('lotto_results').select('*').order('draw_date', { ascending: false }).limit(1).single();
  return data;
}

async function getStats() {
  if (!supabase) return null;
  const { data } = await supabase.from('v_lotto_stats').select('*').single();
  return data;
}

function formatDate(dateStr: string) {
  const months = ['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  const d = new Date(dateStr);
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear() + 543}`;
}

export default async function Home() {
  const latest = await getLatestResult();
  const stats = await getStats();

  return (
    <>
    <style dangerouslySetInnerHTML={{__html: `
      * { margin:0; padding:0; box-sizing:border-box; }
      body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:#0f172a; color:#e2e8f0; }
      
      /* Nav */
      .nav { border-bottom:1px solid rgba(148,163,184,0.15); background:rgba(15,23,42,0.8); backdrop-filter:blur(8px); }
      .nav-in { max-width:1200px; margin:0 auto; padding:14px 16px; display:flex; align-items:center; justify-content:space-between; }
      .logo { font-size:20px; font-weight:bold; }
      .nav-links { display:flex; gap:6px; align-items:center; }
      .nav-links a { text-decoration:none; padding:8px 14px; font-size:14px; border-radius:6px; }
      .btn-ghost { color:#94a3b8; }
      .btn-ghost:hover { color:#fff; }
      .btn-primary { background:#9333ea; color:#fff; font-weight:600; }
      .btn-primary:hover { background:#7e22ce; }
      .btn-outline { border:1px solid #475569; color:#cbd5e1; }
      .btn-outline:hover { border-color:#9333ea; }

      /* Hero */
      .hero { max-width:900px; margin:0 auto; padding:48px 16px 32px; text-align:center; }
      .hero h1 { font-size:36px; font-weight:bold; margin-bottom:12px; line-height:1.3; }
      .gradient { background:linear-gradient(90deg,#c084fc,#f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
      .hero p { color:#94a3b8; font-size:16px; max-width:500px; margin:0 auto 24px; }
      .hero-btns { display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }
      .hero-btns a { text-decoration:none; padding:12px 24px; border-radius:8px; font-weight:600; font-size:15px; }

      /* Latest Result */
      .latest { max-width:700px; margin:0 auto; padding:0 16px 40px; }
      .card { background:rgba(30,41,59,0.5); border:1px solid rgba(148,163,184,0.15); border-radius:14px; padding:22px; }
      .card-title { font-size:15px; font-weight:600; color:#e2e8f0; margin-bottom:14px; display:flex; align-items:center; gap:8px; }
      .row { display:flex; align-items:center; gap:10px; margin-bottom:10px; flex-wrap:wrap; }
      .lbl { color:#94a3b8; font-size:13px; min-width:80px; }
      .chip { background:#1e293b; border:1px solid #334155; padding:5px 10px; border-radius:6px; font-family:monospace; font-size:13px; }
      .chip-gold { background:#92400e; border-color:#b45309; color:#fbbf24; font-weight:bold; }
      .chip-purple { background:#581c87; border-color:#7c3aed; color:#e9d5ff; font-weight:bold; }

      /* Features */
      .features { max-width:1000px; margin:0 auto; padding:0 16px 48px; }
      .feat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }
      .feat-card { background:rgba(30,41,59,0.4); border:1px solid rgba(148,163,184,0.12); border-radius:12px; padding:20px; }
      .feat-icon { font-size:28px; margin-bottom:8px; }
      .feat-card h3 { font-size:15px; font-weight:600; margin-bottom:4px; }
      .feat-card p { color:#64748b; font-size:13px; }
      .feat-card a { color:#a855f7; text-decoration:none; font-size:13px; display:inline-block; margin-top:8px; }

      /* Stats bar */
      .stats-bar { max-width:700px; margin:0 auto; padding:0 16px 32px; }
      .stats-in { display:flex; gap:12px; flex-wrap:wrap; justify-content:center; }
      .stat-pill { background:rgba(30,41,59,0.5); border:1px solid rgba(148,163,184,0.12); border-radius:8px; padding:10px 18px; text-align:center; }
      .stat-val { font-size:20px; font-weight:bold; color:#c084fc; }
      .stat-lbl { font-size:11px; color:#64748b; }

      /* Footer */
      .footer { border-top:1px solid rgba(148,163,184,0.1); margin-top:48px; }
      .footer-in { max-width:1200px; margin:0 auto; padding:20px 16px; text-align:center; color:#475569; font-size:12px; }

      @media(max-width:640px) {
        .hero h1 { font-size:26px; }
        .hero-btns { flex-direction:column; align-items:center; }
      }
    `}} />
    <div>
      <nav className="nav">
        <div className="nav-in">
          <div className="logo">🎰 LottoAI</div>
          <div className="nav-links">
            <a href="/results" className="btn-ghost">ผลหวย</a>
            <a href="/stats" className="btn-ghost">สถิติ</a>
            <a href="/login" className="btn-ghost">เข้าสู่ระบบ</a>
            <a href="/register" className="btn-primary">สมัครฟรี</a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="hero">
        <h1>ตรวจผลหวย<br /><span className="gradient">วิเคราะห์ด้วย AI</span></h1>
        <p>สถิติย้อนหลัง 36 ปี • Hot/Cold/Due • AI ทำนาย • ทำนายฝัน • ปฏิทินหวย</p>
        <div className="hero-btns">
          <a href="/register" className="btn-primary">เริ่มใช้งานฟรี</a>
          <a href="/results" className="btn-outline">ดูผลหวย</a>
        </div>
      </div>

      {/* Stats bar */}
      {stats && (
        <div className="stats-bar">
          <div className="stats-in">
            <div className="stat-pill">
              <div className="stat-val">{stats.total_draws}</div>
              <div className="stat-lbl">งวดทั้งหมด</div>
            </div>
            <div className="stat-pill">
              <div className="stat-val">{stats.first_draw?.substring(0,4) || '?'}</div>
              <div className="stat-lbl">ปีเก่าสุด</div>
            </div>
            <div className="stat-pill">
              <div className="stat-val">{stats.last_draw?.substring(0,4) || '?'}</div>
              <div className="stat-lbl">ล่าสุด</div>
            </div>
          </div>
        </div>
      )}

      {/* Latest Result */}
      {latest && (
        <div className="latest">
          <div className="card">
            <div className="card-title">📋 ผลหวยล่าสุด — งวด {formatDate(latest.draw_date)}</div>
            <div className="row">
              <span className="lbl">รางวัล 1</span>
              {latest.first_prize ? <span className="chip chip-gold">{latest.first_prize}</span> : <span style={{color:'#475569'}}>—</span>}
            </div>
            <div className="row">
              <span className="lbl">เลขหน้า 3</span>
              {(latest.three_digit_first && Array.isArray(latest.three_digit_first) && latest.three_digit_first.length > 0)
                ? latest.three_digit_first.map((n: any, i: number) => <span key={i} className="chip">{n}</span>)
                : <span style={{color:'#475569'}}>—</span>}
            </div>
            <div className="row">
              <span className="lbl">เลขท้าย 3</span>
              {(latest.three_digit_last && Array.isArray(latest.three_digit_last) && latest.three_digit_last.length > 0)
                ? latest.three_digit_last.map((n: any, i: number) => <span key={i} className="chip">{n}</span>)
                : <span style={{color:'#475569'}}>—</span>}
            </div>
            <div className="row">
              <span className="lbl">เลขท้าย 2</span>
              {latest.two_digit ? <span className="chip chip-purple">{latest.two_digit}</span> : <span style={{color:'#475569'}}>—</span>}
            </div>
            <div style={{marginTop:14, paddingTop:12, borderTop:'1px solid rgba(148,163,184,0.1)'}}>
              <a href={`/results?date=${latest.draw_date}`} style={{color:'#a855f7',textDecoration:'none',fontSize:13}}>ดูรายละเอียด →</a>
            </div>
          </div>
        </div>
      )}

      {/* Features */}
      <div className="features">
        <div className="feat-grid">
          <div className="feat-card">
            <div className="feat-icon">📋</div>
            <h3>ผลหวยย้อนหลัง</h3>
            <p>ดูผลหวยทุกงวดย้อนหลัง 36 ปี รางวัลครบทุกประเภท</p>
            <a href="/results">ดูทั้งหมด →</a>
          </div>
          <div className="feat-card">
            <div className="feat-icon">🔥</div>
            <h3>เลขร้อน / เลขเย็น</h3>
            <p>สถิติความถี่ตัวเลข วิเคราะห์ Hot/Cold/Due</p>
            <a href="/stats">ดูสถิติ →</a>
          </div>
          <div className="feat-card">
            <div className="feat-icon">🤖</div>
            <h3>AI ทำนาย</h3>
            <p>AI วิเคราะห์ pattern ให้คอมโบที่มีโอกาสสูงสุด</p>
            <a href="/stats">ดูผล AI →</a>
          </div>
          <div className="feat-card">
            <div className="feat-icon">💭</div>
            <h3>ทำนายฝัน</h3>
            <p>แปลความฝันเป็นเลข พจนานุกรมฝัน 44 คำ</p>
            <a href="/dream">ลองเลย →</a>
          </div>
        </div>
      </div>

      <footer className="footer">
        <div className="footer-in">
          <p>* ผลการวิเคราะห์เป็นเพียงสถิติ ไม่สามารถรับประกันผลลัพธ์ได้ 100%</p>
          <p style={{marginTop:4}}>LottoAI © 2026</p>
        </div>
      </footer>
    </div>
    </>
  );
}
