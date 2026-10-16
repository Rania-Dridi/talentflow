"""Builds the static, backend-free demo into dist-demo/ (deployable on GitHub Pages)."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist-demo"

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(ROOT / "demo", OUT, ignore=shutil.ignore_patterns("*.test.js"))
shutil.copy(ROOT / "app" / "static" / "css" / "app.css", OUT / "app.css")
print(f"Demo built in {OUT}")
