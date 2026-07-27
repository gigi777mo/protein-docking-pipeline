# Citations — Protein Docking Pipeline

Please cite the tools and methods you use. Core references for this pipeline:

## Docking engines

- **AutoDock Vina**  
  Trott O, Olson AJ.  
  *AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading.*  
  Journal of Computational Chemistry. 2010;31(2):455–461.  
  https://doi.org/10.1002/jcc.21334

- **AutoDock Vina 1.2+**  
  Eberhardt J, Santos-Martins D, Tillack AF, Forli S.  
  *AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings.*  
  Journal of Chemical Information and Modeling. 2021;61(8):3891–3898.  
  https://doi.org/10.1021/acs.jcim.1c00203

- **DiffDock** (optional deep-learning path)  
  Corso G, Stärk H, Jing B, Barzilay R, Jaakkola T.  
  *DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking.*  
  ICLR 2023.  
  https://arxiv.org/abs/2210.01776

## Pocket / binding-site prediction

- **P2Rank**  
  Krivák R, Hoksza D.  
  *P2Rank: machine learning based tool for rapid and accurate prediction of ligand-binding sites from protein structure.*  
  Journal of Cheminformatics. 2018;10:39.  
  https://doi.org/10.1186/s13321-018-0285-8

## Preparation & cheminformatics

- **RDKit**  
  RDKit: Open-source cheminformatics. https://www.rdkit.org

- **Open Babel**  
  O'Boyle NM, et al. *Open Babel: An open chemical toolbox.* Journal of Cheminformatics. 2011.

- **Biopython**  
  Cock PJ, et al. *Biopython: freely available Python tools for computational molecular biology and bioinformatics.* Bioinformatics. 2009.

## Scoring function background

- Vina empirical scoring (gauss, repulsion, hydrophobic, H-bond, torsional terms) is described in Trott & Olson (2010) and refined in Eberhardt et al. (2021).  
  See also **[docs/scoring_function.md](scoring_function.md)** in this repository.

## Classic validation example

- Trypsin–benzamidine is a widely used redocking test case (e.g. PDB 3PTB and related structures).

## Suggested acknowledgment

> Molecular docking was performed with AutoDock Vina (Trott & Olson, 2010; Eberhardt et al., 2021). Binding sites were optionally predicted with P2Rank (Krivák & Hoksza, 2018). Ligand and receptor preparation used RDKit and Open Babel.
