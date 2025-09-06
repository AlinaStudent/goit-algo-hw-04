

import argparse
import random
import timeit
from typing import Callable, List, Tuple


# -----------------------------
# Реалізації алгоритмів
# -----------------------------

def insertion_sort(arr: List[int]) -> List[int]:
    """Повертає новий список, відсортований сортуванням вставками (O(n^2))."""
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr: List[int]) -> List[int]:
    """Повертає новий список, відсортований злиттям (O(n log n))."""
    n = len(arr)
    if n <= 1:
        return arr.copy()
    mid = n // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    i = j = 0
    out = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    if i < len(left):
        out.extend(left[i:])
    if j < len(right):
        out.extend(right[j:])
    return out


def timsort_sorted(arr: List[int]) -> List[int]:
    """Вбудований Timsort через sorted()."""
    return sorted(arr)


# -----------------------------
# Генератори наборів даних
# -----------------------------

def make_random(n: int) -> List[int]:
    return [random.randint(0, 10**9) for _ in range(n)]

def make_sorted(n: int) -> List[int]:
    return list(range(n))

def make_reverse(n: int) -> List[int]:
    return list(range(n, 0, -1))

def make_nearly_sorted(n: int, swaps_ratio: float = 0.01) -> List[int]:
    """Починаємо зі відсортованого, робимо випадкові перестановки ~1% елементів."""
    a = list(range(n))
    swaps = max(1, int(n * swaps_ratio))
    for _ in range(swaps):
        i = random.randrange(n)
        j = random.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a

def make_many_duplicates(n: int, uniques: int = 100) -> List[int]:
    """Багато дублікатів — корисно для Timsort (стабільність/адаптивність)."""
    return [random.randrange(uniques) for _ in range(n)]


DATASETS: list[Tuple[str, Callable[[int], List[int]]]] = [
    ("random", make_random),
    ("sorted", make_sorted),
    ("reverse", make_reverse),
    ("nearly_sorted", make_nearly_sorted),
    ("many_duplicates", make_many_duplicates),
]


# -----------------------------
# Бенчмарк
# -----------------------------

def bench_one(func: Callable[[List[int]], List[int]], data: List[int],
              repeat: int, number: int) -> float:
    """
    Вимірює середній час (сек) виконання func(data) за допомогою timeit.
    Кожен запуск працює на копії, щоб вхід не псували попередні сортування.
    """
    timer = timeit.Timer(lambda: func(data))
    # Щоб уникнути "розігріву" кэшу CPU/інтерпретатора, використовуємо repeat і беремо мінімум/середнє
    runs = timer.repeat(repeat=repeat, number=number)
    return sum(runs) / len(runs) / number  # середній час одного виконання


def run_bench(ns: list[int], repeat: int, number: int,
              include_insertion_upper_n: int) -> None:
    algos: list[Tuple[str, Callable[[List[int]], List[int]]]] = [
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Timsort(sorted)", timsort_sorted),
    ]

    # Заголовок
    print(f"\nBenchmark: repeat={repeat}, number={number}")
    print(f"{'n':>8}  {'dataset':<16}  {'Insertion (ms)':>14}  {'Merge (ms)':>11}  {'Timsort (ms)':>13}")
    print("-" * 70)

    for n in ns:
        for name, gen in DATASETS:
            data = gen(n)
            # Замір кожного алгоритму
            times_ms = {"Insertion": None, "Merge": None, "Timsort(sorted)": None}

            for algo_name, algo in algos:
                # Щоб Insertion не «вбив» прогін на дуже великих n
                if algo_name == "Insertion" and n > include_insertion_upper_n:
                    continue
                t = bench_one(lambda d=data: algo(d.copy()), data, repeat, number) * 1000.0
                times_ms[algo_name] = t

            ins = f"{times_ms['Insertion']:.2f}" if times_ms["Insertion"] is not None else "—"
            mer = f"{times_ms['Merge']:.2f}"
            tim = f"{times_ms['Timsort(sorted)']:.2f}"

            print(f"{n:8d}  {name:<16}  {ins:>14}  {mer:>11}  {tim:>13}")


def analyze_scaling():
    """
    Невеликий емпіричний аналіз масштабування на випадкових даних:
    показуємо, як змінюється час при збільшенні n.
    """
    print("\nEmpirical scaling on random data (Insertion vs Merge vs Timsort)")
    for algo_name, algo in [("Insertion", insertion_sort),
                            ("Merge", merge_sort),
                            ("Timsort(sorted)", timsort_sorted)]:
        ns = [2000, 4000, 8000, 16000]
        if algo_name == "Insertion":
            ns = [1000, 2000, 4000, 8000]  # щоб не було занадто довго
        prev_t = None
        print(f"  {algo_name}:")
        for n in ns:
            data = make_random(n)
            t = bench_one(algo, data, repeat=3, number=1)
            ratio = (t / prev_t) if prev_t else float('nan')
            # Очікувано: Insertion ~×4 при подвоєнні n; Merge/Timsort ~×(n log n): ≈×2.2–2.4
            print(f"    n={n:6d}: {t*1000:8.2f} ms  "
                  f"{'(x' + f'{ratio:.2f}' + ')' if prev_t else ''}")
            prev_t = t


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Порівняння Insertion, Merge та Timsort (sorted) за часом виконання."
    )
    p.add_argument("--sizes", "-n", type=str, default="1000,5000,20000",
                   help="Розміри масивів через кому. Напр.: 1000,5000,20000")
    p.add_argument("--repeat", type=int, default=3,
                   help="Скільки разів повторити серію вимірів (timeit.repeat).")
    p.add_argument("--number", type=int, default=1,
                   help="Скільки виконань у межах одного виміру (timeit.number).")
    p.add_argument("--ins-max", type=int, default=20000,
                   help="Макс. n, на якому ще міряємо Insertion (щоб не чекати дуже довго).")
    p.add_argument("--no-scaling", action="store_true",
                   help="Не друкувати емпіричний аналіз масштабування наприкінці.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    random.seed(42)

    ns = [int(x) for x in args.sizes.split(",") if x.strip()]
    run_bench(ns, repeat=args.repeat, number=args.number,
              include_insertion_upper_n=args.ins_max)

    if not args.no_scaling:
        analyze_scaling()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
