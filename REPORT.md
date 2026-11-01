# Assignment 6 Report: Medians, Order Statistics & Elementary Data Structures

All code is plain Python 3 (standard library only; `matplotlib` is used just to draw the charts). Every timing below was measured on the same machine with Python 3.13. Each number is the best of several repeats, and the two benchmark suites were run separately so they did not compete for CPU. Raw data is in `results/*.csv`.

---

## Part 1: Selection Algorithms

**Problem.** Given an unsorted sequence `A` of `n` elements and a rank `k` (1 ≤ k ≤ n), return the k-th smallest element. The median is the case k = ⌈n/2⌉. Sorting first solves this in O(n log n). Both algorithms below do it in linear time.

### 1.1 Implementation

#### Deterministic selection: Median of Medians (`selection/deterministic.py`)

`median_of_medians_select(arr, k)` follows CLRS §9.3 (the BFPRT algorithm):

1. **Base case.** If n ≤ 5, sort and index directly.
2. **Groups of five.** Split the input into ⌈n/5⌉ groups and find the median of each with insertion sort. Each group costs O(1).
3. **Pivot.** Recursively select the true median `x` of those ⌈n/5⌉ medians.
4. **Three-way partition.** Split the input into `L` (< x), a count of elements equal to x, and `G` (> x).
5. **Recurse.** Continue on whichever side holds rank k. If k falls inside the "equal" block, `x` is the answer.

Design choices:

- **Three-way partition for duplicates.** Elements equal to the pivot are counted and then discarded, never recursed on. A two-way partition can keep pushing equal keys to one side. With three-way partitioning, an all-equal array finishes after a single partition pass.
- **Tail-recursion removed.** The large recursive call (step 5) is a `while` loop. Only the pivot-finding recursion (step 3) uses the call stack, and that recursion operates on n/5, n/25, … elements, so stack depth is O(log₅ n).
- **Input is not mutated.** The function works on a copy. Invalid `k`, empty input, and non-integer `k` raise `ValueError`/`TypeError`.

#### Randomized selection: Quickselect (`selection/randomized.py`)

`randomized_select(arr, k, seed=None, in_place=False)` follows CLRS §9.2 (RANDOMIZED-SELECT):

1. Choose a pivot index uniformly at random in `A[lo..hi]`.
2. Partition **in place** with Dijkstra's three-way ("Dutch national flag") scheme into `< p | == p | > p`.
3. If the target index lies in the `== p` block, return it. Otherwise shrink `[lo, hi]` to the side that contains it.

Design choices:

- **Iterative and in place.** The algorithm uses no recursion and only O(1) extra working space. A copy is made only to protect the caller's list, and `in_place=True` skips it.
- **Three-way partition**, for the same duplicate-handling reason as above.
- **Seedable RNG** (`seed=`), so runs and tests are reproducible.

#### Correctness testing (`tests/test_selection.py`)

The tests check every rank `k` against `sorted(arr)[k-1]` for these inputs: a single element, small arrays, sorted and reverse-sorted arrays, many duplicates, all-equal arrays, negatives and floats, strings, a 20,001-element random array, and 200 random fuzz cases. They also verify that the input is not mutated and that invalid arguments are rejected. All tests pass.

### 1.2 Theoretical Analysis

#### Deterministic: O(n) in the worst case

Let `x` be the median of medians. Half of the ⌈n/5⌉ groups have a median ≥ x. Excluding the group containing `x` and the last, possibly partial group, each of those groups contributes 3 elements that are ≥ x. So

  #elements ≥ x ≥ 3(⌈½⌈n/5⌉⌉ − 2) ≥ 3n/10 − 6,

and by symmetry at least 3n/10 − 6 elements are ≤ x. The recursive call in step 5 therefore receives at most **7n/10 + 6** elements, **whatever the input looks like**. This gives the recurrence

  T(n) ≤ T(⌈n/5⌉) + T(7n/10 + 6) + O(n).

Since 1/5 + 7/10 = 9/10 < 1, the two subproblems together shrink by a constant fraction. Substituting T(n) ≤ cn gives
cn/5 + c + 7cn/10 + 6c + an = 9cn/10 + 7c + an ≤ cn, which holds when c ≥ 20a and n ≥ 140. Hence **T(n) = O(n) in the worst case**. No randomness is involved, so no input can force worse behaviour.

