#!/usr/bin/env python3
"""
Prepare a protein receptor for AutoDock Vina.

Steps:
1. Load PDB
2. Remove waters and unwanted heteroatoms
3. Add polar hydrogens (via OpenBabel)
4. Convert to rigid PDBQT
"""

import argparse
import subprocess
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select


class NonWaterSelect(Select):
    def accept_residue(self, residue):
        # Keep protein residues; drop water and most heteroatoms
        if residue.id[0] == " ":  # standard residues
            return True
        # Optionally keep important cofactors (NAD, HEM, etc.) by name
        if residue.resname in ["HEM", "NAD", "FAD", "ATP", "GTP", "MG", "ZN", "CA"]:
            return True
        return False


def clean_pdb(input_pdb: Path, output_pdb: Path):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("receptor", str(input_pdb))

    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output_pdb), NonWaterSelect())
    print(f"[+] Cleaned PDB written to {output_pdb}")


def pdb_to_pdbqt(input_pdb: Path, output_pdbqt: Path):
    """Use OpenBabel to add hydrogens and convert to PDBQT (rigid receptor)."""
    cmd = [
        "obabel",
        str(input_pdb),
        "-O", str(output_pdbqt),
        "-xr",          # rigid receptor (no rotatable bonds)
        "-p", "7.4",    # pH for protonation
        "--partialcharge", "gasteiger"
    ]
    subprocess.run(cmd, check=True)
    print(f"[+] Receptor PDBQT written to {output_pdbqt}")


def main():
    parser = argparse.ArgumentParser(description="Prepare protein receptor for Vina")
    parser.add_argument("-i", "--input", required=True, help="Input PDB file")
    parser.add_argument("-o", "--output", required=True, help="Output PDBQT file")
    parser.add_argument("--keep-hetatm", action="store_true",
                        help="Keep all heteroatoms (not recommended)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cleaned = output_path.with_suffix(".clean.pdb")
    clean_pdb(input_path, cleaned)
    pdb_to_pdbqt(cleaned, output_path)

    # Optional: remove intermediate
    # cleaned.unlink()


if __name__ == "__main__":
    main()
