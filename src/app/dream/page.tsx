'use client';

import { useState } from 'react';

export default function DreamPage() {
  // Dream mapping dictionary
  const dreamMap: Record<string, string[]> = {
    'งู': ['65', '28'],
    'ช้าง': ['42', '11'],
    'ม้า': ['33', '58'],
    'วัว': ['19', '70'],
    'ไก่': ['01', '46'],
    'หมา': ['52', '37'],
    'แมว': ['24', '63'],
    'ปลา': ['08', '75'],
    'นก': ['13', '49'],
    'เสือ': ['56', '21'],
    'กระต่าย': ['38', '67'],
    'ตุ๊กแก': ['44', '15'],
    'เต่า': ['72', '03'],
    'ควาย': ['29', '54'],
    'หมู': ['61', '16'],
    'ลิง': ['47', '82', '05'],
    'จระเข้': ['35', '48'],
    'นางฟ้า': ['09', '76'],
    'ผี': ['66', '31'],
    'บ้าน': ['40', '85'],
    'รถ': ['17', '53'],
    'เงิน': ['74', '22', '90'],
    'ทอง': ['88', '69'],
    'น้ำ': ['06', '39'],
    'ไฟ': ['50', '41'],
    'ดิน': ['14', '71'],
    'ต้นไม้': ['57', '26'],
    'ดอกไม้': ['78', '07'],
    'ผลไม้': ['83', '64'],
    'หมอ': ['12', '93'],
    'ครู': ['34', '77'],
    'ทหาร': ['43', '86'],
    'ตำรวจ': ['55', '20'],
    'พระ': ['02', '96'],
    'วัด': ['10', '59'],
    'โรงเรียน': ['23', '89'],
    'ตลาด': ['30', '62'],
    'ป่า': ['45', '73'],
    'ภูเขา': ['18', '91'],
    'ทะเล': ['04', '87'],
    'แม่น้ำ': ['51', '36'],
    'สะพาน': ['27', '68'],
    'โรงงาน': ['94', '80'],
    'รถไฟ': ['97', '60'],
    'เครื่องบิน': ['98', '32'],
    'ทหารเรือ': ['99', '84'],
    'รถยนต์': ['81', '95'],
    'จักรยาน': ['00', '79'],
  };

  const selectDream = (key: string) => {
    const input = document.getElementById('dreamInput') as HTMLInputElement;
    if (input) input.value = key;
    showResult(key);
  };

  const showResult = (key: string) => {
    const box = document.getElementById('resultBox');
    const kw = document.getElementById('resultKeyword');
    const nums = document.getElementById('resultNums');
    if (!box || !kw || !nums) return;
    if (dreamMap[key]) {
      kw.textContent = 'ความฝัน: ' + key;
      nums.innerHTML = dreamMap[key].map(n =>
        '<span class="result-num">' + n + '</span>'
      ).join('');
      box.className = 'result-box show';
    } else if (key.length > 0) {
      const matches = Object.keys(dreamMap).filter(k => k.includes(key));
      if (matches.length > 0) {
        const allNums: string[] = [];
        matches.forEach(m => allNums.push(...dreamMap[m]));
        kw.textContent = 'คำที่ใกล้เคียง: ' + matches.join(', ');
        nums.innerHTML = [...new Set(allNums)].slice(0, 8).map(n =>
          '<span class="result-num">' + n + '</span>'
        ).join('');
        box.className = 'result-box show';
      }
    }
  };

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
      .btn-primary { padding: 8px 16px; background: #9333ea; color: #fff; border-radius: 8px; font-weight: 600; text-decoration: none; }

      .container { max-width: 800px; margin: 0 auto; padding: 32px 16px; }
      .page-title { font-size: 28px; font-weight: bold; margin-bottom: 8px; }
      .page-subtitle { color: #94a3b8; margin-bottom: 32px; }

      .dream-card { background: linear-gradient(135deg, rgba(147,51,234,0.15), rgba(59,130,246,0.15)); border: 1px solid rgba(148,163,184,0.2); border-radius: 20px; padding: 32px; margin-bottom: 24px; }
      .dream-card h2 { font-size: 20px; font-weight: bold; margin-bottom: 16px; }

      .search-input { width: 100%; padding: 14px 20px; background: #1e293b; border: 2px solid #334155; border-radius: 12px; color: #fff; font-size: 16px; margin-bottom: 16px; }
      .search-input:focus { outline: none; border-color: #9333ea; }
      .search-input::placeholder { color: #64748b; }

      .keyword-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; margin-bottom: 24px; }
      .keyword-btn { padding: 10px 12px; background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 8px; color: #cbd5e1; cursor: pointer; font-size: 14px; text-align: center; transition: all 0.2s; }
      .keyword-btn:hover { background: #9333ea; border-color: #9333ea; color: #fff; }

      .result-box { background: rgba(30,41,59,0.6); border: 1px solid rgba(168,85,247,0.3); border-radius: 16px; padding: 24px; display: none; }
      .result-box.show { display: block; }
      .result-keyword { font-size: 18px; font-weight: bold; color: #c084fc; margin-bottom: 12px; }
      .result-nums { display: flex; gap: 12px; flex-wrap: wrap; }
      .result-num { background: #9333ea; color: #fff; padding: 12px 20px; border-radius: 10px; font-family: monospace; font-size: 24px; font-weight: bold; }

      .info-box { background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 16px; }
      .info-box p { color: #94a3b8; font-size: 14px; line-height: 1.6; }
    `}} />
    <div>
      <nav className="nav">
        <div className="nav-inner">
          <a href="/" className="logo">🎰 LottoAI</a>
          <div className="nav-links">
            <a href="/results">ผลหวย</a>
            <a href="/stats">สถิติ</a>
            <a href="/login">เข้าสู่ระบบ</a>
            <a href="/register" className="btn-primary">สมัครฟรี</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <h1 className="page-title">💭 ทำนายฝัน</h1>
        <p className="page-subtitle">ใส่สิ่งที่ฝันเห็น ระบบแปลเป็นเลขชุตจากพจนานุกรมฝัน</p>

        <div className="dream-card">
          <h2>🔍 ค้นหาความฝัน</h2>
          <input
            type="text"
            id="dreamInput"
            className="search-input"
            placeholder="พิมพ์สิ่งที่ฝันเห็น เช่น งู, ช้าง, น้ำ, ทอง..."
          />
          <div className="keyword-grid">
            {Object.keys(dreamMap).map(kw => (
              <button key={kw} className="keyword-btn" onClick={() => selectDream(kw)}>
                {kw}
              </button>
            ))}
          </div>

          <div id="resultBox" className="result-box">
            <div className="result-keyword" id="resultKeyword"></div>
            <div className="result-nums" id="resultNums"></div>
          </div>
        </div>

        <div className="info-box">
          <p>💡 <strong>วิธีใช้:</strong> พิมพ์หรือกดคำที่ตรงกับความฝัน ระบบจะแปลเป็นเลขชุด 2 ตัวให้อัตโนมัติ ทำนายฝันเป็นเพียงความเชื่อ ไม่มีหลักฐานทางวิทยาศาสร์ยืนยัน</p>
        </div>
      </div>

      <script dangerouslySetInnerHTML={{__html: `
        var dreamMap = ${JSON.stringify(dreamMap)};
        function handleDreamInput(val) {
          var key = val.trim();
          showResult(key);
        }
        function selectDream(key) {
          document.getElementById('dreamInput').value = key;
          showResult(key);
        }
        function showResult(key) {
          var box = document.getElementById('resultBox');
          var kw = document.getElementById('resultKeyword');
          var nums = document.getElementById('resultNums');
          if (dreamMap[key]) {
            kw.textContent = 'ความฝัน: ' + key;
            nums.innerHTML = dreamMap[key].map(n =>
              '<span class="result-num">' + n + '</span>'
            ).join('');
            box.className = 'result-box show';
          } else if (key.length > 0) {
            // partial match
            var matches = Object.keys(dreamMap).filter(k => k.includes(key));
            if (matches.length > 0) {
              var allNums = [];
              matches.forEach(m => allNums = allNums.concat(dreamMap[m]));
              kw.textContent = 'คำที่ใกล้เคียง: ' + matches.join(', ');
              nums.innerHTML = [...new Set(allNums)].slice(0, 8).map(n =>
                '<span class="result-num">' + n + '</span>'
              ).join('');
              box.className = 'result-box show';
            }
          }
        }
      `}} />
    </div>
    </>
  );
}
