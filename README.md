# zsh-glint

[![CI](https://github.com/carefreelove/zsh-glint/actions/workflows/ci.yml/badge.svg)](https://github.com/carefreelove/zsh-glint/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](#english) · [简体中文](#简体中文)

## English

A lightweight, offline Zsh plugin for command-line suggestions. See history suggestions in gray, press **→** to accept them, and use **Tab** for Zsh's native path and argument completion.

```text
❯ git st│atus          Type git st; atus appears in gray
❯ git status│          Press → to accept; Enter to execute

❯ cd Doc│             Press Tab to complete a directory
❯ cd Documents/│
```

This is an interaction sketch. Actual suggestions come from your own shell history.

### Features

- **Inline history suggestions:** literal prefix matching, with the most recent matching command first.
- **Native Tab completion:** Zsh completes files, directories, commands, and arguments, including paths containing spaces.
- **Natural editing:** the right arrow accepts a suggestion at the end of the line and moves the cursor normally elsewhere. Supports Emacs and Vi insert mode; accepting a suggestion can be undone.
- **Configurable:** appearance, minimum prefix length, buffer limit, history scan limit, and an enable switch.
- **Local execution:** the plugin itself uses only Zsh, makes no network requests, calls no AI APIs, and creates no additional history files.
- **Reversible installation:** backs up your configuration and manages a marked block. Repeated installation does not add duplicate blocks.

### Requirements

- **Zsh 5.9+** on macOS or Linux, running in an interactive terminal.
- A UTF-8 terminal for Unicode text; a 256-color terminal for the default gray style.
- The installer uses standard system utilities such as `mktemp`, `cp`, `cmp`, and `mv`.
- Development tests additionally require Python 3.9+ and Git, with no third-party Python dependencies.

Check your version:

```sh
zsh --version
```

### Installation

```sh
git clone https://github.com/carefreelove/zsh-glint.git
cd zsh-glint
zsh scripts/install.zsh
```

Open a new Zsh session to activate the plugin. The installer appends a `source` block to `${ZDOTDIR:-$HOME}/.zshrc`, so **keep the clone directory in place and rerun the installer if you move it**. Existing configuration is backed up as `.zshrc.backup.XXXXXXXX` before changes. File permissions are preserved; existing symlinks stay intact and their targets are updated.

Choose a different configuration file:

```sh
zsh scripts/install.zsh --rc /path/to/.zshrc
```

Try it in your current Zsh session without changing startup configuration:

```zsh
source ./zsh-glint.plugin.zsh
```

You can also load `zsh-glint.plugin.zsh` manually or through a plugin manager. For Oh My Zsh:

```sh
git clone https://github.com/carefreelove/zsh-glint.git \
  "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-glint"
```

Add `zsh-glint` to your existing `plugins=(...)` list. Manual and plugin-manager installations do not require the install script.

### Upgrading from the previous name

This project was previously called `terminal-completion` and is now **zsh-glint**. In your existing clone, run:

```sh
git remote set-url origin https://github.com/carefreelove/zsh-glint.git
git pull --ff-only
zsh scripts/install.zsh
```

Then open a new Zsh session. The installer migrates the old managed block, and the uninstaller recognizes either name. The legacy `terminal-completion.plugin.zsh` entry point, `terminal-completion` command, and `terminal-completion-accept` / `terminal-completion-toggle` widgets remain available. Existing `TC_*` configuration variables are unchanged.

If you installed through Oh My Zsh under the old name, you can retain that directory and your `plugins=(... terminal-completion)` entry. New installations should use `zsh-glint`. You do not need to rename an existing local clone directory.

### Quick start

In a Zsh session with the plugin loaded, run this once:

```sh
git status
```

Now type `git st`. The remaining `atus` should appear in gray. Press → to insert it, then Enter to execute. A suggestion never executes automatically.

| Action | Behavior |
| --- | --- |
| → at the end of the line | Accept the current suggestion |
| → inside the line | Move the cursor normally |
| Tab | Use the native completion system |
| Ctrl+_ in Emacs mode | Undo accepting the suggestion |
| `zsh-glint off` | Pause history suggestions; Tab still works |
| `zsh-glint on` | Enable history suggestions |
| `zsh-glint toggle` | Toggle suggestions |
| `zsh-glint status` | Show version, state, and cached history count |
| `zsh-glint refresh` | Refresh the history cache immediately |
| `zsh-glint unload` | Remove plugin hooks and restore arrow-key widgets still owned by the plugin |

### Configuration

Place configuration **before** the plugin's loading statement in `.zshrc`:

```zsh
TC_ENABLED=1               # 1 to enable, 0 to disable
TC_STYLE='fg=8'            # Zsh highlight format; e.g. fg=cyan or fg=244
TC_MIN_PREFIX=2            # Minimum input length, 1–1024 characters
TC_MAX_BUFFER=512          # Input and full candidate limit, 1–65536 characters
TC_HISTORY_LIMIT=1000      # Recent history entries to examine, 1–100000
TC_INIT_COMPLETION=1       # Run standard compinit if completion is not initialized
```

Invalid numeric values fall back to defaults. Style, enable state, and length changes apply on subsequent redraws. After changing the history limit, run `zsh-glint refresh`. `TC_INIT_COMPLETION` is read only when loading the plugin. The `TC_*` prefix is retained for compatibility with existing installations.

Add custom shortcuts **after** loading the plugin:

```zsh
bindkey -M emacs '^ ' zsh-glint-accept  # Ctrl+Space to accept
bindkey -M viins '^ ' zsh-glint-accept
bindkey -M emacs '^X^T' zsh-glint-toggle # Ctrl+X, Ctrl+T to toggle
```

The plugin wraps `forward-char` and `vi-forward-char` without rewriting your keymaps. If your right arrow uses a different custom widget, bind your preferred shortcut to `zsh-glint-accept` explicitly.

Load the plugin after Oh My Zsh or your own `compinit` setup. If `_comps` exists, initialization is skipped; global `zstyle` settings are not changed. Set `TC_INIT_COMPLETION=0` to manage completion initialization entirely yourself.

### History and privacy

Suggestions come from history already loaded by the current Zsh session, with the most recent matches first. The cache refreshes before each new prompt. Persistence and sharing across sessions follow your existing `HISTFILE`, `HISTSIZE`, `SAVEHIST`, and `SHARE_HISTORY` settings; the plugin does not change them.

History entries starting with whitespace or containing newlines or control characters are excluded. Input starting with whitespace also suppresses suggestions. To keep space-prefixed sensitive commands out of Zsh history, you can enable `setopt HIST_IGNORE_SPACE` in your own configuration. The plugin is not a secret detector: sensitive text in ordinary history entries may still be suggested.

### Uninstallation

```sh
zsh scripts/uninstall.zsh
```

If you installed with `--rc`, use the same path when uninstalling. Open a new terminal, or run this in the current session:

```zsh
zsh-glint unload
```

The uninstaller backs up your configuration and removes only its managed `source` block. It keeps the project directory and shell history. For manual or plugin-manager installations, remove the corresponding loading entry yourself. Remove any shortcuts you added manually as well. `unload` leaves native completion and helper functions available; after sourcing the plugin again, run `zsh-glint on` to re-enable suggestions.

### Limitations and troubleshooting

- **Inline suggestions come only from history.** With no matching history, nothing appears. Paths and arguments are completed with Tab, and Zsh handles complex completion syntax.
- The initial version does not provide fuzzy history search, AI suggestions, or Bash/Fish/PowerShell integration.
- Suggestions are suppressed in Vi command mode, inside the line, for multiline input, during selection, and while input remains queued during a paste.
- Running another history-suggestion plugin that owns `POSTDISPLAY`, such as `zsh-autosuggestions`, is not recommended. zsh-glint yields to existing foreign display content but does not guarantee compatibility with arbitrary plugin loading orders.
- Default arrow-key behavior is tested. Custom terminal shortcuts or other widget wrappers may require an explicit binding.
- If suggestions do not appear, check `zsh-glint status`, available history, and the minimum prefix length.
- If standard `compinit` reports insecure completion directories, correct their permissions and try again. The plugin does not bypass the audit.
- The installer rejects malformed or duplicate managed blocks. Configuration files are written with a final newline, adding one if the original file lacked it.

### Development and testing

```sh
python3 -m unittest discover -s tests -v
```

Tests run in temporary directories without modifying your personal `.zshrc`. Coverage includes literal prefixes, Unicode, history filtering, configuration validation, repeated loading, installation and permissions, legacy-name compatibility and migration, and real PTY interactions for gray suggestions, acceptance and undo, cursor movement, Vi mode, native Tab completion, and preservation of other plugins' display content.

GitHub Actions runs syntax checks and the same test suite on Linux and macOS. Additional implementation notes are in [docs/architecture.md](docs/architecture.md) (Chinese).

### License

[MIT](LICENSE)

---

## 简体中文

轻量、离线、原生的 Zsh 自动补全插件。输入命令时显示灰色历史建议，按 **→** 接受，按 **Tab** 使用 Zsh 的路径和参数补全。

```text
❯ git st│atus          输入 git st，atus 以灰色显示
❯ git status│          按 → 接受建议，按 Enter 才执行

❯ cd Doc│             按 Tab 补全目录
❯ cd Documents/│
```

上方是交互示意；灰色提示来自你自己的历史记录。

### 功能

- **实时历史建议**：按字面前缀匹配，优先显示最近使用过的完整命令。
- **原生 Tab 补全**：保留 Zsh 的文件、目录、命令及参数补全能力，包括带空格的路径。
- **自然的编辑操作**：光标在行尾时按 → 接受建议，在行中时仍向右移动；支持 Emacs 和 Vi insert 模式，接受建议后可以撤销。
- **可配置**：建议颜色、最短前缀、长度上限、历史扫描上限及启用开关。
- **本地运行**：插件运行时仅使用 Zsh，不联网，不调用 AI API，不另存命令历史。
- **可逆安装**：自动备份配置，只维护标记区块；重复安装不会重复添加配置。

### 环境要求

- **Zsh 5.9+**，macOS 或 Linux，交互式终端。
- UTF-8 终端用于中文显示；256 色终端可完整显示默认灰色。
- 安装脚本使用系统自带的 `mktemp`、`cp`、`cmp`、`mv` 等工具。
- 开发测试额外需要 Python 3.9+ 和 Git，无第三方 Python 依赖。

检查版本：

```sh
zsh --version
```

### 安装

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

### 从旧名称升级

本项目原名 `terminal-completion`，现更名为 **zsh-glint**。在已有克隆目录中运行：

```sh
git remote set-url origin https://github.com/carefreelove/zsh-glint.git
git pull --ff-only
zsh scripts/install.zsh
```

随后打开新的 Zsh 会话。安装器会将原来的托管区块迁移到 `zsh-glint`；卸载器也能识别旧区块。旧的 `terminal-completion.plugin.zsh` 入口、`terminal-completion` 命令、`terminal-completion-accept` / `terminal-completion-toggle` widgets 继续可用。现有 `TC_*` 配置项保持不变。

如果通过 Oh My Zsh 的旧名称安装，可以继续保留原来的目录和 `plugins=(... terminal-completion)` 配置；新安装推荐使用 `zsh-glint`。不需要更名现有本地克隆目录。

### 快速体验

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
| `zsh-glint status` | 查看版本、状态、缓存条数 |
| `zsh-glint refresh` | 立即刷新历史缓存 |
| `zsh-glint unload` | 移除插件 hooks 并恢复仍由插件管理的方向键 widgets |

### 配置

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

### 历史与隐私

建议取自当前 Zsh 已加载的历史，按最近优先排序，在每次显示新 prompt 时刷新缓存。跨会话历史是否保存和共享，由你原有的 `HISTFILE`、`HISTSIZE`、`SAVEHIST`、`SHARE_HISTORY` 等配置决定；本插件不修改这些选项。

以空白开头或包含换行、控制字符的历史不会进入建议缓存；输入本身以空白开头时也不显示建议。若要让以空格开头的敏感命令不被 Zsh 保存，可在自己的配置中启用 `setopt HIST_IGNORE_SPACE`。插件不是密钥检测器，普通历史中的敏感内容仍可能被建议。

### 卸载

```sh
zsh scripts/uninstall.zsh
```

使用了 `--rc` 安装时，卸载也指定相同路径。随后打开新终端，或在当前会话执行：

```zsh
zsh-glint unload
```

卸载脚本仅移除它管理的 `source` 区块，并备份配置；保留项目目录和历史记录。手动配置或插件管理器安装，请从相应配置中移除加载项。自行添加的快捷键也由你移除。`unload` 保留已经初始化的原生补全和 helper 函数；重新加载后如需建议，请执行 `zsh-glint on`。

### 边界与排错

- **灰色提示仅来自历史**。没有匹配历史时不显示；路径和命令参数通过 Tab 补全，复杂语法由 Zsh 原生补全处理。
- 首版不提供模糊历史检索、AI 建议、Bash/Fish/PowerShell 接入。
- Vi command 模式、行中编辑、多行输入、选区操作和粘贴队列尚未处理完时，不显示建议。
- 不建议同时启用其他接管 `POSTDISPLAY` 的历史建议插件（例如 `zsh-autosuggestions`）。本插件会避让已存在的其他显示内容，但不保证任意加载顺序下的完整兼容性。
- 默认的右方向键行为已测试；终端自定义快捷键、其他插件接管 widgets 时可能需要手动绑定。
- 没有建议时，先检查 `zsh-glint status`、当前历史以及最短前缀设置。
- 标准 `compinit` 若报告不安全的补全目录，请修复目录权限后重试；插件不会绕过检查。
- 安装器发现损坏或重复的标记区块会拒绝修改。配置写回使用换行结尾；原文件若无末尾换行，会补上换行。

### 开发与验证

```sh
python3 -m unittest discover -s tests -v
```

测试在临时目录中运行，不修改个人 `.zshrc`。覆盖字面前缀、Unicode、历史筛选、配置校验、重复加载、安装卸载与权限、旧名称兼容和配置迁移，以及真实 PTY 下的提示颜色、接受与撤销、行中编辑、Vi 模式、Tab 路径/参数补全和其他插件显示内容的保留。

GitHub Actions 在 Linux 和 macOS 上运行语法检查及同一套测试。实现说明见 [docs/architecture.md](docs/architecture.md)。

### 许可证

[MIT](LICENSE)
