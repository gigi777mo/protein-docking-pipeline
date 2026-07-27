#!/usr/bin/env python3
"""Heavy-atom RMSD between docked pose and reference ligand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


def load_mol(path: Path, remove_hs=True):
    from rdkit import Chem

    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in {".sdf", ".sd", ".mol"}:
        suppl = Chem.SDMolSupplier(str(path), removeHs=False)
        mol = next((m for m in suppl if m is not None), None)
    elif suffix in {".pdb", ".ent"}:
        mol = Chem.MolFromPDBFile(str(path), removeHs=False)
    elif suffix == ".pdbqt":
        with open(path) as f:
            lines = [l for l in f if l.startswith(("ATOM", "HETATM"))]
        temp_pdb = path.with_suffix(".tmp.pdb")
        with open(temp_pdb, "w") as out:
            out.writelines(lines)
            out.write("END\n")
        mol = Chem.MolFromPDBFile(str(temp_pdb), removeHs=False)
        temp_pdb.unlink(missing_ok=True)
    elif suffix == ".mol2":
        mol = Chem.MolFromMol2File(str(path), removeHs=False)
    else:
        raise ValueError(f"Unsupported format: {suffix}")

    if mol is None:
        raise ValueError(f"Could not parse molecule from {path}")
    if remove_hs:
        mol = Chem.RemoveHs(mol)
    return mol


def calc_rmsd(ref_mol, dock_mol):
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign

    ref_heavy = Chem.RemoveHs(ref_mol)
    dock_heavy = Chem.RemoveHs(dock_mol)
    try:
        return float(rdMolAlign.GetBestRMS(dock_heavy, ref_heavy))
    except Exception:
        conf_ref = ref_heavy.GetConformer()
        conf_dock = dock_heavy.GetConformer()
        n = min(ref_heavy.GetNumAtoms(), dock_heavy.GetNumAtoms())
        coords_ref = np.array([list(conf_ref.GetAtomPosition(i)) for i in range(n)])
        coords_dock = np.array([list(conf_dock.GetAtomPosition(i)) for i in range(n)])
        diff = coords_ref - coords_dock
        return float(np.sqrt((diff**2).sum(axis=1).mean()))


def extract_vina_models(pdbqt_path: Path):
    models = []
    current_lines = []
    model_num = 0
    with open(pdbqt_path) as f:
        for line in f:
            if line.startswith("MODEL"):
                if current_lines:
                    models.append((model_num, current_lines))
                try:
                    model_num = int(line.split()[1])
                except (IndexError, ValueError):
                    model_num += 1
                current_lines = []
            elif line.startswith("ENDMDL"):
                if current_lines:
                    models.append((model_num, current_lines))
                current_lines = []
            elif line.startswith(("ATOM", "HETATM")):
                current_lines.append(line)
    if current_lines:
        models.append((model_num or 1, current_lines))
    return models


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calculate RMSD for redocking validation")
    parser.add_argument("--ref", required=True)
    parser.add_argument("--docked", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    try:
        ref_path = Path(args.ref)
        docked_path = Path(args.docked)
        if not ref_path.exists():
            raise FileNotFoundError(f"ref not found: {ref_path}")
        if not docked_path.exists():
            raise FileNotFoundError(f"docked not found: {docked_path}")

        ref_mol = load_mol(ref_path)
        results = []

        text_head = docked_path.read_text(errors="ignore")[:4000]
        if docked_path.suffix.lower() == ".pdbqt" and "MODEL" in text_head:
            models = extract_vina_models(docked_path)
            print(f"Found {len(models)} poses\n")
            print(f"{'Model':>6}  {'RMSD (A)':>10}")
            print("-" * 20)
            for model_num, lines in models:
                temp = docked_path.parent / f"_temp_model_{model_num}.pdb"
                with open(temp, "w") as f:
                    f.writelines(lines)
                    f.write("END\n")
                try:
                    dock_mol = load_mol(temp)
                    rmsd = calc_rmsd(ref_mol, dock_mol)
                    results.append({"model": model_num, "rmsd": rmsd})
                    flag = "  <-- success" if rmsd < 2.0 else ""
                    print(f"{model_num:6d}  {rmsd:10.3f}{flag}")
                except Exception as e:
                    print(f"{model_num:6d}  failed: {e}")
                finally:
                    temp.unlink(missing_ok=True)
        else:
            dock_mol = load_mol(docked_path)
            rmsd = calc_rmsd(ref_mol, dock_mol)
            results.append({"model": 1, "rmsd": rmsd})
            print(f"RMSD = {rmsd:.3f} A")

        if args.out and results:
            import pandas as pd

            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(results).to_csv(out, index=False)
            print(f"\nResults written to {out}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
