#!/usr/bin/env python3
"""Prepare a protein receptor for AutoDock Vina."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from Bio.PDB import PDBIO, PDBParser, Select


class NonWaterSelect(Select):
    def accept_residue(self, residue):
        if residue.id[0] == " ":
            return True
        if residue.resname in {"HEM", "NAD", "FAD", "ATP", "GTP", "MG", "ZN", "CA", "MN"}:
            return True
        return False


def clean_pdb(input_pdb: Path, output_pdb: Path):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("receptor", str(input_pdb))
    io = PDBIO()
    io.set_structure(structure)
    output_pdb.parent.mkdir(parents=True, exist_ok=True)
    io.save(str(output_pdb), NonWaterSelect())
    print(f"[+] Cleaned PDB written to {output_pdb}")


def pdb_to_pdbqt(input_pdb: Path, output_pdbqt: Path):
    if shutil.which("obabel") is None:
        raise RuntimeError(
            "obabel not found. Activate the docking conda env or install openbabel."
        )
    output_pdbqt.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "obabel",
        str(input_pdb),
        "-O",
        str(output_pdbqt),
        "-xr",
        "-p",
        "7.4",
        "--partialcharge",
        "gasteiger",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not output_pdbqt.exists():
        msg = (r.stderr or r.stdout or "obabel failed").strip()
        raise RuntimeError(f"OpenBabel receptor conversion failed: {msg}")
    print(f"[+] Receptor PDBQT written to {output_pdbqt}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare protein receptor for Vina")
    parser.add_argument("-i", "--input", "--receptor", dest="input", required=True)
    parser.add_argument("-o", "--output", "--out", dest="output", required=True)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 1

    try:
        cleaned = output_path.with_suffix(".clean.pdb")
        clean_pdb(input_path, cleaned)
        pdb_to_pdbqt(cleaned, output_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
