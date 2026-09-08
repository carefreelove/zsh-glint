# Compatibility / 兼容性

[Home](../README.md) · [中文首页](../README.zh-CN.md)

| Area / 项目 | Coverage / 验证范围 |
| --- | --- |
| macOS + Linux, Zsh 5.9+ | Both CI platforms run the same PTY and installer tests / 双平台运行相同测试 |
| Emacs + Vi insert | Right-arrow acceptance, Unicode, cursor movement, undo / 接受建议、中文、光标和撤销 |
| Existing native completion | Initialized completion is retained; no global `zstyle` rewrite / 保留已有补全配置 |
| Existing custom forward widget | Saved, delegated to, and restored on unload / 保存、调用并在卸载时恢复 |
| Hooks added through `add-zle-hook-widget` | Preserved when loading before or after glint's hooks / 保留前后注册的 hooks |
| Later widget replacement | Unload preserves later changes; reloading is blocked until a fresh session / 保留后续修改，需新会话才能重新加载 |
| Shell aliases and options | Entry point scopes options and parses implementation with aliases disabled / 选项作用域隔离，避免 alias 干扰实现解析 |
| Old project name | Entry point, command, widgets, configuration, and installer migration / 旧入口、命令、widgets、配置和迁移 |

These are behavior tests with controlled hooks/widgets, not certification of every third-party plugin version. Oh My Zsh installation is documented, but a complete third-party plugin matrix is not included.

这些验证使用受控的 hooks/widgets，不表示已认证所有第三方插件版本。文档提供 Oh My Zsh 安装方法，但目前没有覆盖全部第三方插件组合的测试矩阵。

## Diagnostics

Run `zsh-glint doctor` **inside the affected interactive Zsh session**. It reports invalid numeric/boolean configuration, absent completion, failed directory permission checks, missing hooks, replaced forward widgets, and a known `zsh-autosuggestions` function signature. It prints history counts, not history contents. It does not automatically repair configuration.

请在出现问题的交互式 Zsh 会话中运行 `zsh-glint doctor`。它检查数字和开关配置、补全初始化、目录权限、hooks、方向键 widgets，以及已知的 `zsh-autosuggestions` 函数特征；只输出历史条数，不输出历史内容，也不自动修改配置。

- **Exit 0:** no warnings in the checks performed / 已执行的检查没有警告。
- **Exit 1:** at least one warning; follow the corresponding guidance / 至少一条警告，按对应提示处理。

`doctor` cannot prove absence of every plugin conflict and does not inspect custom key bindings or validate every possible `TC_STYLE` expression. A deliberate `TC_INIT_COMPLETION=0` without a separate `compinit` still produces a completion warning, because native Tab integration has not been initialized.

`doctor` 不能保证发现所有插件冲突，也不检查自定义按键绑定或验证所有 `TC_STYLE` 表达式。若设定 `TC_INIT_COMPLETION=0` 且没有自行运行 `compinit`，仍会提示未初始化原生补全。

## Limits

Use one inline history-suggestion provider at a time. glint preserves foreign `POSTDISPLAY` text it encounters, but arbitrary competing redraw providers may still interfere. Syntax highlighters that cooperate through hooks are covered by representative behavior tests, not by testing each named highlighter.

建议只启用一种行内历史建议插件。glint 会保留遇到的其他 `POSTDISPLAY` 内容，但多个重绘提供方仍可能互相影响。对于通过 hooks 协作的语法高亮器，测试覆盖的是代表性的行为，不是逐一验证所有高亮插件。

If another plugin wraps glint's forward widget and you then unload glint, open a **new Zsh session** before loading it again. This prevents a saved wrapper from recursively calling itself. Plain unload/reload without later widget replacements remains supported.

如果其他插件包装了 glint 的方向键 widget，卸载 glint 后请打开新 Zsh 会话再加载，以防保存的 wrapper 递归调用自身。没有后续 widget 替换时，普通卸载再加载仍受支持。
