import React from 'react';
import type { Email } from '../utils/api';

interface Props {
  emails: Email[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}


export default function EmailList({ emails, selectedId, onSelect }: Props) {
  if (emails.length === 0) {
    return (
      <div style={styles.empty}>
        <p>No emails found.</p>
      </div>
    );
  }

  return (
    <ul style={styles.list}>
      {emails.map(email => (
        <li
          key={email.id}
          style={{
            ...styles.item,
            background: email.id === selectedId ? '#e0e7ff' : email.is_read ? '#fff' : '#f0f4ff',
            fontWeight: email.is_read ? 'normal' : 'bold',
          }}
          onClick={() => onSelect(email.id)}
        >
          <div style={styles.sender}>{email.sender}</div>
          <div style={styles.subject}>{email.subject}</div>
          <div style={styles.snippet}>{email.snippet}</div>
          <div style={styles.date}>{new Date(email.date).toLocaleDateString()}</div>
        </li>
      ))}
    </ul>
  );
}

const styles: Record<string, React.CSSProperties> = {
  list: { listStyle: 'none', margin: 0, padding: 0, overflowY: 'auto', height: '100%' },
  item: {
    padding: '12px 16px',
    cursor: 'pointer',
    borderBottom: '1px solid #e5e7eb',
    transition: 'background 0.15s',
  },
  sender: { fontSize: '0.8rem', color: '#6b7280' },
  subject: { fontSize: '0.95rem', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  snippet: { fontSize: '0.8rem', color: '#9ca3af', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  date: { fontSize: '0.75rem', color: '#9ca3af', marginTop: 4, textAlign: 'right' },
  empty: { padding: 32, textAlign: 'center', color: '#9ca3af' },
};
