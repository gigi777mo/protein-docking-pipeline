# Protein-Ligand Docking Pipeline

**Small-molecule (ligand) docking to proteins** using open-source tools.

A clean, reproducible, modular pipeline centered on **AutoDock Vina 1.2+**, with structure preparation via **Open Babel** and **RDKit**, and analysis helpers in Python.

Ideal for structure-based virtual screening, pose prediction, and binding mode analysis in academic labs.

---

## Pipeline Overview

```
1. Receptor Preparation
   PDB → clean (remove waters/hetatms) → add H → PDBQT

2. Ligand Preparation
   SMILES / SDF / MOL2 → 3D embed + minimize → protonate (pH 7.4) → PDBQT

3. Binding Site Definition
   - From co-crystal ligand (recommended)
   - Manual box coordinates
   - Optional: pocket prediction tools

4. Docking (AutoDock Vina)
   Exhaustiveness, energy range, number of modes configurable

5. Post-processing
   Rank poses by score → extract top poses → optional interaction fingerprints
```

---

## Quick Start

### 1. Install dependencies (Conda recommended)

```bash
# Create environment
conda env create -f environment.yml
conda activate docking

# Or minimal pip install (after system OpenBabel + Vina)
pip install -r requirements.txt
```

**Key tools required:**
- AutoDock Vina ≥ 1.2.0 (`vina` command must be in PATH)
- Open Babel (`obabel`)
- Python 3.9+ with RDKit, Biopython, pandas, numpy

### 2. Prepare your files

Place your files like this:

```
data/
├── receptors/
│   └── my_protein.pdb
├── ligands/
│   ├── ligand1.smi          # or .sdf / .mol2
│   └── ligand2.sdf
└── configs/
    └── docking_config.txt   # Vina config (box, exhaustiveness...)
```

### 3. Run the pipeline

```bash
# Single ligand example
python scripts/run_docking.py \
  --receptor data/receptors/my_protein.pdb \
  --ligand data/ligands/ligand1.smi \
  --config data/configs/docking_config.txt \
  --out results/run1
```

Or use the full modular steps (recommended for understanding):

```bash
# Step 1: Prepare receptor
python scripts/prepare_receptor.py -i data/receptors/my_protein.pdb -o prepared/receptor.pdbqt

# Step 2: Prepare ligand
python scripts/prepare_ligand.py -i data/ligands/ligand1.smi -o prepared/ligand.pdbqt

# Step 3: Dock
vina --config data/configs/docking_config.txt --receptor prepared/receptor.pdbqt --ligand prepared/ligand.pdbqt --out results/docked.pdbqt --log results/vina.log

# Step 4: Analyze
python scripts/analyze_results.py --docked results/docked.pdbqt --out results/summary.csv
```

---

## Directory Structure

```
protein-docking-pipeline/
├── README.md
├── environment.yml
├── requirements.txt
├── scripts/
│   ├── prepare_receptor.py
│   ├── prepare_ligand.py
│   ├── run_docking.py          # end-to-end wrapper
│   ├── analyze_results.py
│   └── utils.py
├── data/
│   ├── receptors/             # put your .pdb files here
│   ├── ligands/               # SMILES / SDF / MOL2
│   └── configs/
│       └── example_config.txt
├── prepared/                 # intermediate PDBQT files
└── results/                   # docking outputs + summaries
```

---

## Defining the Search Box (Critical Step)

AutoDock Vina needs a box that covers the binding site.

**Best practice:** Use a co-crystal ligand if available.

1. Open the complex in PyMOL / ChimeraX / Discovery Studio.
2. Select the ligand → calculate center of mass and approximate size.
3. Or use the provided helper:

```bash
python scripts/utils.py --get-box --ligand data/ligands/crystal_ligand.pdb --padding 5.0
```

Example `docking_config.txt`:

```
center_x = 12.345
center_y = -5.678
center_z = 23.901
size_x = 22
size_y = 22
size_z = 22
exhaustiveness = 32
num_modes = 20
energy_range = 4
```

Higher `exhaustiveness` (16–64) improves sampling for larger or flexible ligands (at cost of time).

---

## Key Scripts Explained

| Script | Purpose |
|--------|---------|
| `prepare_receptor.py` | Removes waters, heteroatoms (optional keep cofactors), adds polar hydrogens, converts to rigid PDBQT |
| `prepare_ligand.py` | Handles SMILES/SDF/MOL2 → generates 3D conformer, minimizes, protonates at pH 7.4, outputs PDBQT with torsions |
| `run_docking.py` | End-to-end: prepare + dock + basic ranking |
| `analyze_results.py` | Parses Vina output, ranks poses by affinity, writes CSV + top poses |

---

## Tips for Good Results

- Always start from a high-quality receptor structure (ideally <2.5 Å resolution, no large missing loops near the site).
- Protonation state of the ligand matters a lot — the pipeline defaults to pH 7.4.
- For virtual screening of large libraries, use lower exhaustiveness first (8), then re-dock top hits with higher exhaustiveness.
- Validate by redocking a known co-crystal ligand (RMSD < 2.0 Å is usually considered successful).
- Consider flexible side chains only for residues known to move significantly (advanced).

---

## Modern Alternatives (2024–2026)

If you need state-of-the-art deep learning docking:

- **DiffDock / DiffDock-L** (https://github.com/gcorso/DiffDock) — diffusion model, excellent for pose prediction
- **GNINA** — Vina + CNN scoring
- **EasyDock** — modern automated pipeline supporting multiple engines

This repository focuses on the classic, fully open, transparent, and easily auditable AutoDock Vina workflow that is still the workhorse in most labs.

---

## Citation

If you use this pipeline, please cite AutoDock Vina:

> Eberhardt J, Santos-Martins D, Tillack AF, Forli S. AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. J Chem Inf Model. 2021.

> Trott O, Olson AJ. AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. J Comput Chem. 2010.

---

## License

MIT License — free for academic and commercial use.

Feel free to open issues or PRs for improvements (e.g., P2Rank integration, batch screening, interaction analysis with PLIP).
