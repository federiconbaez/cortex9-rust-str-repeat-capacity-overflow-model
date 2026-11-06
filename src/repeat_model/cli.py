"""CLI: python -m repeat_model run --len L --n N [--width 16|32|64] [--elem 1]
Integers only; nothing is allocated."""
import argparse
import json

from .repeat import VERSIONS, WIDTHS, repeat


def _int(s):
    return int(s, 0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="repeat_model")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--len", type=_int, required=True)
    r.add_argument("--n", type=_int, required=True)
    r.add_argument("--width", type=int, choices=WIDTHS, default=64)
    r.add_argument("--elem", type=int, default=1)
    a = ap.parse_args(argv)
    out = {}
    for v in VERSIONS:
        try:
            t = repeat(v, a.width, a.len, a.n, a.elem)
        except ValueError as e:
            ap.error(str(e))
        out[v] = {"outcome": t.outcome, "where": t.where, "true_len": t.true_len,
                  "computed_len": t.computed_len, "wrapped": t.wrapped,
                  "capacity": t.capacity, "final_len": t.final_len, "oob": t.oob}
    print(json.dumps(out, indent=2))
    return 0
