# generators/04_build_vanilla_lua_engines.py
from __future__ import annotations

import argparse
import glob
import multiprocessing as mp
import os
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple


DEFAULT_BASE_DIR = Path(os.environ.get("LUA_BUILD_BASE_DIR", "/app"))
DEFAULT_VANILLA_SRC_DIR = "lua_source_vanilla"
DEFAULT_ARCHIVE_DIR = "lua_source_tmp"

COMPILERS = {
    "x86_64": "x86_64-linux-gnu-gcc",
    "aarch64": "aarch64-linux-gnu-gcc",
}

BASE_CFLAGS = [
    "-Wall",
    "-Wextra",
    "-Wno-format",
    "-w",
    "-Wno-unused-result",
    "-Wno-deprecated-declarations",
    "-Wno-all",
    "-Wno-unused-variable",
    "-Wno-unused-parameter",
    "-Wno-incompatible-pointer-types",
    "-DLUA_COMPAT_5_3",
    "-DLUA_COMPAT_5_2",
    "-I.",
    "-I./src",
]


def version_to_tag(version: str) -> str:
    return f"lua_{version.replace('.', '')}"


def parse_csv_or_all(raw_value: str, allowed_values: Iterable[str]) -> List[str]:
    allowed = list(allowed_values)
    if raw_value == "all":
        return allowed
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    invalid = [value for value in values if value not in allowed]
    if invalid:
        raise ValueError(f"invalid values: {invalid}; allowed values: {allowed}")
    return values


def parse_strip_modes(raw_value: str) -> List[bool]:
    if raw_value == "both":
        return [True, False]
    if raw_value == "strip":
        return [True]
    if raw_value == "nostrip":
        return [False]
    raise ValueError("--strip-mode must be one of: strip, nostrip, both")


def load_config(base_dir: Path) -> dict:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required. Run: pip install -r requirements.txt") from exc

    config_path = base_dir / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_source_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute() and str(path).startswith("/app/"):
        return base_dir / path.relative_to("/app")
    return path if path.is_absolute() else base_dir / path


def vanilla_source_root(base_dir: Path, vanilla_source_dir: Path, version: str) -> Path:
    root = vanilla_source_dir if vanilla_source_dir.is_absolute() else base_dir / vanilla_source_dir
    return root / f"lua-{version}"


def archive_path(base_dir: Path, archive_dir: Path, version: str) -> Path:
    root = archive_dir if archive_dir.is_absolute() else base_dir / archive_dir
    return root / f"lua-{version}.tar.gz"


def prepare_vanilla_source(
    base_dir: Path,
    vanilla_source_dir: Path,
    archive_dir: Path,
    version: str,
) -> Path:
    src_root = vanilla_source_root(base_dir, vanilla_source_dir, version)
    if src_root.exists():
        return src_root

    archive = archive_path(base_dir, archive_dir, version)
    if not archive.exists():
        raise FileNotFoundError(f"vanilla Lua archive not found: {archive}")

    output_root = src_root.parent
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Extracting vanilla Lua {version}: {archive} -> {output_root}")
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(output_root)

    if not src_root.exists():
        raise FileNotFoundError(f"expected extracted source tree was not created: {src_root}")
    return src_root


def collect_source_files(src_root: Path) -> List[str]:
    source_files = glob.glob(str(src_root / "src" / "*.c"))
    return [f for f in source_files if Path(f).name != "luac.c"]


def compile_one(
    src_root: Path,
    version: str,
    arch: str,
    opt: str,
    strip: bool,
    bin_dir: Path,
    log_dir: Path,
) -> None:
    compiler = COMPILERS[arch]
    strip_mode = "stripped" if strip else "nostrip"
    version_tag = version_to_tag(version)

    output_dir = bin_dir / f"Lua_{version.replace('.', '')}" / arch / opt / strip_mode
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{version_tag}_vanilla"

    source_files = collect_source_files(src_root)
    if not source_files:
        print(f"source files not found: {src_root / 'src'}")
        return

    cmd = [
        compiler,
        "-w",
        *BASE_CFLAGS,
        f"-{opt}",
        "-o",
        str(output_file),
        *source_files,
        "-lm",
        "-ldl",
    ]

    if strip:
        cmd.append("-s")

    log_filename = f"{version_tag}_{arch}_{opt}_{strip_mode}.log"
    log_path = log_dir / log_filename

    try:
        result = subprocess.run(
            cmd,
            cwd=str(src_root),
            capture_output=True,
            text=True,
            timeout=120,
        )

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Build command: {' '.join(cmd)}\n")
            f.write(f"Return code: {result.returncode}\n")
            f.write(f"Source root: {src_root}\n")
            f.write(f"Output file: {output_file}\n")
            f.write(f"Exists: {output_file.exists()}\n\n")
            f.write("=== STDOUT ===\n")
            f.write(result.stdout + "\n\n")
            f.write("=== STDERR ===\n")
            f.write(result.stderr + "\n")

        if result.returncode == 0 and output_file.exists():
            print(f"OK | {version:5} | {arch:8} | {opt:3} | {strip_mode:8} | {output_file}")
        else:
            print(f"FAIL | {version:5} | {arch:8} | {opt:3} | {strip_mode:8} | rc={result.returncode}")
            print(f"  log: {log_path}")
            print(f"  stderr: {result.stderr[:300]}")
    except Exception as exc:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Exception: {exc}\n")
        print(f"EXCEPTION | {version:5} | {arch:8} | {opt:3} | {strip_mode:8} | {str(exc)[:120]}")
        print(f"  log: {log_path}")


