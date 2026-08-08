import React, { useState } from 'react';
import { useEmails, useEmail } from '../hooks/useEmails';
import { emailApi } from '../utils/api';
import EmailList from '../components/EmailList';
import EmailDetail from '../components/EmailDetail';

const LABELS = ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH'];

export default function InboxPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [activeLabel, setActiveLabel] = useState('INBOX');

  const { emails, loading: listLoading, error: listError, refetch } = useEmails(query, activeLabel);
  const { email: selectedEmail, loading: emailLoading } = useEmail(selectedId);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setQuery(searchInput);
  }

  async function handleArchive(id: string) {
    await emailApi.bulkAction([id], 'archive');
    setSelectedId(null);
    refetch();
  }

  async function handleDelete(id: string) {
    await emailApi.bulkAction([id], 'delete');
    setSelectedId(null);
    refetch();
  }

  return (
    <div style={styles.layout}>
      {/* Sidebar */}
      <aside style={styles.sidebar}>
        <div style={styles.logo}>📧 AI Email</div>
        <nav>
          {LABELS.map(lbl => (
            <button
              key={lbl}
              style={{
                ...styles.navBtn,
                background: lbl === activeLabel ? '#e0e7ff' : 'transparent',
                color: lbl === activeLabel ? '#3730a3' : '#374151',
                fontWeight: lbl === activeLabel ? 700 : 'normal',
              }}
              onClick={() => { setActiveLabel(lbl); setSelectedId(null); }}
            >
              {lbl.charAt(0) + lbl.slice(1).toLowerCase()}
            </button>
          ))}
        </nav>
      </aside>

      {/* Email list pane */}
      <section style={styles.listPane}>
        <form onSubmit={handleSearch} style={styles.searchBar}>
          <input
            style={styles.searchInput}
            value={searchInput}
            onChange={e => setSearchInput(e.target.value)}
            placeholder="Search emails…"
          />
          <button style={styles.searchBtn} type="submit">Search</button>
        </form>

        {listLoading && <p style={styles.info}>Loading…</p>}
        {listError && <p style={styles.error}>{listError}</p>}
        {!listLoading && (
          <EmailList
            emails={emails}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        )}
      </section>

      {/* Email detail pane */}
      <main style={styles.detailPane}>
        {emailLoading && <p style={styles.info}>Loading email…</p>}
        {!emailLoading && selectedEmail && (
          <EmailDetail
            email={selectedEmail}
            onArchive={handleArchive}
            onDelete={handleDelete}
          />
        )}
        {!selectedEmail && !emailLoading && (
          <div style={styles.placeholder}>
            <p>✨ Select an email to read it and use AI features</p>
          </div>
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  layout: { display: 'flex', height: '100vh', fontFamily: 'system-ui, sans-serif', background: '#f9fafb' },
  sidebar: { width: 200, background: '#1e1b4b', color: '#fff', display: 'flex', flexDirection: 'column', padding: '16px 0' },
  logo: { padding: '8px 20px 20px', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.5px' },
  navBtn: { width: '100%', textAlign: 'left', padding: '10px 20px', border: 'none', cursor: 'pointer', fontSize: '0.9rem', borderRadius: 0 },
  listPane: { width: 320, borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', background: '#fff' },
  searchBar: { display: 'flex', padding: 12, gap: 8, borderBottom: '1px solid #e5e7eb' },
  searchInput: { flex: 1, padding: '7px 10px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: '0.875rem' },
  searchBtn: { padding: '7px 14px', borderRadius: 6, border: 'none', background: '#4f46e5', color: '#fff', cursor: 'pointer', fontSize: '0.875rem' },
  detailPane: { flex: 1, background: '#fff', overflow: 'hidden' },
  placeholder: { height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#9ca3af' },
  info: { padding: 16, color: '#6b7280', textAlign: 'center' },
  error: { padding: 16, color: '#dc2626', textAlign: 'center' },
};
