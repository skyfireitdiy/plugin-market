# Jarvis 插件市场

Jarvis 插件市场的结构化清单仓库。本仓库通过 `plugins/` 目录下的**每插件一个 YAML 文件**，
描述每个可用插件的元数据，供 Jarvis 客户端解析、展示与安装社区插件。

## 目录结构

```
plugin-market/
├── README.md
└── plugins/
    ├── <plugin-id>.yaml     # 每个插件一个文件（文件名 = 插件 id）
    └── ...
```

客户端扫描 `plugins/` 目录下所有 `.yaml` 文件，每个文件描述一个插件。

## 插件 YAML 结构

每个插件一个 YAML 文件，文件名建议等于插件 `id`。核心字段：

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

示例见 [`plugins/_example.yaml`](plugins/_example.yaml)。

## 设计原则：不记录版本号

版本号变动频繁，若写入市场清单，每次发版都需同步修改，维护成本高。
因此本仓库**不记录版本号**——客户端从插件仓库本身获取最新版本（git 分支 HEAD / tag），
本清单只维护相对稳定的元数据。

## 如何提交插件到市场

1. 在 [`plugins/`](plugins/) 目录新增一个 `<plugin-id>.yaml` 文件（字段见上，参考示例）
2. 创建 Pull Request 到本仓库
3. 经审核合并后，客户端拉取本仓库即可看到该插件

> 依赖声明（其他插件 / Python 包 / 系统命令）请写在插件自身的 `config.yaml` 的
> `dependencies` 字段，**不要**写进市场清单，避免重复维护。

## 客户端接入

在 Jarvis 的 `config.yaml` 中配置：

```yaml
plugin_market_repo: https://github.com/skyfireitdiy/plugin-market
```

客户端即可通过 `list_market_plugins()` 拉取 `plugins/` 目录下的清单并浏览插件。
