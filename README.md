# cortex9-rust-str-repeat-capacity-overflow-model

An offline model of the integer overflow in `<[T]>::repeat`, the function
behind `str::repeat`, in Rust 1.26.0–1.29.0 (CVE-2018-1000810). The fix
is 1.29.1, commit 1b94b84ad014, which changes
`Vec::with_capacity(self.len() * n)` to
`self.len().checked_mul(n).expect("capacity overflow")`.

**Nothing is allocated.** Capacity, length and every
`copy_nonoverlapping` write are plain integers. Machine arithmetic is
reproduced for a 16-, 32- or 64-bit `usize`, assuming a release-built std
where overflow wraps. The model follows the real 1.29.0 code path:

1. `with_capacity` → `RawVec::allocate_in`, which runs
   `checked_mul(elem_size)` and then `alloc_guard`.
2. `buf.extend(self)` → `spec_extend` → `reserve`, with amortized
   `max(2·cap, needed)` growth.
3. The doubling loop.
4. The `rem_len` copy.

When a write would pass the capacity, the model records it as
`OOB_WRITE` and stops. It does not simulate the undefined behaviour that
would follow.

## Results (`results/sweep_summary.csv`)

The 16-bit sweep is exhaustive: `len` 1–16 × all `n` < 2¹⁶. The 32- and
64-bit sweeps use boundary sets around `2^W / len`.

| version | width | cases | wrapped | OOB_WRITE | PANIC | ALLOC_FAILURE* |
|---|---|---|---|---|---|---|
| 1.29.0 | 16 | 1,048,576 | 827,010 | 413,504 | 524,288 | 0 |
| 1.29.0 | 32 | 378 | 229 | 120 | 182 | 0 |
| 1.29.0 | 64 | 378 | 229 | 120 | 0 | 182 |
| 1.29.1 | 16 | 1,048,576 | 827,010 | **0** | 937,792 | 0 |
| 1.29.1 | 32 | 378 | 229 | **0** | 302 | 0 |
| 1.29.1 | 64 | 378 | 229 | **0** | 229 | 73 |

\* `ALLOC_FAILURE` is an assumption: on 64-bit, `alloc_guard` does
nothing, and the model assumes the allocator refuses any size above
`isize::MAX`.

What the sweep shows:

- In 1.29.0, an out-of-bounds write happens only when `len*n` wraps.
- If it wraps and the wrapped value is still allocatable, the doubling
  loop always writes out of bounds. A test checks this by arithmetic.
- With 64-bit wrapping, the advisory's own doc test
  (`b"0123456789abcdef".repeat(usize::MAX)`) gives `2^64-16`, which is
  above `isize::MAX`. So in this model that particular call fails
  allocation and does not write out of bounds. Inputs such as
  `len=2, n=2^63+1` (wrapping to a capacity of 2) do write out of bounds.

## Usage

```sh
PYTHONPATH=src python3 -m repeat_model run --len 2 --n 0x8000000000000001
PYTHONPATH=src python3 -m repeat_model run --len 3 --n 0x55555556 --width 32
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

See [SOURCES.md](SOURCES.md), [LIMITATIONS.md](LIMITATIONS.md),
[PRACTICE.md](PRACTICE.md) (Spanish) and [README.es.md](README.es.md).

License: Apache-2.0.
