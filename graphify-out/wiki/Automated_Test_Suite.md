# Automated Test Suite

> 11 nodes · cohesion 0.29

## Key Concepts

- **time** (9 connections)
- **test_parallelism.py** (6 connections) — `tests/test_parallelism.py`
- **run_processes()** (5 connections) — `tests/test_parallelism.py`
- **run_threads()** (5 connections) — `tests/test_parallelism.py`
- **cpu_bound_task()** (4 connections) — `tests/test_parallelism.py`
- **test_threading_vs_multiprocessing()** (4 connections) — `tests/test_parallelism.py`
- **concurrent_futures** (2 connections)
- **Run the CPU task across multiple threads and measure time.** (1 connections) — `tests/test_parallelism.py`
- **Run the CPU task across multiple processes and measure time.** (1 connections) — `tests/test_parallelism.py`
- **Verify that multiprocessing bypasses the GIL for true parallelism.** (1 connections) — `tests/test_parallelism.py`
- **A CPU intensive task that just loops and calculates.** (1 connections) — `tests/test_parallelism.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `tests/test_parallelism.py`

## Audit Trail

- EXTRACTED: 14 (88%)
- INFERRED: 2 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*