Why groups of 5? With groups of 3 the fractions become 1/3 + 2/3 = 1, so the work no longer shrinks and the bound becomes O(n log n). Groups of 7 or more also work but cost more per group.

#### Randomized: O(n) in expectation, O(n²) in the worst case

Call a pivot **good** if its rank lies in the middle half [n/4, 3n/4]. A good pivot leaves at most 3n/4 elements. A uniformly random pivot is good with probability ½, so the expected number of partition passes before a good pivot appears is 2. Group the run into phases, where phase j ends when the active size first drops to (3/4)^j·n or below. Each pass in phase j costs at most c(3/4)^j·n, so

  E[T(n)] ≤ Σⱼ 2 · c(3/4)ʲ n = 2cn · 1/(1 − 3/4) = **8cn = O(n)**.

The tighter CLRS analysis gives E[comparisons] ≤ 4n. For the median specifically, the exact expectation is (2 + 2 ln 2)n ≈ 3.39n.

The **worst case is Θ(n²)**. It happens when the pivot is always the minimum or maximum, so each pass removes just one element. With random pivots this needs a long run of unlucky draws, and its probability decays exponentially. It does **not** depend on the input order: sorted, reverse-sorted and adversarial inputs all have the same expected cost. A fixed pivot rule such as "first element" does have such bad inputs (see §1.3).

#### Space complexity and overheads

| | Deterministic (MoM) | Randomized quickselect |
|---|---|---|
| Extra space | O(n): the new `L`/`G` lists and the medians list. Sizes shrink geometrically, so the total live at once is O(n). | O(1) working space, plus an O(n) defensive copy that `in_place=True` avoids |
| Stack depth | O(log n) (pivot-finding recursion only) | O(1) (fully iterative) |
| Comparisons (median) | ≈ 10n–22n: the group medians, the recursive median search and the full partition every round | ≈ 3.4n expected |
| Other overhead | Slicing into groups, list allocation, a second recursion | One random number per pass |

The hidden constant is the main practical difference. MoM spends a lot of work choosing a pivot that is guaranteed good. Quickselect spends almost nothing and gets a good pivot half the time.

### 1.3 Empirical Analysis

Benchmark script: `benchmarks/bench_selection.py`. It selects the median for n from 1,000 to 200,000 on five input distributions:

- **random**: uniform integers in [0, 10n]
- **sorted**: 0, 1, …, n−1
- **reverse**: n, n−1, …, 1
- **few_unique**: values 0–9 only, so heavy duplication
- **all_equal**: every element is 7

