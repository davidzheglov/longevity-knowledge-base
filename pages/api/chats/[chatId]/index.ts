import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/prisma';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const chatId = Number(req.query.chatId);
  if (isNaN(chatId)) return res.status(400).json({ error: 'Invalid chatId' });

  if (req.method === 'DELETE') {
    // delete messages first via cascade in DB if configured; here do explicit deletion for safety
    await prisma.message.deleteMany({ where: { chatId } });
    await prisma.chat.delete({ where: { id: chatId } });
    return res.status(204).end();
  }

  return res.status(405).end();
}
