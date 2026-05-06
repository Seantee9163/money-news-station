'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

type ResultData = { images: string[] };

export default function ResultPage() {
  const params = useSearchParams();
  const groupId = params.get('groupId') || '';
  const [images, setImages] = useState<string[]>([]);

  useEffect(() => {
    if (!groupId) return;
    fetch(`/api/result?groupId=${groupId}`).then((r) => r.json()).then((d: ResultData) => setImages(d.images));
  }, [groupId]);

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-6 py-10">
      <h1 className="mb-6 text-3xl font-bold">生成结果</h1>
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {images.map((src) => (
          <div key={src} className="rounded-xl bg-white p-3 shadow">
            <img src={src} alt="result" className="mb-3 aspect-square w-full rounded object-cover" />
            <a href={`${src}&download=1`} className="inline-block rounded bg-slate-900 px-3 py-2 text-sm text-white">下载图片</a>
          </div>
        ))}
      </div>
      <a href={`/api/download-all/${groupId}`} className="rounded bg-emerald-700 px-4 py-2 text-white">全部下载</a>
    </main>
  );
}
