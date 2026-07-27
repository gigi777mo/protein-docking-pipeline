#!/usr/bin/env python3
"""
Utility helpers for the docking pipeline.
"""

import argparse
from pathlib import Path
from Bio.PDB import PDBParser
import numpy as np


def get_ligand_center_and_size(ligand_pdb: Path, padding: float = 5.0):
    """Calculate approximate box center and size from a co-crystal ligand."""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("lig", str(ligand_pdb))

    coords = []
    for atom in structure.get_atoms():
        coords.append(atom.coord)

    coords = np.array(coords)
    center = coords.mean(axis=0)
    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    size = (maxs - mins) + 2 * padding

    print("Suggested Vina box parameters:")
    print(f"center_x = {center[0]:.3f}")
    print(f"center_y = {center[1]:.3f}")
    print(f"center_z = {center[2]:.3f}")
    print(f"size_x = {size[0]:.1f}")
    print(f"size_y = {size[1]:.1f}")
    print(f"size_z = {size[2]:.1f}")
    return center, size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--get-box", action="store_true")
    parser.add_argument("--ligand", help="Co-crystal ligand PDB")
    parser.add_argument("--padding", type=float, default=5.0)
    args = parser.parse_args()

    if args.get_box:
        if not args.ligand:
            raise ValueError("--ligand is required with --get-box")
        get_ligand_center_and_size(Path(args.ligand), args.padding)


if __name__ == "__main__":
    main()
