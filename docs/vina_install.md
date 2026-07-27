# AutoDock Vina in this pipeline

## Recommended (Miniconda)

```bash
conda env create -f environment.yml
conda activate docking
# provides the `vina` executable via bioconda package autodock-vina
python scripts/check_vina.py
```

## Manual fallback

1. Download from https://github.com/ccsb-scripps/AutoDock-Vina/releases  
2. Place `vina` on your PATH  
3. Run `python scripts/check_vina.py`  

## Python bindings (optional)

The env also installs the `vina` pip package when possible.  
Docking scripts primarily call the **command-line binary**.

## Cite

- Trott O, Olson AJ. *J Comput Chem.* 2010.  
- Eberhardt J, et al. *J Chem Inf Model.* 2021 (Vina 1.2+).  
