"""
performance.py  –  PerformanceAnalyzer for CS 432 Assignment 2 (Module A)

Compares B+ Tree vs BruteForceDB across:
  insertion, search, deletion, range query, random mixed, memory usage
"""

from __future__ import annotations
import time
import random
import tracemalloc
from typing import Callable

from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def _timed(fn: Callable, *args, **kwargs) -> tuple[float, object]:
    """Run *fn* once and return (elapsed_seconds, return_value)."""
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    return time.perf_counter() - t0, result


# ---------------------------------------------------------------------------
# Memory helper
# ---------------------------------------------------------------------------

def _measure_memory(fn: Callable, *args, **kwargs) -> tuple[float, object]:
    """
    Run *fn* inside tracemalloc and return
    (peak_memory_KiB, return_value).
    """
    tracemalloc.start()
    result = fn(*args, **kwargs)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024, result   # bytes → KiB


# ---------------------------------------------------------------------------
# PerformanceAnalyzer
# ---------------------------------------------------------------------------

class PerformanceAnalyzer:
    """
    Benchmark B+ Tree vs BruteForceDB over a range of dataset sizes.

    Parameters
    ----------
    sizes   : list[int]  – number of keys in each test round
    order   : int        – B+ Tree order (default 4)
    seed    : int        – random seed for reproducibility
    """

    def __init__(
        self,
        sizes: list[int] | None = None,
        order: int = 4,
        seed: int = 42,
    ):
        self.sizes = sizes or list(range(100, 5100, 500))
        self.order = order
        self.seed = seed

        # Result containers
        self.results: dict[str, dict[str, list[float]]] = {
            "insert":  {"bptree": [], "brute": []},
            "search":  {"bptree": [], "brute": []},
            "delete":  {"bptree": [], "brute": []},
            "range":   {"bptree": [], "brute": []},
            "random":  {"bptree": [], "brute": []},
            "memory":  {"bptree": [], "brute": []},
        }

    # ------------------------------------------------------------------
    # Individual benchmarks
    # ------------------------------------------------------------------

    def benchmark_insert(self, keys):
        bpt = BPlusTree(order=self.order)
        bf  = BruteForceDB()

        def run_bpt():
            for k in keys:
                bpt.insert(k, k * 10)

        def run_bf():
            for k in keys:
                bf.insert(k)

        t_bpt, _ = _timed(run_bpt)
        t_bf,  _ = _timed(run_bf)

        return {"bptree": t_bpt, "brute": t_bf}

    def benchmark_search(self, bpt: BPlusTree, bf: BruteForceDB,
                     queries: list[int]) -> dict[str, float]:

        def run_bpt():
            for k in queries:
                bpt.search(k)

        def run_bf():
            for k in queries:
                bf.search(k)

        t_bpt, _ = _timed(run_bpt)
        t_bf,  _ = _timed(run_bf)

        return {"bptree": t_bpt, "brute": t_bf}

    def benchmark_delete(self, bpt: BPlusTree, bf: BruteForceDB,
                     to_delete: list[int]) -> dict[str, float]:

        def run_bpt():
            for k in to_delete:
                bpt.delete(k)

        def run_bf():
            for k in to_delete:
                bf.delete(k)

        t_bpt, _ = _timed(run_bpt)
        t_bf,  _ = _timed(run_bf)

        return {"bptree": t_bpt, "brute": t_bf}

    def benchmark_range(self, bpt: BPlusTree, bf: BruteForceDB,
                    start: int, end: int) -> dict[str, float]:

        def run_bpt():
            bpt.range_query(start, end)

        def run_bf():
            bf.range_query(start, end)

        t_bpt, _ = _timed(run_bpt)
        t_bf,  _ = _timed(run_bf)

        return {"bptree": t_bpt, "brute": t_bf}

    def benchmark_random(self, keys: list[int], n_ops: int = 200) -> dict[str, float]:
        """Mixed random workload: insert / search / delete in random order."""
        rng = random.Random(self.seed + 1)

        bpt = BPlusTree(order=self.order)
        bf  = BruteForceDB()

        for k in keys:
            bpt.insert(k, k)
            bf.insert(k)

        ops_bpt: list[Callable] = []
        ops_bf:  list[Callable] = []
        pool = list(keys)

        for _ in range(n_ops):
            op = rng.choice(["search", "insert", "delete"])
            k  = rng.choice(pool)

            if op == "search":
                ops_bpt.append(lambda _k=k: bpt.search(_k))
                ops_bf.append( lambda _k=k: bf.search(_k))

            elif op == "insert":
                new_k = rng.randint(1, 10**6)
                ops_bpt.append(lambda _k=new_k: bpt.insert(_k, _k))
                ops_bf.append( lambda _k=new_k: bf.insert(_k))

            else:  # delete
                ops_bpt.append(lambda _k=k: bpt.delete(_k))
                ops_bf.append( lambda _k=k: bf.delete(_k))

        def run_ops(ops):
            for f in ops:
                f()

        t_bpt, _ = _timed(lambda: run_ops(ops_bpt))
        t_bf,  _ = _timed(lambda: run_ops(ops_bf))

        return {"bptree": t_bpt, "brute": t_bf}

    def benchmark_memory(self, keys):
        def build_bpt():
            tree = BPlusTree(order=self.order)
            for k in keys:
                tree.insert(k, k)
            return tree

        def build_bf():
            db = BruteForceDB()
            for k in keys:
                db.insert(k)
            return db

        mem_bpt, _ = _measure_memory(build_bpt)
        mem_bf,  _ = _measure_memory(build_bf)

        return {"bptree": mem_bpt, "brute": mem_bf}

    # ------------------------------------------------------------------
    # Full automated run
    # ------------------------------------------------------------------

    def run_all(self, verbose: bool = True) -> dict:
        """
        Execute all benchmarks across self.sizes.
        Populates self.results and returns it.
        """
        rng = random.Random(self.seed)

        for n in self.sizes:
            keys    = rng.sample(range(1, n * 10 + 1), n)
            queries = rng.sample(keys, min(n, 100))
            to_del  = rng.sample(keys, min(n // 5 or 1, 50))

            if verbose:
                print(f"  → n={n:>6,} ...", end=" ", flush=True)

            # ── Insert ────────────────────────────────────────────────
            ins = self.benchmark_insert(keys)
            self.results["insert"]["bptree"].append(ins["bptree"])
            self.results["insert"]["brute"].append(ins["brute"])

            # Re-build structures for the remaining tests
            bpt = BPlusTree(order=self.order)
            bf  = BruteForceDB()
            for k in keys:
                bpt.insert(k, k * 10)
                bf.insert(k)

            # ── Search ────────────────────────────────────────────────
            srch = self.benchmark_search(bpt, bf, queries)
            self.results["search"]["bptree"].append(srch["bptree"])
            self.results["search"]["brute"].append(srch["brute"])

            # ── Range query ───────────────────────────────────────────
            lo, hi = min(keys), max(keys)
            mid    = (lo + hi) // 2
            start = max(lo, mid - (hi - lo) // 4)
            end   = min(hi, mid + (hi - lo) // 4)
            rng_r  = self.benchmark_range(bpt, bf,start,
                                           end // 4)
            self.results["range"]["bptree"].append(rng_r["bptree"])
            self.results["range"]["brute"].append(rng_r["brute"])

            # ── Delete ────────────────────────────────────────────────
            dl = self.benchmark_delete(bpt, bf, to_del)
            self.results["delete"]["bptree"].append(dl["bptree"])
            self.results["delete"]["brute"].append(dl["brute"])

            # ── Random mixed ──────────────────────────────────────────
            rand = self.benchmark_random(keys, n_ops=min(n, 300))
            self.results["random"]["bptree"].append(rand["bptree"])
            self.results["random"]["brute"].append(rand["brute"])

            # ── Memory ────────────────────────────────────────────────
            mem = self.benchmark_memory(keys)
            self.results["memory"]["bptree"].append(mem["bptree"])
            self.results["memory"]["brute"].append(mem["brute"])

            if verbose:
                print(
                    f"insert {ins['bptree']*1e3:.2f}/{ins['brute']*1e3:.2f} ms | "
                    f"search {srch['bptree']*1e3:.2f}/{srch['brute']*1e3:.2f} ms"
                )

        return self.results
