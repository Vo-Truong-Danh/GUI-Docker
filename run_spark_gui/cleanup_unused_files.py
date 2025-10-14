import argparse
import os
import re
import sys
from pathlib import Path
import ast


EXCLUDE_DIR_NAMES = {
    '__pycache__',
    '.git',
    '.idea',
    '.vscode',
    'node_modules',
    'dist',
    'build',
    'logs',
    'backups',
}


def is_within_excluded(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    return any(part in EXCLUDE_DIR_NAMES for part in rel_parts)


def find_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob('*.py'):
        if is_within_excluded(p, root):
            continue
        files.append(p)
    return files


def parse_imports(py_file: Path) -> set[str]:
    try:
        source = py_file.read_text(encoding='utf-8')
    except Exception:
        return set()
    try:
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports


def build_module_path_index(root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for py in find_python_files(root):
        name = py.stem
        index.setdefault(name, py)
    return index


def traverse_used_graph(root: Path, entrypoints: list[Path]) -> set[Path]:
    module_index = build_module_path_index(root)
    used: set[Path] = set()
    stack: list[Path] = []

    def push(p: Path):
        if p and p.suffix == '.py' and p.exists() and p not in used:
            used.add(p)
            stack.append(p)

    for ep in entrypoints:
        push(ep)

    while stack:
        current = stack.pop()
        for imp in parse_imports(current):
            target = module_index.get(imp)
            if target and not is_within_excluded(target, root):
                push(target)

    return used


MD_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def collect_markdown_references(root: Path) -> set[Path]:
    referenced: set[Path] = set()
    md_and_text_files: list[Path] = []
    for ext in ('*.md', '*.markdown', '*.MD'):
        md_and_text_files.extend(root.rglob(ext))
    md_and_text_files.extend(root.rglob('*.py'))
    md_and_text_files.extend(root.rglob('*.txt'))

    for p in md_and_text_files:
        if is_within_excluded(p, root):
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for match in MD_LINK_PATTERN.finditer(content):
            target = match.group(1)
            if '://' in target:
                continue
            target_path = (p.parent / target).resolve()
            try:
                target_rel = target_path.relative_to(root)
            except ValueError:
                continue
            if target_path.exists():
                referenced.add(root / target_rel)
    return referenced


def list_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for ext in ('*.md', '*.markdown', '*.MD'):
        for p in root.rglob(ext):
            if is_within_excluded(p, root):
                continue
            files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description='Detect unused .py and .md files (report only).')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--entry', action='append', help='Entrypoint .py file(s) relative to root', default=[])
    parser.add_argument('--include-md', action='store_true', help='Include unused .md files as candidates')
    parser.add_argument('--dry-run', action='store_true', help='Report mode (no effect)')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    entrypoints: list[Path] = [(root / e).resolve() for e in args.entry] if args.entry else [root / 'run_spark_gui' / 'main.py']
    entrypoints = [ep for ep in entrypoints if ep.exists()]

    all_py = set(find_python_files(root))
    used_py = traverse_used_graph(root, entrypoints) if entrypoints else set()
    for ep in entrypoints:
        used_py.add(ep)
    unused_py = sorted(all_py - used_py)

    unused_md: list[Path] = []
    if args.include_md:
        all_md = set(list_markdown_files(root))
        referenced = collect_markdown_references(root)
        for name in ('README.md', 'INDEX.md'):
            p = root / name
            if p.exists():
                referenced.add(p)
        for p in list(all_md):
            try:
                rel = p.relative_to(root)
            except ValueError:
                continue
            if len(rel.parts) == 1:
                referenced.add(p)
        unused_md = sorted(all_md - referenced)

    print('=== Unused Python files (candidates) ===')
    for p in unused_py:
        print(p.relative_to(root))
    print(f'Total: {len(unused_py)}')

    if args.include_md:
        print('\n=== Unused Markdown files (candidates) ===')
        for p in unused_md:
            print(p.relative_to(root))
        print(f'Total: {len(unused_md)}')

    return 0


if __name__ == '__main__':
    sys.exit(main())

import argparse
import os
import re
import shutil
import sys
import time
from pathlib import Path
import ast


EXCLUDE_DIR_NAMES = {
    '__pycache__',
    '.git',
    '.idea',
    '.vscode',
    'node_modules',
    'dist',
    'build',
    'logs',
    'backups',
}


def is_within_excluded(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    return any(part in EXCLUDE_DIR_NAMES for part in rel_parts)


def find_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob('*.py'):
        if is_within_excluded(p, root):
            continue
        files.append(p)
    return files


def parse_imports(py_file: Path) -> set[str]:
    try:
        source = py_file.read_text(encoding='utf-8')
    except Exception:
        return set()
    try:
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports


def build_module_path_index(root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for py in find_python_files(root):
        name = py.stem
        index.setdefault(name, py)
    return index


def traverse_used_graph(root: Path, entrypoints: list[Path]) -> set[Path]:
    module_index = build_module_path_index(root)
    used: set[Path] = set()
    stack: list[Path] = []

    def push(p: Path):
        if p and p.suffix == '.py' and p.exists() and p not in used:
            used.add(p)
            stack.append(p)

    for ep in entrypoints:
        push(ep)

    while stack:
        current = stack.pop()
        for imp in parse_imports(current):
            target = module_index.get(imp)
            if target and not is_within_excluded(target, root):
                push(target)

    return used


MD_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def collect_markdown_references(root: Path) -> set[Path]:
    referenced: set[Path] = set()
    md_and_text_files: list[Path] = []
    for ext in ('*.md', '*.markdown', '*.MD'):
        md_and_text_files.extend(root.rglob(ext))
    md_and_text_files.extend(root.rglob('*.py'))
    md_and_text_files.extend(root.rglob('*.txt'))

    for p in md_and_text_files:
        if is_within_excluded(p, root):
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for match in MD_LINK_PATTERN.finditer(content):
            target = match.group(1)
            if '://' in target:
                continue
            target_path = (p.parent / target).resolve()
            try:
                target_rel = target_path.relative_to(root)
            except ValueError:
                continue
            if target_path.exists():
                referenced.add(root / target_rel)
    return referenced


def list_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for ext in ('*.md', '*.markdown', '*.MD'):
        for p in root.rglob(ext):
            if is_within_excluded(p, root):
                continue
            files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description='Detect unused .py and .md files.')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--entry', action='append', help='Entrypoint .py file(s) relative to root', default=[])
    parser.add_argument('--include-md', action='store_true', help='Include unused .md files as candidates')
    parser.add_argument('--dry-run', action='store_true', help='Only list candidates, do not delete')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    entrypoints: list[Path] = [(root / e).resolve() for e in args.entry] if args.entry else [root / 'run_spark_gui' / 'main.py']
    entrypoints = [ep for ep in entrypoints if ep.exists()]

    all_py = set(find_python_files(root))
    used_py = traverse_used_graph(root, entrypoints) if entrypoints else set()
    for ep in entrypoints:
        used_py.add(ep)
    unused_py = sorted(all_py - used_py)

    unused_md: list[Path] = []
    if args.include_md:
        all_md = set(list_markdown_files(root))
        referenced = collect_markdown_references(root)
        # Keep root README/INDEX
        for name in ('README.md', 'INDEX.md'):
            p = root / name
            if p.exists():
                referenced.add(p)
        # Keep other root .md by default (conservative)
        for p in list(all_md):
            try:
                rel = p.relative_to(root)
            except ValueError:
                continue
            if len(rel.parts) == 1:
                referenced.add(p)
        unused_md = sorted(all_md - referenced)

    print('=== Unused Python files (candidates) ===')
    for p in unused_py:
        print(p.relative_to(root))
    print(f'Total: {len(unused_py)}')

    if args.include_md:
        print('\n=== Unused Markdown files (candidates) ===')
        for p in unused_md:
            print(p.relative_to(root))
        print(f'Total: {len(unused_md)}')

    if not args.dry_run:
        print('\nNote: This temporary checker only reports. No deletions performed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

import argparse
import os
import re
import shutil
import sys
import time
from pathlib import Path
import ast


EXCLUDE_DIR_NAMES = {
    '__pycache__',
    '.git',
    '.idea',
    '.vscode',
    'node_modules',
    'dist',
    'build',
    'logs',
    'backups',
}


def is_within_excluded(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    return any(part in EXCLUDE_DIR_NAMES for part in rel_parts)


def find_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob('*.py'):
        if is_within_excluded(p, root):
            continue
        files.append(p)
    return files


def parse_imports(py_file: Path) -> set[str]:
    """Return a set of module import names found in file (top-level imports)."""
    try:
        source = py_file.read_text(encoding='utf-8')
    except Exception:
        return set()
    try:
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports


def module_name_from_path(root: Path, py_path: Path) -> str:
    rel = py_path.relative_to(root).with_suffix('')
    return '.'.join(rel.parts)


def build_module_path_index(root: Path) -> dict[str, Path]:
    """Map top-level module names to file paths within project."""
    index: dict[str, Path] = {}
    for py in find_python_files(root):
        # index only top-level module name for quick resolution
        name = py.stem
        index.setdefault(name, py)
    return index


def resolve_import_to_path(import_name: str, module_index: dict[str, Path]) -> Path | None:
    return module_index.get(import_name)


def traverse_used_graph(root: Path, entrypoints: list[Path]) -> set[Path]:
    module_index = build_module_path_index(root)
    used: set[Path] = set()
    stack: list[Path] = []

    def push(p: Path):
        if p and p.suffix == '.py' and p.exists() and p not in used:
            used.add(p)
            stack.append(p)

    for ep in entrypoints:
        push(ep)

    while stack:
        current = stack.pop()
        for imp in parse_imports(current):
            target = resolve_import_to_path(imp, module_index)
            if target and not is_within_excluded(target, root):
                push(target)

    return used


MD_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def collect_markdown_references(root: Path) -> set[Path]:
    referenced: set[Path] = set()
    md_and_text_files: list[Path] = []
    for ext in ('*.md', '*.markdown', '*.MD'):
        md_and_text_files.extend(root.rglob(ext))
    # Also scan .py and .txt for explicit references
    md_and_text_files.extend(root.rglob('*.py'))
    md_and_text_files.extend(root.rglob('*.txt'))

    for p in md_and_text_files:
        if is_within_excluded(p, root):
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for match in MD_LINK_PATTERN.finditer(content):
            target = match.group(1)
            if '://' in target:
                continue
            target_path = (p.parent / target).resolve()
            try:
                target_rel = target_path.relative_to(root)
            except ValueError:
                continue
            if target_path.exists():
                referenced.add(root / target_rel)
    return referenced


def list_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for ext in ('*.md', '*.markdown', '*.MD'):
        for p in root.rglob(ext):
            if is_within_excluded(p, root):
                continue
            files.append(p)
    return files


def backup_files(files: list[Path], root: Path, backup_root: Path) -> None:
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    destination_root = backup_root / f'cleanup_{timestamp}'
    for f in files:
        rel = f.relative_to(root)
        dest = destination_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)


def delete_files(files: list[Path]) -> None:
    for f in files:
        try:
            f.unlink(missing_ok=True)
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description='Detect and remove unused .py and .md files safely.')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--entry', action='append', help='Entrypoint .py file(s) relative to root', default=[])
    parser.add_argument('--include-md', action='store_true', help='Include unused .md files as deletion candidates')
    parser.add_argument('--dry-run', action='store_true', help='Only list candidates, do not delete')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory root')
    parser.add_argument('--aggressive-md', action='store_true', help='Treat unreferenced .md as unused even if in root')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: Root not found: {root}")
        return 2

    # Determine entrypoints
    default_entries = [
        root / 'run_spark_gui' / 'main.py',
    ]
    entrypoints: list[Path] = []
    if args.entry:
        for e in args.entry:
            ep = (root / e).resolve()
            if ep.exists():
                entrypoints.append(ep)
    else:
        entrypoints = [ep for ep in default_entries if ep.exists()]

    if not entrypoints:
        print('WARN: No entrypoints found; Python usage analysis may be incomplete.')

    all_py = set(find_python_files(root))
    used_py = traverse_used_graph(root, entrypoints) if entrypoints else set()
    # Always consider entrypoints as used
    for ep in entrypoints:
        used_py.add(ep)

    unused_py = sorted(all_py - used_py)

    # Markdown analysis
    unused_md: list[Path] = []
    if args.include_md:
        all_md = set(list_markdown_files(root))
        referenced = collect_markdown_references(root)

        # Always consider README.md and INDEX.md as used
        for special in ('README.md', 'INDEX.md'):
            p = root / special
            if p.exists():
                referenced.add(p)

        if not args.aggressive_md:
            # Keep root-level .md by default unless explicitly referenced as unused
            for p in list(all_md):
                try:
                    rel = p.relative_to(root)
                except ValueError:
                    continue
                if len(rel.parts) == 1:
                    referenced.add(p)

        unused_md = sorted(all_md - referenced)

    print('=== Unused Python files (candidates) ===')
    for p in unused_py:
        print(p.relative_to(root))
    print(f'Total: {len(unused_py)}')

    if args.include_md:
        print('\n=== Unused Markdown files (candidates) ===')
        for p in unused_md:
            print(p.relative_to(root))
        print(f'Total: {len(unused_md)}')

    candidates: list[Path] = list(unused_py)
    if args.include_md:
        candidates.extend(unused_md)

    if args.dry_run:
        print('\nDry-run mode: no files deleted.')
        return 0

    if not candidates:
        print('OK: No unused files detected.')
        return 0

    backup_root = (root / args.backup_dir).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    print(f'Backing up {len(candidates)} files to: {backup_root}')
    backup_files(candidates, root, backup_root)
    print('Deleting candidates...')
    delete_files(candidates)
    print('OK: Deletion complete. A backup was created under backups/.')
    return 0


if __name__ == '__main__':
    sys.exit(main())


