# User guide

[English](guide.md) · [简体中文](guide.zh-CN.md) · [Home](../README.md)

A lightweight, offline Zsh plugin for command-line suggestions. See history suggestions in gray, press **→** to accept them, and use **Tab** for Zsh's native path and argument completion.

```text
❯ git st│atus          Type git st; atus appears in gray
❯ git status│          Press → to accept; Enter to execute

❯ cd Doc│             Press Tab to complete a directory
❯ cd Documents/│
```

This is an interaction sketch. Actual suggestions come from your own shell history.

## Features

- **Inline history suggestions:** literal prefix matching, with the most recent matching command first.
- **Native Tab completion:** Zsh completes files, directories, commands, and arguments, including paths containing spaces.
- **Natural editing:** the right arrow accepts a suggestion at the end of the line and moves the cursor normally elsewhere. Supports Emacs and Vi insert mode; accepting a suggestion can be undone.
- **Configurable:** appearance, minimum prefix length, buffer limit, history scan limit, and an enable switch.
- **Local execution:** the plugin itself uses only Zsh, makes no network requests, calls no AI APIs, and creates no additional history files.
- **Reversible installation:** backs up your configuration and manages a marked block. Repeated installation does not add duplicate blocks.

## Requirements

- **Zsh 5.9+** on macOS or Linux, running in an interactive terminal.
- A UTF-8 terminal for Unicode text; a 256-color terminal for the default gray style.
- The installer uses standard system utilities such as `mktemp`, `cp`, `cmp`, and `mv`.
- Development tests additionally require Python 3.9+ and Git, with no third-party Python dependencies.

Check your version:

```sh
zsh --version
```

## Installation

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

## Upgrading from the previous name

This project was previously called `terminal-completion` and is now **zsh-glint**. In your existing clone, run:

```sh
git remote set-url origin https://github.com/carefreelove/zsh-glint.git
git pull --ff-only
zsh scripts/install.zsh
```

Then open a new Zsh session. The installer migrates the old managed block, and the uninstaller recognizes either name. The legacy `terminal-completion.plugin.zsh` entry point, `terminal-completion` command, and `terminal-completion-accept` / `terminal-completion-toggle` widgets remain available. Existing `TC_*` configuration variables are unchanged.

If you installed through Oh My Zsh under the old name, you can retain that directory and your `plugins=(... terminal-completion)` entry. New installations should use `zsh-glint`. You do not need to rename an existing local clone directory.

## Quick start

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
| `zsh-glint doctor` | Diagnose configuration, hooks, completion permissions, and common conflicts |
| `zsh-glint status` | Show version, state, and cached history count |
| `zsh-glint refresh` | Refresh the history cache immediately |
| `zsh-glint unload` | Remove plugin hooks and restore arrow-key widgets still owned by the plugin |

## Configuration

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

## History and privacy

Suggestions come from history already loaded by the current Zsh session, with the most recent matches first. The cache refreshes before each new prompt. Persistence and sharing across sessions follow your existing `HISTFILE`, `HISTSIZE`, `SAVEHIST`, and `SHARE_HISTORY` settings; the plugin does not change them.

History entries starting with whitespace or containing newlines or control characters are excluded. Input starting with whitespace also suppresses suggestions. To keep space-prefixed sensitive commands out of Zsh history, you can enable `setopt HIST_IGNORE_SPACE` in your own configuration. The plugin is not a secret detector: sensitive text in ordinary history entries may still be suggested.

## Uninstallation

```sh
zsh scripts/uninstall.zsh
```

If you installed with `--rc`, use the same path when uninstalling. Open a new terminal, or run this in the current session:

```zsh
zsh-glint unload
```

The uninstaller backs up your configuration and removes only its managed `source` block. It keeps the project directory and shell history. For manual or plugin-manager installations, remove the corresponding loading entry yourself. Remove any shortcuts you added manually as well. `unload` leaves native completion and helper functions available; if another plugin retained a wrapped widget, start a fresh Zsh session before reloading to avoid recursion; after sourcing the plugin again, run `zsh-glint on` to re-enable suggestions.

## Limitations and troubleshooting

- **Inline suggestions come only from history.** With no matching history, nothing appears. Paths and arguments are completed with Tab, and Zsh handles complex completion syntax.
- The initial version does not provide fuzzy history search, AI suggestions, or Bash/Fish/PowerShell integration.
- Suggestions are suppressed in Vi command mode, inside the line, for multiline input, during selection, and while input remains queued during a paste.
- Running another history-suggestion plugin that owns `POSTDISPLAY`, such as `zsh-autosuggestions`, is not recommended. zsh-glint yields to existing foreign display content but does not guarantee compatibility with arbitrary plugin loading orders.
- Default arrow-key behavior is tested. Custom terminal shortcuts or other widget wrappers may require an explicit binding.
- If suggestions do not appear, check `zsh-glint status`, available history, and the minimum prefix length.
- If standard `compinit` reports insecure completion directories, correct their permissions and try again. The plugin does not bypass the audit.
- The installer rejects malformed or duplicate managed blocks. Configuration files are written with a final newline, adding one if the original file lacked it.

## Development and testing

```sh
python3 -m unittest discover -s tests -v
```

Tests run in temporary directories without modifying your personal `.zshrc`. Coverage includes literal prefixes, Unicode, history filtering, configuration validation, repeated loading, installation and permissions, legacy-name compatibility and migration, and real PTY interactions for gray suggestions, acceptance and undo, cursor movement, Vi mode, native Tab completion, and preservation of other plugins' display content.

GitHub Actions runs syntax checks and the same test suite on Linux and macOS. Additional implementation notes are in [docs/architecture.md](architecture.md) (Chinese).

## License

[MIT](../LICENSE)
