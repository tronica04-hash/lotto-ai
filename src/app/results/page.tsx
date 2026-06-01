import { supabase } from '@/lib/supabase';
import Link from 'next/link';

async function getResults(year?: string, month?: string) {
  if (!supabase) return [];
  let query = supabase
    .from('lotto_results')
    .select('*')
    .order('draw_date', { ascending: false });

  if (year) {
    query = query.like('draw_date', `${year}%`);
  }
  if (month) {
    const paddedMonth = month.padStart(2, '0');
    query = query.like('draw_date', `%-${paddedMonth}-%`);
  }

  const { data } = await query;
  return data || [];
}

function formatDate(dateStr: string) {
  const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  const d = new Date(dateStr);
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear() + 543}`;
}

export default async function ResultsPage({
  searchParams,
}: {
  searchParams: Promise<{ year?: string; month?: string }>;
}) {
  const params = await searchParams;
  const results = await getResults(params.year, params.month);

  const years = Array.from({ length: 21 }, (_, i) => 2026 - i);
  const months = [
    { value: '1', label: 'มกราคม' },
    { value: '2', label: 'กุมภาพันธ์' },
    { value: '3', label: 'มีนาคม' },
    { value: '4', label: 'เมษายน' },
    { value: '5', label: 'พฤษภาคม' },
    { value: '6', label: 'มิถุนายน' },
    { value: '7', label: 'กรกฎาคม' },
    { value: '8', label: 'สิงหาคม' },
    { value: '9', label: 'กันยายน' },
    { value: '10', label: 'ตุลาคม' },
    { value: '11', label: 'พฤศจิกายน' },
    { value: '12', label: 'ธันวาคม' },
  ];

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
      .page-subtitle { color: #94a3b8; margin-bottom: 24px; }

      /* Filter */
      .filter-row { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
      .filter-row select { background: #1e293b; border: 1px solid #334155; color: #e2e8f0; padding: 10px 16px; border-radius: 8px; font-size: 14px; }
      .filter-row select:focus { outline: none; border-color: #9333ea; }
      .filter-btn { background: #9333ea; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
      .filter-btn:hover { background: #7e22ce; }
      .filter-reset { color: #94a3b8; background: transparent; border: 1px solid #334155; padding: 10px 16px; border-radius: 8px; cursor: pointer; }
      .filter-reset:hover { border-color: #94a3b8; color: #fff; }

      /* Table */
      .table-wrap { overflow-x: auto; }
      table { width: 100%; border-collapse: collapse; }
      th { text-align: left; padding: 12px 16px; background: rgba(30,41,59,0.8); color: #94a3b8; font-size: 13px; font-weight: 600; letter-spacing: 0.05em; position: sticky; top: 0; }
      td { padding: 12px 16px; border-bottom: 1px solid rgba(148,163,184,0.1); font-size: 14px; }
      tr:hover { background: rgba(30,41,59,0.4); }
      .date-link { color: #a855f7; text-decoration: none; font-weight: 600; }
      .date-link:hover { color: #c084fc; }
      .num-cell { font-family: monospace; }
      .gold { color: #fbbf24; font-weight: bold; }
      .chip { background: #1e293b; border: 1px solid #334155; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 13px; margin-right: 4px; display: inline-block; }
      .chip-highlight { background: #9333ea; border-color: #a855f7; color: #fff; }
      .empty { color: #475569; font-size: 13px; }
      .table-info { color: #64748b; font-size: 13px; margin-top: 12px; }

      /* Mobile cards */
      .mobile-cards { display: none; }
      .result-card-mobile { background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
      .mobile-date { font-weight: bold; color: #a855f7; text-decoration: none; font-size: 15px; }
      .mobile-row { display: flex; gap: 8px; margin-top: 8px; align-items: center; flex-wrap: wrap; }
      .mobile-label { color: #94a3b8; font-size: 13px; min-width: 80px; }

      @media (max-width: 768px) {
        .table-wrap { display: none; }
        .mobile-cards { display: block; }
        .filter-row { gap: 8px; }
        .filter-row select { padding: 8px 12px; font-size: 14px; }
      }
    `}} />
    <div>
      <nav className="nav">
        <div className="nav-inner">
          <a href="/" className="logo">🎰 LottoAI</a>
          <div className="nav-links">
            <a href="/results" className="active">ผลหวย</a>
            <a href="/stats">สถิติ</a>
            <a href="/login">เข้าสู่ระบบ</a>
            <a href="/register" className="btn-primary">สมัครฟรี</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <h1 className="page-title">📋 ผลหวยย้อนหลัง</h1>
        <p className="page-subtitle">ผลสลากกินแบ่งรัฐบาลทุกงวด พร้อมรางวัลครบทุกประเภท</p>

        <form method="GET" className="filter-row">
          <select name="year" defaultValue={params.year || ''}>
            <option value="">ทุกปี</option>
            {years.map(y => (
              <option key={y} value={y}>{y + 543}</option>
            ))}
          </select>
          <select name="month" defaultValue={params.month || ''}>
            <option value="">ทุกเดือน</option>
            {months.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
          <button type="submit" className="filter-btn">กรอง</button>
          {(params.year || params.month) && (
            <a href="/results" className="filter-reset">ล้างตัวกรอง</a>
          )}
        </form>

        {/* Desktop Table */}
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>งวด</th>
                <th>รางวัลที่ 1</th>
                <th>เลขหน้า 3</th>
                <th>เลขท้าย 3</th>
                <th>เลขท้าย 2</th>
                <th>ข้างเคียง</th>
              </tr>
            </thead>
            <tbody>
              {results.map(r => (
                <tr key={r.draw_date}>
                  <td>
                    <a href={`/results/${r.draw_date}`} className="date-link">
                      {formatDate(r.draw_date)}
                    </a>
                  </td>
                  <td className="num-cell">{r.first_prize ? <span className="gold">{r.first_prize}</span> : <span className="empty">—</span>}</td>
                  <td className="num-cell">
                    {r.three_digit_first?.length > 0
                      ? r.three_digit_first.map((n: string, i: number) => <span key={i} className="chip">{n}</span>)
                      : <span className="empty">—</span>}
                  </td>
                  <td className="num-cell">
                    {r.three_digit_last?.length > 0
                      ? r.three_digit_last.map((n: string, i: number) => <span key={i} className="chip">{n}</span>)
                      : <span className="empty">—</span>}
                  </td>
                  <td className="num-cell">{r.two_digit ? <span className="chip chip-highlight">{r.two_digit}</span> : <span className="empty">—</span>}</td>
                  <td className="num-cell">
                    {r.nearby_1st?.length > 0
                      ? r.nearby_1st.map((n: string, i: number) => <span key={i} className="chip">{n}</span>)
                      : <span className="empty">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Cards */}
        <div className="mobile-cards">
          {results.map(r => (
            <div key={r.draw_date} className="result-card-mobile">
              <a href={`/results/${r.draw_date}`} className="mobile-date">{formatDate(r.draw_date)}</a>
              <div className="mobile-row">
                <span className="mobile-label">รางวัล 1:</span>
                <span className="gold">{r.first_prize || '—'}</span>
              </div>
              <div className="mobile-row">
                <span className="mobile-label">หน้า 3:</span>
                <span>{r.three_digit_first?.join(', ') || '—'}</span>
              </div>
              <div className="mobile-row">
                <span className="mobile-label">ท้าย 3:</span>
                <span>{r.three_digit_last?.join(', ') || '—'}</span>
              </div>
              <div className="mobile-row">
                <span className="mobile-label">ท้าย 2:</span>
                <span>{r.two_digit || '—'}</span>
              </div>
            </div>
          ))}
        </div>

        <p className="table-info">แสดง {results.length} งวด {params.year || params.month ? '(กรองแล้ว)' : ''}</p>
      </div>
    </div>
    </>
  );
}
