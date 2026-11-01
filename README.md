# Assignment 6: Medians, Order Statistics & Elementary Data Structures

Python implementations, tests and benchmarks for:

- **Part 1:** k-th smallest element selection
  - Deterministic **Median of Medians**: worst-case O(n)
  - **Randomized Quickselect**: expected O(n)
- **Part 2:** Elementary data structures built from scratch
  - Dynamic array and matrix, array-based stack and circular queue, singly linked list (plus linked stack and queue), and a rooted tree (left-child/right-sibling)

The full analysis is in **[REPORT.md](REPORT.md)**.

## Repository layout

```
selection/
  deterministic.py      # median_of_medians_select(arr, k)
  randomized.py         # randomized_select(arr, k, seed=None, in_place=False)
data_structures/
  array.py              # DynamicArray, Matrix
  stack_queue.py        # ArrayStack, ArrayQueue (circular), NaiveArrayQueue (baseline)
  linked_list.py        # SinglyLinkedList, LinkedStack, LinkedQueue
  rooted_tree.py        # RootedTree (left-child / right-sibling)
tests/                  # unittest suites (31 tests)
benchmarks/             # timing experiments that write CSVs and charts to results/
results/                # benchmark CSVs and PNG charts used in the report
REPORT.md               # design, complexity analysis, empirical results, discussion
```

## Requirements

- Python 3.8 or newer
- The algorithms and data structures use only the standard library.
- The benchmarks need `matplotlib` to draw charts:

```bash
pip install -r requirements.txt
```

## How to run

Run all commands from the repository root.

```bash
# 1. Unit tests
python -m unittest discover -s tests -t . -v

# 2. Doctests
python -m doctest selection/deterministic.py selection/randomized.py

# 3. Benchmarks (regenerate results/*.csv and results/*.png)
python -m benchmarks.bench_selection          # takes a few minutes
python -m benchmarks.bench_data_structures    # about a minute
#   add --quick to either one for a fast, smaller run
```

### Quick usage

```python
from selection import median_of_medians_select, randomized_select

data = [7, 2, 9, 4, 4, 1, 8]
median_of_medians_select(data, 4)        # -> 4  (4th smallest, the median)
randomized_select(data, 1, seed=42)      # -> 1  (minimum)

from data_structures import ArrayQueue, SinglyLinkedList
q = ArrayQueue(); q.enqueue("a"); q.enqueue("b"); q.dequeue()   # -> "a"
l = SinglyLinkedList([1, 2, 3]); l.prepend(0); l.reverse(); print(l)  # 3 -> 2 -> 1 -> 0 -> None
```

## Summary of findings

**Selection (median, n = 200,000)**

| Input | Median of Medians | Randomized Quickselect |
|---|---:|---:|
| random | 124.5 ms | 43.1 ms |
| sorted | 77.7 ms | 42.9 ms |
| reverse-sorted | 116.7 ms | 35.4 ms |
| few unique values | 44.4 ms | 27.1 ms |
| all equal | 28.3 ms | 9.5 ms |

- Both algorithms are linear in practice: time per element stays flat as n grows.
- Randomized quickselect is about **2–3× faster** because its constant factor is much smaller (≈ 3.4n expected comparisons vs ≈ 10n or more).
- Median of Medians is **far more predictable**: its run-to-run spread was ±3%, versus ±28% for quickselect.
- A naive first-element-pivot quickselect degrades to Θ(n²) on sorted, reverse or duplicate-heavy input (up to 700× slower). Random pivots and the **three-way partition** used in both implementations avoid this.

**Data structures**

- Array-based stack: about 1.5× faster than the linked stack. The circular array queue and the linked queue perform about the same. All of these operations are O(1).
- A shifting array queue, or inserting at the front of an array, is O(n) per operation. At n = 16,000 that was about **750–1,300× slower** than a circular buffer or a linked list.
- Random access is O(1) in an array and O(i) in a linked list: 0.15 ms vs 177 ms for 2,000 reads at n = 16,000.
- A linked list uses about **48 B per node** versus about 8–13 B per array slot.
- Rule of thumb: use arrays (with a circular buffer for queues) by default. Use linked lists for O(1) splicing at known positions or guaranteed (non-amortised) O(1) operations.
