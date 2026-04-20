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

本仓库已提供两条 GitHub Actions 工作流：

- `.github/workflows/update-news.yml`：手动触发，生成或更新 `news-data.json`
- `.github/workflows/deploy-pages.yml`：将当前静态站点发布到 GitHub Pages

### 1) 配置 `update-news.yml`

当前只启用了 `workflow_dispatch`（手动触发），用于先跑通自动更新流程。

执行逻辑：
1. 读取 `secrets.NEWS_SOURCE_URL` 指向的 JSON 新闻源（数组）
2. 校验并写入 `news-data.json`
3. 若文件发生变化，自动提交并推送到当前分支

> 后续如需定时更新，可在 `on:` 下追加 `schedule`（例如 cron）。

### 2) 配置 `deploy-pages.yml`

- 在 `main` 分支有新提交时会自动部署
- 也支持手动触发部署
- 采用 GitHub 官方 Pages Actions（`configure-pages` / `upload-pages-artifact` / `deploy-pages`）

### 3) 需要添加的 Secrets 名称

请在仓库 `Settings -> Secrets and variables -> Actions` 中添加：

- `NEWS_SOURCE_URL`（必填）：新闻数据源接口地址，返回 JSON 数组
- `NEWS_SOURCE_AUTH_TOKEN`（可选）：若数据源需要鉴权，填入 Bearer Token

### 4) GitHub Pages 仓库设置

在仓库 `Settings -> Pages` 中将 Build and deployment Source 设置为 **GitHub Actions**。
