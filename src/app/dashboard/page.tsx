'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

interface LottoRow {
  draw_date: string; first_prize: string; two_digit: string;
  three_digit_first: any; three_digit_last: any;
  second_prize: any; third_prize: any; nearby_1st: any;
}
interface Analysis {
  total_draws: number; date_range: { from: string; to: string };
  hot_numbers: { digit: string; count: number }[];
  cold_numbers: { digit: string; count: number }[];
  due_numbers: { digit: string; gap: number }[];
  predictions: { number: string; reason: string; confidence: number }[];
}

const DREAM: Record<string,string[]> = {
  'งู':['65','28'],'ช้าง':['42','11'],'ม้า':['33','58'],'วัว':['19','70'],
  'ไก่':['01','46'],'หมา':['52','37'],'แมว':['24','63'],'ปลา':['08','75'],
  'นก':['13','49'],'เสือ':['56','21'],'กระต่าย':['38','67'],'ตุ๊กแก':['44','15'],
  'เต่า':['72','03'],'ควาย':['29','54'],'หมู':['61','16'],'ลิง':['47','82','05'],
  'จระเข้':['35','48'],'นางฟ้า':['09','76'],'ผี':['66','31'],'บ้าน':['40','85'],
  'รถ':['17','53'],'เงิน':['74','22','90'],'ทอง':['88','69'],'น้ำ':['06','39'],
  'ไฟ':['50','41'],'ดิน':['14','71'],'ต้นไม้':['57','26'],'ดอกไม้':['78','07'],
  'ผลไม้':['83','64'],'หมอ':['12','93'],'ครู':['34','77'],'ทหาร':['43','86'],
  'ตำรวจ':['55','20'],'พระ':['02','96'],'วัด':['10','59'],'โรงเรียน':['23','89'],
  'ตลาด':['30','62'],'ป่า':['45','73'],'ภูเขา':['18','91'],'ทะเล':['04','87'],
  'แม่น้ำ':['51','36'],'สะพาน':['27','68'],'รถไฟ':['97','60'],'เครื่องบิน':['98','32'],
  'รถยนต์':['81','95'],'จักรยาน':['00','79'],
};

