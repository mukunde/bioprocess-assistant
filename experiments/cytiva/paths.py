"""Repository-relative locations; no private absolute paths in experiment code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/experiments/cytiva"
V01 = DATA / "pages-097-099-v01"
V02 = DATA / "pages-100-102-v02"
REFERENCE = DATA / "reference-v01"


def candidate_path(name):
    return V01 / ("resultat-sonnet-original.json" if name == "sonnet" else "resultat-sol.json")
