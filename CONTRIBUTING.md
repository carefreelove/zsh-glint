# Contributing to zsh-glint

Small changes that make Zsh input clearer, faster, or more dependable are welcome. Keep the runtime native to Zsh and offline. Suggestion acceptance must never execute a command.

## Working locally

1. Fork and clone the repository, then create a branch for one focused change.
2. Use Zsh 5.9+ and Python 3.9+. Runtime tests use only the Python standard library.
3. Run the checks below from the project root.

```sh
for script in *.plugin.zsh lib/*.zsh scripts/*.zsh; do zsh -n "$script"; done
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
```

Tests use temporary directories and real PTYs. Do not add fixtures copied from personal shell history, credentials, or machine-specific configuration. For a behavior change, include a regression test exercising the observable behavior. Keep the English and Chinese guides consistent.

## Performance changes

```sh
python3 scripts/benchmark.py --output /tmp/glint-benchmark.json
```

Report the environment, workload, median/p95, and any regressions. Compare equivalent settings and distinguish lookup, refresh, startup, and rendering costs. Do not commit machine-specific paths or claim universal speedups from one run. See [the benchmark method](docs/performance.md).

## Recording the demo

The checked-in GIF is rendered from output of a real Zsh PTY in a disposable Git repository, using synthetic history. `demo.cast` preserves the raw recording; `demo.png` offers a still view. Colors and window chrome come from the renderer, while terminal content comes from the recording.

Optional development dependencies, separate from the plugin runtime:

```sh
python3 -m venv /tmp/glint-demo-env
/tmp/glint-demo-env/bin/pip install -r scripts/requirements-demo.txt
/tmp/glint-demo-env/bin/python scripts/record_demo.py
```

On systems without Menlo or DejaVu Sans Mono, pass `--font /path/to/monospace.ttf`. Rendering may vary with font versions. Inspect the animation and still before committing regenerated assets; do not substitute simulated terminal output for a real recording.

## Pull requests and issues

Describe the user-visible behavior, why the change helps, and how it was validated. Include compatibility implications, especially widget ownership, hook order, history filtering, or installer migration. Use the issue templates for bug reports and feature proposals. `zsh-glint doctor` output is useful; inspect it before sharing any additional logs.

## Releases

1. Update the version in `lib/glint.zsh` and add a dated entry to `CHANGELOG.md`.
2. Update both languages, run local checks, and wait for macOS/Linux CI on the exact commit.
3. Tag the tested commit, prepare notes under `docs/releases/`, and publish a GitHub Release.
4. If attaching a source archive, include its SHA-256 checksum. Never overwrite an existing version tag; publish a patch version for corrections.

## 中文说明

欢迎提交让终端输入更清晰、更快、更可靠的改进。请保持原生 Zsh、离线运行，以及“接受建议不会执行命令”的原则。

从项目根目录运行以上检查，行为变更附回归测试，中英文文档同步更新。测试和演示只使用合成历史及临时目录，不要提交个人历史、凭据或机器专属配置。性能改进应说明环境、工作负载及退化场景；演示需要保留真实终端录制，发布前确认同一提交的双平台 CI 通过。
