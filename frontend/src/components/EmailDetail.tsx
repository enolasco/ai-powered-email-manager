import React, { useState } from 'react';
import type { Email, EmailSummary, DraftReply } from '../utils/api';
import { useAI } from '../hooks/useAI';
import { emailApi } from '../utils/api';

interface Props {
  email: Email;
  onArchive: (id: string) => void;
  onDelete: (id: string) => void;
}

const PRIORITY_BADGE: Record<string, React.CSSProperties> = {
  High: { background: '#fee2e2', color: '#991b1b' },
  Medium: { background: '#fef3c7', color: '#92400e' },
  Low: { background: '#dcfce7', color: '#166534' },
};

const SENTIMENT_BADGE: Record<string, React.CSSProperties> = {
  Positive: { background: '#dcfce7', color: '#166534' },
  Neutral: { background: '#f3f4f6', color: '#374151' },
  Negative: { background: '#fee2e2', color: '#991b1b' },
  Urgent: { background: '#fef3c7', color: '#92400e' },
};

export default function EmailDetail({ email, onArchive, onDelete }: Props) {
  const { summarize, draftReply, loading, error } = useAI();
  const [summary, setSummary] = useState<EmailSummary | null>(null);
  const [draft, setDraft] = useState<DraftReply | null>(null);
  const [tone, setTone] = useState('professional');
  const [context, setContext] = useState('');
  const [replyContext, setReplyContext] = useState(false);
  const [sendStatus, setSendStatus] = useState<string | null>(null);

  async function handleSummarize() {
    const s = await summarize(email.id);
    if (s) setSummary(s);
  }

  async function handleDraftReply() {
    const d = await draftReply(email.id, tone, context || undefined);
    if (d) setDraft(d);
  }

  async function handleSend() {
    if (!draft) return;
    try {
      await emailApi.sendReply(email.id, draft.draft, draft.tone, context || undefined);
      setSendStatus('Reply sent!');
      setDraft(null);
    } catch {
      setSendStatus('Failed to send reply.');
    }
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.subject}>{email.subject}</h2>
          <p style={styles.meta}>
            From: <strong>{email.sender}</strong> &nbsp;·&nbsp;
            {new Date(email.date).toLocaleString()}
          </p>
          <p style={styles.meta}>To: {email.recipients.join(', ')}</p>
        </div>
        <div style={styles.actions}>
          <button style={styles.btn} onClick={() => onArchive(email.id)}>Archive</button>
          <button style={{ ...styles.btn, ...styles.btnDanger }} onClick={() => onDelete(email.id)}>Delete</button>
        </div>
      </div>

      {/* Body */}
      <div style={styles.body}>
        <pre style={styles.pre}>{email.body}</pre>
      </div>

      {/* AI Actions */}
      <div style={styles.aiSection}>
        <h3 style={styles.aiTitle}>✨ AI Assistant</h3>
        {error && <p style={styles.error}>{error}</p>}

        <div style={styles.buttonRow}>
          <button style={styles.aiBtn} onClick={handleSummarize} disabled={loading}>
            {loading ? 'Processing…' : '📋 Summarize'}
          </button>
          <button style={styles.aiBtn} onClick={() => setReplyContext(!replyContext)} disabled={loading}>
            ✏️ Draft Reply
          </button>
        </div>

        {/* Summary */}
        {summary && (
          <div style={styles.card}>
            <p style={styles.summaryText}>{summary.summary}</p>
            <div style={styles.badges}>
              <span style={{ ...styles.badge, background: '#e0e7ff', color: '#3730a3' }}>
                {summary.category}
              </span>
              <span style={{ ...styles.badge, ...PRIORITY_BADGE[summary.priority] }}>
                {summary.priority} Priority
              </span>
              <span style={{ ...styles.badge, ...SENTIMENT_BADGE[summary.sentiment] }}>
                {summary.sentiment}
              </span>
            </div>
            {summary.action_items.length > 0 && (
              <div>
                <strong>Action items:</strong>
                <ul style={styles.actionList}>
                  {summary.action_items.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Draft reply form */}
        {replyContext && (
          <div style={styles.card}>
            <label style={styles.label}>Tone</label>
            <select
              style={styles.select}
              value={tone}
              onChange={e => setTone(e.target.value)}
            >
              {['professional', 'friendly', 'concise', 'formal', 'casual'].map(t => (
                <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
            <label style={styles.label}>Additional context (optional)</label>
            <textarea
              style={styles.textarea}
              rows={3}
              value={context}
              onChange={e => setContext(e.target.value)}
              placeholder="e.g. I am available Thursday afternoon"
            />
            <button style={styles.aiBtn} onClick={handleDraftReply} disabled={loading}>
              {loading ? 'Drafting…' : 'Generate Draft'}
            </button>
          </div>
        )}

        {/* Draft output */}
        {draft && (
          <div style={styles.card}>
            <label style={styles.label}>Draft ({draft.tone})</label>
            <textarea
              style={styles.textarea}
              rows={8}
              value={draft.draft}
              onChange={e => setDraft({ ...draft, draft: e.target.value })}
            />
            <div style={styles.buttonRow}>
              <button style={{ ...styles.aiBtn, background: '#16a34a', color: '#fff' }} onClick={handleSend} disabled={loading}>
                📤 Send Reply
              </button>
              <button style={styles.aiBtn} onClick={() => setDraft(null)}>Discard</button>
            </div>
          </div>
        )}

        {sendStatus && <p style={styles.sendStatus}>{sendStatus}</p>}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto' },
  header: { padding: '16px 24px', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' },
  subject: { margin: 0, fontSize: '1.1rem', fontWeight: 700 },
  meta: { margin: '4px 0 0', fontSize: '0.82rem', color: '#6b7280' },
  actions: { display: 'flex', gap: 8 },
  btn: { padding: '6px 14px', borderRadius: 6, border: '1px solid #d1d5db', background: '#f9fafb', cursor: 'pointer', fontSize: '0.85rem' },
  btnDanger: { color: '#dc2626', borderColor: '#fca5a5' },
  body: { padding: '16px 24px', flex: 1 },
  pre: { whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontFamily: 'inherit', fontSize: '0.9rem', margin: 0, lineHeight: 1.6 },
  aiSection: { padding: '16px 24px', borderTop: '1px solid #e5e7eb', background: '#f8fafc' },
  aiTitle: { margin: '0 0 12px', fontSize: '1rem', color: '#4f46e5' },
  error: { color: '#dc2626', marginBottom: 8 },
  buttonRow: { display: 'flex', gap: 8, flexWrap: 'wrap' },
  aiBtn: { padding: '7px 16px', borderRadius: 6, border: '1px solid #a5b4fc', background: '#eef2ff', color: '#3730a3', cursor: 'pointer', fontSize: '0.85rem' },
  card: { marginTop: 12, padding: 14, background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' },
  summaryText: { margin: '0 0 10px', lineHeight: 1.5 },
  badges: { display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 },
  badge: { padding: '2px 10px', borderRadius: 12, fontSize: '0.78rem', fontWeight: 600 },
  actionList: { margin: '6px 0 0 16px', padding: 0, fontSize: '0.85rem' },
  label: { display: 'block', fontSize: '0.8rem', color: '#6b7280', marginTop: 8, marginBottom: 4 },
  select: { width: '100%', padding: '6px 8px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: '0.875rem' },
  textarea: { width: '100%', padding: '8px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: '0.875rem', boxSizing: 'border-box', resize: 'vertical' },
  sendStatus: { marginTop: 10, fontWeight: 600, color: '#16a34a' },
};
