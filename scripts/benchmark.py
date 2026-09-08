#!/usr/bin/env python3
"""Reproducible Zsh matcher/refresh benchmark. No third-party dependencies."""
import argparse
import json
import platform
from pathlib import Path
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CODE = r'''
zmodload zsh/datetime
typeset -a values
integer i count=$1 repetitions=$2
for (( i=1; i<=count; i++ )); do
  printf -v item 'echo job-%06d --verbose' $i
  values+=( "$item" )
done
_tc_history=( "${values[@]}" )
printf -v last_prefix 'echo job-%06d' $count
for scenario prefix in first 'echo job-' last "$last_prefix" miss 'no-such-command' repeated 'no-such-command'; do
  typeset -a samples=()
  _tc_cache_valid=0
  _tc_suggest "$prefix"
  case $scenario in
    first) [[ $REPLY == '000001 --verbose' ]] || exit 10 ;;
    last) [[ $REPLY == ' --verbose' ]] || exit 11 ;;
    *) [[ -z $REPLY ]] || exit 12 ;;
  esac
  for (( i=0; i<repetitions; i++ )); do
    [[ $scenario == repeated ]] || _tc_cache_valid=0
    start=$EPOCHREALTIME
    _tc_suggest "$prefix"
    duration=$(( (EPOCHREALTIME - start) * 1000.0 ))
    samples+=( "$duration" )
  done
  print -r -- "$scenario ${(j:,:)samples}"
done
fc -p
HISTSIZE=$(( count + 10 ))
for item in "${values[@]}"; do print -s -- "$item"; done
print -s -- ' pending event'
TC_HISTORY_LIMIT=1000
typeset -a samples=()
for (( i=0; i<5; i++ )); do
  start=$EPOCHREALTIME
  _tc_refresh_history
  samples+=( "$(( (EPOCHREALTIME - start) * 1000.0 ))" )
done
print -r -- "refresh ${(j:,:)samples}"
fc -P
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", type=Path, default=ROOT / "zsh-glint.plugin.zsh")
    parser.add_argument("--sizes", type=int, nargs="+", default=[1000, 10000, 100000])
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repetitions < 1 or any(n < 1 or n > 100000 for n in args.sizes):
        parser.error("sizes must be 1–100000; repetitions must be positive")
    rows = []
    import os
    import statistics
    for size in args.sizes:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                ["zsh", "-dfi", "-c", "source " + shlex.quote(str(args.plugin.resolve())) + "\n" + CODE,
                 "benchmark", str(size), str(args.repetitions)],
                env=dict(os.environ, ZDOTDIR=directory, TC_INIT_COMPLETION="0", TC_ENABLED="1",
                         TC_MIN_PREFIX="2", TC_MAX_BUFFER="512", TC_HISTORY_LIMIT="1000"),
                text=True, capture_output=True, timeout=180,
            )
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
        for line in result.stdout.splitlines():
            scenario, numbers = line.split(" ", 1)
            samples = sorted(float(n) for n in numbers.split(","))
            rows.append({"entries": size, "scenario": scenario,
                         "median_ms": round(statistics.median(samples), 4),
                         "p95_ms": round(samples[min(len(samples)-1, int(len(samples)*0.95))], 4),
                         "samples": len(samples)})
    report = {
        "platform": platform.system(), "architecture": platform.machine(),
        "zsh": subprocess.check_output(["zsh", "--version"], text=True).strip(),
        "method": "Synthetic unique commands; cold matcher caches invalidated; refresh capped at 1000 cached entries; milliseconds; no terminal rendering/startup included.",
        "results": rows,
    }
    content = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(content)
    print(content, end="")


if __name__ == "__main__":
    main()
