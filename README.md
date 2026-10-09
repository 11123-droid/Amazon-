# Amazon 类目差评选品法

一个可复用的 Codex Skill：调用 SellerSprite MCP，在指定 Amazon 站点和一级类目下筛选有足够评分样本支撑的低评分叶子类目，并生成固定格式的离线 HTML BI 看板。

## 使用

安装后可以直接说：

```text
使用 Amazon 类目差评选品法，US，手持花洒。
```

默认评分阈值为 `4.0`，最低评分样本数为 `30`。也可以在请求中修改这两个参数。

## 前提

- Codex 已配置可用的 SellerSprite MCP。
- MCP 至少提供 `product_node` 和 `market_research`。
- 认证密钥只保存在本机环境配置中，不要提交到仓库。

## 安装

将本仓库安装为 Codex Skill，Skill 名称保持为：

```text
sellersprite-amazon-low-rating-dashboard
```

仓库中不包含 SellerSprite 密钥或看板业务数据。
