# money-news-station

中文商业新闻演示站（纯静态，可直接部署到 GitHub Pages）。

## 页面
- 首页 `index.html`
- 分类页 `category.html`
- 文章详情页 `article.html`

## 新闻数据文件（你每天只改这一个）
- **文件路径：`news-data.json`**

> 首页、分类页、文章页全部从 `news-data.json` 读取，不需要数据库。

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

## 超简单每日更新说明
详细版见：`UPDATE_NEWS.md`
