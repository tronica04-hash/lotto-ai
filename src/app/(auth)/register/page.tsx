'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supabase) {
      setError('ระบบยังไม่ได้ตั้งค่า Supabase');
      return;
    }
    setLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('รหัสผ่านไม่ตรงกัน');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร');
      setLoading(false);
      return;
    }

    const { error } = await supabase.auth.signUp({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setLoading(false);
  };

  if (success) {
    return (
      <>
      <style dangerouslySetInnerHTML={{__html: `
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
      `}} />
      <div style={styles.page}>
        <div style={styles.card}>
          <div style={{textAlign:'center'}}>
            <div style={{fontSize:64,marginBottom:16}}>✅</div>
            <h1 style={styles.successTitle}>สมัครสำเร็จ!</h1>
            <p style={styles.successText}>กรุณายืนยันอีเมลของคุณก่อนเข้าสู่ระบบ</p>
            <Link href="/login" style={styles.successBtn}>
              ไปหน้าเข้าสู่ระบบ
            </Link>
          </div>
        </div>
      </div>
      </>
    );
  }

  return (
    <>
    <style dangerouslySetInnerHTML={{__html: `
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    `}} />
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🎰</span>
          LottoAI
        </div>
        <p style={styles.subtitle}>สมัครสมาชิก</p>

        <form onSubmit={handleRegister} style={styles.form}>
          <div>
            <label style={styles.label}>อีเมล</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              placeholder="your@email.com"
              required
            />
          </div>

          <div>
            <label style={styles.label}>รหัสผ่าน</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              placeholder="อย่างน้อย 6 ตัวอักษร"
              required
            />
          </div>

          <div>
            <label style={styles.label}>ยืนยันรหัสผ่าน</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={styles.input}
              placeholder="กรอกรหัสผ่านอีกครั้ง"
              required
            />
          </div>

          {error && (
            <div style={styles.errorBox}>
              <span style={{marginRight:6}}>⚠️</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={loading ? {...styles.submitBtn, ...styles.submitBtnDisabled} : styles.submitBtn}
          >
            {loading ? 'กำลังสมัคร...' : 'สมัครสมาชิก'}
          </button>
        </form>

        <p style={styles.footerText}>
          มีบัญชีอยู่แล้ว?{' '}
          <Link href="/login" style={styles.link}>
            เข้าสู่ระบบ
          </Link>
        </p>
      </div>
    </div>
    </>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0f172a 0%, #581c87 50%, #0f172a 100%)',
    padding: 16,
  },
  card: {
    background: 'rgba(30,41,59,0.7)',
    border: '1px solid rgba(148,163,184,0.2)',
    borderRadius: 24,
    padding: 40,
    width: '100%',
    maxWidth: 420,
    backdropFilter: 'blur(12px)',
  },
  logo: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center' as const,
    marginBottom: 8,
    background: 'linear-gradient(90deg, #c084fc, #f472b6)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  logoIcon: {
    WebkitTextFillColor: 'initial',
  },
  subtitle: {
    color: '#94a3b8',
    textAlign: 'center' as const,
    marginBottom: 32,
    fontSize: 16,
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 16,
  },
  label: {
    display: 'block',
    color: '#cbd5e1',
    fontSize: 14,
    marginBottom: 6,
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    background: 'rgba(51,65,85,0.5)',
    border: '1px solid rgba(148,163,184,0.3)',
    borderRadius: 10,
    color: '#fff',
    fontSize: 16,
    outline: 'none',
    boxSizing: 'border-box' as const,
  },
  errorBox: {
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 8,
    padding: '10px 14px',
    color: '#f87171',
    fontSize: 14,
    display: 'flex',
    alignItems: 'center',
  },
  submitBtn: {
    width: '100%',
    padding: 14,
    background: 'linear-gradient(135deg, #9333ea, #c026d3)',
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
    marginTop: 8,
  },
  submitBtnDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  footerText: {
    color: '#94a3b8',
    textAlign: 'center' as const,
    marginTop: 24,
    fontSize: 14,
  },
  link: {
    color: '#c084fc',
    textDecoration: 'none',
    fontWeight: 600,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#e2e8f0',
    marginBottom: 8,
  },
  successText: {
    color: '#94a3b8',
    marginBottom: 24,
    fontSize: 16,
  },
  successBtn: {
    display: 'inline-block',
    padding: '12px 24px',
    background: 'linear-gradient(135deg, #9333ea, #c026d3)',
    color: '#fff',
    fontWeight: 'bold',
    borderRadius: 10,
    textDecoration: 'none',
    fontSize: 16,
  },
};