function safeArr(v: any): string[] { if(!v) return []; if(Array.isArray(v)) return v; try{return JSON.parse(v);}catch{return[];} }
function fmtDate(d:string){const m=['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];const dd=new Date(d);return`${dd.getDate()} ${m[dd.getMonth()]} ${dd.getFullYear()+543}`;}

const analyze=(rows:LottoRow[]):Analysis=>{
  const f2:Record<string,number>={},l2:Record<string,number>={};
  rows.forEach((r,i)=>{if(r.two_digit){const t=String(r.two_digit).padStart(2,'0');f2[t]=(f2[t]||0)+1;if(!(t in l2))l2[t]=i;}});
  const hot=Object.entries(f2).map(([d,c])=>({digit:d,count:c})).sort((a,b)=>b.count-a.count).slice(0,10);
  const cold=Object.entries(f2).map(([d,c])=>({digit:d,count:c})).sort((a,b)=>a.count-b.count).slice(0,10);
  const due=Object.entries(l2).map(([d,g])=>({digit:d,gap:g})).sort((a,b)=>b.gap-a.gap).slice(0,10);
  const pred:Analysis['predictions']=[];
  due.slice(0,3).forEach(n=>pred.push({number:n.digit,reason:`ไม่ออก ${n.gap} งวด`,confidence:Math.min(15+Math.floor(n.gap/10),45)}));
  hot.slice(0,2).forEach(n=>pred.push({number:n.digit,reason:`ออก ${n.count} ครั้ง (ร้อน)`,confidence:Math.min(20+Math.floor(n.count/5),40)}));
  return{total_draws:rows.length,date_range:{from:rows[rows.length-1]?.draw_date||'',to:rows[0]?.draw_date||''},hot_numbers:hot,cold_numbers:cold,due_numbers:due,predictions:pred.slice(0,6)};
};

export default function DashboardPage(){
  const[loading,setLoading]=useState(true);
  const[user,setUser]=useState<any>(null);
  const[analysis,setAnalysis]=useState<Analysis|null>(null);
  const[results,setResults]=useState<LottoRow[]>([]);
  const[tab,setTab]=useState('overview');
  const[err,setErr]=useState('');
  // dream
  const[dreamKey,setDreamKey]=useState('');
  const[dreamRes,setDreamRes]=useState<{key:string;nums:string[]}|null>(null);
  // filter
  const[fY,setFY]=useState('');
  const[fM,setFM]=useState('');
  // check
  const[ckNum,setCkNum]=useState('');
  const[ckRes,setCkRes]=useState<{res:string[]}|null>(null);

  useEffect(()=>{
    if(!supabase){setLoading(false);return;}
    supabase.auth.getUser().then(({data})=>{
      if(!data.user){window.location.href='/login';return;}
      setUser(data.user);
      supabase!.from('lotto_results').select('*').order('draw_date',{ascending:false}).then(({data,error})=>{
        if(error){setErr(error.message);setLoading(false);return;}
        if(!data?.length){setAnalysis({total_draws:0,date_range:{from:'',to:''},hot_numbers:[],cold_numbers:[],due_numbers:[],predictions:[]});setLoading(false);return;}
        setResults(data);setAnalysis(analyze(data));setLoading(false);
      });
    });
  },[]);

  const handleDream=(v:string)=>{const k=v.trim();if(!k){setDreamRes(null);return;}if(DREAM[k]){setDreamRes({key:k,nums:DREAM[k]});return;}const ms=Object.keys(DREAM).filter(x=>x.includes(k));if(ms.length>0){setDreamRes({key:ms.join(', '),nums:[...new Set(ms.flatMap(m=>DREAM[m]))].slice(0,8)});return;}setDreamRes(null);};
  const handleLogout=async()=>{await supabase?.auth.signOut();window.location.href='/';};

  const handleCheck=()=>{
    if(ckNum.length!==6){setCkRes(null);return;}
    const r=results[0];if(!r){setCkRes(null);return;}
    const res:string[]=[];
    if(r.first_prize===ckNum)res.push('🎉 ถูกรางวัลที่ 1 (6,000,000)');
    if(safeArr(r.nearby_1st).includes(ckNum))res.push('🎉 ถูกข้างเคียง (100,000)');
    if(safeArr(r.second_prize).includes(ckNum))res.push('🎉 ถูกรางวัลที่ 2 (200,000)');
    if(safeArr(r.third_prize).includes(ckNum))res.push('🎉 ถูกรางวัลที่ 3 (80,000)');
    if(safeArr(r.three_digit_first).includes(ckNum.substring(0,3)))res.push('🎉 ถูกเลขหน้า 3 (4,000)');
    if(safeArr(r.three_digit_last).includes(ckNum.substring(3,6)))res.push('🎉 ถูกเลขท้าย 3 (4,000)');
    if(r.two_digit===ckNum.substring(4,6))res.push('🎉 ถูกเลขท้าย 2 (2,000)');
    if(!res.length)res.push('❌ ไม่ถูกรางวัล');
    setCkRes({res});
  };

  const filtered=results.filter(r=>{
    if(fY&&!r.draw_date.startsWith(fY))return false;
    if(fM&&r.draw_date.split('-')[1]!==fM.padStart(2,'0'))return false;
    return true;
  });

  if(loading)return <div style={s.page}><div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100vh',color:'#94a3b8'}}>🎰 กำลังโหลด...</div></div>;
  if(err)return <div style={{color:'#f87171',padding:40}}>Error: {err}</div>;

  return(<>
  <style dangerouslySetInnerHTML={{__html:`*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f172a;color:#e2e8f0}
  .h{border-bottom:1px solid rgba(148,163,184,0.15);background:rgba(15,23,42,0.85);backdrop-filter:blur(8px);position:sticky;top:0;z-index:50}
  .hi{max-width:1200px;margin:0 auto;padding:12px 16px;display:flex;align-items:center;justify-content:space-between}
  .lg{font-size:19px;font-weight:bold}
  .hr{display:flex;align-items:center;gap:8px}
  .av{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#9333ea,#ec4899);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;color:#fff}
  .em{color:#64748b;font-size:11px}
  .lo{padding:4px 10px;font-size:11px;color:#94a3b8;background:transparent;border:1px solid #334155;border-radius:4px;cursor:pointer}
  .tb{border-bottom:1px solid rgba(148,163,184,0.1);overflow-x:auto}
  .ti{max-width:1200px;margin:0 auto;display:flex;gap:1px;padding:0 16px}
  .t{padding:11px 14px;font-size:12px;color:#94a3b8;background:transparent;border:none;border-bottom:2px solid transparent;cursor:pointer;white-space:nowrap}
  .ta{color:#c084fc;border-bottom-color:#9333ea;font-weight:600}
  .mn{max-width:1200px;margin:0 auto;padding:20px 16px}
  .sc{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-bottom:22px}
  .c{background:rgba(30,41,59,0.5);border:1px solid rgba(148,163,184,0.1);border-radius:10px;padding:16px}
  .cl{font-size:11px;color:#94a3b8;margin-bottom:3px}
  .cv{font-size:24px;font-weight:bold}
  .cs{font-size:10px;color:#475569;margin-top:2px}
  .nr{display:flex;gap:4px;margin-top:6px;flex-wrap:wrap}
  .hc{padding:3px 8px;background:rgba(239,68,68,0.1);color:#f87171;border-radius:4px;font-weight:bold;font-family:monospace;font-size:13px}
  .dc{padding:3px 8px;background:rgba(245,158,11,0.1);color:#fbbf24;border-radius:4px;font-weight:bold;font-family:monospace;font-size:13px}
  .pc{padding:3px 8px;background:rgba(59,130,246,0.1);color:#60a5fa;border-radius:4px;font-weight:bold;font-family:monospace;font-size:13px}
  .aic{background:rgba(30,41,59,0.5);border:1px solid rgba(148,163,184,0.1);border-radius:10px;padding:18px;margin-bottom:18px}
  .pr{display:flex;align-items:center;gap:10px;padding:10px;background:rgba(51,65,85,0.3);border-radius:7px;margin-bottom:6px}
  .pn{font-size:20px;font-weight:bold;font-family:monospace;color:#c084fc;min-width:40px;text-align:center}
  .fg{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}
  .tr{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(148,163,184,0.06);font-size:12px}
  .tn{font-family:monospace;font-weight:bold}
  .tc{color:#64748b;font-size:11px}
  .drc{background:linear-gradient(135deg,rgba(147,51,234,0.08),rgba(59,130,246,0.08));border:1px solid rgba(148,163,184,0.12);border-radius:12px;padding:20px}
  .di{width:100%;padding:10px 14px;background:#1e293b;border:2px solid #334155;border-radius:7px;color:#fff;font-size:14px;margin-bottom:10px}
  .di:focus{outline:none;border-color:#9333ea}
  .kg{display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:4px;margin-bottom:10px}
  .kb{padding:6px 6px;background:rgba(30,41,59,0.5);border:1px solid rgba(148,163,184,0.1);border-radius:4px;color:#cbd5e1;cursor:pointer;font-size:12px;text-align:center}
  .kb:hover{background:#9333ea;color:#fff}
  .drv{background:rgba(30,41,59,0.6);border:1px solid rgba(168,85,247,0.2);border-radius:8px;padding:12px}
  .dk{color:#c084fc;font-weight:bold;margin-bottom:5px;font-size:13px}
  .dn{display:flex;gap:5px;flex-wrap:wrap}
  .dnc{background:#9333ea;color:#fff;padding:5px 10px;border-radius:6px;font-family:monospace;font-size:16px;font-weight:bold}
  .fr{display:flex;gap:5px;margin-bottom:10px;align-items:center;flex-wrap:wrap}
  .sel{background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:6px 10px;border-radius:5px;font-size:12px}
  .rt{width:100%;font-size:12px;border-collapse:collapse}
  .rt th{text-align:left;padding:7px 8px;color:#475569;border-bottom:1px solid rgba(148,163,184,0.1);font-size:11px}
  .rt td{padding:7px 8px;border-bottom:1px solid rgba(148,163,184,0.04);font-family:monospace;font-size:12px}
  .cii{width:44px;height:44px;background:#1e293b;border:2px solid #334155;border-radius:7px;color:#fff;font-size:20px;text-align:center;font-family:monospace;font-weight:bold}
  .cii:focus{outline:none;border-color:#9333ea}
  .cb{background:#9333ea;color:#fff;border:none;padding:9px 16px;border-radius:7px;font-weight:600;cursor:pointer;font-size:13px}
  .crl{padding:3px 0;font-size:13px}
  @media(max-width:640px){.ti{overflow-x:auto}}
  `}}/>
    <div>
      {/* Header */}
      <header className="h"><div className="hi">
        <div className="lg">🎰 LottoAI</div>
        <div className="hr">
          <div className="av">{user?.email?.charAt(0).toUpperCase()}</div>
          <span className="em">{user?.email}</span>
          <button onClick={handleLogout} className="lo">ออก</button>
        </div>
      </div></header>

      {/* Tabs */}
      <div className="tb"><div className="ti">
        {['overview','stats','ai','dream','results','check'].map(t=>(
          <button key={t} onClick={()=>setTab(t)} className={tab===t?'t ta':'t'}>
            {t==='overview'&&'📊 ภาพรวม'}{t==='stats'&&'🔥 สถิติ'}{t==='ai'&&'🤖 AI'}{t==='dream'&&'💭 ทำนายฝัน'}{t==='results'&&'📋 ผลหวย'}{t==='check'&&'🔍 เช็คเลข'}
          </button>
        ))}
      </div></div>

      <main className="mn">
        {/* OVERVIEW */}
        {tab==='overview' && analysis && analysis.total_draws>0 && <>
          <div className="sc">
            <div className="c"><div className="cl">จำนวนงวด</div><div className="cv">{analysis.total_draws}</div><div className="cs">{analysis.date_range.from} → {analysis.date_range.to}</div></div>
            <div className="c"><div className="cl">🔥 เลขร้อน</div><div className="nr">{analysis.hot_numbers.slice(0,5).map((n,i)=><span key={i} className="hc">{n.digit}</span>)}</div></div>
            <div className="c"><div className="cl">❄️ เลขเย็น</div><div className="nr">{analysis.cold_numbers.slice(0,5).map((n,i)=><span key={i} className="pc">{n.digit}</span>)}</div></div>
            <div className="c"><div className="cl">⏰ เลข Due</div><div className="nr">{analysis.due_numbers.slice(0,5).map((n,i)=><span key={i} className="dc">{n.digit}</span>)}</div></div>
          </div>
          <div className="aic"><h2 style={{fontWeight:'bold',marginBottom:10}}>🤖 AI ทำนาย</h2>
            {analysis.predictions.map((p,i)=><div key={i} className="pr"><span className="pn">{p.number}</span><span style={{flex:1,color:'#cbd5e1',fontSize:13}}>{p.reason}</span><span style={{color:'#fbbf24',fontWeight:'bold'}}>{p.confidence}%</span></div>)}
          </div>
          <div className="fg">
            <div className="c"><h3 style={{color:'#f87171',fontWeight:'bold',marginBottom:8,fontSize:13}}>🔥 เลขร้อน</h3>{analysis.hot_numbers.map((n,i)=><div key={i} className="tr"><span className="tn">{n.digit}</span><span className="tc">{n.count} ครั้ง</span></div>)}</div>
            <div className="c"><h3 style={{color:'#60a5fa',fontWeight:'bold',marginBottom:8,fontSize:13}}>❄️ เลขเย็น</h3>{analysis.cold_numbers.map((n,i)=><div key={i} className="tr"><span className="tn">{n.digit}</span><span className="tc">{n.count} ครั้ง</span></div>)}</div>
            <div className="c"><h3 style={{color:'#fbbf24',fontWeight:'bold',marginBottom:8,fontSize:13}}>⏰ Due</h3>{analysis.due_numbers.map((n,i)=><div key={i} className="tr"><span className="tn">{n.digit}</span><span className="tc">{n.gap} งวด</span></div>)}</div>
          </div>
        </>}

        {/* STATS */}
        {tab==='stats' && analysis && <>
          <div className="fg">
            <div className="c"><h3 style={{color:'#f87171',fontWeight:'bold',marginBottom:10}}>🔥 เลขร้อน 2 ตัว</h3>
              {analysis.hot_numbers.map((n,i)=><div key={i} style={{display:'flex',alignItems:'center',gap:6,padding:'4px 0'}}><span style={{fontFamily:'monospace',fontWeight:'bold',minWidth:30,fontSize:13}}>{n.digit}</span><div style={{flex:1,height:3,background:'#1e293b',borderRadius:2}}><div style={{height:'100%',borderRadius:2,background:'#ef4444',width:`${Math.min(100,n.count*10)}%`}}/></div><span style={{color:'#64748b',fontSize:10,minWidth:40,textAlign:'right'}}>{n.count}</span></div>)}
            </div>
            <div className="c"><h3 style={{color:'#60a5fa',fontWeight:'bold',marginBottom:10}}>❄️ เลขเย็น</h3>
              {analysis.cold_numbers.map((n,i)=><div key={i} style={{display:'flex',alignItems:'center',gap:6,padding:'4px 0'}}><span style={{fontFamily:'monospace',fontWeight:'bold',minWidth:30,fontSize:13}}>{n.digit}</span><div style={{flex:1,height:3,background:'#1e293b',borderRadius:2}}><div style={{height:'100%',borderRadius:2,background:'#3b82f6',width:`${Math.min(100,n.count*20)}%`}}/></div><span style={{color:'#64748b',fontSize:10,minWidth:40,textAlign:'right'}}>{n.count}</span></div>)}
            </div>
            <div className="c"><h3 style={{color:'#fbbf24',fontWeight:'bold',marginBottom:10}}>⏰ เลขนาย</h3>
              {analysis.due_numbers.map((n,i)=><div key={i} style={{display:'flex',alignItems:'center',gap:6,padding:'4px 0'}}><span style={{fontFamily:'monospace',fontWeight:'bold',minWidth:30,fontSize:13}}>{n.digit}</span><div style={{flex:1,height:3,background:'#1e293b',borderRadius:2}}><div style={{height:'100%',borderRadius:2,background:'#f59e0b',width:`${Math.min(100,n.gap*2)}%`}}/></div><span style={{color:'#64748b',fontSize:10,minWidth:40,textAlign:'right'}}>{n.gap}</span></div>)}
            </div>
          </div>
        </>}

        {/* AI */}
        {tab==='ai' && analysis && <div className="aic">
          <h2 style={{fontWeight:'bold',marginBottom:4}}>🤖 AI ทำนายเลข</h2>
          <p style={{color:'#475569',fontSize:11,marginBottom:14}}>คำนวณจาก {analysis.total_draws} งวด — frequency + due analysis</p>
          {analysis.predictions.map((p,i)=><div key={i} className="pr"><span className="pn">{p.number}</span><div style={{flex:1}}><div style={{color:'#cbd5e1',fontSize:13}}>{p.reason}</div></div><div style={{textAlign:'right'}}><div style={{color:'#fbbf24',fontWeight:'bold',fontSize:15}}>{p.confidence}%</div><div style={{color:'#475569',fontSize:9}}>มั่นใจ</div></div></div>)}
          <p style={{color:'#475569',fontSize:10,marginTop:10}}>⚠️ เป็นเพียงสถิติ ไม่รับประกันผล</p>
        </div>}

        {/* DREAM */}
        {tab==='dream' && <div style={{maxWidth:550}}>
          <div className="drc">
            <h2 style={{fontWeight:'bold',marginBottom:12}}>💭 ทำนายฝัน</h2>
            <input type="text" value={dreamKey} onChange={e=>{setDreamKey(e.target.value);handleDream(e.target.value);}} placeholder="พิมพ์ความฝัน เช่น งู, น้ำ, ทอง..." className="di"/>
            <div className="kg">{Object.keys(DREAM).map(k=><button key={k} onClick={()=>{setDreamKey(k);handleDream(k);}} className="kb">{k}</button>)}</div>
            {dreamRes && <div className="drv"><div className="dk">ฝัน: {dreamRes.key}</div><div className="dn">{dreamRes.nums.map(n=><span key={n} className="dnc">{n}</span>)}</div></div>}
          </div>
          <p style={{color:'#475569',fontSize:10,textAlign:'center',marginTop:8}}>ทำนายฝันเป็นเพียงความเชื่อ</p>
        </div>}

        {/* RESULTS */}
        {tab==='results' && <>
          <div className="fr">
            <select value={fY} onChange={e=>setFY(e.target.value)} className="sel"><option value="">ทุกปี</option>{[...new Set(results.map(r=>r.draw_date.split('-')[0]))].sort().reverse().map(y=><option key={y} value={y}>{+y+543}</option>)}</select>
            <select value={fM} onChange={e=>setFM(e.target.value)} className="sel"><option value="">ทุกเดือน</option>{[['1','ม.ค.'],['2','ก.พ.'],['3','มี.ค.'],['4','เม.ย.'],['5','พ.ค.'],['6','มิ.ย.'],['7','ก.ค.'],['8','ส.ค.'],['9','ก.ย.'],['10','ต.ค.'],['11','พ.ย.'],['12','ธ.ค.']].map(([v,l])=><option key={v} value={v}>{l}</option>)}</select>
            <span style={{color:'#475569',fontSize:11,alignSelf:'center'}}>{filtered.length} งวด</span>
          </div>
          <div style={{overflowX:'auto'}}><table className="rt"><thead><tr><th>งวด</th><th>รางวัล 1</th><th>หน้า 3</th><th>ท้าย 3</th><th>ท้าย 2</th><th>ข้างเคียง</th></tr></thead><tbody>
            {filtered.map(r=><tr key={r.draw_date}><td>{fmtDate(r.draw_date)}</td><td style={{color:'#fbbf24',fontWeight:'bold'}}>{r.first_prize||'—'}</td><td>{safeArr(r.three_digit_first).join(', ')||'—'}</td><td>{safeArr(r.three_digit_last).join(', ')||'—'}</td><td style={{color:'#c084fc',fontWeight:'bold'}}>{r.two_digit||'—'}</td><td style={{fontSize:11}}>{safeArr(r.nearby_1st).join(', ')||'—'}</td></tr>)}
          </tbody></table></div>
        </>}

        {/* CHECK */}
        {tab==='check' && <div style={{maxWidth:500}}>
          <div className="drc">
            <h2 style={{fontWeight:'bold',marginBottom:12}}>🔍 เช็คเลขของฉัน</h2>
            <p style={{color:'#64748b',fontSize:12,marginBottom:12}}>กรอกเลข 6 หลัก ระบบเช็คกับผลรางวัลงวดล่าสุด ({results[0]&&fmtDate(results[0].draw_date)})</p>
            <div style={{display:'flex',gap:6,marginBottom:12}}>
              {[0,1,2,3,4,5].map(i=>(
                <input key={i} type="text" maxLength={1} value={ckNum[i]||''} onChange={e=>{
                  const v=e.target.value.replace(/\D/g,'');
                  const n=ckNum.split('');n[i]=v;setCkNum(n.join(''));
                  if(v&&i<5){const nx=e.target.nextElementSibling as HTMLInputElement;nx?.focus();}
                  if(ckNum.length>=5)handleCheck();
                }} className="cii"/>
              ))}
            </div>
            <button onClick={handleCheck} className="cb">เช็คเลข</button>
            {ckRes && <div style={{marginTop:12,background:'rgba(30,41,59,0.6)',border:'1px solid rgba(148,163,184,0.12)',borderRadius:8,padding:14}}>
              {ckRes.res.map((r,i)=><div key={i} className="crl">{r}</div>)}
            </div>}
          </div>
        </div>}
      </main>
    </div>
  </>);
}

const s: Record<string, React.CSSProperties> = {
  page: { minHeight:'100vh', background:'#0f172a', color:'#e2e8f0' },
};
