# Module B POI Data Contract (v2)

本目录存放 Module B 的 POI 清洗产物与候选点评估特征。

**最后更新：2026-03-30**
**分类体系版本：v2（含 restaurant / bank / education 三个新分类）**

---

## 1. 当前目录文件说明

| 文件 | 大小 | 说明 |
|------|------|------|
| `poi_cleaned_v1.json` | ~120MB | **主数据源**。312,342 条香港 POI，UTF-8，v2 分类体系，0 unmapped |
| `poi_cleaning_report_v1.json` | <1MB | 清洗质量报告（分类分布、flag 统计、重复检测） |
| `poi_type_mapping_v2.json` | ~20KB | **分类映射表**。150 行确定性 1:1 映射，`raw_major×raw_minor → category+subcategory` |
| `candidate_poi_features_v1.json` | ~50KB | **候选点 POI 特征**。10 个 mock 候选点的 300m/500m 统计，v2 分类体系 |
| `build_candidate_features.py` | ~12KB | 重建 `candidate_poi_features_v1.json` 的 Python 脚本（可重跑） |
| `README.md` | 本文件 | 目录说明 |
| `POI_RECATEGORIZATION_PROMPT.md` | 参考文档 | v2 分类体系设计说明与规则 |
| `POI_CLEANING_COLLAB_PROMPT.md` | 参考文档 | 给外部 AI/数据同事的协作提示 |
| `POI_ACCESSIBILITY_HANDOFF_README.md` | 参考文档 | accessibility_support 分类说明 |
| `POI_LEISURE_HANDOFF_README.md` | 参考文档 | leisure 分类说明 |

---

## 2. 全局原则

1. 不修改 `public/data/moduleA/`。
2. POI 异常值「尽量保留并打标」，不做粗暴删除。
3. 所有产物包含 `schemaVersion`、`generatedAt`、`source`。
4. 前端必须支持 graceful fallback（POI 数据缺失时仍可运行）。

---

## 3. 固定参数（已拍板）

- 统计半径：`300m`、`500m`
- 半径权重：`300m = 0.65`，`500m = 0.35`
- 本阶段仅正向 POI，不纳入负向 POI 惩罚因子
- 去重口径：同类 POI 在 50m 内聚合为 1 个（`count_unique_50m`）

---

## 4. 分类体系 v2（当前生效）

| 分类 | 图标 | 说明 | 原始大类来源 |
|------|------|------|------|
| `medical` | 🏥 | 医院、诊所、药房、急救 | 医疗保健 |
| `transport` | 🚌 | 公交站、地铁、停车场、港口、充电站 | 交通设施、汽车相关 |
| `commercial` | 🛍️ | 超市、便利店、商场、美容、洗衣 | 购物消费、生活服务（部分）、酒店住宿 |
| `public_service` | 🏛️ | 公厕、邮局、图书馆、社区中心 | 生活服务（部分）、科教文化（部分） |
| `leisure` | 🌳 | 公园、运动场、娱乐、博物馆、旅游景点 | 运动健身、旅游景点、休闲娱乐、科教文化（部分） |
| `accessibility_support` | ♿ | 无障碍卫生间、康复中心、辅具 | （名称关键词匹配） |
| `restaurant` ⭐ | 🍽️ | 餐厅、小食亭、咖啡、茶楼、快餐 | 餐饮美食 |
| `bank` ⭐ | 🏦 | 银行、ATM、保险、投资 | 金融机构 |
| `education` ⭐ | 🎓 | 学校、幼儿园、培训中心、大学 | 科教文化（部分） |
| `other` | 📍 | 公司企业、商务住宅（不参与评分） | 公司企业、商务住宅 |

> ⭐ 为 v2 新增分类（v1 时 restaurant 在 commercial，bank 在 other，education 在 public_service）

### 4.1 科教文化内部细分规则

`科教文化` 大类需按中类二级拆分：

- **`education`**：培训单位、幼儿园、中学、小学、高等教育、成人教育、职业技术教育、驾校
- **`public_service`**：图书馆、科研单位、新闻出版、广播电视、档案馆、信息咨询中心、会展展览
- **`leisure`**：博物馆、文化宫、艺术团体、天文馆、美术展览、科技馆

