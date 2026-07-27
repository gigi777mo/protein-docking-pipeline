#!/usr/bin/env python3
"""
End-to-end protein-ligand docking wrapper.

Prepares receptor + ligand, runs AutoDock Vina, and performs basic ranking.
"""

import argparse
import subprocess
from pathlib import Path
import shutil

from prepare_receptor import clean_pdb, pdb_to_pdbqt
from prepare_ligand import smiles_to_3d, sdf_or_mol2_to_pdbqt


def run_vina(config: Path, receptor: Path, ligand: Path, out: Path, log: Path):
    cmd = [
        "vina",
        "--config", str(config),
        "--receptor", str(receptor),
        "--ligand", str(ligand),
        "--out", str(out),
        "--log", str(log)
    ]
    print("[*] Running AutoDock Vina...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Vina failed")
    print(result.stdout)
    print(f"[+] Docking finished. Results: {out}")


def main():
    parser = argparse.ArgumentParser(description="Full protein-ligand docking pipeline")
    parser.add_argument("--receptor", required=True, help="Input protein PDB")
    parser.add_argument("--ligand", required=True, help="Ligand SMILES / SDF / MOL2 / SMI")
    parser.add_argument("--config", required=True, help="Vina config file (box + parameters)")
    parser.add_argument("--out", default="results", help="Output directory")
    parser.add_argument("--ph", type=float, default=7.4)
    args = parser.parse_args()

    out_dir = Path(args.out)
    prepared = out_dir / "prepared"
    prepared.mkdir(parents=True, exist_ok=True)
    (out_dir / "results").mkdir(exist_ok=True)

    receptor_pdbqt = prepared / "receptor.pdbqt"
    ligand_pdbqt = prepared / "ligand.pdbqt"

    # 1. Receptor
    print("=== Preparing receptor ===")
    cleaned = prepared / "receptor.clean.pdb"
    clean_pdb(Path(args.receptor), cleaned)
    pdb_to_pdbqt(cleaned, receptor_pdbqt)

    # 2. Ligand
    print("=== Preparing ligand ===")
    lig_path = Path(args.ligand)
    if lig_path.suffix.lower() in [".smi", ".smiles"] or not lig_path.exists():
        smiles = lig_path.read_text().strip().split()[0] if lig_path.exists() else args.ligand
        temp_sdf = prepared / "ligand.tmp.sdf"
        smiles_to_3d(smiles, temp_sdf)
        sdf_or_mol2_to_pdbqt(temp_sdf, ligand_pdbqt, args.ph)
        temp_sdf.unlink(missing_ok=True)
    else:
        sdf_or_mol2_to_pdbqt(lig_path, ligand_pdbqt, args.ph)

    # 3. Dock
    print("=== Docking ===")
    docked = out_dir / "docked.pdbqt"
    log = out_dir / "vina.log"
    run_vina(Path(args.config), receptor_pdbqt, ligand_pdbqt, docked, log)

    print("\nDone. Check the results/ directory.")
    print("Next: python scripts/analyze_results.py --docked", docked)


if __name__ == "__main__":
    main()
