#!/usr/bin/env python3
"""
Prepare a small-molecule ligand for AutoDock Vina.

Accepts SMILES, SDF, or MOL2.
Generates a reasonable 3D conformer, minimizes, protonates at pH 7.4,
and outputs a flexible PDBQT.
"""

import argparse
import subprocess
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors


def smiles_to_3d(smiles: str, out_sdf: Path):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    mol = Chem.AddHs(mol)
    # Embed + minimize
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) != 0:
        # Fallback
        AllChem.EmbedMolecule(mol, AllChem.ETKDG())

    AllChem.MMFFOptimizeMolecule(mol, maxIters=500)

    writer = Chem.SDWriter(str(out_sdf))
    writer.write(mol)
    writer.close()
    print(f"[+] 3D SDF written to {out_sdf}")
    return mol


def sdf_or_mol2_to_pdbqt(input_file: Path, output_pdbqt: Path, pH: float = 7.4):
    """Convert using OpenBabel with correct protonation."""
    cmd = [
        "obabel",
        str(input_file),
        "-O", str(output_pdbqt),
        "-p", str(pH),
        "--gen3d",          # ensure 3D if needed
        "--partialcharge", "gasteiger"
    ]
    # For ligands we want rotatable bonds (do NOT use -xr)
    subprocess.run(cmd, check=True)
    print(f"[+] Ligand PDBQT written to {output_pdbqt}")


def main():
    parser = argparse.ArgumentParser(description="Prepare small molecule ligand for Vina")
    parser.add_argument("-i", "--input", required=True,
                        help="Input: SMILES string, .smi, .sdf, or .mol2 file")
    parser.add_argument("-o", "--output", required=True, help="Output PDBQT file")
    parser.add_argument("--ph", type=float, default=7.4, help="Target pH (default 7.4)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Detect input type
    if input_path.suffix.lower() in [".smi", ".smiles"] or not input_path.exists():
        # Treat as SMILES (either file containing SMILES or direct string)
        if input_path.exists():
            smiles = input_path.read_text().strip().split()[0]
        else:
            smiles = args.input

        temp_sdf = output_path.with_suffix(".tmp.sdf")
        smiles_to_3d(smiles, temp_sdf)
        sdf_or_mol2_to_pdbqt(temp_sdf, output_path, args.ph)
        temp_sdf.unlink(missing_ok=True)
    else:
        # SDF or MOL2
        sdf_or_mol2_to_pdbqt(input_path, output_path, args.ph)


if __name__ == "__main__":
    main()
