# Protein-Ligand Docking Pipeline

**Small-molecule (ligand) docking to proteins** — clean, modular, and reproducible.

Core engine: **AutoDock Vina 1.2+**  
Preparation: OpenBabel + RDKit + Biopython  
Extras: P2Rank pocket detection • Batch virtual screening • DiffDock (deep learning) option • Redocking validation example

---

## Features

- Receptor & ligand preparation (PDB → PDBQT, SMILES/SDF → PDBQT)
- Automatic binding site prediction with **P2Rank**
- Single-ligand and **batch virtual screening** modes
- Pose ranking + CSV summary
- Optional **DiffDock** path for state-of-the-art deep learning docking
- Ready-to-run **redocking example** (trypsin + benzamidine)

---

## Installation

```bash
git clone https://github.com/gigi777mo/protein-docking-pipeline.git
cd protein-docking-pipeline

# Recommended
conda env create -f environment.yml
conda activate docking

# You still need AutoDock Vina in PATH
# Download from: https://github.com/ccsb-scripps/AutoDock-Vina/releases
# or: conda install -c conda-forge vina
```

**Optional but recommended extras:**

```bash
# P2Rank (pocket prediction)
# Download from https://github.com/rdk/p2rank/releases and add `prank` to PATH

# DiffDock (deep learning docking)
# Follow instructions at https://github.com/gcorso/DiffDock
```

---

## Quick Start (Single Ligand)

```bash
python scripts/run_docking.py \
  --receptor data/receptors/your_protein.pdb \
  --ligand data/ligands/your_ligand.smi \
  --config data/configs/example_config.txt \
  --out results/my_run
```

---

## 1. Automatic Pocket Detection (P2Rank)

If you do not know the binding site:

```bash
# Predict pockets
python scripts/predict_pocket.py \
  --receptor data/receptors/your_protein.pdb \
  --out results/pockets \
  --top 1          # use the top-scoring pocket

# This generates a ready-to-use Vina config file with center + size
```

The script runs `prank predict`, reads the top pocket center from `*_predictions.csv`, and writes a Vina-compatible config (default box size 22 Å, adjustable).

---

## 2. Batch Virtual Screening

Dock many ligands against one receptor:

```bash
python scripts/batch_screen.py \
  --receptor data/receptors/your_protein.pdb \
  --ligands data/ligands/library.sdf   # or .smi (one SMILES per line)
  --config data/configs/example_config.txt \
  --out results/vs_run \
  --exhaustiveness 16
```

Outputs:
- Individual docked poses
- `summary.csv` ranked by best affinity
- Easy to filter top hits for further analysis

---

## 3. DiffDock Option (Deep Learning)

For higher accuracy on many targets (especially when the binding site is unknown or the protein is flexible):

1. Install DiffDock following the official repo: https://github.com/gcorso/DiffDock
2. Use the provided helper:

```bash
python scripts/run_diffdock.py \
  --protein data/receptors/your_protein.pdb \
  --ligand "CCO..." \          # SMILES or path to SDF
  --out results/diffdock_run
```

The script is a thin wrapper that calls DiffDock inference and reorganizes the output for easy comparison with Vina results. DiffDock often outperforms classical docking on pose prediction benchmarks.

---

## 4. Redocking Validation Example (Trypsin + Benzamidine)

Classic, well-behaved system for testing your installation.

**Ligand SMILES (benzamidine):**
```
NC(=N)C1=CC=CC=C1
```

**Recommended steps:**

```bash
# 1. Download the structure (3PTB is the classic entry)
# From RCSB: https://www.rcsb.org/structure/3PTB
# Or use:
mkdir -p data/receptors
wget -O data/receptors/3PTB.pdb https://files.rcsb.org/download/3PTB.pdb

# 2. Extract / prepare the known ligand (or use the SMILES above)
# 3. Calculate box from the co-crystal ligand or use P2Rank
python scripts/utils.py --get-box --ligand path/to/benzamidine_from_pdb.pdb --padding 6

# 4. Run docking and check if top pose has RMSD < 2.0 Å to crystal
```

A successful redocking (RMSD of top pose < 2.0 Å) confirms your environment and parameters are working correctly.

---

## Directory Layout

```
protein-docking-pipeline/
├── scripts/
│   ├── prepare_receptor.py
│   ├── prepare_ligand.py
│   ├── run_docking.py
│   ├── batch_screen.py          # NEW
│   ├── predict_pocket.py         # NEW (P2Rank)
│   ├── run_diffdock.py           # NEW (wrapper)
│   ├── analyze_results.py
│   └── utils.py
├── data/
│   ├── receptors/
│   ├── ligands/
│   │   ├── example_ligand.smi
│   │   └── benzamidine.smi        # NEW
│   └── configs/
├── results/
└── ...
```

---

## Tips for Best Results

- Always redock a known ligand first to validate the setup.
- Use higher `exhaustiveness` (32–64) for final pose prediction; lower (8–16) for large virtual screens.
- Protonation state of the ligand is critical — the pipeline defaults to pH 7.4.
- For flexible receptors, consider induced-fit docking or DiffDock.
- After docking, inspect top poses in PyMOL / ChimeraX and calculate interaction fingerprints if needed (PLIP is excellent).

---

## Citation

**AutoDock Vina**
> Eberhardt J et al. J Chem Inf Model. 2021.  
> Trott O, Olson AJ. J Comput Chem. 2010.

**P2Rank**
> Krivák R, Hoksza D. J Cheminform. 2018.

**DiffDock**
> Corso G et al. ICLR 2023 / DiffDock-L updates.

---

## License

MIT
