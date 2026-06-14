'use client';

import { useEffect, useState, useCallback } from 'react';
import { supabase } from '@/lib/supabase';

// ─── Types ──────────────────────────────────────────────
interface LottoRow {
  draw_date: string;
  first_prize: string | null;
  two_digit: string | null;
  three_digit_first: any;
  three_digit_last: any;
}

interface HelperResult {
  number: string;
  digitLen: number;
  lastSeenDraw: string | null;
  lastSeenIndex: number;       // กี่งวดที่แล้ว (0 = งวดล่าสุด)
  totalHits: number;
  hotCold: 'ร้อน' | 'ปกติ' | 'เย็น';
  estimatedReturn: number;     // เงินคืนโดยประมาณต่อ 80 บาท
  matchType: string;           // ประเภทการตรง
  details: string[];           // รายละเอียดเพิ่มเติม
}

// ─── Helpers ────────────────────────────────────────────
function safeArr(v: any): string[] {
  if (!v) return [];
  if (Array.isArray(v)) return v;
  try { return JSON.parse(v); } catch { return []; }
}

function fmtDate(d: string) {
  const m = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
             'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  const dd = new Date(d);
  return `${dd.getDate()} ${m[dd.getMonth()]} ${dd.getFullYear() + 543}`;
}

// อัตราจ่ายต่อ 1 บาท (หวยรัฐบาลไทย)
const PAYOUT_RATES: Record<string, number> = {
  first_prize: 6000000,   // 6 ล้านต่อ 1 บาท (รางวัลที่ 1)
  nearby_1st: 100000,      // แข่ง 1 แสน
  second_prize: 200000,   // รางวัลที่ 2 ละ 2 แสน
  third_prize: 80000,     // รางวัลที่ 3 ละ 8 หมื่น
  three_digit_front: 4000, // เลขหน้า 3 ตัว ละ 4 พัน
  three_digit_back: 4000,  // เลขท้าย 3 ตัว ละ 4 พัน
  two_digit: 2000,         // เลขท้าย 2 ตัว ละ 2 พัน
};

