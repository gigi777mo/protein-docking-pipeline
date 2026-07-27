#!/usr/bin/env python3
"""Verify AutoDock Vina is available (binary and/or Python package)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def main() -> int:
    print("Checking AutoDock Vina...")
    ok = True

    vina_bin = shutil.which("vina")
    if vina_bin:
        print(f"  [OK] vina binary: {vina_bin}")
        try:
            r = subprocess.run(
                [vina_bin, "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # vina often prints help to stderr
            out = (r.stdout or "") + (r.stderr or "")
            head = out.strip().splitlines()[:3]
            for line in head:
                print(f"       {line}")
        except Exception as e:
            print(f"  [WARN] could not run vina --help: {e}")
    else:
        ok = False
        print("  [MISSING] `vina` not on PATH")
        print("       Fix: conda activate docking")
        print("       Or:  conda install -c bioconda autodock-vina")
        print("       Or download: https://github.com/ccsb-scripps/AutoDock-Vina/releases")

    try:
        import vina  # noqa: F401

        print("  [OK] Python package `vina` importable")
    except Exception as e:
        print(f"  [INFO] Python `vina` package not importable ({e})")
        print("         Binary-only is enough for scripts/run_docking.py")

    if ok:
        print("\nVina is ready.")
        return 0
    print("\nVina is NOT ready. Install with Miniconda (recommended):")
    print("  conda activate docking")
    print("  conda install -c bioconda autodock-vina")
    return 1


if __name__ == "__main__":
    sys.exit(main())
