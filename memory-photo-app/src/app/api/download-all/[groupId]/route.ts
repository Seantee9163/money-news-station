import { NextResponse } from 'next/server';
import AdmZip from 'adm-zip';
import path from 'path';
import fs from 'fs/promises';
import { ROOT, listResultFiles } from '@/lib/storage';

export async function GET(_: Request, { params }: { params: { groupId: string } }) {
  const zip = new AdmZip();
  const files = await listResultFiles(params.groupId);
  for (const file of files) {
    const fullPath = path.join(ROOT, params.groupId, 'output', file);
    const data = await fs.readFile(fullPath);
    zip.addFile(file, data);
  }

  const buffer = zip.toBuffer();
  return new NextResponse(buffer, {
    headers: {
      'Content-Type': 'application/zip',
      'Content-Disposition': `attachment; filename=${params.groupId}-results.zip`,
    },
  });
}
