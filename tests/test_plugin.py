"""Behavior tests using only Python's standard library and a real Zsh PTY."""
import os
from pathlib import Path
import pty
import select
import shlex
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "zsh-glint.plugin.zsh"


def run_zsh(code):
    with tempfile.TemporaryDirectory() as directory:
        env = dict(os.environ, ZDOTDIR=directory, TC_INIT_COMPLETION="0")
        return subprocess.run(
            ["zsh", "-dfi", "-c", "source " + shlex.quote(str(PLUGIN)) + "\n" + code],
            text=True, capture_output=True, env=env, timeout=15,
        )


class EngineTests(unittest.TestCase):
    def check_zsh(self, code):
        result = run_zsh(code)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

    def test_literal_prefix_unicode_exact_and_no_match(self):
        self.check_zsh(r'''
_tc_history=('git status' 'git stash' 'echo [literal]' 'echo $(touch /should-not-exist)' '打印 中文内容')
_tc_suggest 'git st'; [[ $REPLY == atus ]] || exit 1
_tc_suggest 'git status'; [[ -z $REPLY ]] || exit 2
_tc_suggest 'echo ['; [[ $REPLY == 'literal]' ]] || exit 3
_tc_suggest 'echo $('; [[ $REPLY == 'touch /should-not-exist)' ]] || exit 4
_tc_suggest '打印 中'; [[ $REPLY == 文内容 ]] || exit 5
_tc_suggest 'missing'; [[ -z $REPLY ]] || exit 6
''')

    def test_limits_disable_and_invalid_configuration(self):
        self.check_zsh(r'''
_tc_history=('git status')
TC_ENABLED=0; _tc_suggest 'git'; [[ -z $REPLY ]] || exit 1
TC_ENABLED=1; _tc_suggest 'g'; [[ -z $REPLY ]] || exit 2
TC_MIN_PREFIX=1; _tc_suggest 'g'; [[ $REPLY == 'it status' ]] || exit 3
TC_MAX_BUFFER=4; _tc_suggest 'git'; [[ -z $REPLY ]] || exit 4
TC_MAX_BUFFER='$(touch /should-not-exist)'; _tc_suggest 'git'; [[ $REPLY == ' status' ]] || exit 5
_tc_suggest ' git'; [[ -z $REPLY ]] || exit 6
_tc_suggest $'git\n'; [[ -z $REPLY ]] || exit 7
''')

    def test_recent_history_limit_and_private_entries(self):
        self.check_zsh(r'''
fc -p
HISTSIZE=100
print -s -- 'git old'
print -s -- 'git newest'
print -s -- ' pending event'
TC_HISTORY_LIMIT=1
_tc_refresh_history
[[ ${#_tc_history} == 1 && $_tc_history[1] == 'git newest' ]] || exit 1
print -s -- ' secret command'
print -s -- $'echo multiline\nnext'
print -s -- ' pending event'
TC_HISTORY_LIMIT=10
_tc_refresh_history
[[ ${#_tc_history} == 2 ]] || exit 2
_tc_suggest 'git '; [[ $REPLY == newest ]] || exit 3
fc -P
''')

    def test_hook_and_widget_lifecycle(self):
        self.check_zsh(r'''
local_original=${widgets[forward-char]}
source ./zsh-glint.plugin.zsh
[[ ${widgets[forward-char]} == "$local_original" ]] || exit 1
zsh-glint off
[[ $TC_ENABLED == 0 ]] || exit 2
zsh-glint toggle
[[ $TC_ENABLED == 1 ]] || exit 3
zsh-glint unload
[[ ${widgets[forward-char]} == builtin && ! -v _TC_LOADED ]] || exit 4
source ./zsh-glint.plugin.zsh
[[ ${widgets[forward-char]} == user:_tc_forward_char ]] || exit 5
later_widget() { :; }
zle -N forward-char later_widget
zsh-glint unload
[[ ${widgets[forward-char]} == user:later_widget ]] || exit 6
''')

    def test_noninteractive_load_does_nothing(self):
        result = subprocess.run(
            ["zsh", "-dfc", f"source {shlex.quote(str(PLUGIN))}; (( ! ${{+_TC_LOADED}} ))"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_entry_point_command_and_widgets(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                ["zsh", "-dfi", "-c", r'''
source ./terminal-completion.plugin.zsh
[[ $(terminal-completion status) == 'zsh-glint '* ]] || exit 1
terminal-completion off
[[ $TC_ENABLED == 0 ]] || exit 2
zsh-glint on
[[ $TC_ENABLED == 1 ]] || exit 3
[[ ${widgets[terminal-completion-accept]} == ${widgets[zsh-glint-accept]} ]] || exit 4
[[ ${widgets[terminal-completion-toggle]} == ${widgets[zsh-glint-toggle]} ]] || exit 5
saved=${widgets[_tc_saved_forward_char]}
source ./zsh-glint.plugin.zsh
[[ ${widgets[_tc_saved_forward_char]} == "$saved" ]] || exit 6
terminal-completion unload
[[ ${widgets[forward-char]} == builtin ]] || exit 7
'''], cwd=ROOT, text=True, capture_output=True, timeout=15,
                env=dict(os.environ, ZDOTDIR=directory, TC_INIT_COMPLETION="0"),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")


class Terminal:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.snapshot_path = self.directory / "snapshot"
        self.master, slave = pty.openpty()
        env = dict(os.environ, TERM="xterm-256color", ZDOTDIR=directory)
        env.pop("TC_INIT_COMPLETION", None)
        self.process = subprocess.Popen(
            ["zsh", "-dfi"], stdin=slave, stdout=slave, stderr=slave,
            cwd=directory, env=env, start_new_session=True,
        )
        os.close(slave)
        self.read(0.3)
        self.send(
            # Split the literal so echoed setup input cannot look like a ready prompt.
            "PROMPT='TC''> '; RPROMPT=''; HISTSIZE=1000; SAVEHIST=0; "
            "unsetopt beep; bindkey -e; "
            # Isolate tests from third-party completion directories on CI images.
            # Keep compinit's normal permission checks enabled.
            "fpath=( \"${(@M)fpath:#/usr/share/zsh/*}\" ); "
            f"source {shlex.quote(str(PLUGIN))}; "
            "_test_snapshot() { print -rl -- \"$BUFFER\" \"$CURSOR\" \"$POSTDISPLAY\" "
            f"> {shlex.quote(str(self.snapshot_path))}; }}; "
            "zle -N _test_snapshot; bindkey -M emacs '^X^B' _test_snapshot; bindkey -M viins '^X^B' _test_snapshot\n"
        )
        try:
            output = self.read_until(b"TC> ")
            if b"command not found" in output or b"requires Zsh" in output:
                raise AssertionError(output)
        except BaseException:
            self.close()
            raise

    def send(self, text):
        os.write(self.master, text.encode() if isinstance(text, str) else text)

    def read(self, duration=0.15):
        result = b""
        end = time.monotonic() + duration
        while time.monotonic() < end:
            ready, _, _ = select.select([self.master], [], [], max(0, end - time.monotonic()))
            if ready:
                try:
                    result += os.read(self.master, 65536)
                except OSError:
                    break
        return result

    def read_until(self, token, timeout=10):
        result = b""
        end = time.monotonic() + timeout
        while token not in result and time.monotonic() < end:
            result += self.read(0.1)
        if token not in result:
            raise AssertionError(f"Terminal timed out waiting for {token!r}: {result!r}")
        result += self.read(0.2)
        return result

    def command(self, command):
        self.send(command + "\n")
        return self.read_until(b"TC> ")

    def type(self, text):
        self.send(text)
        return self.read()

    def snapshot(self):
        self.snapshot_path.unlink(missing_ok=True)
        self.send(b"\x18\x02")
        end = time.monotonic() + 3
        while not self.snapshot_path.exists() and time.monotonic() < end:
            self.read(0.02)
        self.read(0.05)
        return self.snapshot_path.read_text().splitlines()

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)
        os.close(self.master)


class InteractiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tc-test-")
        self.addCleanup(self.temp.cleanup)
        self.terminal = Terminal(self.temp.name)

    def tearDown(self):
        self.terminal.close()
        self.temp.cleanup()

    def test_ghost_accept_without_execution_and_undo(self):
        t = self.terminal
        marker = Path(self.temp.name) / "not-executed"
        command = f"touch {marker}"
        t.command("print -s -- " + shlex.quote(command))
        output = t.type("touch ")
        self.assertTrue(b"38;5;8m" in output or b"\x1b[90m" in output, output)
        snap = t.snapshot()
        self.assertEqual(snap[0], "touch ")
        self.assertEqual(snap[2], str(marker))
        t.type(b"\x1b[C")
        self.assertEqual(t.snapshot()[0], command)
        self.assertFalse(marker.exists())
        t.type(b"\x1f")  # undo accepting the suggestion
        self.assertEqual(t.snapshot()[0], "touch ")

    def test_midline_forward_preserves_buffer(self):
        t = self.terminal
        t.command("print -s -- 'git status'")
        t.type("git st")
        t.type(b"\x1b[D")
        before = t.snapshot()
        self.assertEqual(before[:2], ["git st", "5"])
        self.assertEqual(before[2], "")
        t.type(b"\x1b[C")
        self.assertEqual(t.snapshot()[:2], ["git st", "6"])

    def test_disable_and_unload_restore_arrow(self):
        t = self.terminal
        t.command("print -s -- 'git status'; zsh-glint off")
        t.type("git st")
        self.assertEqual(t.snapshot()[2], "")
        t.type(b"\x15")
        t.command("zsh-glint on")
        t.type("git st")
        self.assertEqual(t.snapshot()[2], "atus")
        t.type(b"\x15")
        t.command("zsh-glint unload")
        t.type("git st")
        t.type(b"\x1b[C")
        self.assertEqual(t.snapshot()[:2], ["git st", "6"])

    def test_native_path_completion_with_spaces(self):
        t = self.terminal
        (Path(self.temp.name) / "unique folder").mkdir()
        t.type("cd unique")
        t.type(b"\t")
        self.assertEqual(t.snapshot()[0], "cd unique\\ folder/")

    def test_native_git_parameter_completion(self):
        t = self.terminal
        t.type("git --ver")
        t.type(b"\t")
        self.assertEqual(t.snapshot()[0].rstrip(), "git --version")

    def test_vi_insert_and_unicode(self):
        t = self.terminal
        t.command("bindkey -v; print -s -- 'echo 中文内容'")
        t.type("echo 中")
        self.assertEqual(t.snapshot()[2], "文内容")
        t.type(b"\x1b[C")
        self.assertEqual(t.snapshot()[0], "echo 中文内容")

    def test_other_postdisplay_is_preserved(self):
        t = self.terminal
        t.command("_other_display() { POSTDISPLAY='OTHER'; }; zle -N _other_display; bindkey '^X^O' _other_display")
        t.type(b"ab\x18\x0f")
        self.assertEqual(t.snapshot()[2], "OTHER")


class InstallerTests(unittest.TestCase):
    def run_script(self, action, rc):
        return subprocess.run(
            ["zsh", str(ROOT / "scripts" / f"{action}.zsh"), "--rc", str(rc)],
            text=True, capture_output=True, timeout=10,
        )

    def test_install_idempotence_backup_and_uninstall(self):
        with tempfile.TemporaryDirectory(prefix="tc space ") as directory:
            rc = Path(directory) / "config with spaces"
            original = "# existing config\nexport EXAMPLE='keep me'\n\n"
            rc.write_text(original)
            rc.chmod(0o640)
            first = self.run_script("install", rc)
            self.assertEqual(first.returncode, 0, first.stderr)
            content = rc.read_text()
            self.assertTrue(content.startswith(original))
            self.assertEqual(rc.stat().st_mode & 0o777, 0o640)
            backups = list(Path(directory).glob("*.backup.*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), original)
            self.assertEqual(self.run_script("install", rc).returncode, 0)
            self.assertEqual(rc.read_text(), content)
            self.assertEqual(len(list(Path(directory).glob("*.backup.*"))), 1)
            result = self.run_script("uninstall", rc)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(rc.read_text(), original)
            self.assertEqual(self.run_script("uninstall", rc).returncode, 0)

    def test_malformed_block_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            rc = Path(directory) / ".zshrc"
            for content in (
                "# >>> zsh-glint >>>\nkeep\n",
                "# <<< zsh-glint <<<\n",
                "# >>> zsh-glint >>>\n# >>> zsh-glint >>>\n",
                "# >>> terminal-completion >>>\n# <<< zsh-glint <<<\n",
                "# >>> zsh-glint >>>\n# <<< terminal-completion <<<\n",
                "# >>> terminal-completion >>>\n# <<< terminal-completion <<<\n# >>> zsh-glint >>>\n# <<< zsh-glint <<<\n",
            ):
                rc.write_text(content)
                result = self.run_script("install", rc)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(rc.read_text(), content)
            self.assertFalse(list(Path(directory).glob("*.backup.*")))

    def test_legacy_installation_migration_and_uninstall(self):
        with tempfile.TemporaryDirectory() as directory:
            rc = Path(directory) / ".zshrc"
            original = (
                "# existing config\n# >>> terminal-completion >>>\n"
                "source /old/path/terminal-completion.plugin.zsh\n"
                "# <<< terminal-completion <<<\n# trailing config\n"
            )
            rc.write_text(original)
            result = self.run_script("install", rc)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("terminal-completion", rc.read_text())
            self.assertEqual(rc.read_text().count("# >>> zsh-glint >>>"), 1)
            self.assertIn("zsh-glint.plugin.zsh", rc.read_text())
            self.assertTrue(rc.read_text().startswith("# existing config\n# trailing config\n"))
            self.assertEqual(self.run_script("uninstall", rc).returncode, 0)
            self.assertEqual(rc.read_text(), "# existing config\n# trailing config\n")
            rc.write_text(original)
            self.assertEqual(self.run_script("uninstall", rc).returncode, 0)
            self.assertEqual(rc.read_text(), "# existing config\n# trailing config\n")

    def test_symlink_and_new_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "real-config"
            target.write_text("# preserved\n")
            link = Path(directory) / ".zshrc"
            link.symlink_to(target)
            result = self.run_script("install", link)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(link.is_symlink())
            self.assertIn("source ", target.read_text())
            new_rc = Path(directory) / "new" / ".zshrc"
            result = self.run_script("install", new_rc)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(new_rc.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
