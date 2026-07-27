#!/usr/bin/env python3
"""End-to-end protein-ligand docking wrapper (AutoDock Vina)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# allow running as python scripts/run_docking.py
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from prepare_ligand import sdf_or_mol2_to_pdbqt, smiles_to_3d
from prepare_receptor import clean_pdb, pdb_to_pdbqt


def run_vina(config: Path, receptor: Path, ligand: Path, out: Path, log: Path):
    if shutil.which("vina") is None:
        raise RuntimeError(
            "vina not found on PATH. Run: conda activate docking && python scripts/check_vina.py"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "vina",
        "--receptor",
        str(receptor),
        "--ligand",
        str(ligand),
        "--config",
        str(config),
        "--out",
        str(out),
    ]
    print("[*] Running AutoDock Vina...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    combined = (result.stdout or "") + (result.stderr or "")
    log.write_text(combined)
    if result.returncode != 0:
        raise RuntimeError(f"Vina failed (exit {result.returncode}):\n{combined}")
    print(combined)
    print(f"[+] Docking finished. Results: {out}")
    print(f"[+] Log: {log}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Full protein-ligand docking pipeline")
    parser.add_argument("--receptor", required=True, help="Input protein PDB")
    parser.add_argument("--ligand", required=True, help="Ligand SMILES / SDF / MOL2 / SMI")
    parser.add_argument("--config", required=True, help="Vina config (box + parameters)")
    parser.add_argument("--out", default="results", help="Output directory")
    parser.add_argument("--ph", type=float, default=7.4)
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    prepared = out_dir / "prepared"
    prepared.mkdir(parents=True, exist_ok=True)

    receptor_pdb = Path(args.receptor)
    if not receptor_pdb.exists():
        print(f"ERROR: receptor not found: {receptor_pdb}", file=sys.stderr)
        return 1
    if not Path(args.config).exists():
        print(f"ERROR: config not found: {args.config}", file=sys.stderr)
        return 1

    receptor_pdbqt = prepared / "receptor.pdbqt"
    ligand_pdbqt = prepared / "ligand.pdbqt"

    try:
        print("=== Preparing receptor ===")
        cleaned = prepared / "receptor.clean.pdb"
        clean_pdb(receptor_pdb, cleaned)
        pdb_to_pdbqt(cleaned, receptor_pdbqt)

        print("=== Preparing ligand ===")
        lig_path = Path(args.ligand)
        if lig_path.suffix.lower() in {".smi", ".smiles"} or not lig_path.exists():
            if lig_path.exists():
                smiles = lig_path.read_text().strip().splitlines()[0].split()[0]
            else:
                smiles = args.ligand
            temp_sdf = prepared / "ligand.tmp.sdf"
            smiles_to_3d(smiles, temp_sdf)
            sdf_or_mol2_to_pdbqt(temp_sdf, ligand_pdbqt, args.ph)
            temp_sdf.unlink(missing_ok=True)
        else:
            sdf_or_mol2_to_pdbqt(lig_path, ligand_pdbqt, args.ph)

        print("=== Docking ===")
        docked = out_dir / "docked.pdbqt"
        log = out_dir / "vina.log"
        run_vina(Path(args.config), receptor_pdbqt, ligand_pdbqt, docked, log)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
