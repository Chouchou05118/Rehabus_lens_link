# POI 清洗与分类协作提示（给外部 AI / 数据同事）

> 项目根目录：`D:\BaiduSyncdisk\00Rehabus\app`
>
> 当前阶段：Module B 已有评分与可解释框架，但真实 POI 尚未形成“清洗 → 特征统计 → 建议/评分接入”闭环。

---

## 1) 现状与边界（必须遵守）

1. 前端技术栈：React + TypeScript + deck.gl。
2. Module B 已实现：
   - 权重重算（efficiency / equity / feasibility）
   - 约束规则（spacing/conflict/exits）
   - Confirm Site 后 residual heatmap 高斯扣减
   - InfoCard 可解释展示
3. 当前缺口：
   - `data_202406/POI.csv` 尚未完成标准化清洗产物
   - 候选点周边 POI 特征（300m/500m）尚未形成稳定输入
   - POI 尚未系统接入建议层/评分层

### 约束

- 不修改：`public/data/moduleA/`
- Module B 产物仅放：`public/data/moduleB/poi/`
- 异常值策略：尽量保留并打标，不直接删除
- 必须支持 graceful fallback（POI 数据缺失时前端仍可运行）

---

## 2) 已拍板规则（本任务固定决策）

1. 目标大类至少包含：
   - `medical`
   - `transport`
   - `commercial`
   - `public_service`
   - `leisure`
   - `accessibility_support`（新增：无障碍支持设施）

2. 候选点 POI 统计口径必须同时输出：
   - `count_300m`
   - `count_500m`
   - `nearest_distance_m`
   - `density_score`

3. 半径权重固定：
   - 300m 权重 `0.65`
   - 500m 权重 `0.35`

4. 接入策略：`先建议后评分`（先做建议层，再逐步注入总分）

5. 负向 POI（噪声/工业风险等）本阶段不纳入。

6. 字段策略：英文标准字段 + 中文原始字段镜像并存。

7. 超出研究范围 POI：保留并打 `out_of_study_bbox`，默认统计不计入。

8. 导出能力：
   - P1：单候选点 JSON 导出
   - P2：批量 CSV + JSON 导出

---

## 3) 输入文件

- 原始输入：`data_202406/POI.csv`
- 当前已知原字段（中文）：
  - `名称`
  - `大类`
  - `中类`
  - `经度`
  - `纬度`
  - `省份`
  - `地级市`

---

## 4) 清洗输出契约（建议 v1）

请输出到：`public/data/moduleB/poi/poi_cleaned_v1.json`

### 顶层结构建议

```json
{
  "schemaVersion": "poi-cleaned-v1",
  "generatedAt": "2026-03-07T00:00:00.000Z",
  "source": {
    "file": "data_202406/POI.csv",
    "encoding": "utf-8|utf-8-sig|gb18030",
    "rowCountRaw": 0,
    "rowCountOutput": 0
  },
  "config": {
    "studyBbox": [113.8, 22.15, 114.5, 22.6],
    "radiusWeights": { "r300m": 0.65, "r500m": 0.35 }
  },
  "records": []
}
```

### 单条 POI 记录建议字段

```json
{
  "id": "poi-000001",
  "name": "Public Toilet A",
  "category": "public_service",
  "subcategory": "toilet",
  "lng": 114.300778,
  "lat": 22.273126,
  "district": "香港特别行政区",
  "city": "香港特别行政区",

  "raw_name": "公厕",
  "raw_major": "生活服务",
  "raw_minor": "公厕",

  "quality_flags": ["out_of_study_bbox", "missing_minor", "possible_duplicate"],
  "is_in_study_bbox": true,
  "is_valid_coord": true,

  "source": "POI.csv"
}
```

---

## 5) 类型映射要求（必须可追溯）

请另外输出映射表（可 json/csv）：
- `public/data/moduleB/poi/poi_type_mapping_v1.json`

要求：
1. 每个原始 `大类/中类` 对应一个目标 `category/subcategory`
2. 对无法识别类型，回落到 `category = "other"` 并打 `unmapped_category`
3. 映射表要可扩展，可被前端/脚本复用

---

## 6) 质量标记规则（建议）

- `invalid_coord`：经纬度缺失或越界
- `out_of_study_bbox`：超出研究范围框
- `missing_name`：名称缺失
- `missing_major`：大类缺失
- `missing_minor`：中类缺失
- `possible_duplicate`：同名且近邻（如 < 20m）
- `unmapped_category`：未匹配分类映射
- `mixed_language_name`：中英混合可选标记

注意：异常记录尽量保留，不删；通过 flags 让前端可筛选。

---

## 7) 候选点特征输出契约（给 Module B）

请输出：`public/data/moduleB/poi/candidate_poi_features_v1.json`

结构建议：

```json
{
  "schemaVersion": "candidate-poi-features-v1",
  "generatedAt": "2026-03-07T00:00:00.000Z",
  "source": {
    "poi": "public/data/moduleB/poi/poi_cleaned_v1.json",
    "candidates": "public/data/moduleB/depot_candidates_scored.json"
  },
  "radius": [300, 500],
  "radiusWeights": { "300": 0.65, "500": 0.35 },
  "candidates": [
    {
      "candidateId": "depot-001",
      "siteCode": "Site #A-017",
      "poiFactors": {
        "medical": {
          "count_300m": 2,
          "count_500m": 4,
          "nearest_distance_m": 180,
          "density_score": 74.2
        }
      },
      "poiComposite": {
        "suggestionTier": "good",
        "topStrengths": ["medical", "public_service"],
        "topGaps": ["accessibility_support"]
      }
    }
  ]
}
```

