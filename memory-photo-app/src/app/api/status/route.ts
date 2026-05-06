import { NextRequest, NextResponse } from 'next/server';
import { getStatus } from '@/lib/storage';

export async function GET(req: NextRequest) {
  const groupId = req.nextUrl.searchParams.get('groupId');
  if (!groupId) return NextResponse.json({ error: 'missing groupId' }, { status: 400 });
  const status = getStatus(groupId);
  if (!status) return NextResponse.json({ error: 'not found' }, { status: 404 });
  return NextResponse.json(status);
}
