# Jarvis 插件市场

Jarvis 插件市场的结构化清单仓库。本仓库维护一份机器可读的插件清单（[`market.yaml`](market.yaml)），
供 Jarvis 客户端解析、展示与安装社区插件。

## 什么是插件市场

Jarvis 插件生态分散在各处，缺乏统一的发现入口。本仓库作为**集中式插件目录**，
通过一份结构化清单（YAML）描述每个可用插件的元数据（名称/介绍/仓库链接/发布分支/作者/许可证/分类），
让用户能方便地发现、浏览、检索并安装社区插件。

## 清单结构

见 [`market.yaml`](market.yaml) 顶部注释。核心字段：

| 字段 | 说明 |
|------|------|
| `id` | 插件唯一标识（建议与插件 config.yaml 的 `name` 一致） |
| `name` | 插件展示名 |
| `description` | 插件功能说明 |
| `repo` | 插件源码仓库地址（git 仓库） |
| `branch` | 插件发布分支（默认 `main`） |
| `author` | 插件作者 |
| `license` | 开源协议 |
| `categories` | 分类/标签（可选） |

## 设计原则：不记录版本号

版本号变动频繁，若写入市场清单，每次发版都需同步修改，维护成本高。
因此本清单**不记录版本号**——客户端从插件仓库本身获取最新版本（git 分支 HEAD / tag），
本清单只维护相对稳定的元数据。

## 如何提交插件到市场

1. 在 [`market.yaml`](market.yaml) 的 `plugins` 列表新增一条记录（字段见上）
2. 创建 Pull Request 到本仓库
3. 经审核合并后，客户端拉取本清单即可看到该插件

> 依赖声明（其他插件 / Python 包 / 系统命令）请写在插件自身的 `config.yaml` 的
> `dependencies` 字段，**不要**写进市场清单，避免重复维护。

## 客户端接入

在 Jarvis 的 `config.yaml` 中配置：

```yaml
plugin_market_repo: https://github.com/skyfireitdiy/plugin-market
```

客户端即可通过 `list_market_plugins()` 拉取本清单并浏览插件。
