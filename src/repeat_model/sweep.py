"""Sweeps: exhaustive for a 16-bit usize on small lengths; boundary sets for 32/64 bits."""
from .repeat import VERSIONS, repeat

EXHAUSTIVE_LENS = range(1, 17)


def boundary_ns(width, length):
    top = 1 << width
    base = {0, 1, 2, 3, top - 1, top >> 1, (top >> 1) + 1}
    q = top // length
    for d in range(-3, 4):
        base.add(q + d)
        base.add(2 * q + d)
    return sorted(x for x in base if 0 <= x < top)


def cases():
    for length in EXHAUSTIVE_LENS:
        for n in range(1 << 16):
            yield 16, length, n
    for width in (32, 64):
        for length in list(range(1, 17)) + [255, 4097, 65535]:
            for n in boundary_ns(width, length):
                yield width, length, n


def sweep():
    rows = {}
    for width, length, n in cases():
        for v in VERSIONS:
            t = repeat(v, width, length, n)
            k = (v, width)
            r = rows.setdefault(k, {"cases": 0, "wrapped": 0, "ok": 0, "panic": 0,
                                    "alloc_failure": 0, "oob_write": 0, "wrong_length": 0,
                                    "oob_without_wrap": 0, "wrap_without_oob_or_stop": 0})
            r["cases"] += 1
            r["wrapped"] += t.wrapped
            key = {"OK": "ok", "PANIC": "panic", "ALLOC_FAILURE": "alloc_failure",
                   "OOB_WRITE": "oob_write", "WRONG_LENGTH": "wrong_length"}[t.outcome]
            r[key] += 1
            r["oob_without_wrap"] += t.outcome == "OOB_WRITE" and not t.wrapped
            r["wrap_without_oob_or_stop"] += t.wrapped and t.outcome in ("OK", "WRONG_LENGTH")
    return rows
