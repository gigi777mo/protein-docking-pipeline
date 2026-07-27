# Example: Dock calcitriol (active vitamin D) to the vitamin D receptor (VDR)

This is a classic, well-published system.

| Item | Detail |
|------|--------|
| **Receptor** | Human VDR ligand-binding domain |
| **Structure** | **PDB 1DB1** (1.8 Å) — Rochel et al., *Molecular Cell* 2000 |
| **Ligand** | **Calcitriol** = 1α,25-dihydroxyvitamin D₃ (active hormone) |
| **PDB ligand code** | VDX |

> **Important:** Dietary vitamin D₃ (cholecalciferol) is **not** the high-affinity VDR ligand. The body converts it to **calcitriol**, which binds VDR and regulates transcription.

---

## Why this example

1DB1 already contains calcitriol bound in the pocket. You can:

1. **Redock** calcitriol into the emptied pocket and measure **RMSD** vs the crystal pose (good test of the pipeline).
2. Later dock **analogs** or metabolites and compare scores to calcitriol.

---

## Step-by-step (Miniconda)

### 0. Environment

```bash
cd protein-docking-pipeline
conda activate docking
python scripts/check_vina.py
```

### 1. Download the structure

```bash
mkdir -p data/receptors
wget -O data/receptors/1DB1.pdb https://files.rcsb.org/download/1DB1.pdb
# or: curl -L -o data/receptors/1DB1.pdb https://files.rcsb.org/download/1DB1.pdb
```

### 2. Prepare receptor (remove ligand + water; keep protein)

You need a clean protein for docking. Conceptually:

- Keep chain with the LBD
- Remove ligand **VDX**, waters, and other heteroatoms
- Convert to PDBQT (charges + atom types)

```bash
python scripts/prepare_receptor.py \
  --receptor data/receptors/1DB1.pdb \
  --out data/receptors/1DB1_receptor.pdbqt
```

If the prepare script does not strip ligands automatically, remove HETATM VDX lines in a text editor or PyMOL first, save as `1DB1_clean.pdb`, then prepare that file.

### 3. Prepare calcitriol ligand

SMILES file is already in the repo:

`data/ligands/calcitriol.smi`

```bash
python scripts/prepare_ligand.py \
  --ligand data/ligands/calcitriol.smi \
  --out data/ligands/calcitriol.pdbqt
```

### 4. Set the search box on the binding site

Config template: `data/configs/vdr_calcitriol_config.txt`

**Best practice:** open 1DB1 in PyMOL/ChimeraX, select ligand VDX, get its center coordinates, and put those into `center_x/y/z`. Box size ~20–26 Å per side is typical for this pocket.

Or predict the pocket:

```bash
python scripts/predict_pocket.py --receptor data/receptors/1DB1_clean.pdb --out results/vdr_pockets
```

### 5. Run Vina docking

```bash
python scripts/run_docking.py \
  --receptor data/receptors/1DB1_receptor.pdbqt \
  --ligand data/ligands/calcitriol.pdbqt \
  --config data/configs/vdr_calcitriol_config.txt \
  --out results/vdr_calcitriol
```

Or call Vina directly if your scripts expect that layout:

```bash
vina --config data/configs/vdr_calcitriol_config.txt --out results/vdr_calcitriol/out.pdbqt --log results/vdr_calcitriol/log.txt
```

### 6. Validate (redocking RMSD)

Extract the crystal ligand from 1DB1 (VDX) as a reference PDB/PDBQT, then:

```bash
python scripts/calculate_rmsd.py \
  --ref data/ligands/crystal_VDX.pdb \
  --docked results/vdr_calcitriol/out.pdbqt
```

**Rule of thumb:** top pose **RMSD &lt; 2.0 Å** vs crystal = successful redocking.

---

## What to expect

| Output | Meaning |
|--------|--------|
| Vina score (kcal/mol) | More negative ≈ better predicted affinity (use for **ranking**) |
| Multiple poses | Ranked binding modes |
| Low RMSD on redock | Pipeline + box settings are working |

Scores are **not** exact experimental ΔG values.

---

## Biology checklist

| Form | Binds VDR tightly? |
|------|---------------------|
| Vitamin D₃ (cholecalciferol) | Weak / not the active hormone |
| 25-hydroxyvitamin D₃ (calcidiol) | Intermediate |
| **1,25-dihydroxyvitamin D₃ (calcitriol)** | **Yes — endogenous high-affinity ligand** |

---

## Cite

- Rochel N, et al. *The crystal structure of the nuclear receptor for vitamin D bound to its natural ligand.* Molecular Cell. 2000;5:173–179. (PDB **1DB1**)
- Trott & Olson, *J Comput Chem* 2010; Eberhardt et al., *JCIM* 2021 (AutoDock Vina)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `vina` not found | `conda activate docking` + `python scripts/check_vina.py` |
| Empty poses / very poor scores | Box not on the pocket — recenter on crystal VDX |
| High RMSD | Increase exhaustiveness (32–64); check ligand stereo/SMILES |
| Prepare fails | Install openbabel/rdkit in the `docking` env |
