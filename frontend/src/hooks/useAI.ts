import { useState } from 'react';
import type { EmailSummary, DraftReply } from '../utils/api';
import { emailApi } from '../utils/api';

export function useAI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function summarize(emailId: string): Promise<EmailSummary | null> {
    setLoading(true);
    setError(null);
    try {
      const res = await emailApi.summarize(emailId);
      return res.data;
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Summarization failed');
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function draftReply(emailId: string, tone: string, context?: string): Promise<DraftReply | null> {
    setLoading(true);
    setError(null);
    try {
      const res = await emailApi.draftReply(emailId, tone, context);
      return res.data;
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Draft reply failed');
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function classify(emailId: string): Promise<{ category: string; priority: string } | null> {
    setLoading(true);
    setError(null);
    try {
      const res = await emailApi.classify(emailId);
      return res.data;
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Classification failed');
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { summarize, draftReply, classify, loading, error };
}
