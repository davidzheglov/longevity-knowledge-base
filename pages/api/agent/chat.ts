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
    const timeoutMs = Number((globalThis as any).process?.env?.NEXT_AGENT_TIMEOUT_MS || 120000);
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), Math.max(1000, timeoutMs));

    // Minimal server-side logging for diagnosis
    console.log('[api/agent/chat] → forwarding to agent', {
      sessionId: body.sessionId || 'web',
      len: body.message.length,
      url: `${AGENT_API_URL}/chat`,
      timeoutMs
    });

    const r = await fetch(`${AGENT_API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: body.message, session_id: body.sessionId || 'web' }),
      signal: controller.signal
    }).finally(() => clearTimeout(t));
    if (!r.ok) {
      const txt = await r.text().catch(()=> '');
      console.warn('[api/agent/chat] ← agent non-OK', r.status, txt.slice(0,200));
      return res.status(502).json({ error: 'agent_bad_gateway', detail: txt.slice(0,1000) });
    }
    const data = await r.json();
    // Rewrite artifact URLs to go through our web proxy so the browser doesn't need to reach `agent` directly
    try{
      const AGENT_API_URL_N = new URL(`${AGENT_API_URL}`);
      if (Array.isArray(data?.artifacts)){
        data.artifacts = data.artifacts.map((a:any)=>{
          const out = { ...(a||{}) };
          const u = String(a?.url || '');
          try{
            const parsed = new URL(u);
            const isAgent = (parsed.host === AGENT_API_URL_N.host);
            const isOutputs = parsed.pathname.startsWith('/outputs/');
            if (isAgent && isOutputs){
              out.url = `/api/agent/file?u=${encodeURIComponent(u)}`;
            }
          }catch(e){/* ignore bad URL */}
          return out;
        });
      }
    }catch(e){/* ignore rewrite errors */}
    console.log('[api/agent/chat] ← agent OK', {
      hasOutput: typeof data?.output === 'string',
      artifacts: Array.isArray(data?.artifacts) ? data.artifacts.length : 0
    });
    return res.status(200).json(data);
  } catch (e: any) {
    const isAbort = e?.name === 'AbortError';
    console.error('[api/agent/chat] error', isAbort ? 'timeout' : e);
    return res.status(isAbort ? 504 : 500).json({ error: isAbort ? 'agent_timeout' : 'agent_request_failed', detail: String(e) });
  }
}
