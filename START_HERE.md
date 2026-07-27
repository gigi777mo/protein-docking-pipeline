# START HERE (no docking experience needed)

---

> ## 🔴 USE MINICONDA
>
> **Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) first.**  
> Then create the project environment.  
> You also need **AutoDock Vina** installed and on your PATH.

---

## What this does (plain English)

Predicts how a **small molecule** sits on a **protein** (docking score + poses).  
Uses **AutoDock Vina** (standard academic tool).

---

## Step 1 — Miniconda

https://docs.conda.io/en/latest/miniconda.html  
Install → open a new terminal.

---

## Step 2 — Code + environment

```bash
git clone https://github.com/gigi777mo/protein-docking-pipeline.git
cd protein-docking-pipeline

conda env create -f environment.yml
conda activate docking
```

---

## Step 3 — Install AutoDock Vina (required)

1. Download a release: https://github.com/ccsb-scripps/AutoDock-Vina/releases  
2. Put the `vina` program somewhere on your PATH  
3. Check: `vina --help` should print help text  

---

## Step 4 — Your files

- Protein structure: `.pdb`  
- Ligand: SMILES file (`.smi`) or prepared structure  

Example ligand file (`data/ligands/benzamidine.smi` is included).

---

## Step 5 — Run a simple docking

```bash
conda activate docking

python scripts/run_docking.py \
  --receptor data/receptors/your_protein.pdb \
  --ligand data/ligands/your_ligand.smi \
  --config data/configs/example_config.txt \
  --out results/my_run
```

Follow README for pocket detection, batch screening, RMSD, DiffDock options.

---

## If it fails

| Problem | Fix |
|---------|-----|
| `vina: command not found` | Install Vina; fix PATH |
| `conda not found` | Install Miniconda; new terminal |
| Bad poses | Check receptor preparation; try higher exhaustiveness |

Scoring details: [docs/scoring_function.md](docs/scoring_function.md)  
Citations: [docs/CITATIONS.md](docs/CITATIONS.md)
