'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const steps = ['正在检查照片', '正在修复老照片', '正在生成写真风', '正在生成漫画风', '正在生成趣味风', '正在整理下载结果'];

export default function ProcessingPage() {
  const params = useSearchParams();
  const groupId = params.get('groupId') || '';
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!groupId) return;

    const timer = setInterval(async () => {
      const res = await fetch(`/api/status?groupId=${groupId}`);
      const data = await res.json();
      setCurrentStep(data.step || 0);
      if (data.done) {
        clearInterval(timer);
        router.push(`/result?groupId=${groupId}`);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [groupId, router]);

  const activeIndex = useMemo(() => Math.max(currentStep - 1, 0), [currentStep]);

  return (
    <main className="mx-auto min-h-screen w-full max-w-2xl px-6 py-10">
      <h1 className="mb-6 text-3xl font-bold">处理中</h1>
      <div className="space-y-3 rounded-xl bg-white p-6 shadow">
        {steps.map((s, idx) => (
          <div key={s} className={`rounded p-3 ${idx <= activeIndex ? 'bg-emerald-100' : 'bg-slate-100'}`}>{s}</div>
        ))}
      </div>
    </main>
  );
}