// ─── Main Component ─────────────────────────────────────
export default function LottoHelperPage() {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [results, setResults] = useState<LottoRow[]>([]);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<HelperResult | null>(null);
  const [err, setErr] = useState('');
  const [searching, setSearching] = useState(false);

  // Auth check + load data
  useEffect(() => {
    if (!supabase) { setLoading(false); return; }
    supabase.auth.getUser().then(({ data }) => {
      if (!data.user) { window.location.href = '/login'; return; }
      setUser(data.user);
      supabase!.from('lotto_results')
        .select('*')
        .order('draw_date', { ascending: false })
        .then(({ data: d, error }) => {
          if (error || !d?.length) {
            // Fallback: local JSON
            fetch('/lotto-data.json')
              .then(r => r.json())
              .then(localData => {
                if (localData?.length > 0) {
                  setResults(localData);
                } else {
                  setErr('ไม่สามารถโหลดข้อมูลได้');
                }
                setLoading(false);
              })
              .catch(() => { setErr('ไม่สามารถโหลดข้อมูลได้'); setLoading(false); });
            return;
          }
          setResults(d);
          setLoading(false);
        });
    });
  }, []);

  // ─── Search Logic ─────────────────────────────────────
  const handleSearch = useCallback(() => {
    setResult(null);
    setErr('');

    const q = query.trim().replace(/\D/g, '');
    if (!q || q.length < 2 || q.length > 6) {
      setErr('กรุณากรอกตัวเลข 2-6 หลัก');
      return;
    }

    setSearching(true);
    setTimeout(() => { // prevent UI freeze
      try {
        const searchResult = searchNumber(q, results);
        setResult(searchResult);
      } catch (e: any) {
        setErr(e.message || 'เกิดข้อผิดพลาด');
      }
      setSearching(false);
    }, 50);
  }, [query, results]);

  const handleLogout = async () => {
    await supabase?.auth.signOut();
    window.location.href = '/';
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  // ─── Render ───────────────────────────────────────────
  if (loading) {
    return (
      <div style={s.page}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', color: '#94a3b8', fontSize: 16 }}>
          🎰 กำลังโหลด...
        </div>
      </div>
    );
  }

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: `
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }

        .lh { min-height: 100vh; background: linear-gradient(135deg, #0f172a 0%, #581c87 50%, #0f172a 100%); color: #e2e8f0; }
        .lh-header { border-bottom: 1px solid rgba(148,163,184,0.15); background: rgba(15,23,42,0.85); backdrop-filter: blur(8px); position: sticky; top: 0; z-index: 50; }
        .lh-header-inner { max-width: 900px; margin: 0 auto; padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; }
        .lh-logo { font-size: 20px; font-weight: bold; background: linear-gradient(90deg, #c084fc, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .lh-right { display: flex; align-items: center; gap: 8px; }
        .lh-av { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #9333ea, #ec4899); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #fff; }
        .lh-em { color: #64748b; font-size: 12px; }
        .lh-logout { padding: 5px 12px; font-size: 12px; color: #94a3b8; background: transparent; border: 1px solid #334155; border-radius: 6px; cursor: pointer; }
        .lh-logout:hover { border-color: #9333ea; color: #c084fc; }
        .lh-back { padding: 5px 12px; font-size: 12px; color: #94a3b8; background: transparent; border: 1px solid #334155; border-radius: 6px; cursor: pointer; text-decoration: none; }
        .lh-back:hover { border-color: #9333ea; color: #c084fc; }

        .lh-main { max-width: 700px; margin: 0 auto; padding: 32px 20px; }
        .lh-title { font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 6px; }
        .lh-subtitle { color: #94a3b8; text-align: center; font-size: 14px; margin-bottom: 28px; }

        .lh-search-box { display: flex; gap: 10px; margin-bottom: 28px; }
        .lh-input { flex: 1; padding: 14px 18px; background: rgba(30,41,59,0.6); border: 2px solid rgba(148,163,184,0.2); border-radius: 12px; color: #fff; font-size: 24px; font-family: monospace; font-weight: bold; text-align: center; letter-spacing: 6px; outline: none; transition: border-color 0.2s; }
        .lh-input:focus { border-color: #9333ea; }
        .lh-input::placeholder { color: #475569; font-size: 16px; letter-spacing: 2px; font-weight: normal; }
        .lh-btn { padding: 14px 28px; background: linear-gradient(135deg, #9333ea, #c026d3); color: #fff; font-weight: bold; font-size: 16px; border: none; border-radius: 12px; cursor: pointer; white-space: nowrap; transition: opacity 0.2s; }
        .lh-btn:hover { opacity: 0.9; }
        .lh-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .lh-err { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 12px 16px; color: #f87171; font-size: 14px; margin-bottom: 20px; text-align: center; }

        .lh-result { background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.12); border-radius: 16px; padding: 24px; margin-bottom: 20px; }
        .lh-num-display { font-size: 48px; font-weight: bold; font-family: monospace; text-align: center; background: linear-gradient(90deg, #c084fc, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px; }
        .lh-match-type { text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 20px; }

        .lh-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
        .lh-stat { background: rgba(51,65,85,0.3); border-radius: 10px; padding: 14px; }
        .lh-stat-label { color: #64748b; font-size: 11px; margin-bottom: 4px; }
        .lh-stat-value { font-size: 20px; font-weight: bold; }
        .lh-stat-sub { color: #475569; font-size: 11px; margin-top: 2px; }

        .lh-hot { color: #f87171; }
        .lh-cold { color: #60a5fa; }
        .lh-normal { color: #fbbf24; }

        .lh-return-box { background: linear-gradient(135deg, rgba(147,51,234,0.15), rgba(192,38,211,0.1)); border: 1px solid rgba(147,51,234,0.3); border-radius: 12px; padding: 18px; text-align: center; }
        .lh-return-label { color: #94a3b8; font-size: 12px; margin-bottom: 4px; }
        .lh-return-value { font-size: 32px; font-weight: bold; color: #c084fc; }
        .lh-return-sub { color: #475569; font-size: 11px; margin-top: 4px; }

        .lh-details { margin-top: 16px; }
        .lh-details-title { color: #94a3b8; font-size: 12px; margin-bottom: 8px; }
        .lh-detail-item { padding: 6px 0; border-bottom: 1px solid rgba(148,163,184,0.06); font-size: 13px; color: #cbd5e1; }

        .lh-tips { background: rgba(30,41,59,0.4); border: 1px solid rgba(148,163,184,0.08); border-radius: 12px; padding: 18px; }
        .lh-tips-title { color: #94a3b8; font-size: 13px; font-weight: 600; margin-bottom: 10px; }
        .lh-tips-list { color: #64748b; font-size: 12px; line-height: 1.8; }

        .lh-disclaimer { text-align: center; color: #334155; font-size: 11px; margin-top: 24px; }

        @media(max-width: 640px) {
          .lh-grid { grid-template-columns: 1fr; }
          .lh-search-box { flex-direction: column; }
          .lh-num-display { font-size: 36px; }
        }
      ` }} />

      <div className="lh">
        {/* Header */}
        <header className="lh-header">
          <div className="lh-header-inner">
            <div className="lh-logo">🎰 LottoAI</div>
            <div className="lh-right">
              <a href="/dashboard" className="lh-back">← Dashboard</a>
              <div className="lh-av">{user?.email?.charAt(0).toUpperCase()}</div>
              <span className="lh-em">{user?.email}</span>
              <button onClick={handleLogout} className="lh-logout">ออก</button>
            </div>
          </div>
        </header>

        {/* Main */}
        <main className="lh-main">
          <h1 className="lh-title">🔍 ผู้ช่วยคิดหวย</h1>
          <p className="lh-subtitle">ค้นหาเลขของคุณ ดูสถิติย้อนหลัง {results.length} งวด</p>

          {/* Search */}
          <div className="lh-search-box">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value.replace(/\D/g, ''))}
              onKeyDown={handleKeyDown}
              placeholder="กรอกเลข 2-6 หลัก"
              className="lh-input"
              maxLength={6}
              autoFocus
            />
            <button
              onClick={handleSearch}
              disabled={searching || !query.trim()}
              className="lh-btn"
            >
              {searching ? '🔄 ค้นหา...' : '🔍 ค้นหา'}
            </button>
          </div>

          {/* Error */}
          {err && <div className="lh-err">⚠️ {err}</div>}

          {/* Result */}
          {result && (
            <>
              <div className="lh-result">
                {/* Number display */}
                <div className="lh-num-display">{result.number}</div>
                <div className="lh-match-type">{result.matchType}</div>

                {/* Stats grid */}
                <div className="lh-grid">
                  <div className="lh-stat">
                    <div className="lh-stat-label">ออกครั้งล่าสุด</div>
                    <div className="lh-stat-value" style={{ fontSize: 18 }}>
                      {result.lastSeenIndex === 0
                        ? 'งวดล่าสุด!'
                        : `${result.lastSeenIndex} งวดที่แล้ว`}
                    </div>
                    {result.lastSeenDraw && (
                      <div className="lh-stat-sub">{fmtDate(result.lastSeenDraw)}</div>
                    )}
                  </div>

                  <div className="lh-stat">
                    <div className="lh-stat-label">ออกทั้งหมด</div>
                    <div className="lh-stat-value">{result.totalHits} ครั้ง</div>
                    <div className="lh-stat-sub">จาก {results.length} งวด ({(result.totalHits / results.length * 100).toFixed(1)}%)</div>
                  </div>

                  <div className="lh-stat">
                    <div className="lh-stat-label">สถานะ</div>
                    <div className={`lh-stat-value ${result.hotCold === 'ร้อน' ? 'lh-hot' : result.hotCold === 'เย็น' ? 'lh-cold' : 'lh-normal'}`}>
                      {result.hotCold === 'ร้อน' ? '🔥 ร้อน' : result.hotCold === 'เย็น' ? '❄️ เย็น' : '🟡 ปกติ'}
                    </div>
                    <div className="lh-stat-sub">
                      {result.hotCold === 'ร้อน'
                        ? 'ออกใน 10 งวดล่าสุด'
                        : result.hotCold === 'เย็น'
                          ? 'ไม่ออกเกิน 20 งวด'
                          : 'ออกปกติ'}
                    </div>
                  </div>

                  <div className="lh-stat">
                    <div className="lh-stat-label">ค่าเฉลี่ยต่องวด</div>
                    <div className="lh-stat-value" style={{ fontSize: 18 }}>
                      {(result.totalHits / results.length * 100).toFixed(1)}%
                    </div>
                    <div className="lh-stat-sub">
                      คาดว่าออกทุก {result.totalHits > 0 ? Math.round(results.length / result.totalHits) : '—'} งวด
                    </div>
                  </div>
                </div>

                {/* Estimated return */}
                <div className="lh-return-box">
                  <div className="lh-return-label">💰 คาดการณ์เงินคืนต่อการซื้อ 80 บาท</div>
                  <div className="lh-return-value">
                    {result.estimatedReturn > 0
                      ? `~${result.estimatedReturn.toLocaleString()} บาท`
                      : '— บาท'}
                  </div>
                  <div className="lh-return-sub">
                    {result.estimatedReturn > 0
                      ? `กำไร/ขาดทุน: ${result.estimatedReturn > 80 ? '+' : ''}${(result.estimatedReturn - 80).toLocaleString()} บาท`
                      : 'ไม่มีข้อมูการถูกรางวัล'}
                  </div>
                </div>

                {/* Details */}
                {result.details.length > 0 && (
                  <div className="lh-details">
                    <div className="lh-details-title">📋 รายละเอียด</div>
                    {result.details.map((d, i) => (
                      <div key={i} className="lh-detail-item">{d}</div>
                    ))}
                  </div>
                )}
              </div>

              {/* Tips */}
              <div className="lh-tips">
                <div className="lh-tips-title">💡 วิธีอ่านผล</div>
                <div className="lh-tips-list">
                  • <strong>🔥 ร้อน</strong> = เลขนี้ออกบ่อยในช่วง 10 งวดล่าสุด — ฟรีเคนซี่สูงกว่าค่าเฉลี่ย<br />
                  • <strong>❄️ เย็น</strong> = ไม่ออกมานานเกิน 20 งวด — อาจจะ "ถึงเวลาออก" ตามสถิติ<br />
                  • <strong>🟡 ปกติ</strong> = ออกตามค่าเฉลี่ย ไม่มีอะไรผิดปกติ<br />
                  • <strong>เงินคืนโดยประมาณ</strong> = คำนวณจากอัตราจ่ายจริง × ความถี่ย้อนหลัง ไม่รับประกันผล<br />
                  • ข้อมูลจาก {results.length} งวดย้อนหลัง ({results[results.length - 1]?.draw_date} — {results[0]?.draw_date})
                </div>
              </div>
            </>
          )}

          {/* Empty state */}
          {!result && !err && (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <div style={{ fontSize: 64, marginBottom: 16 }}>🎲</div>
              <div style={{ color: '#64748b', fontSize: 15, marginBottom: 8 }}>
                กรอกเลขที่ต้องการค้นหา
              </div>
              <div style={{ color: '#475569', fontSize: 13 }}>
                ระบบจะค้นหาในเลขท้าย 2 ตัว, เลข 3 ตัว และรางวัลที่ 1 ทั้งหมด
              </div>
            </div>
          )}

          <div className="lh-disclaimer">
            ⚠️ ข้อมูลนี้เป็นเพียงสถิติย้อนหลัง ไม่รับประกันผลการถูกรางวัล เล่นหวยอย่างมีสติ
          </div>
        </main>
      </div>
    </>
  );
}

