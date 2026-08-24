# 休闲娱乐 POI 专项清洗交接说明

> 根目录：`D:\BaiduSyncdisk\00Rehabus\app`
>
> 本文用于说明“公园/海滨长廊/文化/体育”等休闲娱乐设施 POI 的提取规则与产物，便于后续 Agent 识别与继续处理。

---

## 1. 目标范围

已确认需要提取的子类：

- `park`（公园/绿地/花园）
- `promenade`（海滨长廊/滨海步道/海旁步道）
- `square`（广场/步行街）
- `scenic_spot`（景点/观景台/景观带）
- `culture`（博物馆/图书馆/文化中心/剧院）
- `sports`（体育馆/运动场/健身房/球场）

并且：
- 文化类、体育类要求单独输出
- 中英混合名称保留
- 需要排除住宅/地产等噪声

---

## 2. 规则文件

路径：
`public/data/moduleB/poi/poi_leisure_rules_v1.json`

规则内容：
- 每个子类包含 `keywords` + `majorHints` + `minorHints`
- 支持排除词 `exclude` + 全局 `excludeKeywords`

---

## 3. 输出产物（执行后生成）

- `public/data/moduleB/poi/poi_leisure_v1.json`
- `public/data/moduleB/poi/poi_leisure_report_v1.json`
- `public/data/moduleB/poi/manual_review_leisure_topN_v1.json`

其中：
- `poi_leisure_v1.json` 为主数据（单一数组，每条含 `subcategory` 字段）
- `poi_leisure_report_v1.json` 包含数量统计
- `manual_review_leisure_topN_v1.json` 是边界样本复核池

---

## 4. 过滤与排除原则

全局排除关键词：
- 住宅、小区、写字楼、地产、酒店、公寓、花园小区 等

若命中排除词，则丢弃该条记录。

---

## 5. 后续建议

1. 若提取结果过多，可收紧 `square` 或 `scenic_spot` 的关键词。
2. 若提取结果过少，可放宽 `majorHints` 与 `minorHints`。
3. 可将 `poi_leisure_v1.json` 直接接入 IconLayer 展示。

---

## 6. 执行入口

```bash
cd /d D:\BaiduSyncdisk\00Rehabus\app
node scripts\poi\build_poi_leisure_v1.mjs
```

---

## 7. 当前状态

- 规则文件已生成 ✅
- 专项脚本已执行并生成产物 ✅
- 已产出：`poi_leisure_v1.json`、`poi_leisure_report_v1.json`、`manual_review_leisure_topN_v1.json`

## 8. 最新审查结论（2026-03-19）

基于 `poi_leisure_report_v1.json` 与人工复核池抽样，当前口径可用于前端解释层，但存在以下风险：

1. `culture` 数量偏高（10156），疑似混入“办公/管理/泛文化”噪声，需继续审计。
2. `promenade`（25）与 `scenic_spot`（15）偏低，可能由关键词过严或映射漏召回造成。
3. 建议下一版输出 `culture_audit_v1.json`，至少包含：
   - 样本池（命中规则、原始大中类、名称）
   - 人工判定标签（true/false/uncertain）
   - 子类 precision 粗估值

已确认可继续推进 `candidate_poi_features_v2.json`（保持 v1 兼容，新增 `poiFactorsSub`）。
