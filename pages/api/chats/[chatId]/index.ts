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

  if (req.method === 'DELETE') {
    // Ensure the chat belongs to the authenticated user
    const chat = await prisma.chat.findUnique({ where: { id: chatId } });
    if (!chat) return res.status(404).json({ error: 'Not found' });
    if (!userId || String(chat.userId) !== String(userId)) return res.status(403).json({ error: 'Forbidden' });
    // delete messages first via cascade in DB if configured; here do explicit deletion for safety
    await prisma.message.deleteMany({ where: { chatId } });
    await prisma.chat.delete({ where: { id: chatId } });
    return res.status(204).end();
  }

  if (req.method === 'PATCH') {
    const { title } = (typeof req.body === 'string' ? JSON.parse(req.body) : req.body) || {};
    if (typeof title !== 'string' || !title.trim()) return res.status(400).json({ error: 'title is required' });
    const chat = await prisma.chat.findUnique({ where: { id: chatId } });
    if (!chat) return res.status(404).json({ error: 'Not found' });
    if (!userId || String(chat.userId) !== String(userId)) return res.status(403).json({ error: 'Forbidden' });
    const updated = await prisma.chat.update({ where: { id: chatId }, data: { title } });
    return res.status(200).json(updated);
  }

  return res.status(405).end();
}
