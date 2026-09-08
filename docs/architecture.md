# 实现说明

## 运行流程

1. 在交互式 Zsh 5.9+ 中加载插件，初始化默认配置；重复加载直接返回。
2. 若允许初始化且 `_comps` 尚不存在，调用标准 `compinit`。已有补全配置保持原样。
3. `precmd` hook 从 Zsh 的 `history` 参数提取最近历史，过滤空白开头及控制字符条目，构建内存数组。
4. `line-pre-redraw` hook 先清理自己的显示，再检查光标位置、编辑上下文、按键队列及开关。
5. 使用字面前缀匹配，选取最近的较长候选，将后缀写入 `POSTDISPLAY`，用带有 `memo=zsh-glint` 的 `region_highlight` 条目着色。
6. `forward-char` / `vi-forward-char` wrapper 在行尾且当前 buffer 与建议来源一致时接受建议；否则调用加载前保存的 widget。
7. `line-finish` 清理建议。Enter 仍由 Zsh 自己处理，插件不会执行候选命令。

Tab 的路径和参数补全全部由 Zsh completion system 提供；本项目不复制命令参数数据库。

## 性能与安全边界

历史 key 排序发生在 prompt 边界，成本随 Shell 已加载的历史总量增长。缓存最多保存 `TC_HISTORY_LIMIT` 范围内的有效候选；每次重绘的匹配是对缓存的线性扫描。默认上限为 1000 条、512 字符，键入时不启动外部进程。

候选匹配中的用户前缀被引用，`[`、`*`、`$()` 等均按普通文本处理，不使用 `eval`，不执行命令替换。数字配置先检查范围再用于算术。历史仅在内存中缓存，不产生额外磁盘副本，不发送到网络。

插件只清理自己带 memo 标记的高亮；已有其他 `POSTDISPLAY` 内容时不显示本插件建议。卸载只恢复仍指向本插件实现的 widgets，以免覆盖其他插件后续修改。其他建议插件的完整兼容性不在首版保证范围内。

## 安装器

`scripts/config.zsh` 为安装和卸载共用的区块编辑器。它定位目标配置文件并解析符号链接，只编辑完整且唯一的托管区块。异常标记导致立即退出。

新内容写入同目录临时文件；无变化时不创建备份。已有文件发生变化时保留原文件权限并创建备份，最终以 rename 替换目标。不会删除项目目录或用户历史。为避免并发编辑覆盖，运行安装器时不要同时保存目标配置。

项目更名为 `zsh-glint` 后，安装器同时识别旧的 `terminal-completion` 区块，并在重新安装时迁移到新名称。混合首尾标记或同时出现多个新旧区块会被拒绝。旧入口文件转发到 `zsh-glint.plugin.zsh`，旧命令和 widgets 委托给同一实现，`TC_*` 配置及加载保护保持兼容。

## 验证方式

测试分为三个层次：纯匹配与生命周期测试、临时配置文件安装器测试、真实 Zsh PTY 集成测试。PTY 通过独立测试 widget 读取实际 `BUFFER`、`CURSOR` 和 `POSTDISPLAY`，验证接受建议只改变输入行；通过屏幕转义序列验证灰色提示，通过文件系统检查候选命令未被执行。

测试仅加载 `/usr/share/zsh` 下的系统补全目录，并等待真正的 prompt，避免把启动命令的回显误认为 Shell 已就绪。Linux CI 镜像中的 `/usr/share/zsh` 和 `vendor-completions` 存在过宽写权限，workflow 在临时 runner 中先移除组写入和其他用户写入权限，再运行 `compaudit`；插件本身不修改系统目录或跳过权限检查。

参考：[ZLE 文档](https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html)、[Completion System](https://zsh.sourceforge.io/Doc/Release/Completion-System.html)、[add-zle-hook-widget](https://zsh.sourceforge.io/Doc/Release/User-Contributions.html#Manipulating-Hook-Functions)。
