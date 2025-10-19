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
    const where = userId ? { where: { userId } } : {} as any;
    const chats = await prisma.chat.findMany({ ...(where as any), orderBy: { updatedAt: 'desc' } });
    return res.json(chats);
  }
  if (req.method === 'POST') {
    const { title } = req.body;
    const chat = await prisma.chat.create({ data: { userId: userId || undefined, title } });
    return res.status(201).json(chat);
  }
  return res.status(405).end();
}
