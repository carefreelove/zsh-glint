![zsh-glint — 为命令行点亮一束微光。](docs/assets/banner.svg)

[![CI](https://github.com/carefreelove/zsh-glint/actions/workflows/ci.yml/badge.svg)](https://github.com/carefreelove/zsh-glint/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/carefreelove/zsh-glint)](https://github.com/carefreelove/zsh-glint/releases)
[![Zsh 5.9+](https://img.shields.io/badge/Zsh-5.9%2B-8be9dd)](docs/guide.zh-CN.md#环境要求)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README.md) · **简体中文**

轻量、安静的历史命令建议。输入前缀，按 **→** 接受灰色提示，按 **Tab** 使用 Zsh 原生路径和参数补全。离线运行，无需额外插件运行时。

![真实 Zsh 录制：灰色历史建议、右键接受、原生目录补全和状态查询。](docs/assets/demo.gif)

[静态图片](docs/assets/demo.png) · [原始终端录制](docs/assets/demo.cast) · [演示制作方法](CONTRIBUTING.md#recording-the-demo)

## 一分钟安装

需要 macOS 或 Linux，以及 **Zsh 5.9+**。

```sh
git clone https://github.com/carefreelove/zsh-glint.git
cd zsh-glint
zsh scripts/install.zsh
```

随后打开新的 Zsh 会话。安装器会备份 `.zshrc` 并添加一个托管区块，**请保留克隆目录**。自定义 `ZDOTDIR`、Oh My Zsh 和手动安装见[完整指南](docs/guide.zh-CN.md#安装)。

想先试用，可以在已有 Zsh 会话中进入克隆目录，运行：

```zsh
source ./zsh-glint.plugin.zsh
```

## 操作少一点，输入顺一点

| 你的操作 | glint 的响应 |
| --- | --- |
| 输入历史命令的前缀 | 以灰色显示最近匹配的历史命令 |
| 在行尾按 → | 填入建议，**仍需按 Enter 才会执行** |
| 在行中按 → | 正常移动光标 |
| 按 Tab | 使用 Zsh 原生文件、目录和参数补全 |
| 运行 `zsh-glint doctor` | 自检配置、hooks、widget 归属和补全目录权限 |
| 运行 `zsh-glint off` / `on` | 暂停或恢复建议 |

Emacs 与 Vi insert 模式均有真实终端测试。颜色、长度限制和快捷键见[配置指南](docs/guide.zh-CN.md#配置)。

## 性能有数据，也有测量方法

v0.2 使用 Zsh 原生数组搜索，并复用输入未变时的查询结果。在本次 macOS arm64 / Zsh 5.9 基准中，**1,000 条合成候选的首次未命中查询**中位耗时从 **2.21 ms 降至 0.10 ms**。数据受硬件、工作负载和机器负载影响，不包含终端渲染或 Shell 启动时间。

[完整结果与方法](docs/performance.md) · [优化前数据](docs/benchmark-before.json) · [优化后数据](docs/benchmark-after.json)

## 本地运行，行为明确，方便卸载

- 使用当前 Shell 已加载的历史，不联网，不另存命令历史。
- 灰色建议**仅来自历史**；路径和参数使用 Tab 补全。没有 AI 或模糊搜索。
- `doctor` 只报告检查结果与条目数，不打印历史命令，也不修改配置。退出码 `0` 表示没有警告，`1` 表示有待处理项。
- 保留标准 `compinit` 权限检查。其他使用 `POSTDISPLAY` 的插件可能冲突，建议只启用一种历史建议插件。

卸载托管配置后，打开新的 Zsh 会话：

```sh
zsh scripts/uninstall.zsh
```

更多说明：[历史与隐私](docs/guide.zh-CN.md#历史与隐私)、[兼容性](docs/compatibility.md)、[从旧名称升级](docs/guide.zh-CN.md#从旧名称升级)。

## 参与项目

[使用指南](docs/guide.zh-CN.md) · [更新记录](CHANGELOG.md) · [贡献指南](CONTRIBUTING.md) · [版本发布](https://github.com/carefreelove/zsh-glint/releases) · [MIT 许可证](LICENSE)

运行 `python3 -m unittest discover -s tests -v` 执行测试。CI 覆盖 macOS 和 Linux，包括真实 PTY 交互、安装迁移、自检和插件加载顺序。
