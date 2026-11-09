#!/usr/bin/env python3
"""
measure_quality.py — Herramienta de Análisis Estático de Calidad Backend
Proyecto: "Auditoría y Optimización de Esquemas PostgreSQL mediante LLMs"
Asignatura: Calidad de Software (Ciclo 6) — Rol: Miembro 5 (Métricas)

Calcula de forma determinista mediante el AST nativo de Python:
- Complejidad Ciclomática de McCabe (CC) según v(G) = 1 + sum(pi)
- Líneas de Código Físicas (LOC) y Lógicas (LLOC / SLOC)
- Líneas de Código Defensivo (SLOC_def)
- Consultas Previas de Verificación Relacional (Q_prev)
- Comparativa Delta (Δ) entre backend defensivo y backend normalizado.
"""

import ast
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def get_radon_rank(cc: int) -> str:
    """Retorna la clasificación cualitativa de riesgo estandarizada por Radon."""
    if cc <= 5:
        return "A (Bajo Riesgo)"
    elif cc <= 10:
        return "B (Riesgo Bajo-Medio)"
    elif cc <= 20:
        return "C (Riesgo Moderado)"
    elif cc <= 30:
        return "D (Riesgo Alto)"
    elif cc <= 40:
        return "E (Riesgo Muy Alto)"
    else:
        return "F (Crítico / Inmantenible)"


