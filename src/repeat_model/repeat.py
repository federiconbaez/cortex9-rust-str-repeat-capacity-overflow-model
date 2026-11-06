"""Abstract execution of `<[T]>::repeat` (used by `str::repeat`) in Rust 1.29.0 and 1.29.1.

Nothing is allocated: capacity, length and writes are integers. Machine
arithmetic is reproduced for a chosen usize width (16, 32 or 64 bits),
assuming a release-built std (overflow wraps; no debug overflow checks).

Sources (rust-lang/rust tag 1.29.0, src/liballoc):
  slice.rs  l.420  Vec::with_capacity(self.len() * n)        (1.29.1: checked_mul(n).expect)
            l.423  buf.extend(self)
            l.427  while m > 0 { copy_nonoverlapping(buf, buf+len, len); set_len(len*2) } (l.437)
            l.446  rem_len = self.len() * n - buf.len()
            l.458  buf.set_len(buf.capacity())
  raw_vec.rs l.94-95  allocate_in: cap.checked_mul(elem_size); alloc_guard
             l.432-440 amortized_new_size = max(cap*2, used+needed)
             l.745-751 alloc_guard: only when size_of::<usize>() < 8, size > isize::MAX
  vec.rs   l.1949-1956 spec_extend for slice::Iter<Copy>: reserve(len) then copy
"""
from dataclasses import dataclass, field

VERSIONS = ("1.29.0", "1.29.1")
WIDTHS = (16, 32, 64)


@dataclass
class Trace:
    outcome: str = ""              # OK | PANIC | OOB_WRITE | ALLOC_FAILURE
    where: str = ""
    capacity: int = 0
    true_len: int = 0              # self.len() * n in unbounded integers
    computed_len: int = 0          # self.len() * n as the machine computes it
    wrapped: bool = False
    final_len: int = 0
    oob: dict = field(default_factory=dict)
    steps: list = field(default_factory=list)


def _guard(width: int, size: int) -> bool:
    """alloc_guard: True if it would return Err (only for usize < 8 bytes)."""
    return width < 64 and size > (1 << (width - 1)) - 1


def _alloc(t: Trace, width: int, cap: int, elem: int, where: str) -> bool:
    mask = (1 << width) - 1
    size = cap * elem
    if size > mask:
        t.outcome, t.where = "PANIC", f"{where}: cap.checked_mul(elem_size) -> capacity overflow"
        return False
    if _guard(width, size):
        t.outcome, t.where = "PANIC", f"{where}: alloc_guard -> capacity overflow"
        return False
    if size > (1 << (width - 1)) - 1:
        # 64-bit: no guard; the allocator is assumed to refuse > isize::MAX.
        t.outcome, t.where = "ALLOC_FAILURE", f"{where}: size > isize::MAX (assumed allocator refusal, handle_alloc_error)"
        return False
    return True


def repeat(version: str, width: int, self_len: int, n: int, elem: int = 1) -> Trace:
    if version not in VERSIONS or width not in WIDTHS:
        raise ValueError((version, width))
    mask = (1 << width) - 1
    if not (0 <= self_len <= mask and 0 <= n <= mask and elem >= 1):
        raise ValueError("self_len and n must fit in usize")
    if self_len * elem > (1 << (width - 1)) - 1:
        raise ValueError("a slice cannot exceed isize::MAX bytes")
    t = Trace(true_len=self_len * n)
    if n == 0:
        t.outcome, t.where = "OK", "n == 0 -> Vec::new()"
        return t
    if version == "1.29.1" and self_len * n > mask:
        t.computed_len, t.wrapped = (self_len * n) & mask, True
        t.outcome, t.where = "PANIC", "slice.rs: checked_mul(n).expect(\"capacity overflow\")"
        return t
    want = (self_len * n) & mask
    t.computed_len, t.wrapped = want, self_len * n > mask
    if not _alloc(t, width, want, elem, "with_capacity"):
        return t
    cap, length = want, 0
    t.steps.append(("with_capacity", cap))
    # buf.extend(self): reserve(self_len) via amortized growth
    if cap - length < self_len:
        new_cap = max(cap * 2, length + self_len)
        if not _alloc(t, width, new_cap, elem, "extend/reserve"):
            return t
        cap = new_cap
        t.steps.append(("reserve", cap))
    length += self_len
    m = n >> 1
    while m > 0:
        if length + length > cap:
            t.outcome, t.where = "OOB_WRITE", "doubling loop copy_nonoverlapping"
            t.oob = {"write_offset": length, "write_count": length, "capacity": cap,
                     "elements_past_capacity": length + length - cap}
            t.capacity = cap
            return t
        length = (length * 2) & mask
        t.steps.append(("double", length))
        m >>= 1
    rem_len = (want - length) & mask
    if rem_len > 0:
        if length + rem_len > cap:
            t.outcome, t.where = "OOB_WRITE", "rem copy_nonoverlapping"
            t.oob = {"write_offset": length, "write_count": rem_len, "capacity": cap,
                     "elements_past_capacity": length + rem_len - cap}
            t.capacity = cap
            return t
        length = cap   # buf.set_len(buf_cap)
        t.steps.append(("rem", length))
    t.capacity, t.final_len = cap, length
    t.outcome = "OK" if length == t.true_len else "WRONG_LENGTH"
    t.where = t.where or "returned"
    return t
