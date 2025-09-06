import argparse
import logging
import shutil
import sys
from pathlib import Path


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Рекурсивне копіювання/переміщення файлів з сортуванням за розширенням."
    )
    parser.add_argument("source_dir", nargs="?", type=Path,
                        help="Шлях до вихідної директорії")
    parser.add_argument("dest_dir", nargs="?", default=Path("dist"), type=Path,
                        help="Шлях до директорії призначення (за замовчуванням: ./dist)")
    parser.add_argument("--move", action="store_true",
                        help="Перемістити файли (замість копіювання)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Детальні логи")
    parser.add_argument("--create-test", action="store_true",
                        help="Створити тестову директорію з файлами і використати її як source_dir")
    parser.add_argument("--print-tree", action="store_true",
                        help="Після завершення вивести дерево директорії призначення")
    return parser.parse_args()


def iter_files_recursively(root: Path, skip: Path | None = None):
    """Рекурсивно обходить усі файли у директорії."""
    try:
        for entry in root.iterdir():
            if skip and entry.resolve() == skip:
                continue
            if entry.is_dir() and not entry.is_symlink():
                yield from iter_files_recursively(entry, skip=skip)
            elif entry.is_file():
                yield entry
    except Exception as e:
        logging.warning(f"Помилка доступу до {root}: {e}")


def safe_dest_path(dest_dir: Path, src_file: Path) -> Path:
    """Формує безпечний шлях (якщо ім’я вже існує — додає _1, _2...)."""
    ext = src_file.suffix
    stem = src_file.stem
    candidate = dest_dir / f"{stem}{ext}"
    counter = 1
    while candidate.exists():
        candidate = dest_dir / f"{stem}_{counter}{ext}"
        counter += 1
    return candidate


def place_for(src_file: Path, dest_root: Path) -> Path:
    """Повертає теку для файлу згідно з його розширенням."""
    ext = src_file.suffix.lower().lstrip(".")
    subdir = ext if ext else "no_extension"
    return dest_root / subdir


def copy_or_move(src: Path, dst: Path, move: bool) -> None:
    """Копіює або переміщує файл."""
    try:
        if move:
            shutil.move(src, dst)
        else:
            shutil.copy2(src, dst)
    except Exception as e:
        logging.warning(f"Помилка під час операції {src} -> {dst}: {e}")


def create_test_directory(base: Path) -> Path:
    """Створює тестову теку з кількома файлами."""
    test_dir = base / "src_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "file1.txt").write_text("hello")
    (test_dir / "file2.doc").write_text("world")
    (test_dir / "file3").write_text("no extension")
    subdir = test_dir / "sub"
    subdir.mkdir(exist_ok=True)
    (subdir / "nested.py").write_text("print('nested')")
    logging.info(f"Створено тестову теку: {test_dir}")
    return test_dir


def print_tree(root: Path) -> None:
    """Друкує структуру директорії у вигляді 'ялинки'."""
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        indent = "    " * (len(rel.parts) - 1)
        prefix = "└── " if path.is_file() else "📂 "
        print(f"{indent}{prefix}{rel.name}")


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)

    # Якщо треба створити тестову теку
    if args.create_test:
        base = Path.cwd()
        source = create_test_directory(base)
    else:
        if not args.source_dir:
            print("Помилка: потрібно вказати source_dir або використати --create-test")
            return 1
        source = args.source_dir.resolve()

    dest = args.dest_dir.resolve()

    if not source.exists() or not source.is_dir():
        logging.error(f"Невірна вихідна директорія: {source}")
        return 1

    dest.mkdir(parents=True, exist_ok=True)

    processed = 0
    for file_path in iter_files_recursively(source, skip=dest):
        target_dir = place_for(file_path, dest)
        target_dir.mkdir(parents=True, exist_ok=True)
        final_path = safe_dest_path(target_dir, file_path)
        copy_or_move(file_path, final_path, move=args.move)
        processed += 1

    logging.info(f"Готово. Опрацьовано файлів: {processed}")

    if args.print_tree:
        print(f"\nСтруктура папки {dest}:")
        print_tree(dest)

    return 0


if __name__ == "__main__":
    sys.exit(main())

# python task_1.py --create-test --print-tree
