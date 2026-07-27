# START HERE (no docking experience needed)

---

> ## 🔴 USE MINICONDA
>
> **Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) first.**  
> The environment file now **includes AutoDock Vina** (`autodock-vina` from bioconda).

---

## What this does (plain English)

Predicts how a **small molecule** binds to a **protein** using **AutoDock Vina**, then helps you rank poses and check RMSD.

---

## Step 1 — Miniconda

https://docs.conda.io/en/latest/miniconda.html  
Install → open a **new** terminal / Anaconda Prompt.

---

## Step 2 — Get code + create environment (includes Vina)

```bash
git clone https://github.com/gigi777mo/protein-docking-pipeline.git
cd protein-docking-pipeline

conda env create -f environment.yml
conda activate docking
```

This installs Python tools **and** the **`vina`** program.

---

## Step 3 — Confirm Vina works

```bash
conda activate docking
python scripts/check_vina.py
# or:
vina --help
```

You should see help text and `[OK] vina binary`.

If missing:

```bash
conda install -c bioconda autodock-vina
```

Or download a release: https://github.com/ccsb-scripps/AutoDock-Vina/releases

---

## Step 4 — Your files

- Protein: `.pdb`  
- Ligand: `.smi` (SMILES) or prepared ligand  

Example SMILES files are under `data/ligands/`.

---

## Step 5 — Run docking

```bash
conda activate docking

python scripts/run_docking.py \
  --receptor data/receptors/your_protein.pdb \
  --ligand data/ligands/your_ligand.smi \
  --config data/configs/example_config.txt \
  --out results/my_run
```

---

## If it fails

| Problem | Fix |
|---------|-----|
| `vina: command not found` | `conda activate docking` then `python scripts/check_vina.py` |
| Env create fails | `conda update -n base conda` and retry |
| Bad poses | Check receptor; raise exhaustiveness in config |

Scoring: [docs/scoring_function.md](docs/scoring_function.md)  
Citations: [docs/CITATIONS.md](docs/CITATIONS.md)
