# Limitations

- **Abstract execution.** The model allocates and copies nothing; lengths
  and offsets are integers. Real out-of-bounds writes corrupt the heap,
  and what follows is undefined behaviour. The model stops at the first
  out-of-bounds write.
- **Release std assumed.** A std built with debug assertions and overflow
  checks would panic on the multiplication instead.
- **Allocator.** On 64-bit, `alloc_guard` is a no-op. The model assumes
  any request above `isize::MAX` fails (`ALLOC_FAILURE`). The model does
  not represent real memory limits (RAM, overcommit) for large but valid
  sizes.
- **Coverage.** The 16-bit sweep is exhaustive for `len` ≤ 16. The 32- and
  64-bit sweeps use boundary sets only, not an exhaustive search.
- **Scope.** The model covers `<[T]>::repeat` with a `Copy` element type.
  `str::repeat` calls it on bytes (`elem=1`). Other `Vec` paths are out of
  scope.
- **CI.** The workflow runs the tests on Python 3.10–3.13, regenerates
  `results/` and compares it byte by byte. See the Actions page for run
  status.
