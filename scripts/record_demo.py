#!/usr/bin/env python3
"""Record a real, isolated Zsh PTY and render its output as a GIF.

Development-only dependencies: Pillow and pyte. The plugin needs neither.
"""
import argparse
import codecs
import fcntl
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import termios
import time

from PIL import Image, ImageDraw, ImageFont
import pyte

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_plugin import Terminal

COLUMNS, ROWS = 82, 12
BACKGROUND, FOREGROUND = "#101a29", "#dce8f5"
COLORS = {"default": FOREGROUND, "black": BACKGROUND, "red": "#f18c96",
          "green": "#99dbc0", "brown": "#edce8b", "blue": "#8eaefa",
          "magenta": "#cbb0f6", "cyan": "#8be9dd", "white": FOREGROUND,
          "brightblack": "#8292a8"}


class RecordingTerminal(Terminal):
    def __init__(self, directory):
        self.events = []
        self.recording = False
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        super().__init__(directory)

    def read(self, duration=0.15):
        data = super().read(duration)
        if self.recording and data:
            decoded = self.decoder.decode(data)
            if decoded:
                self.events.append([round(time.monotonic() - self.started, 4), "o", decoded])
        return data

    def type_slowly(self, text):
        for char in text:
            self.send(char)
            self.read(0.075)


def color(value):
    if value in COLORS:
        return COLORS[value]
    if len(value) == 6 and all(c in "0123456789abcdef" for c in value.lower()):
        return "#" + value
    return FOREGROUND


def render(events, destination, font_path):
    font = ImageFont.truetype(str(font_path), 17)
    small = ImageFont.truetype(str(font_path), 12)
    cell_width = font.getlength("M")
    cell_height = 25
    width, height = int(COLUMNS * cell_width + 64), ROWS * cell_height + 112
    screen = pyte.Screen(COLUMNS, ROWS)
    stream = pyte.Stream(screen)
    frames, durations = [], []
    still_saved = False
    for index, (timestamp, kind, data) in enumerate(events):
        stream.feed(data)
        canvas = Image.new("RGB", (width, height), "#0b1220")
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle((1, 1, width-2, height-2), radius=18, fill=BACKGROUND, outline="#293950")
        for x, fill in ((25, "#f18c96"), (45, "#edce8b"), (65, "#99dbc0")):
            draw.ellipse((x, 22, x+9, 31), fill=fill)
        draw.text((95, 18), "zsh-glint  /  real terminal session", font=small, fill="#a6b8ce")
        draw.line((20, 50, width-20, 50), fill="#293950")
        for y in range(ROWS):
            for x in range(COLUMNS):
                char = screen.buffer[y][x]
                if char.data.strip():
                    fg = "#8292a8" if char.fg == "black" and char.bold else color(char.fg)
                    draw.text((30+x*cell_width, 65+y*cell_height), char.data, font=font, fill=fg)
        if not screen.cursor.hidden:
            x, y = screen.cursor.x, screen.cursor.y
            draw.rectangle((30+x*cell_width, 67+y*cell_height, 32+x*cell_width, 85+y*cell_height), fill="#8be9dd")
        draw.text((30, height-29), "History suggests. Right arrow accepts. Enter executes.", font=small, fill="#91a6c1")
        frames.append(canvas)
        if not still_saved and screen.display[0].startswith('> git status --short') and screen.cursor.x == 8:
            canvas.save(destination.with_suffix('.png'))
            still_saved = True
        next_time = events[index+1][0] if index+1 < len(events) else timestamp+2.0
        durations.append(max(30, int((next_time-timestamp)*1000)))
    frames[0].save(destination, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=2)
    if not still_saved:
        frames[-1].save(destination.with_suffix('.png'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    fonts = [args.font, Path("/System/Library/Fonts/Menlo.ttc"),
             Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")]
    font_path = next((p for p in fonts if p and p.exists()), None)
    if not font_path:
        parser.error("Provide a monospace font using --font")
    target = ROOT / "docs" / "assets"
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="glint-demo-") as directory:
        work = Path(directory)
        (work / "Documents").mkdir()
        (work / "README.md").write_text("# Demo repository\n")
        subprocess.run(["git", "init", "-q", "-b", "main", directory], check=True)
        # Keep temporary terminal/configuration files out of the demo's git output.
        (work / ".git" / "info" / "exclude").write_text(".zcompdump*\nsnapshot\n")
        terminal = RecordingTerminal(directory)
        try:
            fcntl.ioctl(terminal.master, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLUMNS, 0, 0))
            terminal.command("print -s -- 'git status --short'")
            terminal.send("PROMPT='%F{cyan}>%f '; RPROMPT=''\n")
            terminal.read(0.5)
            terminal.started = time.monotonic()
            terminal.recording = True
            terminal.send(b"\x0c")
            terminal.read(0.4)
            terminal.type_slowly("git st")
            terminal.read(1.0)
            terminal.send(b"\x1b[C")
            terminal.read(0.8)
            terminal.send("\n")
            terminal.read(0.8)
            terminal.type_slowly("cd Doc")
            terminal.send(b"\t")
            terminal.read(0.9)
            terminal.send("\n")
            terminal.read(0.6)
            terminal.type_slowly("zsh-glint status")
            terminal.send("\n")
            terminal.read(1.2)
        finally:
            terminal.close()
    header = {"version": 2, "width": COLUMNS, "height": ROWS,
              "title": "zsh-glint: history suggestions and native Tab completion",
              "env": {"TERM": "xterm-256color"}}
    content = "\n".join(json.dumps(item, ensure_ascii=False) for item in [header, *terminal.events]) + "\n"
    (target / "demo.cast").write_text(content)
    render(terminal.events, target / "demo.gif", font_path)
    print(f"Recorded {len(terminal.events)} output events to {target}")


if __name__ == "__main__":
    main()
