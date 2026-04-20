# money-news-station

中文商业新闻演示站（纯静态，可直接部署到 GitHub Pages）。

## 页面
- 首页 `index.html`
- 分类页 `category.html`
- 历史归档页 `archive.html`
- 文章详情页 `article.html`

## 新闻数据文件（你每天只改这一个）
- **文件路径：`news-data.json`**
- **空白模板：`news-template.jsonc`（含字段填写注释）**

> 首页、分类页、文章页全部从 `news-data.json` 读取，不需要数据库。
> 每天新增新闻时：先复制 `news-template.jsonc` 的对象模板，再粘贴到 `news-data.json` 中并填写内容。

## 数据格式（适合手动维护）
`news-data.json` 是一个 JSON 数组，每条新闻是一个对象。推荐字段顺序如下：

- `id`（必填，整数，不能重复）
- `title`（必填）
- `category`（必填）
- `date`（必填，格式 `YYYY-MM-DD`）
- `is_featured`（必填，`true/false`，是否置顶）
- `summary`（必填）
- `opportunity`（必填）
- `content`（必填）
- `source_name`（必填）
- `source_url`（可留空，建议填）
- `risk`（可留空）
- `why_it_matters`（可留空）

留空时的自动隐藏规则：
- `source_url` 为空：详情页隐藏“打开来源链接”按钮
- `risk` 为空：详情页隐藏风险提示区
- `why_it_matters` 为空：详情页隐藏 why_it_matters 模块

## 超简单每日更新说明
详细版见：`UPDATE_NEWS.md`

## 自动更新配置说明

当前仓库只保留以下两条工作流，避免重复部署：

- `.github/workflows/update-news.yml`：手动触发，强制重写 `news-data.json` 为一条带 UTC 时间戳的测试新闻
- `.github/workflows/deploy-pages.yml`：监听 `main` 分支 `push` 并自动发布到 GitHub Pages

### 1) `update-news.yml` 当前行为

执行逻辑：
1. 使用 Python 每次重写 `news-data.json`
2. 写入一条测试新闻，标题和正文包含当前 UTC 时间戳
3. 检查 `news-data.json` 是否有差异
4. 仅在有差异时 `commit + push`
5. 若无差异，日志输出：`No changes detected in news-data.json, skipping commit and push.`

> 这样可以先验证自动更新链路，后续再切回真实新闻源。

### 2) `deploy-pages.yml` 当前行为

- 当 `main` 有新提交时自动触发
- 使用官方 Pages Actions（`configure-pages` / `upload-pages-artifact` / `deploy-pages`）
- 因此 `update-news.yml` 推送到 `main` 后会继续触发 Pages 自动发布

### 3) GitHub Pages 仓库设置

在仓库 `Settings -> Pages` 中将 Build and deployment Source 设置为 **GitHub Actions**。

## 自动更新测试方法

1. 打开 GitHub 仓库 `Actions` 页面，运行 **Update News Data**。
2. 观察日志中 `news-data.json rewritten at ... UTC` 输出。
3. 确认出现 `chore: auto-update news-data.json` 自动提交（若有变更）。
4. 提交进入 `main` 后，检查 **Deploy static site to Pages** 是否自动触发并成功。
5. 打开 Pages 站点，确认首页可见“自动更新测试新闻（时间戳）”。