---

## 5. poi_cleaned_v1.json 字段说明

### 5.1 顶层字段

```json
{
  "schemaVersion": "poi-cleaned-v1",
  "generatedAt": "2026-03-30T...",
  "source": {
    "file": "data_202406/POI.csv",
    "encoding": "utf-8",
    "mappingVersion": "poi-type-mapping-v2",
    "rowCountRaw": 312342,
    "rowCountOutput": 312342
  },
  "config": {
    "studyBbox": [113.8, 22.15, 114.5, 22.6],
    "radiusWeights": { "r300m": 0.65, "r500m": 0.35 }
  },
  "records": []
}
```

### 5.2 records[] 字段

```json
{
  "id": "poi-000001",
  "name": "专用停车场",
  "category": "transport",
  "subcategory": "parking",
  "lng": 114.300494,
  "lat": 22.271364,
  "district": "香港特别行政区",
  "city": "香港特别行政区",
  "raw_name": "专用停车场",
  "raw_major": "交通设施",
  "raw_minor": "停车场",
  "quality_flags": [],
  "is_in_study_bbox": true,
  "is_valid_coord": true,
  "source": "POI.csv"
}
```

### 5.3 quality_flags 枚举

| Flag | 含义 |
|------|------|
| `invalid_coord` | 经纬度缺失或越界 |
| `out_of_study_bbox` | 超出研究范围框 |
| `missing_name` | 名称缺失（当前数据集：17条） |
| `missing_major` | 大类缺失 |
| `missing_minor` | 中类缺失 |
| `possible_duplicate` | 同名且近邻（当前数据集：5,692条） |
| `unmapped_category` | 未匹配分类映射（当前数据集：0条） |

---

## 6. poi_type_mapping_v2.json 字段说明

**用途**：驱动 `build_candidate_features.py` 和未来任何重建脚本。每个 `raw_major×raw_minor` 对应唯一的 `category+subcategory`，无歧义。

```json
{
  "schemaVersion": "poi-type-mapping-v2",
  "rows": [
    {
      "raw_major": "交通设施",
      "raw_minor": "停车场",
      "category": "transport",
      "subcategory": "parking"
    }
  ]
}
```

**与 v1 的区别**：v1 存在同一组合映射到多个 category 的歧义行（1:N），v2 严格 1:1。

---

## 7. candidate_poi_features_v1.json 字段说明

### 7.1 顶层

```json
{
  "schemaVersion": "candidate-poi-features-v1",
  "radius": [300, 500],
  "radiusWeights": { "300": 0.65, "500": 0.35 },
  "metadata": {
    "aggregation_radius_m": 500,
    "dedupe_radius_m": 50,
    "mainCategories": ["medical","transport","commercial","public_service","leisure",
                       "accessibility_support","restaurant","bank","education"]
  },
  "candidates": []
}
```

### 7.2 candidates[] 字段

```json
{
  "candidateId": "depot-001",
  "siteCode": "Site #A-017",
  "lng": 114.188,
  "lat": 22.312,
  "poiFactors": {
    "medical":   { "count_300m": 13, "count_500m": 58, "nearest_distance_m": 18.6, "density_score": 12.0, "count_unique_50m": 0 },
    "restaurant":{ "count_300m": 40, "count_500m": 180, "nearest_distance_m": 25.0, "density_score": 15.0, "count_unique_50m": 30 },
    "bank":      { "count_300m": 5,  "count_500m": 19,  "nearest_distance_m": 80.0, "density_score": 19.0, "count_unique_50m": 8  },
    "education": { "count_300m": 3,  "count_500m": 27,  "nearest_distance_m": 120.0,"density_score": 27.0, "count_unique_50m": 10 }
  },
  "poiFactorsSub": {
    "bus_stop":  { "count_300m": 17, "count_500m": 65, "nearest_distance_m": 130.8, "count_unique_50m": 36 },
    "parking":   { "count_300m": 3,  "count_500m": 41, "nearest_distance_m": 123.4, "count_unique_50m": 30 }
  },
  "poiComposite": {
    "suggestionTier": "weak",
    "topStrengths": ["transport", "education"],
    "topGaps": ["accessibility_support"],
    "subcategoryStrengths": ["bus_stop"],
    "subcategoryGaps": ["accessible_toilet"]
  },
  "poiSuggestions": [
    "500m 内无障碍支持设施偏少，建议优先配置无障碍卫生间、辅具支持与休憩点。"
  ]
}
```

