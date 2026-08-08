import React from 'react';
import { authApi } from '../utils/api';

export default function LoginPage() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>📧 AI Email Manager</h1>
        <p style={styles.subtitle}>
          Manage your inbox intelligently with AI-powered summaries,
          classifications, and automated reply drafts.
        </p>
        <ul style={styles.features}>
          <li>✅ Auto-classify & prioritize emails</li>
          <li>✅ AI-generated summaries & action items</li>
          <li>✅ Draft replies in your preferred tone</li>
          <li>✅ Bulk actions to keep your inbox clean</li>
        </ul>
        <button style={styles.btn} onClick={() => authApi.login()}>
          Sign in with Google
        </button>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #1e1b4b 0%, #4f46e5 100%)',
    fontFamily: 'system-ui, sans-serif',
  },
  card: {
    background: '#fff',
    borderRadius: 16,
    padding: '48px 40px',
    maxWidth: 440,
    width: '100%',
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
    textAlign: 'center',
  },
  title: { margin: '0 0 12px', fontSize: '1.75rem', fontWeight: 800, color: '#1e1b4b' },
  subtitle: { color: '#6b7280', lineHeight: 1.6, margin: '0 0 24px' },
  features: { textAlign: 'left', listStyle: 'none', padding: 0, margin: '0 0 32px', lineHeight: 2, color: '#374151' },
  btn: {
    width: '100%',
    padding: '14px 0',
    borderRadius: 8,
    border: 'none',
    background: '#4f46e5',
    color: '#fff',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
  },
};
