# Protein-Ligand Docking Pipeline

**Small-molecule (ligand) docking to proteins** — clean, modular, and reproducible.

Core engine: **AutoDock Vina 1.2+**  
Preparation: OpenBabel + RDKit + Biopython  
Extras: P2Rank pocket detection • Batch virtual screening • DiffDock option • RMSD validation • Example library • GitHub Actions CI

---

## Features

- Receptor & ligand preparation (PDB → PDBQT, SMILES/SDF → PDBQT)
- Automatic binding site prediction with **P2Rank**
- Single-ligand and **batch virtual screening** modes
- Pose ranking + CSV summary
- **RMSD calculation** for redocking validation
- Optional **DiffDock** path for deep-learning docking
- Ready-to-run **redocking example** (trypsin + benzamidine)
- Small example multi-ligand library
- Basic GitHub Actions CI (syntax + import checks)

---

## Installation

```bash
git clone https://github.com/gigi777mo/protein-docking-pipeline.git
cd protein-docking-pipeline

conda env create -f environment.yml
conda activate docking

# AutoDock Vina must be in PATH
# https://github.com/ccsb-scripps/AutoDock-Vina/releases
```

Optional:
- P2Rank → https://github.com/rdk/p2rank
- DiffDock → https://github.com/gcorso/DiffDock

---

## Quick Start

### Single ligand
```bash
python scripts/run_docking.py \
  --receptor data/receptors/your_protein.pdb \
  --ligand data/ligands/your_ligand.smi \
  --config data/configs/example_config.txt \
  --out results/my_run
```

### Automatic pocket detection (P2Rank)
```bash
python scripts/predict_pocket.py --receptor protein.pdb --out results/pockets
```

### Batch virtual screening
```bash
python scripts/batch_screen.py \
  --receptor protein.pdb \
  --ligands data/ligands/example_library.smi \
  --config data/configs/example_config.txt \
  --out results/vs_run
```

### Calculate RMSD (redocking validation)
```bash
python scripts/calculate_rmsd.py \
  --ref reference_ligand.pdb \
  --docked results/docked.pdbqt
```
A top pose with **RMSD < 2.0 Å** is generally considered a successful redocking.

### DiffDock (deep learning)
```bash
python scripts/run_diffdock.py \
  --protein protein.pdb \
  --ligand "SMILES_OR_FILE" \
  --out results/diffdock_run \
  --diffdock-dir /path/to/DiffDock
```

---

## Example Multi-Ligand Library

`data/ligands/example_library.smi` contains 6 simple drug-like molecules (benzamidine, aspirin, caffeine, ibuprofen, etc.) ready for testing the batch screening script.

---

## Redocking Validation Example

Classic system: **trypsin + benzamidine**

```bash
# Download structure
mkdir -p data/receptors
wget -O data/receptors/3PTB.pdb https://files.rcsb.org/download/3PTB.pdb

# Use the provided SMILES
# data/ligands/benzamidine.smi

# After docking, check RMSD of the poses against the crystal ligand
python scripts/calculate_rmsd.py --ref crystal_benzamidine.pdb --docked results/docked.pdbqt
```

---

## Directory Layout

```
scripts/
  prepare_receptor.py
  prepare_ligand.py
  run_docking.py
  batch_screen.py
  predict_pocket.py
  run_diffdock.py
  analyze_results.py
  calculate_rmsd.py      # NEW
  utils.py

data/ligands/
  example_library.smi    # NEW – small test library
  benzamidine.smi
  example_ligand.smi
```

---

## Continuous Integration

A basic GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:
- Syntax checking of all Python scripts
- Import tests for core modules
- Verification that the example library is readable

Full end-to-end docking tests require Vina + OpenBabel and are left for local runs.

---

## Tips

- Always validate with a known redocking case first.
- Use higher exhaustiveness (32–64) for final poses; lower (8–16) for large screens.
- Protonation at pH 7.4 is the default — adjust if your ligand has unusual pKa.
- After docking, inspect poses visually and consider interaction analysis (PLIP is excellent).

---

## Citation

**AutoDock Vina** — Eberhardt et al. (2021), Trott & Olson (2010)  
**P2Rank** — Krivák & Hoksza (2018)  
**DiffDock** — Corso et al. (2023)

---

## License

MIT
