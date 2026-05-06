import { NextRequest, NextResponse } from 'next/server';
import { getResultFile } from '@/lib/storage';

export async function GET(req: NextRequest, { params }: { params: { groupId: string } }) {
  const file = req.nextUrl.searchParams.get('file');
  if (!file) return new NextResponse('missing file', { status: 400 });
  const svg = await getResultFile(params.groupId, file);
  const download = req.nextUrl.searchParams.get('download');
  return new NextResponse(svg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      ...(download ? { 'Content-Disposition': `attachment; filename=${file}` } : {}),
    },
  });
}
