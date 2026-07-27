# Scoring Function Details

This document explains the **scoring functions** used in the protein-ligand docking pipeline.

---

## AutoDock Vina Scoring Function (Default)

AutoDock Vina uses an **empirical scoring function** designed for speed and reasonable accuracy in pose prediction and ranking.

### Overall Form

The binding affinity (in kcal/mol) is calculated as:

```
ΔG = ΔG_gauss1 + ΔG_gauss2 + ΔG_repulsion + ΔG_hydrophobic + ΔG_hydrogen + ΔG_rot
```

Where each term is weighted by empirically derived coefficients.

### Individual Terms

| Term | Description | Physical meaning |
|------|-------------|------------------|
| **gauss1** | Attractive Gaussian | Favorable steric contacts at short distance (~0–2 Å beyond van der Waals) |
| **gauss2** | Attractive Gaussian | Broader attractive term for medium-range contacts |
| **repulsion** | Steric repulsion | Penalizes atomic clashes (overlapping atoms) |
| **hydrophobic** | Hydrophobic interaction | Rewards contacts between hydrophobic atoms |
| **hydrogen** | Hydrogen bonding | Directional H-bond term between donor and acceptor |
| **rot** | Torsional entropy | Penalty proportional to the number of rotatable bonds in the ligand |

### Key Characteristics

- **Units**: kcal/mol (more negative = stronger predicted binding)
- **Not a true free energy**: It is an empirical approximation trained on experimental structures and affinities.
- **Rigid receptor assumption**: The standard Vina score treats the protein as rigid (unless flexible residues are explicitly defined).
- **No explicit solvation or electrostatics**: Polar interactions are captured mainly through the hydrogen-bond term and implicit effects in the training data.
- **Speed-optimized**: Designed for high-throughput virtual screening.

### Interpretation of Scores

| Score range (kcal/mol) | Typical interpretation |
|------------------------|------------------------|
| < −10 | Very strong binder (often leads or tight inhibitors) |
| −8 to −10 | Strong / promising |
| −6 to −8 | Moderate |
| > −6 | Weak or non-binder (context-dependent) |

**Important**: Absolute scores are less reliable than **relative ranking** within a chemical series or against a known reference ligand. Always validate with redocking (RMSD) and experimental data when possible.

### Vina 1.2 Improvements

Starting with Vina 1.2.0 (Eberhardt et al., 2021):

- Expanded atom typing and force-field terms
- Better support for macrocycles and multi-ligand docking
- Improved handling of hydrated docking protocols
- Python bindings for programmatic access to the scoring function

---

## Alternative / Related Scoring Functions

### 1. AutoDock4 Scoring Function
Older, more physics-based (includes explicit electrostatics and desolvation). Generally slower and less accurate for pose prediction than Vina, but still used in some specialized protocols.

### 2. Vinardo
A re-parameterized version of Vina’s scoring function with improved weighting. Available in some forks (e.g., Smina).

### 3. Smina / QVina
Smina allows custom scoring function weights. QuickVina (QVina2/QVina-W) keeps the same scoring function as Vina but accelerates the search.

### 4. GNINA
Combines Vina’s search with a **CNN (convolutional neural network)** scoring function trained on protein-ligand complexes. Often improves ranking accuracy over classical Vina scores.

### 5. DiffDock Confidence Model
DiffDock does **not** use a classical energy-based score. Instead it outputs a **confidence score** from a neural network that estimates the likelihood that a generated pose is correct. Higher confidence ≈ more reliable pose.

---

## Practical Recommendations in This Pipeline

1. **Use Vina scores primarily for ranking** within a single virtual screen, not as absolute binding free energies.
2. **Always redock a known ligand** and check RMSD (< 2.0 Å is the usual success criterion).
3. For higher accuracy ranking of top hits, consider re-scoring with GNINA or a free-energy method (MM-GBSA, FEP) if available.
4. When comparing different series or targets, be cautious — the scoring function is not perfectly transferrable.
5. Inspect the top poses visually (PyMOL, ChimeraX) and with interaction analysis tools (PLIP, LigPlot+, etc.).

---

## References

- Trott O, Olson AJ. *AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading.* J Comput Chem. 2010.
- Eberhardt J, Santos-Martins D, Tillack AF, Forli S. *AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings.* J Chem Inf Model. 2021.
- Quiroga R, Villarreal MA. *Vinardo: A Scoring Function Based on Autodock Vina Improves Scoring, Docking, and Virtual Screening.* PLoS One. 2016.
