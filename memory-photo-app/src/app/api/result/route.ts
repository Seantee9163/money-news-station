import { NextRequest, NextResponse } from 'next/server';
import { getResults } from '@/lib/storage';

export async function GET(req: NextRequest) {
  const groupId = req.nextUrl.searchParams.get('groupId');
  if (!groupId) return NextResponse.json({ error: 'missing groupId' }, { status: 400 });
  return NextResponse.json({ images: getResults(groupId) });
}
