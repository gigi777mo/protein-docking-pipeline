#!/usr/bin/env python3
"""
Thin wrapper / helper for running DiffDock.

This script does not install DiffDock. It assumes you have already set up
the DiffDock environment following the official instructions:
https://github.com/gcorso/DiffDock

It simply provides a convenient interface that matches the rest of this pipeline.
"""

import argparse
import subprocess
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description="Helper to run DiffDock inference")
    parser.add_argument("--protein", required=True, help="Protein PDB file")
    parser.add_argument("--ligand", required=True,
                        help="Ligand SMILES string or path to SDF/MOL2")
    parser.add_argument("--out", default="results/diffdock")
    parser.add_argument("--samples", type=int, default=40,
                        help="Number of poses to sample (DiffDock default ~40)")
    parser.add_argument("--diffdock-dir", default=None,
                        help="Path to your local DiffDock repository clone")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    protein = Path(args.protein).resolve()
    ligand = args.ligand

    print("DiffDock helper")
    print("===============")
    print(f"Protein : {protein}")
    print(f"Ligand  : {ligand}")
    print(f"Output  : {out_dir}")
    print()

    if args.diffdock_dir:
        diffdock_path = Path(args.diffdock_dir)
        if not (diffdock_path / "inference.py").exists():
            print("[!] inference.py not found in the provided DiffDock directory")
            return
    else:
        # Try to find it in PATH or common locations
        if shutil.which("python") is None:
            print("Python not found")
            return
        print("No --diffdock-dir provided.")
        print("Please either:")
        print("  1. Activate your DiffDock conda environment, then run this script with --diffdock-dir /path/to/DiffDock")
        print("  2. Or run DiffDock manually:")
        print()
        print("Example DiffDock command:")
        print(f"  python inference.py --protein_path {protein} \\")
        print(f"      --ligand \"{ligand}\" \\")
        print(f"      --out_dir {out_dir} \\")
        print(f"      --samples_per_complex {args.samples} \\")
        print("      --inference_steps 20 --batch_size 10")
        return

    # If directory is provided, try to call it
    cmd = [
        "python", str(diffdock_path / "inference.py"),
        "--protein_path", str(protein),
        "--out_dir", str(out_dir),
        "--samples_per_complex", str(args.samples),
        "--inference_steps", "20",
        "--batch_size", "8",
        "--actual_steps", "18",
        "--no_final_step_noise"
    ]

    # Ligand handling
    if Path(ligand).exists():
        cmd += ["--ligand", ligand]
    else:
        cmd += ["--ligand", ligand]  # SMILES is also accepted by DiffDock

    print("[*] Launching DiffDock...")
    print(" ".join(cmd))
    subprocess.run(cmd, check=False)

    print(f"\n[+] Check results in {out_dir}")
    print("DiffDock ranks poses by confidence. Higher confidence is better.")


if __name__ == "__main__":
    main()