Two baselines give context: `sorted(arr)[k-1]` (Python's C-implemented Timsort) and a **naive quickselect** that always picks the first element as pivot and uses a two-way partition.

![time by distribution](results/selection_time_by_distribution.png)

**Results at n = 200,000 (median selection):**

| Distribution | Deterministic (MoM) | Randomized | MoM / Randomized | Sort + index (C) |
|---|---:|---:|---:|---:|
| random | 124.5 ms | 43.1 ms | 2.9× | 34.6 ms |
| sorted | 77.7 ms | 42.9 ms | 1.8× | 1.6 ms |
| reverse | 116.7 ms | 35.4 ms | 3.3× | 1.4 ms |
| few_unique | 44.4 ms | 27.1 ms | 1.6× | 12.4 ms |
| all_equal | 28.3 ms | 9.5 ms | 3.0× | 0.9 ms |

**Observations and how they relate to the theory**

1. **Both algorithms are linear.** On every distribution, time grows in a straight line with n. The per-element chart makes this clearest. MoM stays at roughly 580–790 ns per element from n = 1,000 to 200,000, which is the flat line O(n) predicts. Quickselect stays at roughly 140–310 ns per element. Its line is flat on average but noisier, as expected for a random variable.

   ![time per element](results/selection_time_per_element.png)

2. **The randomized algorithm is about 2–3× faster.** This matches the constant-factor analysis: about 3.4n expected comparisons versus 10n or more for MoM, plus MoM's extra list allocation and second recursion. The O(n) worst-case guarantee costs a larger constant on every input.

3. **Variance: guaranteed vs expected.** Over 200 runs on the same random input (n = 100,000), quickselect averaged 28.7 ms with a standard deviation of 8.0 ms (a ±28% spread) and ranged from 14.2 to 60.1 ms. Over 30 runs, MoM averaged 62.7 ms with a standard deviation of only 2.0 ms (±3%). MoM's slowest run was still slower than quickselect's typical run, but its time is predictable. This is the practical meaning of "worst-case O(n)" versus "expected O(n)".

   ![variance](results/selection_variance.png)

4. **Input order does not hurt the randomized algorithm, but it does hurt a fixed pivot.** Randomized quickselect took about the same time on random, sorted and reverse inputs (35–43 ms at n = 200,000). The first-element-pivot version collapses to Θ(n²) on ordered input:

   | n = 5,000 | Naive (first pivot) | Randomized | Slowdown |
   |---|---:|---:|---:|
   | sorted | 183.5 ms | 0.71 ms | ≈ 260× |
   | reverse | 498.1 ms | 1.12 ms | ≈ 440× |
   | all_equal | 176.3 ms | 0.25 ms | ≈ 700× |

   The naive version had to be capped at n = 5,000 on these inputs to keep the benchmark short.

   ![naive vs random](results/selection_naive_vs_random_sorted.png)

5. **Duplicates.** The naive two-way partition also degrades on the `few_unique` input, taking **3.6 s** at n = 200,000. The three-way-partition versions take 27 ms (randomized) and 44 ms (MoM). Both of our algorithms are fastest on the duplicate-heavy inputs, because the "equal" block removes many elements per pass. This confirms that the three-way partition handles the duplicates edge case.

6. **Sorted vs reverse for MoM** (78 ms vs 117 ms). This gap comes from the group-of-5 insertion sort. A sorted group needs no swaps, while a reversed group needs the maximum number. Only the constant changes; both are linear.

7. **Why `sorted()` looks so fast.** This does not contradict the asymptotics. `sorted` runs as optimised C, while our algorithms run as interpreted Python, which costs roughly 50–100× more per operation. Timsort also detects already-sorted or reversed runs and handles them in O(n), which explains its ~1.5 ms on sorted and reverse input. On random input it is O(n log n), and its per-element cost rises steadily (94 → 173 ns per element from n = 10³ to 2·10⁵). The selection algorithms' per-element cost stays flat. For a fair asymptotic comparison, both sides would need to be written in the same language.

**Conclusion.** Both algorithms are linear in practice, as the theory predicts. Randomized quickselect is the better default: it is 2–3× faster, works in place, and is insensitive to input order. MoM is worth its higher constant when a hard worst-case bound is required, for example in real-time systems, in adversarial settings where an attacker could predict pivots, or as the fallback in introselect. Introselect is what C++ `std::nth_element` does: it runs quickselect and switches to median of medians if the recursion goes badly.

---

## Part 2: Elementary Data Structures

All structures are in `data_structures/`. They are built from scratch on top of a fixed-size block of slots: Python lists are pre-allocated and never grown with `append`/`insert`, so every resize and shift is done explicitly.

### 2.1 Implementation summary

| Module | Class | Notes |
|---|---|---|
| `array.py` | `DynamicArray` | Manages its own capacity: doubles when full, halves when ¼ full. Supports access, set, append, insert(i), delete(i), pop, remove, search. |
| `array.py` | `Matrix` | Row-major flat storage, so `A[r,c]` = `data[r*cols + c]`. Supports access, set, insert/delete row and column, transpose, `+`, `@`. |
| `stack_queue.py` | `ArrayStack` | Top of the stack is the end of the array. Resizes by doubling and halving. |
| `stack_queue.py` | `ArrayQueue` | **Circular buffer**: head index plus size, wraps around with modulo, grows by doubling. |
| `stack_queue.py` | `NaiveArrayQueue` | Dequeue shifts every element left. Included only as a benchmark baseline. |
| `linked_list.py` | `SinglyLinkedList` | Keeps `head`, `tail` and a size counter. Supports prepend, append, insert_after, insert_at, delete_head, delete_tail, delete(value), delete_at, find, get, traverse, reverse. |
| `linked_list.py` | `LinkedStack`, `LinkedQueue` | Built on the linked list. The stack pushes and pops at the head; the queue enqueues at the tail and dequeues at the head. |
| `rooted_tree.py` | `RootedTree` (optional part) | Left-child/right-sibling representation (CLRS §10.4). Supports add_child, children, depth, height, preorder, level-order (using our `ArrayQueue`), find, remove_subtree. |

`tests/test_data_structures.py` covers normal operations, resizing, ring-buffer wrap-around, tail-pointer maintenance after every kind of deletion, empty-structure errors, and tree traversals.

### 2.2 Time complexity of operations

**Arrays and matrices**

| Operation | DynamicArray | Why |
|---|---|---|
| access / update `a[i]` | O(1) | Address arithmetic |
| append | O(1) amortised, O(n) worst | Doubling: n appends cause at most 1 + 2 + 4 + … + n < 2n copies in total |
| insert at i | O(n − i) | Elements after i shift right |
| delete at i | O(n − i) | Elements after i shift left |
| pop (end) | O(1) amortised | Halving at ¼ full, not ½, avoids thrashing between grow and shrink |
| search | O(n) | Linear scan (O(log n) only if the data were kept sorted) |

For an r × c **Matrix**: access is O(1); inserting or deleting a row or column, and transposing, are O(rc); multiplying (n×m)(m×p) is O(nmp).

**Stacks and queues**

| Operation | ArrayStack | LinkedStack | ArrayQueue (circular) | LinkedQueue | NaiveArrayQueue |
|---|---|---|---|---|---|
| push / enqueue | O(1) amortised | O(1) | O(1) amortised | O(1) | O(1) amortised |
| pop / dequeue | O(1) amortised | O(1) | O(1) amortised | O(1) | **O(n)** |
| peek, size, is_empty | O(1) | O(1) | O(1) | O(1) | O(1) |

**Singly linked list**

| Operation | Time |
|---|---|
| prepend, append (thanks to the tail pointer), insert_after(node) | O(1) |
| insert_at(i), get(i), delete_at(i) | O(i) |
| delete_head | O(1) |
| delete_tail | O(n): no `prev` pointer, so the predecessor must be found by walking the list |
| find / delete(value) / traverse / reverse | O(n) |

**Rooted tree (LCRS):** add_child is O(1); children(v) is O(deg v); depth is O(depth); traversal, height and find are O(n). Space is O(n) however many children a node has.

### 2.3 Empirical comparison

Benchmark script: `benchmarks/bench_data_structures.py`.

![data structure benchmarks](results/data_structures_benchmarks.png)

| Experiment | Size | Array-based | Linked / alternative |
|---|---|---:|---:|
| Stack: n push + n pop | 400,000 | **93 ms** (ArrayStack) | 143 ms (LinkedStack) |
| Queue: n enqueue + n dequeue | 400,000 | 184 ms (circular ArrayQueue) | **160 ms** (LinkedQueue) |
| Queue: shifting vs circular | 16,000 | 4,015 ms (Naive) | **5.4 ms** (circular) |
| Insert at front, n times | 16,000 | 3,785 ms (`insert(0)`) | **2.9 ms** (`prepend`) |
| 2,000 random reads at index i | 16,000 | **0.15 ms** (`a[i]`) | 177 ms (`get(i)`) |
| Memory per element (n = 100,000) | | **≈ 10.5 B** | ≈ 48 B per node |

**What the numbers show**

- **Same big-O, different constants.** Stack and queue operations are O(1) in both versions, and both grow linearly in n. The array stack is about 1.5× faster because it allocates no node object per push, only a pointer write into an existing slot (plus a rare resize). The circular array queue is slightly *slower* than the linked queue here. Its modulo arithmetic and extra index bookkeeping cost more in interpreted Python than the linked queue's node allocation. In a compiled language, the array queue would usually win because of cache locality.
- **Asymptotic differences dominate everything else.** Making dequeue O(n) by shifting (the naive queue) or inserting at the front of an array is about **750–1,300× slower** at n = 16,000, and doubling n roughly quadruples the time, which is the Θ(n²) total. Linked-list random access is O(i) per read, so 2,000 reads went from 7 ms to 177 ms as n grew. The array stayed flat at about 0.15–0.2 ms.
- **Memory.** The array stores one 8-byte pointer per element, plus 0–100% spare capacity from doubling (measured 8–13 B per element). Each linked node is a separate object of about 48 B, even with `__slots__`: an object header plus `value` and `next` pointers. That makes the linked list about 4–5× larger before counting the stored values. Arrays are also contiguous, which suits CPU caches, while nodes are scattered across the heap.

### 2.4 Arrays vs linked lists for stacks and queues: trade-offs

| Criterion | Array-based | Linked-list-based |
|---|---|---|
| Time per operation | O(1) **amortised**: an occasional O(n) resize causes latency spikes | O(1) **worst case**: every operation costs the same |
| Memory | Compact (one pointer per element) but can be up to 50% empty after doubling | Exact count, but every element pays for a node header and a `next` pointer (≈ 4–5× here) |
| Cache locality | Excellent (contiguous) | Poor (pointer chasing) |
| Capacity | Needs resizing logic or a fixed bound | Grows one node at a time with no copying |
| Queue specifics | Needs the circular-buffer trick, or dequeue becomes O(n) | Natural: just a tail pointer |
| Implementation | Index arithmetic and wrap-around are easy to get wrong | Pointer updates are easy to get wrong (e.g. forgetting to reset `tail`) |

**Recommendation.** Use an array (a circular buffer for queues) by default: it is faster in practice and uses less memory. Choose a linked implementation when hard O(1) worst-case latency matters, when the maximum size is unknown and copying large buffers is unacceptable, or when nodes must be spliced in and out given a pointer to them.

### 2.5 Practical applications

**Arrays and matrices**
- Any indexed collection, such as lookup tables, image pixels and audio buffers, where O(1) random access is essential.
- Matrices underpin graphics transforms, machine learning (weights and activations), adjacency matrices for dense graphs, and spreadsheets and dynamic-programming tables.
- *Prefer* when reads and random access dominate and most writes are at the end.

**Stacks (LIFO)**
- Function call stacks and recursion, and undo/redo in editors.
- Expression evaluation and parsing: balanced brackets, infix to postfix, compilers.
- Depth-first search and backtracking (mazes, Sudoku), and browser back-navigation.

**Queues (FIFO)**
- OS process scheduling, printer spoolers, and web-server request queues.
- Breadth-first search and level-order traversal (used by our `RootedTree.level_order`).
- Producer–consumer buffers. Circular buffers are standard in network cards, audio streaming and keyboard input, where the size is bounded and allocation must be avoided.

**Linked lists**
- Frequent insertion or deletion in the middle, given a node: an LRU cache (hash map + doubly linked list), free-memory lists in allocators, adjacency lists for sparse graphs.
- Hash-table chaining and polynomial arithmetic with sparse terms.
- *Avoid* when you need indexing or binary search, or when memory and cache efficiency matter.

**Rooted trees**
- File systems (directories with any number of children), the HTML/XML DOM, organisation charts, parse trees, and game trees. The LCRS representation supports any branching factor in O(n) space.

**Choosing between them by scenario**

| Scenario | Best choice | Reason |
|---|---|---|
| Read the i-th item often | Array | O(1) vs O(i) (1,000× faster in our test) |
| Insert/remove at the front often | Linked list (or a deque) | O(1) vs O(n) |
| FIFO buffer with a known maximum size | Circular array | No allocation, cache-friendly, bounded memory |
| Hard real-time, no latency spikes | Linked structure, or a pre-sized array | No amortised resize |
| Memory-constrained device | Array | About 4–5× less overhead per element |
| Quick to implement correctly | Array stack; linked queue | Fewest edge cases |

---

## References

- Cormen, Leiserson, Rivest, Stein. *Introduction to Algorithms*, 3rd/4th ed., Chapter 9 (Medians and Order Statistics) and Chapter 10 (Elementary Data Structures).
- Blum, Floyd, Pratt, Rivest, Tarjan. "Time bounds for selection." *Journal of Computer and System Sciences* 7(4), 1973.
- Hoare, C. A. R. "Algorithm 65: Find." *Communications of the ACM* 4(7), 1961.
