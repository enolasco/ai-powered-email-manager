import { useState, useEffect, useCallback } from 'react';
import type { Email } from '../utils/api';
import { emailApi } from '../utils/api';

export function useEmails(query?: string, label?: string) {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEmails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await emailApi.list({ query, label, max_results: 30 });
      setEmails(res.data.emails);
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Failed to load emails');
    } finally {
      setLoading(false);
    }
  }, [query, label]);

  useEffect(() => { fetchEmails(); }, [fetchEmails]);

  return { emails, loading, error, refetch: fetchEmails };
}

export function useEmail(id: string | null) {
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    emailApi.get(id)
      .then(res => setEmail(res.data))
      .catch(e => setError(e.response?.data?.detail ?? 'Failed to load email'))
      .finally(() => setLoading(false));
  }, [id]);

  return { email, loading, error };
}
