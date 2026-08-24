# POI 重新分类与细化提示词

**目标**：根据以下规范，对 `poi_cleaned_v1.json` 中的 POI 进行重新分类和细化，以支持 Module B 放大镜功能的精准展示。

**当前问题**：
- 部分诊所、专业医疗被错误归入 `accessibility_support`
- 部分酒店、银行被错误归入 `other`
- 学堂、学校等教育设施被归入 `public_service`，应独立为 `education`
- 小食亭、餐饮、小吃店、饭店、早茶等餐饮类被归入 `commercial`，应独立为 `restaurant`
- 银行应独立为 `bank` 分类，而非 `commercial`

---

## 1. 新增分类体系（v2）

在原有分类基础上，新增以下分类：

| 分类 | 图标 | 说明 | 示例 |
|------|------|------|------|
| `medical` | 🏥 | 医疗卫生设施 | 医院、诊所、卫生所、医疗中心 |
| `transport` | 🚌 | 交通运输设施 | 公交站、地铁站、停车场、加油站 |
| `commercial` | 🛍️ | 商业零售（非餐饮、非银行） | 超市、便利店、百货商场、服装店 |
| `public_service` | 🏛️ | 公共服务（非教育、非医疗） | 警察局、消防站、邮局、图书馆 |
| `leisure` | 🌳 | 休闲娱乐设施 | 公园、运动场、游乐园、咖啡馆 |
| `accessibility_support` | ♿ | 无障碍支持设施 | 无障碍卫生间、康复中心、辅具店、轮椅租赁 |
| **`education`** | 🎓 | **教育设施（新增）** | **学校、幼儿园、培训中心、学堂、补习班** |
| **`restaurant`** | 🍽️ | **餐饮设施（新增）** | **餐厅、饭店、小食亭、早茶、小吃店、面档、粥铺** |
| **`bank`** | 🏦 | **金融服务（新增）** | **银行、ATM、金融中心、保险公司** |
| `other` | 📍 | 其他无法分类的设施 | 未知类型 |

---

## 2. 分类规则与关键词映射

### 2.1 `medical` 医疗卫生
**关键词**（中文）：
- 医院、诊所、卫生所、医疗中心、门诊、中医、西医、牙科、眼科、妇科、儿科、康复、理疗、护理院、安老院、养老院

**排除规则**：
- ❌ 如果名称包含"无障碍"、"轮椅"、"辅具"等，应归入 `accessibility_support`
- ❌ 如果是"养老院"但主要提供无障碍设施，优先考虑 `accessibility_support`

**示例**：
- ✅ 中山医院 → `medical`
- ✅ 社区卫生服务中心 → `medical`
- ❌ 无障碍康复中心 → `accessibility_support`（如果主要强调无障碍）

---

### 2.2 `education` 教育设施（新增）
**关键词**（中文）：
- 学校、小学、中学、高中、大学、幼儿园、托儿所、培训中心、补习班、学堂、教室、教育中心、课程中心、艺术学校、音乐学校、舞蹈学校

**排除规则**：
- ❌ 如果是"图书馆"，应归入 `public_service`
- ❌ 如果是"运动学校"但主要是体育设施，可考虑 `leisure`

**示例**：
- ✅ 香港大学 → `education`
- ✅ 幼儿园 → `education`
- ✅ 补习中心 → `education`
- ❌ 图书馆 → `public_service`

---

### 2.3 `restaurant` 餐饮设施（新增）
**关键词**（中文）：
- 餐厅、饭店、食堂、小食亭、小吃店、面档、粥铺、早茶、茶楼、酒楼、火锅、烧烤、快餐、便当、外卖、咖啡馆、茶馆、酒吧、酒馆、夜宵、烧味、卤味

**排除规则**：
- ❌ 如果是"超市内的餐饮区"，应归入 `commercial`
- ❌ 如果是"酒店的餐厅"但酒店本身是主体，考虑 `commercial`（或新增 `hotel` 分类）
- ❌ 如果是"咖啡馆"但主要是书店或艺术空间，可考虑 `leisure`

**示例**：
- ✅ 小食亭 → `restaurant`
- ✅ 早茶楼 → `restaurant`
- ✅ 面档 → `restaurant`
- ✅ 粥铺 → `restaurant`
- ❌ 酒店 → `commercial`（暂时，或新增 `hotel`）

---

### 2.4 `bank` 金融服务（新增）
**关键词**（中文）：
- 银行、ATM、金融中心、保险公司、证券公司、基金公司、贷款公司、换汇、外汇

**排除规则**：
- ❌ 如果是"邮局"，应归入 `public_service`
- ❌ 如果是"超市内的 ATM"，应归入 `commercial`

**示例**：
- ✅ 中国银行 → `bank`
- ✅ ATM → `bank`
- ✅ 保险公司 → `bank`
- ❌ 邮局 → `public_service`

---

### 2.5 `accessibility_support` 无障碍支持设施
**关键词**（中文）：
- 无障碍卫生间、无障碍停车、轮椅租赁、辅具店、康复中心、无障碍通道、无障碍电梯、无障碍设施、盲人服务、聋人服务

**排除规则**：
- ❌ 如果是"医院"但不强调无障碍，应归入 `medical`
- ❌ 如果是"停车场"但不强调无障碍，应归入 `transport`

**示例**：
- ✅ 无障碍卫生间 → `accessibility_support`
- ✅ 轮椅租赁店 → `accessibility_support`
- ❌ 普通停车场 → `transport`

---

### 2.6 其他分类（保持不变）

