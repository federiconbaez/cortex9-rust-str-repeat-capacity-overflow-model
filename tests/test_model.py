import json
import pathlib
import unittest

from repeat_model.repeat import VERSIONS, repeat
from repeat_model.sweep import sweep

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _n(x):
    return int(x, 0) if isinstance(x, str) else x


class Fixtures(unittest.TestCase):
    def test_cases(self):
        for c in json.loads((ROOT / "fixtures/cases.json").read_text())["cases"]:
            for v, exp in c["expect"].items():
                t = repeat(v, c["width"], c["len"], _n(c["n"]), c["elem"])
                with self.subTest(id=c["id"], v=v):
                    self.assertEqual(t.outcome, exp["outcome"])
                    if "final_len" in exp:
                        self.assertEqual(t.final_len, exp["final_len"])
                    for k in ("write_offset", "write_count", "elements_past_capacity"):
                        if k in exp:
                            self.assertEqual(t.oob[k], exp[k])


class Properties(unittest.TestCase):
    def test_post_never_writes_oob(self):
        s = sweep()
        for (v, w), r in s.items():
            if v == "1.29.1":
                self.assertEqual(r["oob_write"] + r["wrong_length"], 0, w)
            self.assertEqual(r["oob_without_wrap"], 0)
            self.assertEqual(r["wrap_without_oob_or_stop"], 0)
        self.assertGreater(s[("1.29.0", 16)]["oob_write"], 0)

    def test_oob_iff_wrapped_and_allocatable_16(self):
        # Independent arithmetic: in 1.29.0 a 16-bit usize writes OOB exactly when
        # len*n wraps and the wrapped value (and any reserve) passes alloc_guard.
        for length in (1, 2, 3, 5):
            for n in range(2, 1 << 16, 97):
                t = repeat("1.29.0", 16, length, n)
                wrapped = (length * n) & 0xFFFF
                cap = wrapped if wrapped >= length else max(2 * wrapped, length)
                expect = length * n > 0xFFFF and wrapped <= 0x7FFF and cap <= 0x7FFF
                self.assertEqual(t.outcome == "OOB_WRITE", expect, (length, n))

    def test_no_large_allocation(self):
        t = repeat("1.29.0", 64, 2, 0x8000000000000001)
        self.assertEqual(t.capacity, 2)
        self.assertTrue(all(isinstance(s[1], int) for s in t.steps))

    def test_versions(self):
        self.assertEqual(VERSIONS, ("1.29.0", "1.29.1"))


if __name__ == "__main__":
    unittest.main()
