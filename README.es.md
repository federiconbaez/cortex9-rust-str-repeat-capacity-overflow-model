# cortex9-rust-str-repeat-capacity-overflow-model

Modelo offline del desbordamiento entero en `<[T]>::repeat` (la base de
`str::repeat`) en Rust 1.26.0–1.29.0 (CVE-2018-1000810). El fix es 1.29.1,
el commit 1b94b84ad014, que usa `checked_mul`.

**No se reserva memoria.** Capacidad, longitud y escrituras son enteros, y
la aritmética se reproduce para un `usize` de 16, 32 o 64 bits. Se sigue el
camino real:

1. `with_capacity` → `allocate_in` (`checked_mul(elem_size)` y
   `alloc_guard`);
2. `extend` → `reserve`, con crecimiento `max(2·cap, needed)`;
3. el bucle de duplicación;
4. la copia de `rem_len`.

La primera escritura fuera de capacidad se registra como `OOB_WRITE` y el
modelo se detiene ahí.

## Resultados

- **1.29.0:** escribe fuera de límites solo cuando `len*n` envuelve. Si
  envuelve y el valor resultante sigue siendo reservable, el bucle de
  duplicación siempre se sale de la capacidad.
- **1.29.1:** 0 `OOB_WRITE`, porque todo caso que envuelve hace `PANIC`.
- **Supuesto:** en 64 bits se asume que el asignador rechaza tamaños por
  encima de `isize::MAX` (`ALLOC_FAILURE`). Por eso el doc test del aviso
  (`len=16, n=usize::MAX`) no escribe fuera de límites en este modelo.

Para el detalle, consulta README.md, SOURCES.md, LIMITATIONS.md y
PRACTICE.md.

Licencia: Apache-2.0.
