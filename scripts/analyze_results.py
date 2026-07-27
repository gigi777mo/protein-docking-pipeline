#!/usr/bin/env python3
"""
Parse AutoDock Vina output and produce a ranked summary.
"""

import argparse
from pathlib import Path
import pandas as pd
import re


def parse_vina_pdbqt(pdbqt_file: Path):
    """Extract model number, affinity, and RMSD from Vina multi-model PDBQT."""
    poses = []
    current = {}
    with open(pdbqt_file) as f:
        for line in f:
            if line.startswith("MODEL"):
                current = {"model": int(line.split()[1])}
            elif line.startswith("REMARK VINA RESULT"):
                # REMARK VINA RESULT:    -8.5      0.000      0.000
                parts = line.split()
                current["affinity"] = float(parts[3])
                current["rmsd_lb"] = float(parts[4])
                current["rmsd_ub"] = float(parts[5])
            elif line.startswith("ENDMDL"):
                if "affinity" in current:
                    poses.append(current)
    return poses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--docked", required=True, help="Vina output .pdbqt")
    parser.add_argument("--out", default="results/summary.csv")
    args = parser.parse_args()

    poses = parse_vina_pdbqt(Path(args.docked))
    if not poses:
        print("No poses found. Check the PDBQT file.")
        return

    df = pd.DataFrame(poses)
    df = df.sort_values("affinity")  # more negative = better
    df.to_csv(args.out, index=False)

    print("\nTop poses (kcal/mol):")
    print(df.head(10).to_string(index=False))
    print(f"\n[+] Full ranking saved to {args.out}")


if __name__ == "__main__":
    main()
