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
    // Only allow messages to be fetched if the chat belongs to the authenticated user.
    const chat = await prisma.chat.findUnique({ where: { id: chatId } });
    if (chat && chat.userId) {
      if (!userId || String(chat.userId) !== String(userId)) return res.status(403).json({ error: 'Forbidden' });
    } else {
      // chat is unowned (shouldn't exist in DB) - deny access
      return res.status(404).json({ error: 'Not found' });
    }
    const messages = await prisma.message.findMany({ where: { chatId }, orderBy: { createdAt: 'asc' } });
    return res.json(messages);
  }

  if (req.method === 'POST') {
    const { role, content, metadata } = req.body;
    // Ensure the chat exists and belongs to the authenticated user
    const chat = await prisma.chat.findUnique({ where: { id: chatId } });
    if (!chat) return res.status(404).json({ error: 'Chat not found' });
    if (!userId || String(chat.userId) !== String(userId)) return res.status(403).json({ error: 'Forbidden' });

    const msg = await prisma.message.create({ data: { chatId, role, content, userId, metadata } as any });
    // touch chat updatedAt
    await prisma.chat.update({ where: { id: chatId }, data: { updatedAt: new Date() } });
    return res.status(201).json(msg);
  }

  return res.status(405).end();
}
