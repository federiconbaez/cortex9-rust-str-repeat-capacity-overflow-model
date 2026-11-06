# Guía práctica / Practice guide

Ejercicios **offline** de aritmética modular. No se reserva memoria ni se
compila Rust. *English summary at the end.*

## Comandos locales

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m repeat_model run --len 3 --n 4
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

## Ejercicios graduados

**Nivel 1: caso normal.** Calcula la longitud final de `"abc".repeat(4)`.
Comprobación: `final_len` = 12 en las dos versiones (caso `small`).

**Nivel 2: envoltura en 16 bits.** Calcula a mano `2*0x8001 mod 2^16`.
Comprobación: `computed_len` = 2 y `OOB_WRITE` en 1.29.0 con
`write_offset` = 2 (caso `wrap-16`).

**Nivel 3: el fix.** ¿Qué devuelve `checked_mul` en el mismo caso y qué
ocurre en 1.29.1?
Comprobación: `None` → `expect` → `PANIC`.

**Nivel 4: reserve en extend.** En `wrap-reserve-32` la capacidad
envuelta (2) es menor que `len` (3). Calcula la nueva capacidad.
Comprobación: `max(2*2, 3)` = 4, y la escritura sobrepasa la capacidad en
2 elementos.

**Nivel 5: alloc_guard.** ¿Por qué `len=1, n=0xffff` hace panic en 16 bits
aunque no haya envoltura?
Comprobación: 65535 > `isize::MAX` (32767) → `PANIC` en ambas versiones.

**Nivel 6: frontera exacta.** Comprueba que `7*4681` cabe justo en
`isize::MAX` de 16 bits.
Comprobación: 32767 → `OK` con `final_len` = 32767.

**Nivel 7: el doc test del aviso.** En 64 bits, ¿cuánto vale
`16*(2^64-1) mod 2^64`? ¿Por qué el modelo no escribe fuera de límites?
Comprobación: `2^64-16` > `isize::MAX` → `ALLOC_FAILURE` (supuesto
documentado).

**Nivel 8: invariante.** En `results/sweep_summary.csv`, verifica las
columnas de 1.29.1 y la relación entre la envoltura y `OOB_WRITE` en
1.29.0.
Comprobación: `oob_write` = 0 en 1.29.1; `oob_without_wrap` = 0 y
`wrap_without_oob_or_stop` = 0 en todas las filas.

## English summary

Eight levels: a normal repeat, 16-bit wraparound, the `checked_mul` fix,
the reserve inside `extend`, `alloc_guard`, the exact `isize::MAX`
boundary, why the advisory's 64-bit doc test fails allocation rather than
writing out of bounds in this model, and the sweep invariants.