### 7.3 density_score 计算规则

- `density_score` 范围 0–100，基于同批次候选点的相对排名（min-max 归一化）
- 公式：`w = count_300m * 0.65 + count_500m * 0.35`，再除以批次最大值 * 100
- `count_unique_50m`：同类 POI 在 50m 格内去重后的数量（用于密集区噪声控制）

---

## 8. 前端接入状态

### 8.1 MapCanvas.tsx — 放大镜 POI 展示

- 加载：`fetch('/data/moduleB/poi/poi_cleaned_v1.json')` （Module B 首次激活时，force-cache）
- 使用字段：`id`, `name`, `category`, `subcategory`, `lng`, `lat`
- 抽稀算法：3×3 网格均匀抽稀，1km 半径，50m 互斥距离
- 图标：由 `POI_ICON_BY_SUBCATEGORY` / `POI_ICON_BY_CATEGORY` 映射（含 restaurant/bank/education）

### 8.2 App.tsx — 候选点 POI 特征

- 加载：`fetch('/data/moduleB/poi/candidate_poi_features_v1.json')`
- 匹配：通过 `candidateId` 或 `siteCode` 与当前 `selectedCandidate` 对应
- 评分注入：`poiFactors[*].density_score` → `avgDensity` → `poiDelta`（可由 strength slider 控制）
- Graceful fallback：文件缺失或解析失败时不阻断 Module B 主流程

### 8.3 InfoCard.tsx — POI 贡献展示

- `POI Contribution Summary`：展示 `avgDensity`, `poiDelta`
- `Show details` 展开区：`count_300m`, `count_500m`, `nearest_distance_m`, `density_score`
- `poiSuggestions`：展示建议文案
- 当 POI 数据不可用时显示 `POI data unavailable`，不报错中断

---

## 9. 重建流程（如需更新数据）

### 9.1 重建 poi_cleaned_v1.json

如果 `data_202406/POI.csv` 或 `poi_type_mapping_v2.json` 发生变化，重建步骤：

1. 确认 `poi_type_mapping_v2.json` 已更新
2. 运行：
   ```bash
   # 在 public/data/moduleB/poi/ 目录下
   python build_candidate_features.py  # 此脚本仅重建 features
   ```
   若需重建 `poi_cleaned_v1.json` 本身，需恢复 `build_poi_cleaned_v2.py`（见 Git history）

### 9.2 重建 candidate_poi_features_v1.json

候选点坐标或 POI 数据变化时：

```bash
python public/data/moduleB/poi/build_candidate_features.py
```

- 自动从 `poi_cleaned_v1.json` 读取 POI
- 自动从现有 `candidate_poi_features_v1.json` 读取候选点列表（保持 candidateId/siteCode 不变）
- 支持全部 9 个主分类 + 约 40 个子分类
- 运行时间：约 1–2 分钟（312k 条 POI × 10 候选点）

### 9.3 新增候选点

在 `build_candidate_features.py` 顶部的 `cand_list` 或来源文件中增加候选点条目，重跑脚本即可。

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-03-12 | 初始清洗，6个分类（medical/transport/commercial/public_service/leisure/accessibility_support） |
| v2 | 2026-03-30 | **当前版本**。新增 restaurant/bank/education 分类；修复 poi_type_mapping 1:N 歧义；清理旧中间文件 |

---

## 11. 导出能力路线

- ✅ P1：单候选点 JSON 导出（已完成）
- P2：批量 CSV + JSON 导出（待实现）

---

## 12. 联系与反馈

如有分类问题：
1. 在 `poi_type_mapping_v2.json` 中修改对应行
2. 重跑 `build_candidate_features.py`
3. 更新本 README 版本历史
