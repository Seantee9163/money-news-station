# 每日更新说明（超简单）

## 1) 每天打开哪个文件？
打开：`news-data.json`

---

## 2) 新增一条新闻时复制哪段模板？
在 `news-data.json` 里，复制下面这一段，粘贴到数组最前面（或任意位置都行，首页会自动排序）：

```json
{
  "id": 13,
  "title": "这里写标题",
  "category": "这里写分类",
  "date": "2026-04-20",
  "is_featured": false,
  "summary": "这里写一句摘要",
  "opportunity": "这里写机会判断",
  "content": "这里写正文",
  "source_name": "这里写来源名",
  "source_url": "https://example.com/news-link",
  "risk": "这里写风险（可留空）",
  "why_it_matters": "这里写为什么重要（可留空）"
}
```

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

建议：`source_url` 尽量填写，方便以后回看来源。

---

## 5) 置顶规则怎么用？
- 想让某条出现在“今日核心机会”：把它的 `is_featured` 改成 `true`
- 建议同一天只有 1 条 `is_featured: true`
- 首页排序规则：**置顶优先，其次按日期倒序**

