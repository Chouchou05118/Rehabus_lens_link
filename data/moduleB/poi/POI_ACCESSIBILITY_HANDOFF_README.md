# POI 可达性筛选与接入交接说明（给后续对话/LLM）

> 项目根目录：`D:\BaiduSyncdisk\00Rehabus\app`
>
> 本文目标：让新的助手在最短时间内接力当前进度，继续完成 **Module B 的 POI 接入（InfoCard 展示、导出、后续评分注入）**。

---

## 1. 当前已完成内容（状态快照）

### 1.1 已完成的基础清洗与特征产物

目录：`public/data/moduleB/poi/`

已生成：
- `poi_type_mapping_v1.json`（原始类型映射统计）
- `poi_cleaned_v1.json`（全量标准化清洗）
- `poi_cleaning_report_v1.json`（清洗报告）
- `candidate_poi_features_v1.json`（候选点 POI 特征）

已确认的固定参数：
- 统计半径：`300m`、`500m`
- 权重：`300m=0.65`，`500m=0.35`

### 1.2 已完成的“残障相关 + 公共服务”二次筛选

已实现两版筛选：

#### v1
- 规则文件：`poi_accessibility_rules_v1.json`
- 输出：`poi_accessibility_filtered_v1.json`
- 报告：`poi_accessibility_filter_report_v1.json`
- 排除集：`poi_accessibility_excluded_v1.json`
- 人工复核池：`manual_review_topN_v1.json`

#### v1.1（更高精度）
- 规则文件：`poi_accessibility_rules_v1_1.json`
- 输出：`poi_accessibility_filtered_v1_1.json`
- 报告：`poi_accessibility_filter_report_v1_1.json`
- 排除集：`poi_accessibility_excluded_v1_1.json`
- 人工复核池：`manual_review_topN_v1_1.json`

业务决策已锁定：
- 保留：公交站/巴士站
- 排除：码头/停车场
- 医疗类：保留
- 语言：中简/中繁/英文都要覆盖
- 偏好：高精度优先

---

## 2. 本轮用户已确认需求（接入阶段必须遵守）

1. 先做“建议层”，后做“评分注入”（策略 C）
2. InfoCard 展示要求：
   - 简要贡献（summary）
   - 完整因子分解（可展开）
3. 要有导出能力：
   - P1：单候选点 JSON 导出
   - P2：批量 CSV + JSON 导出
4. 允许 graceful fallback：数据缺失时前端仍可运行
5. 不修改 `public/data/moduleA/`
6. Module B 数据集中在 `public/data/moduleB/`

---

## 3. 关键脚本与用途

### 3.1 清洗与特征
- `public/data/moduleB/poi/build_poi_moduleb.mjs`
  - 从 `data_202406/POI.csv` 生成：
    - `poi_cleaned_v1.json`
    - `poi_cleaning_report_v1.json`
    - `poi_type_mapping_v1.json`
    - `candidate_poi_features_v1.json`

### 3.2 残障/公共服务筛选
- `public/data/moduleB/poi/filter_accessibility_poi.mjs`（v1）
- `public/data/moduleB/poi/filter_accessibility_poi_v1_1.mjs`（v1.1 提纯）

---

## 4. 建议后续助手优先读取文件

1. `README.md`（重点 12.3）
2. `CLAUDE.md`（重点 5.1）
3. `src/App.tsx`
4. `src/components/LeftPanel.tsx`
5. `src/components/RightPanel.tsx`
6. `src/components/ui/InfoCard.tsx`
7. `src/types/MockData.ts`
8. `public/data/moduleB/poi/README.md`
9. `public/data/moduleB/poi/poi_accessibility_filter_report_v1_1.json`
10. `public/data/moduleB/poi/candidate_poi_features_v1.json`

---

## 5. 接下来应完成的工作（TODO for next LLM）

### P1（优先）前端接入建议层

目标：不改总分，只把 POI 因子接入解释与建议。

1. 在 `App.tsx` 增加对以下文件的加载（含 fallback）：
   - `candidate_poi_features_v1.json`
   - 可选优先：`poi_accessibility_filtered_v1_1.json`（用于只显示高精度 POI）
2. 在 `InfoCard.tsx` 中新增：
   - `POI Contribution Summary`（类别+分值摘要）
   - `Show details` 展开区（count_300m / count_500m / nearest_distance_m / density_score）
   - 规则建议文案（来自 `poiSuggestions`）
3. 保持 fallback：
   - 若文件缺失，则显示 `POI data unavailable`，但不报错中断。
4. 单候选点导出（JSON）：
   - 导出当前候选点基础信息 + poiFactors + poiComposite + timestamp + schemaVersion

### P2（随后）评分注入（可开关）

1. 增加 `enablePoiScoring` 开关
2. 在总分公式中引入轻量 `poiDelta`（可解释）
3. 在 InfoCard 显示 `POI score impact: +x / -x`

---

## 6. 已知风险与注意事项

1. 数据规模较大（30万级），前端不要加载全量 POI 做实时重算；优先使用离线产物。
2. `v1.1` 输出是“高精度优先”版本，适合先接入。
3. 若需进一步提纯，先看 `manual_review_topN_v1_1.json` 回灌规则后再出 `v1.2`。
4. 不要动 `public/data/moduleA/`。

---

## 7. 验收标准（供后续接入阶段）

1. InfoCard 能显示 POI 摘要与展开明细。
2. 关闭/缺失 POI 数据时，Module B 仍可完整运行。
3. 单候选点导出 JSON 可用且字段齐全。
4. 不引入新的前端 lints。
5. 所有新字段在 `public/data/moduleB/poi/README.md` 中有说明。

---

## 8. 备注

- 本交接文档由当前对话自动生成，目的是让新对话直接进入“接入实现”阶段。
- 如用户要求，以 `v1.1` 为默认数据源优先接入；`v1` 作为对照/回退。

## 9. 与 v2 解释层接入的兼容约定（2026-03-19）

为支持 leisure 子类与无障碍细分解释，前端已按“兼容优先”策略接入：

1. `candidate_poi_features_v1.json` 保持主数据源不变（避免主链风险）。
2. 若数据中存在 `poiFactorsSub`，InfoCard 额外展示子类细分（解释层增量）。
3. `poiFactorsSub` 缺失时自动回退至 v1 显示，不影响总分与交互。
4. 本阶段不改总分主链；POI 注入逻辑继续沿用现有 `poiFactors`。
