# Changelog

## 0.2.0 — 2026-09-08

### Added

- `zsh-glint doctor` for configuration, hooks, widget ownership, completion initialization, and permission checks. Reports counts without printing command history.
- Reproducible matcher/refresh benchmarks with raw before/after reports.
- Microglint logo and banner, a real terminal recording, an animated demo, and a still alternative.
- Separate English/Chinese homepages and detailed user guides, compatibility notes, contribution instructions, and issue templates.

### Changed

- Native Zsh array search replaces the expanded shell loop. Unchanged queries reuse a cache that is invalidated by history refresh or effective length changes.
- The entry point loads implementation code inside a local option scope with aliases disabled, preserving the caller's aliases and options.

### Fixed

- Reject reloading after a later plugin retained a forward-widget wrapper, preventing recursive wrapper chains. A fresh Zsh session is required in that case.
- Expanded regression coverage for diagnostics, literal matching, cache invalidation, aliases, and representative hook/widget loading orders.

### 中文摘要

新增 `doctor` 自检、可复现性能基准和原始数据；完善微光视觉、真实终端动图、中英首页及维护文档。原生数组搜索与查询缓存降低匹配开销，加载过程隔离 alias 和选项，并防止特定卸载重载场景中的 widget 递归。历史排序、快捷键默认行为和 `TC_*` 配置保持兼容。

## 0.1.0 — 2026-09-08

- Initial native Zsh history suggestions, right-arrow acceptance, and native Tab integration.
- Configuration, reversible installation, legacy-name migration, bilingual documentation, and macOS/Linux PTY tests.
- Project renamed from `terminal-completion` to `zsh-glint`, preserving old entry points.
- 原生历史建议、方向键接受和 Tab 接入；可逆安装、旧名称迁移、双语文档及双平台测试。
