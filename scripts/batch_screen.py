#!/usr/bin/env python3
"""Batch virtual screening with AutoDock Vina."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import pandas as pd

from analyze_results import parse_vina_pdbqt
from prepare_ligand import sdf_or_mol2_to_pdbqt, smiles_to_3d
from prepare_receptor import clean_pdb, pdb_to_pdbqt


def prepare_receptor_once(receptor_pdb: Path, prepared_dir: Path):
    receptor_pdbqt = prepared_dir / "receptor.pdbqt"
    if receptor_pdbqt.exists():
        return receptor_pdbqt
    cleaned = prepared_dir / "receptor.clean.pdb"
    clean_pdb(receptor_pdb, cleaned)
    pdb_to_pdbqt(cleaned, receptor_pdbqt)
    return receptor_pdbqt


def process_smiles_file(smiles_file: Path):
    ligands = []
    with open(smiles_file) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            smi = parts[0]
            name = parts[1] if len(parts) > 1 else f"lig_{i+1:04d}"
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
            ligands.append((safe or f"lig_{i+1:04d}", smi))
    return ligands


def process_sdf(sdf_file: Path):
    from rdkit import Chem

    ligands = []
    suppl = Chem.SDMolSupplier(str(sdf_file))
    for i, mol in enumerate(suppl):
        if mol is None:
            continue
        name = mol.GetProp("_Name") if mol.HasProp("_Name") else f"lig_{i+1:04d}"
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        smi = Chem.MolToSmiles(mol)
        ligands.append((safe or f"lig_{i+1:04d}", smi))
    return ligands


def dock_one(receptor_pdbqt, ligand_pdbqt, config, out_pdbqt, log_file, exhaustiveness=None):
    if shutil.which("vina") is None:
        raise RuntimeError("vina not on PATH; conda activate docking")
    cmd = [
        "vina",
        "--receptor",
        str(receptor_pdbqt),
        "--ligand",
        str(ligand_pdbqt),
        "--config",
        str(config),
        "--out",
        str(out_pdbqt),
    ]
    if exhaustiveness:
        cmd += ["--exhaustiveness", str(exhaustiveness)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_file.write_text((result.stdout or "") + (result.stderr or ""))
    if result.returncode != 0:
        print(f"  [!] Vina failed for {ligand_pdbqt.name}")
        print((result.stderr or result.stdout or "")[:300])
        return None
    return out_pdbqt


def main(argv=None):
    parser = argparse.ArgumentParser(description="Batch virtual screening with Vina")
    parser.add_argument("--receptor", required=True)
    parser.add_argument("--ligands", required=True, help="SDF or SMILES file")
    parser.add_argument("--config", required=True, help="Vina config (box)")
    parser.add_argument("--out", default="results/batch")
    parser.add_argument("--exhaustiveness", type=int, default=16)
    parser.add_argument("--ph", type=float, default=7.4)
    args = parser.parse_args(argv)

    try:
        out_dir = Path(args.out)
        prepared = out_dir / "prepared"
        poses_dir = out_dir / "poses"
        prepared.mkdir(parents=True, exist_ok=True)
        poses_dir.mkdir(exist_ok=True)

        if not Path(args.receptor).exists():
            raise FileNotFoundError(f"receptor not found: {args.receptor}")
        if not Path(args.ligands).exists():
            raise FileNotFoundError(f"ligands not found: {args.ligands}")
        if not Path(args.config).exists():
            raise FileNotFoundError(f"config not found: {args.config}")

        print("=== Preparing receptor ===")
        receptor_pdbqt = prepare_receptor_once(Path(args.receptor), prepared)

        lig_path = Path(args.ligands)
        if lig_path.suffix.lower() in {".sdf", ".sd"}:
            ligands = process_sdf(lig_path)
        else:
            ligands = process_smiles_file(lig_path)

        print(f"[+] {len(ligands)} ligands to dock")
        results = []
        for name, smi in ligands:
            print(f"\n--- {name} ---")
            lig_pdbqt = prepared / f"{name}.pdbqt"
            temp_sdf = prepared / f"{name}.tmp.sdf"
            try:
                smiles_to_3d(smi, temp_sdf)
                sdf_or_mol2_to_pdbqt(temp_sdf, lig_pdbqt, args.ph)
                temp_sdf.unlink(missing_ok=True)
            except Exception as e:
                print(f"  [!] Ligand preparation failed: {e}")
                continue

            out_pdbqt = poses_dir / f"{name}_docked.pdbqt"
            log_file = poses_dir / f"{name}.log"
            docked = dock_one(
                receptor_pdbqt,
                lig_pdbqt,
                Path(args.config),
                out_pdbqt,
                log_file,
                args.exhaustiveness,
            )
            if docked is None:
                continue

            poses = parse_vina_pdbqt(docked)
            if poses:
                best = min(poses, key=lambda x: x["affinity"])
                results.append(
                    {
                        "name": name,
                        "smiles": smi,
                        "best_affinity": best["affinity"],
                        "model": best["model"],
                    }
                )
                print(f"  Best affinity: {best['affinity']:.2f} kcal/mol")

        if results:
            df = pd.DataFrame(results).sort_values("best_affinity")
            summary = out_dir / "summary.csv"
            df.to_csv(summary, index=False)
            print(f"\n[+] Ranked results saved to {summary}")
            print(df.head(10).to_string(index=False))
        else:
            print("No successful dockings.")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
