"""Download locked dependencies into the vendored wheelhouse."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REQUIREMENTS = ROOT_DIR / "requirements" / "dev.lock"
DEFAULT_DEST = ROOT_DIR / "vendor"


def fetch(requirements: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--dest",
        str(destination),
        "-r",
        str(requirements),
    ]
    subprocess.check_call(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "requirements",
        nargs="?",
        default=str(DEFAULT_REQUIREMENTS),
        help="Path to the locked requirements file (default: requirements/dev.lock)",
    )
    parser.add_argument(
        "--dest",
        default=str(DEFAULT_DEST),
        help="Directory to store downloaded wheels (default: vendor/)",
    )
    args = parser.parse_args()

    fetch(Path(args.requirements), Path(args.dest))
