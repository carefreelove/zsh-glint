# 使用指南

[English](guide.md) · [简体中文](guide.zh-CN.md) · [首页](../README.zh-CN.md)

轻量、离线、原生的 Zsh 自动补全插件。输入命令时显示灰色历史建议，按 **→** 接受，按 **Tab** 使用 Zsh 的路径和参数补全。

```text
❯ git st│atus          输入 git st，atus 以灰色显示
❯ git status│          按 → 接受建议，按 Enter 才执行

❯ cd Doc│             按 Tab 补全目录
❯ cd Documents/│
```

上方是交互示意；灰色提示来自你自己的历史记录。

## 功能

- **实时历史建议**：按字面前缀匹配，优先显示最近使用过的完整命令。
- **原生 Tab 补全**：保留 Zsh 的文件、目录、命令及参数补全能力，包括带空格的路径。
- **自然的编辑操作**：光标在行尾时按 → 接受建议，在行中时仍向右移动；支持 Emacs 和 Vi insert 模式，接受建议后可以撤销。
- **可配置**：建议颜色、最短前缀、长度上限、历史扫描上限及启用开关。
- **本地运行**：插件运行时仅使用 Zsh，不联网，不调用 AI API，不另存命令历史。
- **可逆安装**：自动备份配置，只维护标记区块；重复安装不会重复添加配置。

## 环境要求

- **Zsh 5.9+**，macOS 或 Linux，交互式终端。
- UTF-8 终端用于中文显示；256 色终端可完整显示默认灰色。
- 安装脚本使用系统自带的 `mktemp`、`cp`、`cmp`、`mv` 等工具。
- 开发测试额外需要 Python 3.9+ 和 Git，无第三方 Python 依赖。

检查版本：

```sh
zsh --version
```

## 安装

```sh
git clone https://github.com/carefreelove/zsh-glint.git
cd zsh-glint
zsh scripts/install.zsh
```

随后打开一个新的 Zsh 终端。安装器在 `${ZDOTDIR:-$HOME}/.zshrc` 末尾添加 `source` 区块，因此**请保留克隆目录，移动目录后重新运行安装器**。已有配置在修改前备份为 `.zshrc.backup.XXXXXXXX`，权限保持不变；已有符号链接保持不变，更新其目标文件。

指定配置文件：

```sh
zsh scripts/install.zsh --rc /path/to/.zshrc
```

仅在当前 Zsh 会话试用，不修改启动配置：

```zsh
source ./zsh-glint.plugin.zsh
```

手动安装或插件管理器也可以直接加载 `zsh-glint.plugin.zsh`。例如 Oh My Zsh：

```sh
git clone https://github.com/carefreelove/zsh-glint.git \
  "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-glint"
```

将 `zsh-glint` 加入已有 `plugins=(...)` 列表即可。手动安装和插件管理器安装不需要再运行安装脚本。

## 从旧名称升级

本项目原名 `terminal-completion`，现更名为 **zsh-glint**。在已有克隆目录中运行：

```sh
git remote set-url origin https://github.com/carefreelove/zsh-glint.git
git pull --ff-only
zsh scripts/install.zsh
```

随后打开新的 Zsh 会话。安装器会将原来的托管区块迁移到 `zsh-glint`；卸载器也能识别旧区块。旧的 `terminal-completion.plugin.zsh` 入口、`terminal-completion` 命令、`terminal-completion-accept` / `terminal-completion-toggle` widgets 继续可用。现有 `TC_*` 配置项保持不变。

如果通过 Oh My Zsh 的旧名称安装，可以继续保留原来的目录和 `plugins=(... terminal-completion)` 配置；新安装推荐使用 `zsh-glint`。不需要更名现有本地克隆目录。

## 快速体验

在加载插件的 Zsh 中，先运行一次：

```sh
git status
```

然后输入 `git st`，应看到灰色 `atus`。按 → 将建议写入输入行，再按 Enter 执行。建议本身从不自动执行。

常用操作：

| 操作 | 效果 |
| --- | --- |
| →，光标位于行尾 | 接受当前建议 |
| →，光标位于行中 | 正常移动光标 |
| Tab | 使用原生 completion system |
| Ctrl+_，Emacs 模式 | 撤销刚才接受的建议 |
| `zsh-glint off` | 暂停历史建议，Tab 仍可用 |
| `zsh-glint on` | 启用历史建议 |
| `zsh-glint toggle` | 切换开关 |
| `zsh-glint doctor` | 自检配置、hooks、补全目录权限和常见冲突 |
| `zsh-glint status` | 查看版本、状态、缓存条数 |
| `zsh-glint refresh` | 立即刷新历史缓存 |
| `zsh-glint unload` | 移除插件 hooks 并恢复仍由插件管理的方向键 widgets |

