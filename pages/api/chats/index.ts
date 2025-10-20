import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/prisma';

function getUserIdFromReq(req: NextApiRequest){
  const cookie = req.headers.cookie || '';
  const match = cookie.match(/token=([^;]+)/);
  if (!match) return null;
  try{ const jwt = require('jsonwebtoken'); const payload = jwt.verify(match[1], process.env.JWT_SECRET || 'devsecret') as any; return payload.id }catch(e){ return null }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const userId = getUserIdFromReq(req);

  if (req.method === 'GET') {
    // Only return persisted chats for authenticated users.
    if (!userId) return res.json([]);
    const chats = await prisma.chat.findMany({ where: { userId }, orderBy: { updatedAt: 'desc' } });
    return res.json(chats);
  }
  if (req.method === 'POST') {
    const { title } = req.body;
    // Visitors cannot create persisted chats. Require authentication to persist chat history.
    if (!userId) return res.status(401).json({ error: 'Authentication required to create chats' });
    const chat = await prisma.chat.create({ data: { userId, title } });
    return res.status(201).json(chat);
  }
  return res.status(405).end();
}
