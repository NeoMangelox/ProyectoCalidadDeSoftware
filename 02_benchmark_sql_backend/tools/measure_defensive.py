#!/usr/bin/env python3
"""Medicion preliminar: SLOC_def (lineas entre marcadores DEFENSIVE-BEGIN/END) y CC (radon).
Uso: python tools/measure_defensive.py   (requiere: pip install radon)"""
import re
from pathlib import Path
from radon.complexity import cc_visit
from radon.raw import analyze

ROOT = Path(__file__).resolve().parent.parent


def measure(backend):
    sloc = sloc_def = cc = 0
    for f in sorted((ROOT / backend / "app").rglob("*.py")):
        src = f.read_text()
        sloc += analyze(src).sloc
        cc += sum(b.complexity for b in cc_visit(src))
        inside = False
        for line in src.splitlines():
            if "DEFENSIVE-BEGIN" in line: inside = True; continue
            if "DEFENSIVE-END" in line: inside = False; continue
            if inside and line.strip() and not line.strip().startswith("#"): sloc_def += 1
    return sloc, sloc_def, cc


if __name__ == "__main__":
    d, n = measure("backend_defensive"), measure("backend_normalized")
    print(f"{'backend':<20}{'SLOC':>6}{'SLOC_def':>10}{'CC total':>10}")
    for name, m in (("defensive", d), ("normalized", n)):
        print(f"{name:<20}{m[0]:>6}{m[1]:>10}{m[2]:>10}")
    print(f"\nDelta CC (%) = {(d[2]-n[2])/d[2]*100:.1f}   | SLOC_def/SLOC defensive = {d[1]/d[0]*100:.1f}%")
