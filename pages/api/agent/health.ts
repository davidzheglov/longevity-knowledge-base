import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET'){
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }
  const AGENT_API_URL = (globalThis as any).process?.env?.AGENT_API_URL || 'http://127.0.0.1:8000';
  try {
    const r = await fetch(`${AGENT_API_URL}/health`, { method: 'GET' });
    if (!r.ok){
      const txt = await r.text().catch(()=> '');
      return res.status(502).json({ status: 'bad_gateway', detail: txt.slice(0,1000) });
    }
    const data = await r.json().catch(()=> ({}));
    return res.status(200).json({ status: 'ok', agent: data });
  } catch (e: any) {
    const isAbort = e?.name === 'AbortError';
    return res.status(isAbort ? 504 : 500).json({ status: isAbort ? 'timeout' : 'error', detail: String(e) });
  }
}
