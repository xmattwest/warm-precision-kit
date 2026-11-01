#!/usr/bin/env python3
"""Check, snapshot and render Warm Precision scenes with a pinned HyperFrames release.

Run build.py first: it writes each scene as a self-contained HyperFrames project under
handbook/scenes/<name>/. This script only calls `npx hyperframes`; it installs nothing
into the kit. Needs Node 22+ and FFmpeg.

  python3 design-system/scripts/scenes.py check [name ...]
  python3 design-system/scripts/scenes.py snapshot name [--at 0.5,3,9] [--frames 9]
  python3 design-system/scripts/scenes.py render [name ...] [--format mp4|gif|webm] [--quality draft|looks|delivery]
"""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

HYPERFRAMES = "hyperframes@0.8.228"
PACKAGE = Path(__file__).resolve().parents[1]
PROJECT = PACKAGE.parent
BUILT = PROJECT / "handbook" / "scenes"
RENDERS = BUILT / "renders"


def available():
    return sorted(p.parent.name for p in (PACKAGE / "scenes").glob("*/index.html"))


def project(name):
    path = BUILT / name
    if not (path / "index.html").is_file():
        sys.exit(f"No built scene at {path}. Run: python3 design-system/scripts/build.py --embed-fonts")
    return path


def hyperframes(*args):
    if not shutil.which("npx"):
        sys.exit("npx not found. Install Node 22 or newer.")
    command = ["npx", "--yes", HYPERFRAMES, *args]
    print("$ " + " ".join(command), flush=True)
    return subprocess.run(command, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "snapshot", "render", "list"))
    parser.add_argument("names", nargs="*", help=f"Scene names (default: all). Available: {', '.join(available())}")
    parser.add_argument("--at", help="Snapshot: comma-separated times in seconds")
    parser.add_argument("--frames", type=int, default=9, help="Snapshot: evenly spaced frames (default 9)")
    parser.add_argument("--format", default="mp4", choices=("mp4", "gif", "webm"), help="Render: output format")
    parser.add_argument("--quality", default="looks", choices=("draft", "looks", "delivery"), help="Render: quality preset")
    args = parser.parse_args()
    if args.command == "list":
        print("\n".join(available()))
        return
    names = args.names or available()
    unknown = sorted(set(names) - set(available()))
    if unknown:
        sys.exit(f"Unknown scene: {', '.join(unknown)}. Available: {', '.join(available())}")
    if args.command == "snapshot" and len(names) != 1:
        sys.exit("snapshot takes one scene name")
    failures = 0
    for name in names:
        path = project(name)
        if args.command == "check":
            failures += hyperframes("check", str(path)) != 0
        elif args.command == "snapshot":
            out = RENDERS / f"{name}-frames"
            timing = ["--at", args.at] if args.at else ["--frames", str(args.frames)]
            failures += hyperframes("snapshot", str(path), *timing, "-o", str(out)) != 0
            for sheet in sorted(out.glob("contact-sheet*.jpg")):
                print(f"Contact sheet: {sheet}")
        else:
            RENDERS.mkdir(parents=True, exist_ok=True)
            out = RENDERS / f"{name}.{args.format}"
            extra = ["--fps", "15"] if args.format == "gif" else []
            failures += hyperframes("render", str(path), "-o", str(out), "--format", args.format, "--quality", args.quality, *extra) != 0
            if args.format == "mp4" and out.is_file() and shutil.which("ffmpeg"):
                poster = out.with_suffix(".jpg")  # the finished frame, for <video poster>
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.2", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(poster)], check=False)
            print(f"Rendered: {out}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
