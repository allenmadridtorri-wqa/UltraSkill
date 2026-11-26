#!/usr/bin/env python3
"""Automated static pre-review scanner for Python, JS/TS, and GDScript files catching P0/P1 anti-patterns."""

import argparse
import ast
import json
import pathlib
import re
import sys
from typing import Any, Dict, List


MAX_FUNC_LINES = 90
SKIP_DIRS = {".git", "node_modules", "dist", "__pycache__", ".venv"}


def scan_python_ast(source: str, rel_path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as exc:
        return [{"severity": "P0", "file": rel_path, "line": exc.lineno or 1, "rule": "SYNTAX_ERROR", "msg": str(exc)}]

    for node in ast.walk(tree):
        # 1. Bare except: or silent except: pass
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                findings.append({
                    "severity": "P1",
                    "file": rel_path,
                    "line": node.lineno,
                    "rule": "BARE_EXCEPT",
                    "msg": "Bare 'except:' catches SystemExit/KeyboardInterrupt; catch specific exceptions.",
                })
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                findings.append({
                    "severity": "P1",
                    "file": rel_path,
                    "line": node.lineno,
                    "rule": "SILENT_EXCEPT_PASS",
                    "msg": "Silent 'except ...: pass' swallows errors without logging or handling.",
                })

        # 2. Mutable default arguments in function definitions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default_node in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
                if isinstance(default_node, (ast.List, ast.Dict, ast.Set)):
                    findings.append({
                        "severity": "P1",
                        "file": rel_path,
                        "line": node.lineno,
                        "rule": "MUTABLE_DEFAULT_ARG",
                        "msg": f"Function '{node.name}' uses mutable default literal (list/dict/set).",
                    })
            end_line = getattr(node, "end_lineno", node.lineno)
            if (end_line - node.lineno) > MAX_FUNC_LINES:
                findings.append({
                    "severity": "P2",
                    "file": rel_path,
                    "line": node.lineno,
                    "rule": "OVERSIZED_FUNCTION",
                    "msg": f"Function '{node.name}' is {end_line - node.lineno} lines (> {MAX_FUNC_LINES}).",
                })

        # 3. Dangerous eval / exec / shell=True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                findings.append({
                    "severity": "P0",
                    "file": rel_path,
                    "line": node.lineno,
                    "rule": "UNSAFE_EVAL_EXEC",
                    "msg": f"Call to '{node.func.id}()' enables arbitrary code execution.",
                })
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    findings.append({
                        "severity": "P0",
                        "file": rel_path,
                        "line": node.lineno,
                        "rule": "SUBPROCESS_SHELL_TRUE",
                        "msg": "subprocess call with shell=True risks OS command injection.",
                    })

    return findings


def scan_text_patterns(source: str, rel_path: str, suffix: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for idx, line in enumerate(source.splitlines(), start=1):
        if suffix in {".js", ".ts", ".tsx"} and "new THREE.Vector3(" in line and "requestAnimationFrame" in source:
            findings.append({
                "severity": "P2",
                "file": rel_path,
                "line": idx,
                "rule": "POTENTIAL_HOTPATH_ALLOC",
                "msg": "Verify 'new THREE.Vector3()' is not allocated inside per-frame render loop.",
            })
        if re.search(r"\b(?:TODO|FIXME|HACK)\s*:", line):
            findings.append({
                "severity": "P1",
                "file": rel_path,
                "line": idx,
                "rule": "UNRESOLVED_PLACEHOLDER",
                "msg": "Unresolved placeholder comment marker.",
            })
    return findings


def scan_path(target: pathlib.Path) -> Dict[str, Any]:
    files = [target] if target.is_file() else sorted(target.rglob("*"))
    base = target.parent if target.is_file() else target
    all_findings: List[Dict[str, Any]] = []
    scanned_count = 0

    for f in files:
        if not f.is_file() or any(p in SKIP_DIRS for p in f.parts):
            continue
        suffix = f.suffix.lower()
        if suffix not in {".py", ".js", ".ts", ".tsx", ".gd"}:
            continue
        scanned_count += 1
        rel = str(f.relative_to(base))
        text = f.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".py":
            all_findings.extend(scan_python_ast(text, rel))
        if f.name != "pre_review_scan.py" and f.name != "validate.py":
            all_findings.extend(scan_text_patterns(text, rel, suffix))

    p0_p1 = [x for x in all_findings if x["severity"] in {"P0", "P1"}]
    return {
        "files_scanned": scanned_count,
        "total_findings": len(all_findings),
        "blocking_p0_p1_count": len(p0_p1),
        "verdict": "CHANGES_REQUESTED" if p0_p1 else "APPROVED",
        "findings": all_findings,
    }


def run_self_test() -> int:
    bad_code = "def bad(x=[]):\n    try:\n        eval(x)\n    except:\n        pass\n"
    hits = scan_python_ast(bad_code, "bad_sample.py")
    rules = {h["rule"] for h in hits}
    expected = {"MUTABLE_DEFAULT_ARG", "UNSAFE_EVAL_EXEC", "BARE_EXCEPT"}
    if not expected.issubset(rules):
        print(f"Self-test failed: expected {expected}, got {rules}", file=sys.stderr)
        return 1
    print(f"Self-test PASSED: AST scanner caught {sorted(rules)}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=pathlib.Path, help="File or directory to scan")
    parser.add_argument("--self-test", action="store_true", help="Run built-in AST pre-review self-test")
    args = parser.parse_args()

    if args.self_test or args.path is None:
        return run_self_test()

    report = scan_path(args.path)
    print(json.dumps(report, indent=2))
    return 0 if report["blocking_p0_p1_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
