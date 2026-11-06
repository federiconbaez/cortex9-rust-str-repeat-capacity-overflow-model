"""Regenerate results/ (deterministic). Usage: gen_results.py [outdir]"""
import csv
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from repeat_model.repeat import VERSIONS, repeat  # noqa: E402
from repeat_model.sweep import sweep  # noqa: E402

out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results"
out.mkdir(parents=True, exist_ok=True)
with open(out / "cases.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "version", "width", "len", "n", "elem", "computed_len", "wrapped",
                "outcome", "where", "capacity", "final_len", "oob_write_offset", "oob_write_count",
                "oob_elements_past_capacity"])
    for c in json.loads((ROOT / "fixtures/cases.json").read_text())["cases"]:
        n = int(c["n"], 0) if isinstance(c["n"], str) else c["n"]
        for v in VERSIONS:
            t = repeat(v, c["width"], c["len"], n, c["elem"])
            w.writerow([c["id"], v, c["width"], c["len"], hex(n), c["elem"], t.computed_len,
                        t.wrapped, t.outcome, t.where, t.capacity, t.final_len,
                        t.oob.get("write_offset", ""), t.oob.get("write_count", ""),
                        t.oob.get("elements_past_capacity", "")])
KEYS = ["cases", "wrapped", "ok", "panic", "alloc_failure", "oob_write", "wrong_length",
        "oob_without_wrap", "wrap_without_oob_or_stop"]
with open(out / "sweep_summary.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["version", "width"] + KEYS)
    for (v, width), r in sorted(sweep().items()):
        w.writerow([v, width] + [r[k] for k in KEYS])
FILES = ("cases.csv", "sweep_summary.csv")
(out / "SHA256SUMS").write_text("".join(
    f"{hashlib.sha256((out / n).read_bytes()).hexdigest()}  {n}\n" for n in FILES))
