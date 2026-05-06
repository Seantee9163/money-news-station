import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI 纪念照片生成器',
  description: '上传照片，一键修复并生成 6 张温暖风格纪念图',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
