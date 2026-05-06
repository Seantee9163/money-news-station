import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import { createGroup, mockProcess } from '@/lib/storage';

export async function POST(req: Request) {
  const form = await req.formData();
  const photos = form.getAll('photos') as File[];

  if (photos.length < 1 || photos.length > 3) {
    return NextResponse.json({ error: '需要 1 到 3 张照片' }, { status: 400 });
  }

  const groupId = uuidv4();
  await createGroup(groupId, photos);
  mockProcess(groupId);

  return NextResponse.json({ groupId });
}
