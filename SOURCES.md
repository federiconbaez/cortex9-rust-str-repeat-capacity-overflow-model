# Sources

All files were fetched once and read offline. The SHA-256 hashes are of
the local copies.

| File | Origin | SHA-256 |
|---|---|---|
| rust-1b94b84ad014.diff | https://github.com/rust-lang/rust/commit/1b94b84ad0143ea2039610e3aec9e929a8a20733.diff ("std: Check for overflow in `str::repeat`") | d574f67ff4cd4bb9899aec0a610ee1ea3f5a340eb3810d5183bbbf8169b2ee65 |
| src/liballoc/slice.rs @ 1.29.0 | https://raw.githubusercontent.com/rust-lang/rust/1.29.0/src/liballoc/slice.rs | 4bbb250df0d7f1b944540f6a5ff3c25d87925717c335221bb3563e29734a5a16 |
| src/liballoc/raw_vec.rs @ 1.29.0 | same tag | d1341913d7f683f9701884997984934a221af26be4ecf626c9db7510797a78d3 |
| src/liballoc/vec.rs @ 1.29.0 | same tag | 1894e044049bc1f53dc1637913a7a69ae05471712f0ed5a67b6d088eb8e828cb |
| Rust blog advisory (2018-09-21) | https://blog.rust-lang.org/2018/09/21/Security-advisory-for-std.html | 9294dac9c38c9f080bf86f22d18d32bd74d20941bced42ee2caf882b51e0307a |
| NVD CVE-2018-1000810 JSON (CPEs 1.26.0–1.29.0) | https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2018-1000810 | cb8fc67c2ab6ae6a1022dbb06b87ef985ebb1c2812948b8b7fadbc5ea82a46ba |

## Source-to-model trace (1.29.0)

| Source | Model (`repeat.py`) |
|---|---|
| slice.rs l.420, `Vec::with_capacity(self.len() * n)` | `want = (len*n) & mask` |
| raw_vec.rs l.94-95, `checked_mul(elem_size)`, `alloc_guard` | `_alloc` |
| raw_vec.rs l.745-751, guard only if `size_of::<usize>() < 8` | `_guard` |
| slice.rs l.423, `buf.extend(self)` → vec.rs l.1949-1956 `reserve` | reserve branch |
| raw_vec.rs l.432-440, `max(cap*2, required)` | `new_cap` |
| slice.rs l.427-440, doubling `copy_nonoverlapping` | doubling loop / OOB check |
| slice.rs l.446-458, `rem_len` copy and `set_len(cap)` | rem branch |
| 1.29.1 diff, `checked_mul(n).expect("capacity overflow")` | the 1.29.1 `PANIC` |
