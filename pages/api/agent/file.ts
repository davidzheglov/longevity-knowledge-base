import type { NextApiRequest, NextApiResponse } from 'next'

// Proxy a single artifact file from the agent's /outputs path to the browser.
// Accepts query `u` which must point to `${AGENT_API_URL}/outputs/...`.

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET'){
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }
  const u = String(req.query.u || '');
  if (!u){
    return res.status(400).json({ error: 'missing_param', detail: 'u is required' });
  }
  const AGENT_API_URL = (globalThis as any).process?.env?.AGENT_API_URL || 'http://127.0.0.1:8000';
  try{
    const agentBase = new URL(AGENT_API_URL);
    const target = new URL(u);
    const sameHost = (target.host === agentBase.host);
    const isOutputs = target.pathname.startsWith('/outputs/');
    if (!sameHost || !isOutputs){
      return res.status(400).json({ error: 'invalid_url', detail: 'URL must point to agent outputs' });
    }

    const r = await fetch(target.toString());
    if (!r.ok){
      const txt = await r.text().catch(()=> '');
      return res.status(r.status).send(txt);
    }
    // Pass through content-type and length if present
    const ct = r.headers.get('content-type') || 'application/octet-stream';
    const cl = r.headers.get('content-length');
    if (cl) res.setHeader('Content-Length', cl);
    res.setHeader('Content-Type', ct);
    const buf = Buffer.from(await r.arrayBuffer());
    return res.status(200).send(buf);
  }catch(e:any){
    return res.status(500).json({ error: 'proxy_failed', detail: String(e) });
  }
}
