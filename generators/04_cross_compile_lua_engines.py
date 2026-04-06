# generators/02_build_custom.py
import os
import subprocess
from pathlib import Path
import yaml
from datetime import datetime
import multiprocessing as mp
import glob

# ====================== 설정 ======================
BASE_DIR = Path("/app")
CONFIG_PATH = BASE_DIR / "config.yaml"
GENERATED_SRC_DIR = BASE_DIR / "generated_lua_custom"
BIN_DIR = BASE_DIR / "binaries"
BIN_DIR.mkdir(parents=True, exist_ok=True)

# 로그 디렉토리 추가
LOG_DIR = BIN_DIR / "build_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

config = yaml.safe_load(open(CONFIG_PATH, encoding="utf-8"))
OPT_LEVELS = config.get("binary", {}).get("optimization_levels", ["O0", "O1", "O2", "O3", "Os"])
ARCHS = config.get("binary", {}).get("architectures", ["x86_64", "aarch64"])
STRIP_OPTIONS = config.get("binary", {}).get("strip_symbols", [True, False])
BUILD_PARALLEL = config.get("binary", {}).get("build_parallel", 8)

COMPILERS = {
    "x86_64": "x86_64-linux-gnu-gcc",
    "aarch64": "aarch64-linux-gnu-gcc"
}

# Lua 빌드 기본 플래그
BASE_CFLAGS = [
    "-Wall", "-Wextra",
    "-Wno-format",
    "-w",                                   # 모든 warning을 에러로 취급하지 않음
    "-Wno-unused-result",                   # tmpnam 경고 억제
    "-Wno-deprecated-declarations",         # deprecated 함수 경고 억제
    "-Wno-all",
    "-Wno-unused-variable",
    "-Wno-unused-parameter",
    "-Wno-incompatible-pointer-types",
    "-Wno-deprecated-declarations",
    "-Wno-unused-result",
    "-DLUA_COMPAT_5_3", "-DLUA_COMPAT_5_2",
    "-I.", "-I./src"
]

def compile_one(src_root: Path, arch: str, opt: str, strip: bool):
    compiler = COMPILERS[arch]
    output_dir = BIN_DIR / arch / opt / ("stripped" if strip else "nostrip")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"lua_{src_root.name}"

    # src/*.c 파일 수집 + luac.c 제외
    source_files = glob.glob(str(src_root / "src" / "*.c"))
    source_files = [f for f in source_files if "luac.c" not in Path(f).name]

    if not source_files:
        print(f"❌ 소스 파일 없음: {src_root / 'src'}")
        return

    cmd = [
        compiler,
        '-w',
        *BASE_CFLAGS,
        f"-{opt}",
        "-o", str(output_file),
        *source_files,
        "-lm"
    ]

    if strip:
        cmd.append("-s")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(src_root),
            capture_output=True,
            text=True,
            timeout=120
        )

        # 로그 파일 저장 (성공/실패 모두)
        strip_str = "strip" if strip else "nostrip"
        log_filename = f"{src_root.name}_{arch}_{opt}_{strip_str}.log"
        log_path = LOG_DIR / log_filename

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Build command: {' '.join(cmd)}\n")
            f.write(f"Return code: {result.returncode}\n")
            f.write(f"Output file: {output_file}\n")
            f.write(f"Exists: {output_file.exists()}\n\n")
            f.write("=== STDOUT ===\n")
            f.write(result.stdout + "\n\n")
            f.write("=== STDERR ===\n")
            f.write(result.stderr + "\n")

        # 콘솔 출력 (기존 로직 그대로)
        if result.returncode == 0 and output_file.exists():
            print(f"✅ 성공 | {arch:8} | {opt:3} | {'strip' if strip else 'nostrip'} | {src_root.name}")
            print(f"   로그 저장됨: {log_path}")
        else:
            print(f"❌ 실패 | {arch:8} | {opt:3} | {src_root.name} → returncode={result.returncode}")
            print(f"   에러: {result.stderr[:300]}")
            print(f"   로그 저장됨: {log_path}")

    except Exception as e:
        print(f"❌ 예외 | {arch:8} | {opt:3} | {src_root.name} → {str(e)[:100]}")
        # 예외 발생 시에도 로그 저장
        log_path = LOG_DIR / f"{src_root.name}_{arch}_{opt}_{'strip' if strip else 'nostrip'}_EXCEPTION.log"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Exception: {str(e)}\n")
        print(f"   예외 로그 저장됨: {log_path}")

# ====================== 메인 실행 ======================
print(f"[{datetime.now()}] === Lua 커스텀 엔진 대량 컴파일 시작 ===")
src_roots = list(GENERATED_SRC_DIR.glob("lua_547_*"))
print(f"발견된 소스 폴더: {len(src_roots)}개")
print(f"예상 총 바이너리: 약 {len(src_roots) * len(ARCHS) * len(OPT_LEVELS) * len(STRIP_OPTIONS)}개\n")

tasks = []
for src_root in src_roots:
    for arch in ARCHS:
        for opt in OPT_LEVELS:
            for strip in STRIP_OPTIONS:
                tasks.append((src_root, arch, opt, strip))

print(f"총 작업량: {len(tasks)}개\n")

with mp.Pool(processes=BUILD_PARALLEL) as pool:
    pool.starmap(compile_one, tasks)

print(f"\n[{datetime.now()}] === 전체 컴파일 완료 ===")
print(f"바이너리 저장 위치: {BIN_DIR}")
print(f"빌드 로그 저장 위치: {LOG_DIR}")