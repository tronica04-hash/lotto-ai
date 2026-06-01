'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supabase) {
      setError('ระบบยังไม่ได้ตั้งค่า Supabase');
      return;
    }
    setLoading(true);
    setError('');

    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    router.push('/dashboard');
    router.refresh();
  };

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
        <p style={styles.subtitle}>เข้าสู่ระบบ</p>

        <form onSubmit={handleLogin} style={styles.form}>
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
              placeholder="••••••••"
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
            {loading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ'}
          </button>
        </form>

        <p style={styles.footerText}>
          ยังไม่มีบัญชี?{' '}
          <Link href="/register" style={styles.link}>
            สมัครสมาชิก
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
};
