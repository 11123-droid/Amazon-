# SellerSprite 数据与执行规则

## 1. 一级类目定位

用 `product_node`，字段只取 `nodeIdPath,nodeLabelPath,nodeLabelPathLocale,isLeaf`。

- 用户给一级 `nodeIdPath`：按 `:` 分割后必须只有一个 ID。
- 用户给一级类目名称：只接受语义一致且路径层级为 1 的唯一结果。
- 用户给商品或细分类目描述：先查语义一致的完整路径，取其第一个节点和英文路径第一段作为一级类目。只有所有精确匹配都指向同一一级节点时才可自动继续。
- 多个一级候选无法唯一判断时，请用户选择，禁止按销量或返回顺序猜测。

## 2. 候选采集

使用 `market_research`，禁止替换成关键词、ASIN、竞品或统计接口。首个请求的逻辑参数：

```json
{
  "marketplace": "US",
  "nodeIdPath": "一级节点",
  "month": "yyyyMM",
  "maxAvgRating": 4,
  "minAvgRatings": 30,
  "page": 1,
  "size": 200,
  "returnFields": "nodeIdPath,nodeLabelPath,avgRating,avgRatings"
}
```

参数嵌套和类型服从实时 MCP schema。读取 `data.pages`、`data.page`、`data.total`、`data.items`，从第 1 页连续拉到最后一页。所有页参数必须一致。按完整 `nodeIdPath` 去重；重复时保留字段完整且属于查询月份的记录。核心字段缺失、为空或结构不可确认时不得估算、补零或换接口替代。

## 3. 固定筛选

合并分页后按顺序执行：

1. 保留 `0 < avgRating <= maxAvgRating` 且 `avgRatings >= minAvgRatings`。
2. 只保留 `nodeIdPath` 层级不少于 4。
3. 父级剔除：若另一路径满足 `B.startsWith(A + ":")`，剔除 `A`。必须在全量合并去重后判断。
4. 对每个候选调用 `product_node(nodeIdPath=完整路径)`。
   - 精确记录明确 `isLeaf=true`：保留。
   - 返回成功、`code="OK"` 且 `data=[]`：保留，这是叶子结果。
   - 返回下级节点：剔除。
   - 报错、超时、结构异常或无法确认：剔除并记为未验证。
5. 最终按 `avgRating` 升序，再按完整 `nodeIdPath` 升序。

## 4. 中英文路径

- 英文：优先取 `market_research.nodeLabelPath`；缺失时取 `product_node` 精确路径记录；仍缺失则写 `未匹配（MCP 未返回）`。
- 中文：取路径最后一个节点 ID，调用 `product_node(keyword=最后节点ID)`，只接受 `nodeIdPath` 完全相等记录的 `nodeLabelPathLocale`。缺失时写 `未匹配（MCP 未返回）`，不得自行翻译。
- 查询叶子完整路径得到的空数组只用于叶子验证，不能用来清空名称。

## 5. 生成数据

传给生成脚本的 JSON：

```json
{
  "status": "ready",
  "blockReason": "",
  "marketplace": "US",
  "rootCategory": "Tools & Home Improvement",
  "rootNodeIdPath": "228013",
  "month": "202609",
  "maxAvgRating": 4,
  "minAvgRatings": 30,
  "resultCount": 1,
  "items": [
    {
      "nodeIdPath": "228013:...",
      "avgRating": 3.8,
      "categoryPathEn": "...",
      "categoryPathZh": "..."
    }
  ]
}
```

原始 `avgRatings` 用于筛选和执行期校验，不写入最终 `items`。每条记录只展示评分、英文路径、中文路径和一条以 5 分为满分的进度条。

若 MCP 核心数据无法取得，仍可用相同模板生成 `status="blocked"` 的异常页，写入已确认参数和简短原因，不得伪造列表。结果为 0 时是正常 `ready` 页面。

## 6. 交付前校验

- 参数、月份与用户输入或默认值一致。
- 每条均通过评分、样本、层级、父级和叶子验证。
- 顺序为评分升序、路径升序。
- 页面不显示单条 `avgRatings`、销量、销售额、价格、商品数、图表、筛选器、输入框或按钮。
- HTML 不含未替换占位符，不依赖 CDN、网络字体、远程脚本或图片。
