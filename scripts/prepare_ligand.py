#!/usr/bin/env python3
"""Prepare a small-molecule ligand for AutoDock Vina."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def smiles_to_3d(smiles: str, out_sdf: Path):
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    mol = Chem.AddHs(mol)
    ok = -1
    try:
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        ok = AllChem.EmbedMolecule(mol, params)
    except Exception:
        ok = -1
    if ok != 0:
        try:
            ok = AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        except Exception:
            ok = AllChem.EmbedMolecule(mol, randomSeed=42)
    if ok != 0:
        raise RuntimeError("Could not generate 3D coordinates for ligand")

    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=500)
        except Exception:
            pass

    out_sdf.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(out_sdf))
    writer.write(mol)
    writer.close()
    print(f"[+] 3D SDF written to {out_sdf}")
    return mol


def sdf_or_mol2_to_pdbqt(input_file: Path, output_pdbqt: Path, pH: float = 7.4):
    if shutil.which("obabel") is None:
        raise RuntimeError(
            "obabel not found. Activate the docking conda env or install openbabel."
        )
    output_pdbqt.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "obabel",
        str(input_file),
        "-O",
        str(output_pdbqt),
        "-p",
        str(pH),
        "--partialcharge",
        "gasteiger",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not output_pdbqt.exists():
        # retry with gen3d
        cmd2 = cmd + ["--gen3d"]
        r = subprocess.run(cmd2, capture_output=True, text=True)
    if r.returncode != 0 or not output_pdbqt.exists():
        msg = (r.stderr or r.stdout or "obabel failed").strip()
        raise RuntimeError(f"OpenBabel conversion failed: {msg}")
    print(f"[+] Ligand PDBQT written to {output_pdbqt}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare small molecule ligand for Vina")
    parser.add_argument("-i", "--input", "--ligand", dest="input", required=True,
                        help="SMILES string, .smi, .sdf, or .mol2")
    parser.add_argument("-o", "--output", "--out", dest="output", required=True,
                        help="Output PDBQT file")
    parser.add_argument("--ph", type=float, default=7.4)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if input_path.suffix.lower() in {".smi", ".smiles"} or not input_path.exists():
            if input_path.exists():
                line = input_path.read_text().strip().splitlines()[0]
                smiles = line.split()[0]
            else:
                smiles = args.input
            temp_sdf = output_path.with_suffix(".tmp.sdf")
            smiles_to_3d(smiles, temp_sdf)
            sdf_or_mol2_to_pdbqt(temp_sdf, output_path, args.ph)
            temp_sdf.unlink(missing_ok=True)
        else:
            sdf_or_mol2_to_pdbqt(input_path, output_path, args.ph)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