def build_tasks(args: argparse.Namespace, config: dict) -> List[Tuple[Path, str, str, str, bool, Path, Path]]:
    source_paths = config.get("source_paths", {})
    available_versions = [str(v) for v in source_paths.keys()]
    default_versions = [str(v) for v in config.get("lua_versions", available_versions)]
    versions = default_versions if args.versions == "all" else parse_csv_or_all(args.versions, available_versions)

    configured_archs = config.get("binary", {}).get("architectures", list(COMPILERS))
    archs = parse_csv_or_all(args.archs, configured_archs)

    configured_opts = config.get("binary", {}).get("optimization_levels", ["O0", "O1", "O2", "O3", "Os"])
    opts = parse_csv_or_all(args.opts, configured_opts)

    strip_modes = parse_strip_modes(args.strip_mode)

    tasks = []
    for version in versions:
        if args.use_config_source_paths:
            src_root = resolve_source_path(source_paths[version], args.base_dir)
        else:
            src_root = prepare_vanilla_source(
                args.base_dir,
                args.vanilla_source_dir,
                args.archive_dir,
                version,
            )
        if not src_root.exists():
            raise FileNotFoundError(f"source path does not exist for Lua {version}: {src_root}")
        for arch in archs:
            for opt in opts:
                for strip in strip_modes:
                    tasks.append((src_root, version, arch, opt, strip, args.output_dir, args.log_dir))
    return tasks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build vanilla Lua binaries from clean tarball extracts")
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR, help="Project base dir inside Docker")
    parser.add_argument("--versions", default="all", help="Comma-separated Lua versions from config, or all")
    parser.add_argument("--archs", default="all", help="Comma-separated architectures from config, or all")
    parser.add_argument("--opts", default="all", help="Comma-separated optimization levels from config, or all")
    parser.add_argument("--strip-mode", default="both", choices=["strip", "nostrip", "both"])
    parser.add_argument("--jobs", type=int, default=None, help="Parallel build jobs")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory")
    parser.add_argument(
        "--vanilla-source-dir",
        type=Path,
        default=Path(DEFAULT_VANILLA_SRC_DIR),
        help="Clean extracted vanilla Lua source directory",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path(DEFAULT_ARCHIVE_DIR),
        help="Directory containing lua-<version>.tar.gz archives",
    )
    parser.add_argument(
        "--use-config-source-paths",
        action="store_true",
        help="Use config.yaml source_paths directly instead of lua_source_vanilla",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.base_dir = args.base_dir.resolve()
    args.output_dir = args.output_dir or (args.base_dir / "binaries_vanilla")
    args.log_dir = args.output_dir / "build_logs"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(args.base_dir)
    jobs = args.jobs or int(config.get("binary", {}).get("build_parallel", 8))
    tasks = build_tasks(args, config)

    print(f"[{datetime.now()}] === Vanilla Lua build start ===")
    print(f"Base dir: {args.base_dir}")
    print(f"Vanilla source dir: {args.vanilla_source_dir}")
    print(f"Output dir: {args.output_dir}")
    print(f"Tasks: {len(tasks)}")

    if not tasks:
        print("No build tasks found.")
        return

    with mp.Pool(processes=jobs) as pool:
        pool.starmap(compile_one, tasks)

    print(f"[{datetime.now()}] === Vanilla Lua build done ===")
    print(f"Binaries: {args.output_dir}")
    print(f"Logs: {args.log_dir}")


if __name__ == "__main__":
    main()