**`medical`**、**`transport`**、**`commercial`**、**`public_service`**、**`leisure`** 的规则保持原有定义，但需要排除上述新增分类的内容。

---

## 3. 处理流程

### 步骤 1：数据审查
1. 加载 `poi_cleaned_v1.json`
2. 逐条审查每个 POI 的 `name`、`raw_name`、`raw_major`、`raw_minor` 字段
3. 根据上述关键词规则重新分类

### 步骤 2：关键词匹配
使用以下伪代码逻辑：

```python
def recategorize_poi(poi):
    text = f"{poi['name']} {poi['raw_name']} {poi['raw_major']} {poi['raw_minor']}".lower()
    
    # 优先级 1：无障碍
    if any(kw in text for kw in ['无障碍', '轮椅', '辅具', '康复', '盲人', '聋人']):
        return 'accessibility_support'
    
    # 优先级 2：教育
    if any(kw in text for kw in ['学校', '幼儿园', '培训', '补习', '学堂', '教育']):
        return 'education'
    
    # 优先级 3：餐饮
    if any(kw in text for kw in ['餐厅', '饭店', '小食', '面档', '粥铺', '早茶', '茶楼', '火锅', '烧烤', '快餐', '咖啡', '酒吧']):
        return 'restaurant'
    
    # 优先级 4：金融
    if any(kw in text for kw in ['银行', 'atm', '金融', '保险', '证券']):
        return 'bank'
    
    # 优先级 5：医疗
    if any(kw in text for kw in ['医院', '诊所', '卫生', '医疗', '牙科', '眼科']):
        return 'medical'
    
    # 优先级 6：交通
    if any(kw in text for kw in ['公交', '地铁', '停车', '加油', '车站']):
        return 'transport'
    
    # 优先级 7：公共服务
    if any(kw in text for kw in ['警察', '消防', '邮局', '图书馆', '政府']):
        return 'public_service'
    
    # 优先级 8：休闲
    if any(kw in text for kw in ['公园', '运动', '游乐', '娱乐', '体育']):
        return 'leisure'
    
    # 优先级 9：商业
    if any(kw in text for kw in ['超市', '便利店', '商场', '店铺', '商店']):
        return 'commercial'
    
    # 默认
    return 'other'
```

### 步骤 3：质量检查
1. 检查是否有遗漏的关键词
2. 对于边界情况（如"酒店"），标记为需要人工审查
3. 生成分类报告，统计各分类的数量

### 步骤 4：输出
更新 `poi_cleaned_v1.json`，确保：
- `category` 字段使用新的 9 个分类之一
- `subcategory` 字段进一步细化（可选）
- 保留 `quality_flags` 标记任何不确定的分类

---

## 4. 特殊情况处理

### 4.1 酒店（Hotel）
**当前状态**：被错误归入 `other` 或 `commercial`

**建议**：
- 短期：归入 `commercial`（作为商业设施）
- 长期：考虑新增 `hotel` 分类

**示例**：
- ✅ 五星酒店 → `commercial`（暂时）
- ✅ 青年旅舍 → `commercial`（暂时）

### 4.2 诊所 vs 医院
**规则**：
- 诊所、卫生所、医疗中心 → `medical`
- 专业医疗（如牙科诊所、眼科诊所） → `medical`
- ❌ 不应归入 `accessibility_support`，除非明确标注无障碍服务

### 4.3 咖啡馆 vs 餐厅
**规则**：
- 纯咖啡馆 → `restaurant`
- 咖啡馆 + 书店 → 优先 `leisure`（如果书店是主体）
- 咖啡馆 + 餐饮 → `restaurant`

---

## 5. 前端集成说明

### 5.1 图标映射
前端 `MapCanvas.tsx` 中已定义以下图标映射：

```typescript
const POI_ICON_BY_CATEGORY: Record<string, string> = {
  medical: '🏥',
  transport: '🚌',
  commercial: '🛍️',
  public_service: '🏛️',
  leisure: '🌳',
  accessibility_support: '♿',
  education: '🎓',      // 新增
  restaurant: '🍽️',    // 新增
  bank: '🏦',           // 新增
  other: '📍',
};
```

### 5.2 放大镜参数
- **搜索半径**：1km（从 1.5km 缩小）
- **网格抽稀**：3×3 网格，每个网格最多 ~4 个 POI
- **单类别上限**：40 个（总计）
- **最小间距**：50m（从 100m 缩小）
- **POI 透明度**：50%

### 5.3 数据源
- **文件**：`/data/moduleB/poi/poi_cleaned_v1.json`
- **字段**：`category`、`subcategory`、`name`、`lng`、`lat`
- **质量标记**：`quality_flags`（用于追溯分类不确定性）

---

## 6. 验收标准

完成重新分类后，应满足以下条件：

1. ✅ 所有 POI 的 `category` 字段使用新的 9 个分类之一
2. ✅ 诊所、医疗设施不在 `accessibility_support` 中
3. ✅ 酒店、银行不在 `other` 中
4. ✅ 学校、幼儿园等教育设施在 `education` 中
5. ✅ 餐饮类设施在 `restaurant` 中
6. ✅ 银行在 `bank` 中
7. ✅ 生成分类报告，统计各分类的 POI 数量
8. ✅ 标记任何不确定的分类，供人工审查

---

## 7. 联系与反馈

如有疑问或发现新的分类问题，请：
1. 在 `quality_flags` 中标记为 `needs_manual_review`
2. 在分类报告中记录问题 POI 的 ID 和原因
3. 反馈给主要开发者进行后续调整

---

**版本**：v1  
**生成日期**：2026-03-30  
**适用范围**：Module B 放大镜 POI 展示功能
