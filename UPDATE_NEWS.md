# 每日更新说明（超简单）

## 1) 每天打开哪个文件？
打开两个文件：
- 模板：`news-template.jsonc`
- 数据：`news-data.json`

---

## 2) 新增一条新闻时复制哪段模板？
每天从 `news-template.jsonc` 复制整段对象，粘贴到 `news-data.json` 数组最前面（或任意位置都行，首页会自动排序）。

> 注意：`news-template.jsonc` 里有注释（方便你看说明），但 `news-data.json` 里不能有注释，只能保留纯 JSON 字段。

---

## 3) 哪些字段必须填？
必须填：
- `id`（不能重复，新增时用更大的数字）
- `title`
- `category`
- `date`（必须是 `YYYY-MM-DD`）
- `is_featured`（只能是 `true` 或 `false`）
- `summary`
- `opportunity`
- `content`
- `source_name`

---

## 4) 哪些字段可以留空？
可以留空：
- `source_url`
- `risk`
- `why_it_matters`

留空后的页面表现：
- `source_url` 为空：详情页会自动隐藏“打开来源链接”按钮
- `risk` 为空：详情页会自动隐藏风险提示区
- `why_it_matters` 为空：详情页会自动隐藏 why_it_matters 模块

---

## 5) 置顶规则怎么用？
- 想让某条出现在“今日核心机会”：把它的 `is_featured` 改成 `true`
- 建议同一天只有 1 条 `is_featured: true`
- 首页排序规则：**置顶优先，其次按日期倒序**