// ─── Search Engine ──────────────────────────────────────
function searchNumber(q: string, results: LottoRow[]): HelperResult {
  const len = q.length;
  let totalHits = 0;
  let lastSeenIndex = -1;
  let lastSeenDraw: string | null = null;
  let matchType = '';
  const details: string[] = [];

  // นับใน 10 งวดล่าสุด (hot/cold)
  let recentHits = 0;
  const recentDraws = Math.min(10, results.length);

  if (len === 2) {
    // ── ค้นใน two_digit ──
    matchType = 'ค้นในเลขท้าย 2 ตัว (รางวัลเลขท้าย 2 ตัว)';
    const padded = q.padStart(2, '0');

    results.forEach((r, i) => {
      const td = r.two_digit ? String(r.two_digit).padStart(2, '0') : '';
      if (td === padded) {
        totalHits++;
        if (lastSeenIndex === -1) { lastSeenIndex = i; lastSeenDraw = r.draw_date; }
        if (i < recentDraws) recentHits++;
      }
    });

    // นับด้วย three_digit_last (2 ตัวท้าย)
    let t3BackHits = 0;
    results.forEach((r, i) => {
      const arr = safeArr(r.three_digit_last);
      arr.forEach(n => {
        if (String(n).endsWith(padded)) {
          t3BackHits++;
          if (lastSeenIndex === -1) { lastSeenIndex = i; lastSeenDraw = r.draw_date; }
        }
      });
    });
    if (t3BackHits > 0) {
      details.push(`ตรงกับเลขท้าย 2 ตัวของ "เลขท้าย 3 ตัว" ${t3BackHits} ครั้ง`);
    }
    totalHits += t3BackHits;

    // นับด้วย first_prize (2 ตัวท้าย)
    let fpHits = 0;
    results.forEach(r => {
      if (r.first_prize && String(r.first_prize).endsWith(padded)) fpHits++;
    });
    if (fpHits > 0) {
      details.push(`เป็น 2 ตัวท้ายของรางวัลที่ 1: ${fpHits} ครั้ง`);
    }
    totalHits += fpHits;

  } else if (len === 3) {
    // ── ค้นใน three_digit_last และ three_digit_first ──
    matchType = 'ค้นในเลข 3 ตัว (ท้าย 3 + หน้า 3)';

    results.forEach((r, i) => {
      const backArr = safeArr(r.three_digit_last);
      const frontArr = safeArr(r.three_digit_first);
      const padded = q.padStart(3, '0');

      const backMatch = backArr.includes(padded) || backArr.includes(q);
      const frontMatch = frontArr.includes(padded) || frontArr.includes(q);

      if (backMatch) {
        totalHits++;
        if (lastSeenIndex === -1) { lastSeenIndex = i; lastSeenDraw = r.draw_date; }
        if (i < recentDraws) recentHits++;
        details.push(`${fmtDate(r.draw_date)} — ตรงกับเลขท้าย 3 ตัว`);
      }
      if (frontMatch) {
        totalHits++;
        if (lastSeenIndex === -1) { lastSeenIndex = i; lastSeenDraw = r.draw_date; }
        if (i < recentDraws) recentHits++;
        details.push(`${fmtDate(r.draw_date)} — ตรงกับเลขหน้า 3 ตัว`);
      }
    });

    // นับด้วย first_prize (3 ตัวท้าย หรือ 3 ตัวหน้า)
    let fpBack = 0, fpFront = 0;
    results.forEach(r => {
      if (!r.first_prize || r.first_prize.length < 3) return;
      if (String(r.first_prize).endsWith(q.padStart(3, '0'))) fpBack++;
      if (String(r.first_prize).substring(0, 3) === q.padStart(3, '0')) fpFront++;
    });
    if (fpBack > 0) details.push(`เป็น 3 ตัวท้ายของรางวัลที่ 1: ${fpBack} ครั้ง`);
    if (fpFront > 0) details.push(`เป็น 3 ตัวหน้าของรางวัลที่ 1: ${fpFront} ครั้ง`);
    totalHits += fpBack + fpFront;

  } else if (len >= 4 && len <= 6) {
    // ── ค้นใน first_prize ──
    matchType = `ค้นในรางวัลที่ 1 (${len} หลัก)`;
    const padded = q.padStart(6, '0');

    results.forEach((r, i) => {
      if (!r.first_prize) return;
      const fp = String(r.first_prize).padStart(6, '0');

      if (len === 6 && fp === padded) {
        totalHits++;
        if (lastSeenIndex === -1) { lastSeenIndex = i; lastSeenDraw = r.draw_date; }
        if (i < recentDraws) recentHits++;
        details.push(`${fmtDate(r.draw_date)} — ถูกรางวัลที่ 1 🎉`);
      } else if (len < 6) {
        // ค้นแบบ substring
        if (fp.includes(q) || fp.includes(padded.substring(6 - len))) {
          totalHits++;
          if (lastSeenIndex === -1) { lastSeenIndex = i; lastSeenDraw = r.draw_date; }
          if (i < recentDraws) recentHits++;
        }
      }
    });
  }

  // ── คำนวณ Hot/Cold ──
  let hotCold: 'ร้อน' | 'ปกติ' | 'เย็น' = 'ปกติ';
  if (lastSeenIndex !== -1) {
    if (lastSeenIndex < 10) hotCold = 'ร้อน';
    else if (lastSeenIndex >= 20) hotCold = 'เย็น';
  }

  // ── คำนวณเงินคืนโดยประมาณ ──
  // ใช้ expected value = sum(payout_rate × probability)
  let estimatedReturn = 0;
  const totalDraws = results.length;

  if (totalHits > 0 && len === 2) {
    const prob = totalHits / totalDraws;
    estimatedReturn = Math.round(prob * PAYOUT_RATES.two_digit * 80);
  } else if (totalHits > 0 && len === 3) {
    const prob = totalHits / totalDraws;
    estimatedReturn = Math.round(prob * PAYOUT_RATES.three_digit_back * 80);
  } else if (totalHits > 0 && len === 6) {
    const prob = totalHits / totalDraws;
    estimatedReturn = Math.round(prob * PAYOUT_RATES.first_prize * 80);
  } else if (totalHits > 0 && len >= 4) {
    const prob = totalHits / totalDraws;
    estimatedReturn = Math.round(prob * PAYOUT_RATES.first_prize * 80);
  }

  // จำกัด details ไม่เกิน 10 รายการ
  const limitedDetails = details.slice(0, 10);
  if (details.length > 10) {
    limitedDetails.push(`... และอีก ${details.length - 10} รายการ`);
  }

  return {
    number: q,
    digitLen: len,
    lastSeenDraw,
    lastSeenIndex: lastSeenIndex === -1 ? 999 : lastSeenIndex,
    totalHits,
    hotCold,
    estimatedReturn,
    matchType,
    details: limitedDetails,
  };
}

// ─── Styles ─────────────────────────────────────────────
const s: Record<string, React.CSSProperties> = {
  page: { minHeight: '100vh', background: '#0f172a', color: '#e2e8f0' },
};
