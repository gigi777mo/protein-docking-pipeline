# Protein-Ligand Docking Pipeline

---

> ## 🔴 USE MINICONDA
>
> **Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) first.**  
> `conda env create -f environment.yml` → `conda activate docking`  
> Also install **AutoDock Vina** on your PATH.

---

**New user?** Open **[START_HERE.md](START_HERE.md)**.

Small-molecule docking to proteins (AutoDock Vina + optional P2Rank / DiffDock).

```bash
conda env create -f environment.yml
conda activate docking
# vina must be on PATH
python scripts/run_docking.py --receptor protein.pdb --ligand ligand.smi --config data/configs/example_config.txt --out results/run1
```

Citations: [docs/CITATIONS.md](docs/CITATIONS.md)  
Pip notes: [INSTALL_PIP.md](INSTALL_PIP.md)

## License

MIT
