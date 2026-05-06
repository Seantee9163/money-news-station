import fs from 'fs/promises';
import path from 'path';
import { STYLE_PROMPTS } from '@/prompts/prompts';

const ROOT = path.join(process.cwd(), 'uploads');
const STEPS = 6;

type Task = { step: number; done: boolean; resultPaths: string[] };

const tasks = new Map<string, Task>();

export async function ensureDir(dir: string) {
  await fs.mkdir(dir, { recursive: true });
}

export async function createGroup(groupId: string, files: File[]) {
  const groupDir = path.join(ROOT, groupId, 'input');
  await ensureDir(groupDir);

  for (let i = 0; i < files.length; i += 1) {
    const file = files[i];
    const buffer = Buffer.from(await file.arrayBuffer());
    await fs.writeFile(path.join(groupDir, `${i + 1}-${file.name}`), buffer);
  }

  tasks.set(groupId, { step: 0, done: false, resultPaths: [] });
}

function svgContent(title: string, subtitle: string) {
  return `<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='1024'><rect width='100%' height='100%' fill='#f5e8dc'/><text x='50%' y='45%' text-anchor='middle' font-size='52' fill='#6b4f3f' font-family='sans-serif'>${title}</text><text x='50%' y='55%' text-anchor='middle' font-size='30' fill='#8b6a55' font-family='sans-serif'>${subtitle}</text></svg>`;
}

export async function mockProcess(groupId: string) {
  const task = tasks.get(groupId);
  if (!task || task.done) return;
  const groupOutDir = path.join(ROOT, groupId, 'output');
  await ensureDir(groupOutDir);

  for (let i = 1; i <= STEPS; i += 1) {
    await new Promise((r) => setTimeout(r, 800));
    task.step = i;
  }

  const resultPaths: string[] = [];
  for (const style of STYLE_PROMPTS) {
    const name = `${style.key}.svg`;
    const filePath = path.join(groupOutDir, name);
    await fs.writeFile(filePath, svgContent(style.key, style.label), 'utf8');
    resultPaths.push(`/api/result/${groupId}?file=${encodeURIComponent(name)}`);
  }

  task.done = true;
  task.resultPaths = resultPaths;
}

export function getStatus(groupId: string) {
  const task = tasks.get(groupId);
  if (!task) return null;
  return { groupId, step: task.step, done: task.done };
}

export function getResults(groupId: string) {
  const task = tasks.get(groupId);
  return task?.resultPaths ?? [];
}

export async function getResultFile(groupId: string, file: string) {
  const filePath = path.join(ROOT, groupId, 'output', file);
  const data = await fs.readFile(filePath, 'utf8');
  return data;
}

export async function listResultFiles(groupId: string) {
  const dir = path.join(ROOT, groupId, 'output');
  return fs.readdir(dir);
}

export { ROOT };
