# Install with Python + pip (from GitHub)

```bash
git clone https://github.com/gigi777mo/protein-docking-pipeline.git
cd protein-docking-pipeline

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -U pip
pip install -r requirements.txt
# or: pip install -e .
```

**Also install system tools (not on PyPI):**
- AutoDock Vina — https://github.com/ccsb-scripps/AutoDock-Vina/releases (must be on PATH)
- Optional: Open Babel, P2Rank, DiffDock

Then run scripts under `scripts/` (e.g. `python scripts/run_docking.py ...`).
