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
