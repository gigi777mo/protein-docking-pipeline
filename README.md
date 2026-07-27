# Protein-Ligand Docking Pipeline

---

> ## 🔴 USE MINICONDA
>
> **Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) first.**  
> `conda env create -f environment.yml` → `conda activate docking`  
> **AutoDock Vina is included** in `environment.yml` (`autodock-vina`).

---

**New user?** Open **[START_HERE.md](START_HERE.md)**.

Small-molecule docking with **AutoDock Vina** (+ optional P2Rank / DiffDock).

```bash
conda env create -f environment.yml
conda activate docking
python scripts/check_vina.py
python scripts/run_docking.py --receptor protein.pdb --ligand ligand.smi --config data/configs/example_config.txt --out results/run1
```

| Check | Command |
|-------|--------|
| Is Vina installed? | `python scripts/check_vina.py` or `vina --help` |

Citations: [docs/CITATIONS.md](docs/CITATIONS.md)  
Scoring: [docs/scoring_function.md](docs/scoring_function.md)

## License

MIT
