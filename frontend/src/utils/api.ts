import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
});

export interface Email {
  id: string;
  thread_id: string;
  subject: string;
  sender: string;
  recipients: string[];
  body: string;
  snippet: string;
  date: string;
  is_read: boolean;
  labels: string[];
}

export interface EmailSummary {
  email_id: string;
  summary: string;
  category: string;
  priority: string;
  sentiment: string;
  action_items: string[];
}

export interface DraftReply {
  email_id: string;
  draft: string;
  tone: string;
}

export const emailApi = {
  list: (params?: { query?: string; label?: string; max_results?: number }) =>
    api.get<{ emails: Email[]; total: number }>('/emails/', { params }),

  get: (id: string) => api.get<Email>(`/emails/${id}`),

  summarize: (id: string) => api.post<EmailSummary>(`/emails/${id}/summarize`),

  classify: (id: string) =>
    api.post<{ category: string; priority: string }>(`/emails/${id}/classify`),

  draftReply: (id: string, tone = 'professional', context?: string) =>
    api.post<DraftReply>(`/emails/${id}/draft-reply`, { email_id: id, tone, context }),

  sendReply: (id: string, draft: string, tone = 'professional', context?: string) =>
    api.post(`/emails/${id}/send-reply`, { email_id: id, draft, tone, context }),

  bulkAction: (email_ids: string[], action: string, label?: string) =>
    api.post('/emails/bulk-action', { email_ids, action, label }),
};

export const authApi = {
  status: () => api.get<{ authenticated: boolean }>('/auth/status'),
  login: () => { window.location.href = `${api.defaults.baseURL}/auth/login`; },
  logout: () => api.get('/auth/logout'),
};

export default api;
