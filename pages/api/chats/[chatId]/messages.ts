import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/prisma';

function getUserIdFromReq(req: NextApiRequest){
  const cookie = req.headers.cookie || '';
  const match = cookie.match(/token=([^;]+)/);
  if (!match) return null;
  try{ const jwt = require('jsonwebtoken'); const payload = jwt.verify(match[1], process.env.JWT_SECRET || 'devsecret') as any; return payload.id }catch(e){ return null }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const chatId = Number(req.query.chatId);
  if (isNaN(chatId)) return res.status(400).json({ error: 'Invalid chatId' });
  const userId = getUserIdFromReq(req);

  if (req.method === 'GET') {
    const messages = await prisma.message.findMany({ where: { chatId }, orderBy: { createdAt: 'asc' } });
    return res.json(messages);
  }

  if (req.method === 'POST') {
    const { role, content, metadata } = req.body;
    const msg = await prisma.message.create({ data: { chatId, role, content, userId: userId || undefined, metadata } as any });
    // update chat updatedAt
    await prisma.chat.update({ where: { id: chatId }, data: {} });
    return res.status(201).json(msg);
  }

  return res.status(405).end();
}
