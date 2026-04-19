# money-news-station

中文商业新闻演示站（纯静态，可直接部署到 GitHub Pages）。

## 已完成页面
- 首页 `index.html`
- 分类页 `category.html`
- 文章详情页 `article.html`

## 数据结构（单文件可维护）
所有新闻统一放在：`news-data.json`

每条新闻字段固定为：
- `id`
- `title`
- `category`
- `date`
- `summary`
- `opportunity`
- `content`
- `source_name`
- `source_url`
- `risk`
- `why_it_matters`

> 首页、分类页、文章页全部从 `news-data.json` 读取。

## 展示规则
- 首页默认按 `date` 从新到旧排序。
- “今日核心机会”会自动读取**最新日期**里的**第一条新闻**。
- 不使用数据库，GitHub Pages 直接可运行。

## iPad 每日更新（最简单）
给小白版 4 步：

1. 打开 GitHub 仓库，进入 `news-data.json`。
2. 点右上角 ✏️ 编辑。
3. 把最上面那条新闻改成今天的内容（或复制一条旧新闻改字段），注意：
   - `id` 不要重复（新文章用更大的数字）
   - `date` 用 `YYYY-MM-DD`（例如 `2026-04-20`）
4. 点 **Commit changes** 保存。

完成后，GitHub Pages 会自动更新页面内容。

## 本地运行
这是纯静态站点。

推荐使用本地服务器（避免浏览器直接打开文件时无法读取 JSON）：

```bash
python3 -m http.server 8000
```

然后访问 `http://localhost:8000`。
