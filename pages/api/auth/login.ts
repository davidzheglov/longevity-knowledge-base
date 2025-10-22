import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/prisma';
import bcrypt from 'bcryptjs';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end();
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Missing fields' });

  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return res.status(401).json({ error: 'Invalid credentials' });

  const jwt = require('jsonwebtoken');
  const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET || 'devsecret', { expiresIn: '7d' });
  res.setHeader('Set-Cookie', `token=${token}; HttpOnly; Path=/; Max-Age=${7 * 24 * 60 * 60}`);
  return res.json({ user: { id: user.id, email: user.email, name: user.name } });
}
