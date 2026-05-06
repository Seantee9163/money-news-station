# Memory Photo App - API SPEC (MVP)

> 目标：上传多组照片（含老照片）-> 自动修复 -> 生成6种风格 -> 次晨下载结果  
> 说明：这是最小可行版本（MVP）接口定义。

---

## Base URL
`/api`

---

## 1. 创建批次

### POST `/batches`

创建一个新批次（当天 18:00 前可继续加组，18:00 后进入夜间处理队列）。

#### Request JSON
```json
{
  "user_name": "demo_user"
}
```

#### Response 201
```json
{
  "batch_id": "b_20260506_001",
  "status": "collecting",
  "cutoff_time": "2026-05-06T18:00:00+08:00"
}
```

---

## 2. 创建照片组

### POST `/batches/{batch_id}/groups`

在批次下创建一组照片并返回上传凭证。

#### Request JSON
```json
{
  "group_name": "family_trip",
  "style_ids": ["style_vintage", "style_film", "style_watercolor"]
}
```

#### Response 201
```json
{
  "group_id": "g_001",
  "upload_slots": [
    {
      "slot_id": "s_001",
      "upload_url": "https://upload.example.com/presigned-1",
      "expires_in_sec": 3600
    }
  ]
}
```

---

## 3. 上传照片完成回调

### POST `/groups/{group_id}/photos:complete`

客户端上传完全部原图后，通知后端开始该组预处理。

#### Request JSON
```json
{
  "photo_count": 12,
  "contains_old_photos": true
}
```

#### Response 200
```json
{
  "group_id": "g_001",
  "status": "queued_for_restore"
}
```

---

## 4. 查询批次状态

### GET `/batches/{batch_id}`

返回批次汇总状态与预计完成时间。

#### Response 200
```json
{
  "batch_id": "b_20260506_001",
  "status": "processing_nightly",
  "groups_total": 3,
  "groups_done": 1,
  "eta_ready_time": "2026-05-07T09:00:00+08:00"
}
```

---

## 5. 查询组内任务状态

### GET `/groups/{group_id}`

查看单组从修复到风格化的执行进度。

#### Response 200
```json
{
  "group_id": "g_001",
  "status": "stylizing",
  "steps": [
    {"name": "restore", "status": "done"},
    {"name": "style_generate", "status": "running"},
    {"name": "package_zip", "status": "pending"}
  ]
}
```

---

## 6. 下载结果

### GET `/batches/{batch_id}/downloads`

次晨可下载批次内所有组结果。

#### Response 200
```json
{
  "batch_id": "b_20260506_001",
  "ready": true,
  "files": [
    {
      "group_id": "g_001",
      "style_id": "style_vintage",
      "download_url": "https://cdn.example.com/results/g_001_vintage.zip",
      "expires_in_sec": 86400
    }
  ]
}
```

---

## 7. 错误码（MVP）

| code | meaning |
|---|---|
| `BATCH_CLOSED` | 超过 18:00，不可新增组 |
| `INVALID_STYLE` | style_id 不在支持列表 |
| `UPLOAD_EXPIRED` | 上传凭证过期 |
| `GROUP_NOT_READY` | 组结果尚未生成 |
| `INTERNAL_ERROR` | 服务内部异常 |
