import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/prisma';
import fs from 'fs';

function getUserIdFromReq(req: NextApiRequest){
  const cookie = req.headers.cookie || '';
  const match = cookie.match(/token=([^;]+)/);
  if (!match) return null;
  try{ const jwt = require('jsonwebtoken'); const payload = jwt.verify(match[1], process.env.JWT_SECRET || 'devsecret') as any; return payload.id }catch(e){ return null }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse){
  const userId = getUserIdFromReq(req);
  if (!userId) return res.status(401).json({ error: 'Unauthorized' });

  if (req.method === 'GET'){
    const user = await prisma.user.findUnique({ where: { id: userId } });
    if (!user) return res.status(404).json({ error: 'Not found' });
    return res.json({ user: { id: user.id, email: user.email, name: user.name || null, bio: (user as any).bio || null, avatarUrl: (user as any).avatarUrl || null, education: (user as any).education || null } });
  }

  if (req.method === 'PUT'){
    const { name, bio, education, avatarUrl } = req.body;
    const data: any = {};
    if (name !== undefined) data.name = name;
    if (bio !== undefined) data.bio = bio;
    if (education !== undefined) data.education = education;
    if (avatarUrl !== undefined) data.avatarUrl = avatarUrl;
    const updated = await prisma.user.update({ where: { id: userId }, data });
    return res.json({ user: { id: updated.id, email: updated.email, name: updated.name || null, bio: (updated as any).bio || null, avatarUrl: (updated as any).avatarUrl || null, education: (updated as any).education || null } });
  }

  return res.status(405).end();
}
