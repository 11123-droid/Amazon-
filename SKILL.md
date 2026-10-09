---
name: sellersprite-amazon-low-rating-dashboard
description: 使用卖家精灵 SellerSprite MCP，在指定 Amazon 站点和一级类目下筛选有足够评分样本支撑的低评分叶子类目，并生成固定格式的离线 HTML BI 看板。适用于用户说“Amazon 类目差评选品法”“低评分叶子类目”“差评类目机会”“Amazon 低评分看板”，或只给出商品/细分类目描述并希望先定位所属一级类目的场景；不用于关键词趋势、ASIN 趋势或类目销量趋势。
---

# Amazon 类目差评选品法

根据用户输入调用 SellerSprite MCP，生成一个自包含 HTML 文件。不要用关键词、ASIN、竞品样本或 `market_research_statistics` 替代类目评分筛选。

## 输入

- 必填：站点，以及一级类目名称、一级 `nodeIdPath`，或可唯一定位一级类目的商品/细分类目描述。
- 站点仅限 `US`、`UK`、`AU`、`CA`、`JP`、`DE`、`FR`、`IT`、`ES`、`MX`、`BR`、`IN`、`AE`。
- `maxAvgRating` 默认 `4.0`，范围 `(0, 5]`。
- `minAvgRatings` 默认 `30`，必须为正整数。
- 月份固定为执行日上一个完整自然月，格式 `yyyyMM`。

输入缺失或无效时先请用户补充，不调用 MCP，不生成文件。用户若只给商品描述，先用 `product_node` 找精确语义匹配路径；只有当匹配结果能唯一确定同一个一级节点时才继续，否则列出一级候选请用户选择。

## 执行

执行前完整阅读 [references/workflow.md](references/workflow.md)。使用当前环境实际暴露的 SellerSprite MCP 工具名和实时 schema；每次请求都设置最小必要 `returnFields`。

完成数据采集与叶子验证后，将固定结构 JSON 交给 [scripts/build_dashboard.py](scripts/build_dashboard.py)。脚本必须使用 [assets/dashboard-template.html](assets/dashboard-template.html)，输出到当前工作区 `outputs/amazon_low_rating_leaf_categories_<站点>_<月份>.html`。

不得修改 `sources/` 下的任何同步文件。不得保存或输出 SellerSprite 密钥。

## 交付

最终回复只说明：站点、一级类目、数据月份、评分阈值、最低评分样本数阈值、结果数量、HTML 文件路径。不要在聊天中复述明细或排行。
