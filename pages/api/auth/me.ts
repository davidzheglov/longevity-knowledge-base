import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/prisma';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const cookie = req.headers.cookie || '';
  const match = cookie.match(/token=([^;]+)/);
  if (!match) return res.json({ user: null });
  const token = match[1];
  try {
    const jwt = require('jsonwebtoken');
    const payload = jwt.verify(token, process.env.JWT_SECRET || 'devsecret') as any;
    const user = await prisma.user.findUnique({ where: { id: payload.id } });
    if (!user) return res.json({ user: null });
    return res.json({ user: { id: user.id, email: user.email, name: user.name } });
  } catch (e) {
    return res.json({ user: null });
  }
}
