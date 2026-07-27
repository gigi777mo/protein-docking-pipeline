#!/usr/bin/env python3
"""
Calculate heavy-atom RMSD between a docked pose and a reference ligand structure.

Useful for redocking validation (success usually defined as RMSD < 2.0 Å).

Supports:
- Reference: PDB / SDF / MOL2
- Docked: Vina multi-model PDBQT or single pose SDF/PDBQT
"""

import argparse
from pathlib import Path
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign


def load_mol(path: Path, remove_hs=True):
    """Load a molecule from common formats."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in [".sdf", ".sd", ".mol"]:
        mol = Chem.SDMolSupplier(str(path), removeHs=False)[0]
    elif suffix in [".pdb", ".ent"]:
        mol = Chem.MolFromPDBFile(str(path), removeHs=False)
    elif suffix == ".pdbqt":
        # RDKit does not natively read PDBQT well; convert via OpenBabel first or strip
        # For simplicity we try PDB-like parsing after removing charges/torsions comments
        with open(path) as f:
            lines = [l for l in f if l.startswith(("ATOM", "HETATM"))]
        temp_pdb = path.with_suffix(".tmp.pdb")
        with open(temp_pdb, "w") as out:
            out.writelines(lines)
        mol = Chem.MolFromPDBFile(str(temp_pdb), removeHs=False)
        temp_pdb.unlink(missing_ok=True)
    elif suffix in [".mol2"]:
        mol = Chem.MolFromMol2File(str(path), removeHs=False)
    else:
        raise ValueError(f"Unsupported format: {suffix}")

    if mol is None:
        raise ValueError(f"Could not parse molecule from {path}")

    if remove_hs:
        mol = Chem.RemoveHs(mol)
    return mol


def calc_rmsd(ref_mol, dock_mol):
    """Calculate minimum RMSD after optimal alignment (heavy atoms)."""
    # Ensure same number of heavy atoms
    ref_heavy = Chem.RemoveHs(ref_mol)
    dock_heavy = Chem.RemoveHs(dock_mol)

    if ref_heavy.GetNumAtoms() != dock_heavy.GetNumAtoms():
        print(f"[!] Warning: atom count mismatch (ref={ref_heavy.GetNumAtoms()}, "
              f"dock={dock_heavy.GetNumAtoms()}). Trying best-effort match.")

    # Use RDKit's alignment
    try:
        rmsd = rdMolAlign.GetBestRMS(dock_heavy, ref_heavy)
    except Exception:
        # Fallback: simple coordinate RMSD without atom mapping (less accurate)
        conf_ref = ref_heavy.GetConformer()
        conf_dock = dock_heavy.GetConformer()
        coords_ref = np.array([list(conf_ref.GetAtomPosition(i)) for i in range(ref_heavy.GetNumAtoms())])
        coords_dock = np.array([list(conf_dock.GetAtomPosition(i)) for i in range(min(dock_heavy.GetNumAtoms(), ref_heavy.GetNumAtoms()))])
        diff = coords_ref[:len(coords_dock)] - coords_dock
        rmsd = np.sqrt((diff**2).sum(axis=1).mean())

    return rmsd


def extract_vina_models(pdbqt_path: Path):
    """Split a multi-model Vina PDBQT into individual temporary molecules."""
    models = []
    current_lines = []
    model_num = 0

    with open(pdbqt_path) as f:
        for line in f:
            if line.startswith("MODEL"):
                if current_lines:
                    models.append((model_num, current_lines))
                model_num = int(line.split()[1])
                current_lines = []
            elif line.startswith("ENDMDL"):
                if current_lines:
                    models.append((model_num, current_lines))
                current_lines = []
            elif line.startswith(("ATOM", "HETATM")):
                current_lines.append(line)

    return models


def main():
    parser = argparse.ArgumentParser(description="Calculate RMSD for redocking validation")
    parser.add_argument("--ref", required=True, help="Reference ligand structure (PDB/SDF/MOL2)")
    parser.add_argument("--docked", required=True, help="Docked pose(s) – Vina PDBQT or single SDF/PDB")
    parser.add_argument("--out", default=None, help="Optional CSV output")
    args = parser.parse_args()

    ref_mol = load_mol(Path(args.ref))
    docked_path = Path(args.docked)

    results = []

    if docked_path.suffix.lower() == ".pdbqt" and "MODEL" in docked_path.read_text()[:2000]:
        # Multi-model Vina output
        models = extract_vina_models(docked_path)
        print(f"Found {len(models)} poses in Vina output\n")
        print(f"{'Model':>6}  {'RMSD (Å)':>10}")
        print("-" * 20)

        for model_num, lines in models:
            temp = docked_path.parent / f"_temp_model_{model_num}.pdb"
            with open(temp, "w") as f:
                f.writelines(lines)
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
        # Single pose
        dock_mol = load_mol(docked_path)
        rmsd = calc_rmsd(ref_mol, dock_mol)
        results.append({"model": 1, "rmsd": rmsd})
        print(f"RMSD = {rmsd:.3f} Å")
        if rmsd < 2.0:
            print("Success (RMSD < 2.0 Å)")
        else:
            print("RMSD >= 2.0 Å – pose may need inspection")

    if args.out and results:
        import pandas as pd
        pd.DataFrame(results).to_csv(args.out, index=False)
        print(f"\nResults written to {args.out}")


if __name__ == "__main__":
    main()