## 配置

将以下配置放在 `.zshrc` 中加载插件的语句**之前**：

```zsh
TC_ENABLED=1               # 1 开启，0 关闭
TC_STYLE='fg=8'            # Zsh highlight 格式，如 fg=cyan 或 fg=244
TC_MIN_PREFIX=2            # 输入至少几个字符才显示建议，1–1024
TC_MAX_BUFFER=512          # 输入与整条候选命令的字符数上限，1–65536
TC_HISTORY_LIMIT=1000      # 每次刷新最多考察的最近历史条数，1–100000
TC_INIT_COMPLETION=1       # 没有初始化原生补全时执行标准 compinit
```

无效的数字配置回退到默认值。颜色、开关和长度配置对后续重绘生效；修改历史条数后运行 `zsh-glint refresh`。`TC_INIT_COMPLETION` 仅在加载时读取。

可在加载插件**之后**增加快捷键：

```zsh
bindkey -M emacs '^ ' zsh-glint-accept  # Ctrl+Space 接受
bindkey -M viins '^ ' zsh-glint-accept
bindkey -M emacs '^X^T' zsh-glint-toggle # Ctrl+X，Ctrl+T 切换
```

插件通过包装 `forward-char` 和 `vi-forward-char` 接受建议，不重写你的 keymap。若你的右方向键绑定到其他自定义 widget，请自行将所需快捷键绑定到 `zsh-glint-accept`。

如果已有 Oh My Zsh 或自己的 `compinit` 配置，请将本插件放在它们之后加载。插件检测到 `_comps` 时不会重复初始化，也不修改全局 `zstyle`。想完全自行管理补全初始化，可设置 `TC_INIT_COMPLETION=0`。

## 历史与隐私

建议取自当前 Zsh 已加载的历史，按最近优先排序，在每次显示新 prompt 时刷新缓存。跨会话历史是否保存和共享，由你原有的 `HISTFILE`、`HISTSIZE`、`SAVEHIST`、`SHARE_HISTORY` 等配置决定；本插件不修改这些选项。

以空白开头或包含换行、控制字符的历史不会进入建议缓存；输入本身以空白开头时也不显示建议。若要让以空格开头的敏感命令不被 Zsh 保存，可在自己的配置中启用 `setopt HIST_IGNORE_SPACE`。插件不是密钥检测器，普通历史中的敏感内容仍可能被建议。

## 卸载

```sh
zsh scripts/uninstall.zsh
```

使用了 `--rc` 安装时，卸载也指定相同路径。随后打开新终端，或在当前会话执行：

```zsh
zsh-glint unload
```

卸载脚本仅移除它管理的 `source` 区块，并备份配置；保留项目目录和历史记录。手动配置或插件管理器安装，请从相应配置中移除加载项。自行添加的快捷键也由你移除。`unload` 保留已经初始化的原生补全和 helper 函数；如果其他插件保留了旧 widget，则需要打开新会话后再加载，以避免递归；重新加载后如需建议，请执行 `zsh-glint on`。

## 边界与排错

- **灰色提示仅来自历史**。没有匹配历史时不显示；路径和命令参数通过 Tab 补全，复杂语法由 Zsh 原生补全处理。
- 首版不提供模糊历史检索、AI 建议、Bash/Fish/PowerShell 接入。
- Vi command 模式、行中编辑、多行输入、选区操作和粘贴队列尚未处理完时，不显示建议。
- 不建议同时启用其他接管 `POSTDISPLAY` 的历史建议插件（例如 `zsh-autosuggestions`）。本插件会避让已存在的其他显示内容，但不保证任意加载顺序下的完整兼容性。
- 默认的右方向键行为已测试；终端自定义快捷键、其他插件接管 widgets 时可能需要手动绑定。
- 没有建议时，先检查 `zsh-glint status`、当前历史以及最短前缀设置。
- 标准 `compinit` 若报告不安全的补全目录，请修复目录权限后重试；插件不会绕过检查。
- 安装器发现损坏或重复的标记区块会拒绝修改。配置写回使用换行结尾；原文件若无末尾换行，会补上换行。

## 开发与验证

```sh
python3 -m unittest discover -s tests -v
```

测试在临时目录中运行，不修改个人 `.zshrc`。覆盖字面前缀、Unicode、历史筛选、配置校验、重复加载、安装卸载与权限、旧名称兼容和配置迁移，以及真实 PTY 下的提示颜色、接受与撤销、行中编辑、Vi 模式、Tab 路径/参数补全和其他插件显示内容的保留。

GitHub Actions 在 Linux 和 macOS 上运行语法检查及同一套测试。实现说明见 [docs/architecture.md](architecture.md)。

## 许可证

[MIT](../LICENSE)
