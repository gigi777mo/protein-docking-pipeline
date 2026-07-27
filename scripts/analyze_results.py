#!/usr/bin/env python3
"""Parse AutoDock Vina output and produce a ranked summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def parse_vina_pdbqt(pdbqt_file: Path):
    poses = []
    current = {}
    path = Path(pdbqt_file)
    if not path.exists():
        return poses
    with open(path) as f:
        for line in f:
            if line.startswith("MODEL"):
                try:
                    current = {"model": int(line.split()[1])}
                except (IndexError, ValueError):
                    current = {"model": len(poses) + 1}
            elif "VINA RESULT" in line:
                parts = line.split()
                try:
                    # REMARK VINA RESULT:  affinity  rmsd_lb  rmsd_ub
                    idx = parts.index("RESULT:") if "RESULT:" in parts else 3
                    # find first float after RESULT
                    floats = []
                    for p in parts:
                        try:
                            floats.append(float(p))
                        except ValueError:
                            continue
                    if len(floats) >= 1:
                        current["affinity"] = floats[0]
                    if len(floats) >= 3:
                        current["rmsd_lb"] = floats[1]
                        current["rmsd_ub"] = floats[2]
                except Exception:
                    pass
            elif line.startswith("ENDMDL"):
                if "affinity" in current:
                    poses.append(current)
                current = {}
    return poses


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--docked", required=True, help="Vina output .pdbqt")
    parser.add_argument("--out", default="results/summary.csv")
    args = parser.parse_args(argv)

    try:
        docked = Path(args.docked)
        if not docked.exists():
            print(f"ERROR: file not found: {docked}", file=sys.stderr)
            return 1
        poses = parse_vina_pdbqt(docked)
        if not poses:
            print("No poses found. Check the PDBQT file.")
            return 1
        df = pd.DataFrame(poses).sort_values("affinity")
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        print("\nTop poses (kcal/mol):")
        print(df.head(10).to_string(index=False))
        print(f"\n[+] Full ranking saved to {out}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
