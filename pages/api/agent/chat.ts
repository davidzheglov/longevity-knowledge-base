import type { NextApiRequest, NextApiResponse } from 'next'

type ChatReq = { message: string; sessionId?: string };

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }
  try {
    const body = (typeof req.body === 'string') ? JSON.parse(req.body) : req.body as ChatReq;
    if (!body?.message || typeof body.message !== 'string') {
      return res.status(400).json({ error: 'message is required' });
    }
  const AGENT_API_URL = (globalThis as any).process?.env?.AGENT_API_URL || 'http://127.0.0.1:8000';
    const r = await fetch(`${AGENT_API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: body.message, session_id: body.sessionId || 'web' })
    });
    if (!r.ok) {
      const txt = await r.text().catch(()=> '');
      return res.status(502).json({ error: 'agent_bad_gateway', detail: txt.slice(0,1000) });
    }
    const data = await r.json();
    return res.status(200).json(data);
  } catch (e: any) {
    return res.status(500).json({ error: 'agent_request_failed', detail: String(e) });
  }
}