class McCabeASTVisitor(ast.NodeVisitor):
    """
    Calcula la Complejidad Ciclomática de McCabe recorriendo el AST.
    Alineado formalmente con el algoritmo canónico de Radon.
    """

    def __init__(self):
        self.complexity = 1  # Base complexity para un procedimiento conexo (P=1)
        self.decision_points = []

    def visit_If(self, node: ast.If):
        self.complexity += 1
        self.decision_points.append(("If", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp):
        self.complexity += 1
        self.decision_points.append(("IfExp (ternario)", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.complexity += 1
        self.decision_points.append(("For", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self.complexity += 1
        self.decision_points.append(("AsyncFor", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.complexity += 1
        self.decision_points.append(("While", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.complexity += 1
        self.decision_points.append(("ExceptHandler", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        self.complexity += 1
        self.decision_points.append(("Assert", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension):
        self.complexity += 1
        self.decision_points.append(("comprehension", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        # Cada operador lógico adicional en cortocircuito (and, or) bifurca el flujo
        branches = len(node.values) - 1
        self.complexity += branches
        self.decision_points.append((f"BoolOp (+{branches})", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_Match(self, node):
        # Soporte para pattern matching (Python 3.10+)
        if hasattr(node, "cases"):
            branches = max(0, len(node.cases) - 1)
            self.complexity += branches
            self.decision_points.append((f"MatchCases (+{branches})", getattr(node, "lineno", 0)))
        self.generic_visit(node)


class FunctionMetricsExtractor(ast.NodeVisitor):
    """Extrae métricas individuales por función / endpoint."""

    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.lines = source_code.splitlines()
        self.functions_metrics: List[Dict[str, Any]] = []

    def _is_defensive_line(self, line_text: str) -> bool:
        """Heurística para identificar código defensivo compensatorio."""
        # Comentarios explícitos del desarrollador
        if re.search(r"#\s*(defensive|código defensivo|validación defensiva|compensación|1fn|2fn|3fn|fk_check)", line_text, re.IGNORECASE):
            return True
        # Heurísticas de consultas de existencia previa
        if re.search(r"(SELECT\s+COUNT|SELECT\s+EXISTS|SELECT\s+1\s+FROM)", line_text, re.IGNORECASE):
            return True
        # Parsing manual de strings para 1FN
        if re.search(r"(\.split\s*\(\s*['\"][,\s|;]+['\"]\s*\)|re\.findall|re\.split)", line_text):
            return True
        # Verificaciones defensivas de existencia previa
        if re.search(r"if\s+not\s+\w+_(exists|count|parent|valido)", line_text, re.IGNORECASE):
            return True
        return False

    def _is_prior_query(self, line_text: str, inside_defensive: bool = False) -> bool:
        """Detecta si la línea ejecuta una consulta previa de verificación relacional."""
        if re.search(r"(SELECT\s+COUNT|SELECT\s+EXISTS|SELECT\s+1\s+FROM)", line_text, re.IGNORECASE):
            return True
        if inside_defensive and re.search(r"SELECT\s+.*\s+FROM\s+", line_text, re.IGNORECASE):
            return True
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._analyze_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._analyze_function(node, is_async=True)

    def _analyze_function(self, node, is_async: bool):
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        func_lines = self.lines[start_line - 1 : end_line]
        loc = len(func_lines)

        # Logical SLOC: sentencias ejecutables sin contar comentarios ni líneas vacías
        sloc = 0
        sloc_def = 0
        q_prev = 0
        inside_defensive = False
        has_markers = any("DEFENSIVE-BEGIN" in l for l in func_lines)

        for line in func_lines:
            if "DEFENSIVE-BEGIN" in line:
                inside_defensive = True
                continue
            if "DEFENSIVE-END" in line:
                inside_defensive = False
                continue

            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            sloc += 1
            if has_markers:
                if inside_defensive:
                    sloc_def += 1
            elif self._is_defensive_line(line):
                sloc_def += 1

            if self._is_prior_query(line, inside_defensive):
                q_prev += 1

        # Calcular McCabe CC sobre el cuerpo de la función
        visitor = McCabeASTVisitor()
        # Visitamos únicamente los hijos directos para evitar reiniciar en 1 por sub-visita
        for child in node.body:
            visitor.visit(child)

        cc = visitor.complexity
        rank = get_radon_rank(cc)

        self.functions_metrics.append({
            "file": self.file_path,
            "function": node.name,
            "is_async": is_async,
            "start_line": start_line,
            "end_line": end_line,
            "loc": loc,
            "sloc": sloc,
            "sloc_def": sloc_def,
            "q_prev": q_prev,
            "cc": cc,
            "rank": rank,
            "decision_points": visitor.decision_points,
        })


def analyze_file(file_path: Path) -> List[Dict[str, Any]]:
    """Analiza un único archivo Python y retorna las métricas de sus funciones."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        extractor = FunctionMetricsExtractor(content, file_path.name)
        extractor.visit(tree)
        return extractor.functions_metrics
    except Exception as e:
        print(f"[ERROR] No se pudo analizar {file_path}: {e}", file=sys.stderr)
        return []


def analyze_directory(dir_path: Path) -> List[Dict[str, Any]]:
    """Analiza recursivamente todos los archivos .py en un directorio."""
    all_metrics = []
    for py_file in dir_path.rglob("*.py"):
        if "__pycache__" in str(py_file) or "venv" in str(py_file):
            continue
        all_metrics.extend(analyze_file(py_file))
    return all_metrics


def compare_metrics(
    defensive_metrics: List[Dict[str, Any]],
    normalized_metrics: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Compara métricas entre funciones defensivas y normalizadas."""
    norm_map = {m["function"]: m for m in normalized_metrics}
    comparisons = []

    for def_m in defensive_metrics:
        func_name = def_m["function"]
        
        # Si la función es defensiva, buscar su contraparte normalizada
        if func_name.endswith("_defensivo"):
            clean_name = func_name[:-10]
            norm_m = norm_map.get(clean_name + "_normalizado") or norm_map.get(clean_name)
        elif func_name.endswith("_defensive"):
            clean_name = func_name[:-10]
            norm_m = norm_map.get(clean_name + "_normalized") or norm_map.get(clean_name)
        elif "_defensivo" not in func_name and "_defensive" not in func_name:
            # Caso donde los directorios son diferentes pero las funciones se llaman igual
            clean_name = func_name
            norm_m = norm_map.get(clean_name)
        else:
            continue

        if not norm_m or norm_m == def_m:
            continue

        cc_def = def_m["cc"]
        cc_norm = norm_m["cc"]
        delta_cc = ((cc_def - cc_norm) / cc_def * 100.0) if cc_def > 0 else 0.0

        sloc_def_lines = def_m["sloc_def"]
        norm_def_lines = norm_m["sloc_def"]
        delta_sloc_def = ((sloc_def_lines - norm_def_lines) / sloc_def_lines * 100.0) if sloc_def_lines > 0 else 0.0

        q_def = def_m["q_prev"]
        q_norm = norm_m["q_prev"]
        delta_q = ((q_def - q_norm) / q_def * 100.0) if q_def > 0 else 0.0

        comparisons.append({
            "function": clean_name,
            "cc_def": cc_def,
            "cc_norm": cc_norm,
            "delta_cc_pct": round(delta_cc, 1),
            "rank_def": def_m["rank"],
            "rank_norm": norm_m["rank"],
            "sloc_def_lines": sloc_def_lines,
            "norm_def_lines": norm_def_lines,
            "delta_sloc_def_pct": round(delta_sloc_def, 1),
            "q_prev_def": q_def,
            "q_prev_norm": q_norm,
            "delta_q_pct": round(delta_q, 1),
        })

    return comparisons


def print_single_summary(metrics: List[Dict[str, Any]], title: str):
    """Muestra un resumen estilizado de métricas en consola."""
    print("\n" + "=" * 80)
    print(f"📊 INFORME DE ANÁLISIS ESTÁTICO DE CALIDAD: {title}")
    print("=" * 80)
    print(f"{'Función / Endpoint':<30} | {'SLOC':<6} | {'SLOC_def':<9} | {'Q_prev':<7} | {'CC':<4} | {'Rango Radon'}")
    print("-" * 80)
    for m in metrics:
        print(f"{m['function']:<30} | {m['sloc']:<6} | {m['sloc_def']:<9} | {m['q_prev']:<7} | {m['cc']:<4} | {m['rank']}")
    print("=" * 80)


def print_comparison_table(comparisons: List[Dict[str, Any]]):
    """Muestra la tabla comparativa de ganancia de calidad (Delta)."""
    print("\n" + "#" * 90)
    print("🏆 TABLA COMPARATIVA DE DIFERENCIAL DE CALIDAD (Δ) — ISO/IEC 25010")
    print("#" * 90)
    header = f"{'Endpoint / Función':<25} | {'CC (Def->Norm)':<16} | {'Δ CC (%)':<10} | {'SLOC_def':<10} | {'Δ SLOC_def':<12} | {'Δ Q_prev':<10}"
    print(header)
    print("-" * 90)
    for c in comparisons:
        cc_str = f"{c['cc_def']} -> {c['cc_norm']}"
        sloc_str = f"{c['sloc_def_lines']} -> {c['norm_def_lines']}"
        q_str = f"{c['q_prev_def']} -> {c['q_prev_norm']}"
        row = f"{c['function']:<25} | {cc_str:<16} | {c['delta_cc_pct']:>8}% | {sloc_str:<10} | {c['delta_sloc_def_pct']:>10}% | {c['delta_q_pct']:>8}%"
        print(row)
    print("#" * 90)


def export_markdown_table(comparisons: List[Dict[str, Any]], out_path: Path):
    """Genera una tabla en formato Markdown para incrustar en el Paper o en Obsidian."""
    md_lines = [
        "| Endpoint / Función | $CC$ Defectuoso | $CC$ Normalizado | $\\Delta CC$ (%) | $SLOC_{def}$ Inicial | $SLOC_{def}$ Final | $\\Delta SLOC_{def}$ (%) | Impacto ISO/IEC 25010 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for c in comparisons:
        impact = "Alta Analizabilidad (+)" if c["delta_cc_pct"] > 50 else "Modificabilidad (+)"
        if c["delta_sloc_def_pct"] == 100:
            impact += " / Cero Deuda Técnica"
        row = f"| `{c['function']}` | {c['cc_def']} ({c['rank_def'][:1]}) | {c['cc_norm']} ({c['rank_norm'][:1]}) | **-{c['delta_cc_pct']}%** | {c['sloc_def_lines']} | {c['norm_def_lines']} | **-{c['delta_sloc_def_pct']}%** | {impact} |"
        md_lines.append(row)

    out_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\n[OK] Tabla Markdown para el Paper exportada a: {out_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auditor de Calidad y Complejidad Ciclomática Backend")
    parser.add_argument("target", nargs="?", default=".", help="Archivo o directorio a analizar")
    parser.add_argument("--compare", help="Segundo archivo o directorio (normalizado) para calcular Δ")
    parser.add_argument("--json", help="Ruta para exportar métricas en formato JSON")
    parser.add_argument("--csv", help="Ruta para exportar métricas en formato CSV")
    parser.add_argument("--md", help="Ruta para exportar tabla comparativa en formato Markdown")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: La ruta {target_path} no existe.", file=sys.stderr)
        sys.exit(1)

    if target_path.is_file():
        metrics = analyze_file(target_path)
    else:
        metrics = analyze_directory(target_path)

    if not args.compare:
        print_single_summary(metrics, str(target_path))
        if args.json:
            Path(args.json).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
            print(f"[OK] JSON exportado a {args.json}")
        if args.csv:
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["file", "function", "sloc", "sloc_def", "q_prev", "cc", "rank"])
                writer.writeheader()
                for m in metrics:
                    writer.writerow({k: m[k] for k in ["file", "function", "sloc", "sloc_def", "q_prev", "cc", "rank"]})
            print(f"[OK] CSV exportado a {args.csv}")
    else:
        compare_path = Path(args.compare)
        if not compare_path.exists():
            print(f"Error: La ruta de comparación {compare_path} no existe.", file=sys.stderr)
            sys.exit(1)

        norm_metrics = analyze_file(compare_path) if compare_path.is_file() else analyze_directory(compare_path)
        comparisons = compare_metrics(metrics, norm_metrics)
        print_comparison_table(comparisons)

        if args.md:
            export_markdown_table(comparisons, Path(args.md))
        if args.json:
            Path(args.json).write_text(json.dumps(comparisons, indent=2), encoding="utf-8")
            print(f"[OK] JSON comparativo exportado a {args.json}")


if __name__ == "__main__":
    main()

