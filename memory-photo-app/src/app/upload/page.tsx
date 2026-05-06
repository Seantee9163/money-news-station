'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const types = ['母婴', '家庭', '毕业', '追思', '朋友', '其他'];

export default function UploadPage() {
  const router = useRouter();
  const [name, setName] = useState('我的纪念组');
  const [kind, setKind] = useState('家庭');
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    if (!files || files.length < 1 || files.length > 3) return alert('请上传 1 到 3 张照片');
    setLoading(true);
    const form = new FormData();
    form.append('name', name);
    form.append('kind', kind);
    Array.from(files).forEach((f) => form.append('photos', f));

    const res = await fetch('/api/upload', { method: 'POST', body: form });
    const data = await res.json();
    router.push(`/processing?groupId=${data.groupId}`);
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-2xl px-6 py-10">
      <h1 className="mb-6 text-3xl font-bold">上传照片</h1>
      <div className="space-y-4 rounded-xl bg-white p-6 shadow">
        <input className="w-full rounded border p-2" value={name} onChange={(e) => setName(e.target.value)} placeholder="组名" />
        <select className="w-full rounded border p-2" value={kind} onChange={(e) => setKind(e.target.value)}>
          {types.map((t) => <option key={t}>{t}</option>)}
        </select>
        <input type="file" multiple accept="image/*" onChange={(e) => setFiles(e.target.files)} />
        <p className="text-sm text-slate-500">每组可上传 1 到 3 张照片。</p>
        <button onClick={onSubmit} disabled={loading} className="rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-50">开始生成</button>
      </div>
    </main>
  );
}
