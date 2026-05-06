import Link from 'next/link';

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
      <h1 className="mb-4 text-4xl font-bold">AI 纪念照片生成器</h1>
      <p className="mb-8 text-lg text-slate-600">上传照片，一键修复并生成 6 张温暖风格纪念图</p>
      <Link href="/upload" className="rounded-lg bg-slate-900 px-8 py-3 text-white hover:bg-slate-700">开始制作</Link>
    </main>
  );
}