---

## 8) 建议层文案（P1）

请基于 `poiFactors` 自动生成建议字段（供 InfoCard 展示）：
- `poiSuggestions`: string[]
- 示例：
  - “500m 内公共便民服务不足，建议配置无障碍卫生间与休憩点。”
  - “医疗资源近邻度较高，适合优先布局应急充电与接驳。”

---

## 9) 验收标准（交付必须满足）

1. `poi_cleaned_v1.json` 可被稳定解析，且含版本/来源/配置信息。
2. 每条记录具备：`id/name/category/lng/lat/quality_flags`。
3. 提供独立映射表并可追溯原分类。
4. `candidate_poi_features_v1.json` 覆盖全部候选点，包含 300m/500m 统计与 `density_score`。
5. 半径权重在产物内明确标注为 `0.65/0.35`。
6. 异常点未被粗暴删除，而是通过 flags 标注。
7. 产物目录内有 README 解释字段、单位、示例。

---

## 10) 交付清单（最少）

- `public/data/moduleB/poi/poi_cleaned_v1.json`
- `public/data/moduleB/poi/poi_cleaning_report_v1.json`
- `public/data/moduleB/poi/poi_type_mapping_v1.json`
- `public/data/moduleB/poi/candidate_poi_features_v1.json`
- `public/data/moduleB/poi/README.md`

---

## 11) 给执行者的实现建议（可选）

- 推荐 Python（pandas + geopandas/scipy 可选）做离线清洗。
- 编码兼容：依次尝试 `utf-8-sig` → `utf-8` → `gb18030`。
- 距离计算建议用 haversine（米）。
- 去重逻辑建议“软去重”：保留全部，仅打 `possible_duplicate`。
- 输出 JSON 前做 `NaN/null` 规整，避免前端解析异常。

---

## 12) 追加优化请求（请优先考虑）

### 12.1 子类细分（提升 tags 建议可信度）

请在 `poi_cleaned_v1.json` 中新增更细子类字段，并在 `candidate_poi_features_v1.json` 中输出子类级统计（count / nearest）。建议包含：

- accessibility_support → `accessible_toilet`, `rehab_center`, `assistive_device`, `barrier_free_service`
- commercial → `retail_food`, `supermarket`, `shopping_mall`
- leisure → `park`, `sports`, `entertainment`
- transport → `bus_stop`, `mtr_station`, `parking`, `ferry_pier`

### 12.2 去重与聚合（减轻密集区噪音）

- 同类 POI 在 50m 内聚合为 1 个（输出 `count_unique_50m`）
- 同时保留 `raw_count` 以便对照
- `candidate_poi_features_v1.json` 中建议加入 `count_unique_50m` 版本的统计

### 12.3 tags 建议的香港/无障碍阈值（前端已接入）

前端基于以下阈值推导 tags 建议数量，请确保 `nearest_distance_m` 字段可靠：

- 无障碍 / 公厕：200m（accessibility_support）
- 公园：300m（leisure: park）
- 餐饮/休闲：300m（commercial + leisure）
- 交通/停车：400m（transport + public_service）

### 12.4 输出结构建议（不破坏兼容性）

建议在 `candidate_poi_features_v1.json` 中新增：

- `poiFactorsSub`: 子类级统计
- `poiComposite.subcategoryStrengths` / `subcategoryGaps`
- `metadata`: `aggregation_radius_m`, `dedupe_radius_m`

保持原字段不变，新增字段即可。

---

## 13) 最新对话接力状态（2026-03）

### 13.1 前端已接入状态（请勿重复实现）

- Module B 已有 Operator Marker Popup（附着 marker、Cancel 保留 temp、Clear 归零、Confirm 固化）。
- InfoCard 已支持：
  - Tags 贡献显示（ScoreRing 蓝色半透明分段）
  - POI 提示文案（基于候选点 POI 特征）
- 当前 tags 建议阈值（香港+无障碍口径）已在前端启用：
  - accessibility_support: 200m
  - leisure(park proxy): 300m
  - commercial+leisure: 300m
  - transport+public_service: 400m

### 13.2 本次新增的数据交接文件（必须阅读）

- `POI_LEISURE_HANDOFF_README.md`
- `POI_ACCESSIBILITY_HANDOFF_README.md`
- `README.md`（本目录）
- `poi_leisure_v1.json`
- `poi_leisure_report_v1.json`
- `poi_leisure_rules_v1.json`
- `manual_review_leisure_topN_v1.json`

### 13.3 对清洗 Agent 的明确增量任务

1. 基于现有体系迭代，不重建：
   - 输入：`poi_cleaned_v1.json` + `poi_leisure_v1.json`
   - 输出：`candidate_poi_features_v2.json`
2. 兼容 v1 字段，不破坏前端：
   - 保留 `poiFactors/poiComposite/poiSuggestions`
   - 新增 `poiFactorsSub`（含 leisure 子类）
3. 新增质量报告：
   - `poi_feature_report_v2.json`（子类分布、覆盖率、Top gaps）
   - `culture_audit_v1.json`（抽样误判检查）
4. 去重增强：
   - 同类 50m 聚合统计，输出 `count_unique_50m` 与 `raw_count`

### 13.4 已识别风险

- leisure 的 `culture` 数量偏高，可能存在“泛文化/办公类”噪声。
- promenade/scenic_spot 数量偏低，可能规则偏严或真实稀缺，需要审计样本。
- handoff 文档与“已执行状态”可能存在版本不同步，后续需统一口径。