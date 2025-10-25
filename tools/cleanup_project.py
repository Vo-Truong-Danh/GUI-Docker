import argparse
import fnmatch
import json
import os
import shutil
from pathlib import Path


DEFAULT_PRESETS = {
    "patterns": [
        # Build and cache artifacts
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/.ruff_cache/**",
        "**/.cache/**",
        # Logs and temp
        "**/*.log",
        "**/*.tmp",
        "**/tmp/**",
        # Reports and large one-off docs
        "**/*SUMMARY*.md",
        "**/*REPORT*.md",
        "**/*COMPLETION*.md",
        "**/*COMPLETE*.md",
        "**/*FINAL*.md",
        "**/*QUICK*START*.md",
        "**/*QUICK*REFERENCE*.md",
        "**/*GUIDE*.md",
        "**/*CHANGELOG*.md",
        "**/*OPTIMIZATION*.md",
        "**/*FEATURES*.md",
        "**/*README*FIX*.md",
        "**/README_FIX_*.md",
        # Generated HTML previews
        "**/*.html",
        # Tests and experiments (optional — can be disabled via allowlist)
        "**/test_*.py",
        "**/tests/**",
        "**/TEST_*.py",
        # Helper scripts duplicates
        "**/*.bat",
        "**/*.ps1",
    ],
    "allowlist": [
        # Core keepers (never delete)
        ".git/**",
        "requirements.txt",
        "run_spark_gui/requirements_ai.txt",
        "docker-compose.yml",
        "README.md",
        "run_spark_gui/README.md",
        "main.py",
        "run_spark_gui/main.py",
        # Source trees
        "run_spark_gui/**",
        "spark_jobs/**",
        # Configs
        "**/*.json",
        "**/*.yaml",
        "**/*.yml",
    ],
}


def load_presets(presets_path: Path | None) -> dict:
    if presets_path and presets_path.exists():
        with presets_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults (user overrides/extends)
        merged = {
            "patterns": list(dict.fromkeys(DEFAULT_PRESETS["patterns"] + data.get("patterns", []))),
            "allowlist": list(dict.fromkeys(DEFAULT_PRESETS["allowlist"] + data.get("allowlist", []))),
        }
        return merged
    return DEFAULT_PRESETS


def path_matches_any(path: Path, patterns: list[str]) -> bool:
    # Normalize to posix for pattern matching consistency
    p = path.as_posix()
    for pat in patterns:
        if fnmatch.fnmatch(p, pat):
            return True
    return False


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip .git early
        if ".git" in dirpath.split(os.sep):
            continue
        for name in filenames:
            yield Path(dirpath) / name


def should_keep(file_path: Path, allowlist: list[str]) -> bool:
    # Keep if matches allowlist
    return path_matches_any(file_path, allowlist)


def plan_cleanup(root: Path, patterns: list[str], allowlist: list[str]):
    candidates: list[Path] = []
    for f in iter_files(root):
        # Always keep allowlisted
        if should_keep(f, allowlist):
            continue
        if path_matches_any(f, patterns):
            candidates.append(f)
    return candidates


def archive_files(files: list[Path], root: Path, archive_dir: Path):
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved: list[tuple[Path, Path]] = []
    for f in files:
        rel = f.relative_to(root)
        dest = archive_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), str(dest))
        moved.append((f, dest))
    return moved


def delete_files(files: list[Path]):
    deleted: list[Path] = []
    failed: list[tuple[Path, str]] = []
    truncated: list[Path] = []
    for f in files:
        try:
            f.unlink(missing_ok=True)
            deleted.append(f)
            continue
        except IsADirectoryError:
            try:
                shutil.rmtree(f, ignore_errors=True)
                deleted.append(f)
                continue
            except Exception as e:  # pragma: no cover
                failed.append((f, str(e)))
                continue
        except (PermissionError, OSError) as e:
            # Best-effort: try to truncate log files if deletion blocked
            if f.suffix.lower() == ".log":
                try:
                    with open(f, "w", encoding="utf-8") as fh:
                        fh.truncate(0)
                    truncated.append(f)
                    continue
                except Exception as e2:  # still locked exclusively
                    failed.append((f, f"truncate_failed: {e2}"))
                    continue
            failed.append((f, str(e)))
            continue
    return deleted, failed, truncated


def summarize(files: list[Path]):
    from collections import Counter
    cnt = Counter(p.suffix.lower() for p in files)
    total = len(files)
    lines = [f"Total candidates: {total}"]
    for ext, n in cnt.most_common():
        key = ext or "<no-ext>"
        lines.append(f"  {key}: {n}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Project cleanup tool (safe by default)")
    parser.add_argument("--root", default=".", help="Project root (default: .)")
    parser.add_argument("--presets", default="cleanup_presets.json", help="Custom presets JSON (optional)")
    parser.add_argument("--apply", action="store_true", help="Apply deletion (otherwise dry-run)")
    parser.add_argument("--archive", action="store_true", help="Archive instead of delete (folder: ./.archive)")
    parser.add_argument("--archive-dir", default=".archive", help="Archive folder path")
    parser.add_argument("--include-tests", action="store_true", help="Include tests in cleanup (off by default)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    presets_path = Path(args.presets)
    presets = load_presets(presets_path if presets_path.exists() else None)

    patterns = presets["patterns"].copy()
    allowlist = presets["allowlist"].copy()

    if not args.include_tests:
        # Remove test patterns when the flag is not set
        patterns = [
            p for p in patterns
            if not (p.startswith("**/test_") or "/tests/" in p or p.startswith("**/TEST_"))
        ]

    candidates = plan_cleanup(root, patterns, allowlist)

    print("Cleanup plan (dry-run by default):")
    print(summarize(candidates))
    # Show up to 50 entries for preview
    preview = candidates[:50]
    if preview:
        print("\nPreview (first 50):")
        for p in preview:
            print(f"  {p.relative_to(root)}")

    if not args.apply:
        print("\nNo changes made (dry-run). Use --apply to execute.")
        return

    if args.archive:
        archive_dir = (root / args.archive_dir).resolve()
        moved = archive_files(candidates, root, archive_dir)
        print(f"\nArchived {len(moved)} items to {archive_dir}")
    else:
        deleted, failed, truncated = delete_files(candidates)
        print(f"\nDeleted {len(deleted)} items.")
        if truncated:
            print(f"Truncated {len(truncated)} log files (in use):")
            for p in truncated[:10]:
                print(f"  {p}")
        if failed:
            print(f"Failed to delete {len(failed)} items (likely in use):")
            for p, err in failed[:10]:
                print(f"  {p} -> {err}")


if __name__ == "__main__":
    main()
