# 파일명: check_binary_duplicates.py
# 실행 위치: /app 에서 실행하면 됩니다.
# 사용법: python check_binary_duplicates.py

import os
import hashlib
from pathlib import Path
from collections import defaultdict
import argparse

def compute_sha256(file_path):
    """파일의 SHA256 해시를 계산합니다."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_duplicates(directory):
    """지정된 디렉토리 내 바이너리 파일들의 중복을 확인합니다."""
    path = Path(directory)
    if not path.is_dir():
        print(f"디렉토리가 존재하지 않습니다: {directory}")
        return

    print(f"\n대상 디렉토리: {path.resolve()}")
    print("파일 스캔 중...\n")

    # 파일 정보 수집: (파일명, 크기, 해시)
    file_info = []
    for file in path.iterdir():
        if file.is_file():
            size = file.stat().st_size
            hash_val = compute_sha256(file)
            file_info.append((file.name, size, hash_val))

    total_files = len(file_info)
    print(f"총 파일 수: {total_files}개\n")

    # 크기별 그룹화 → 같은 크기끼리만 해시 비교
    size_groups = defaultdict(list)
    for name, size, h in file_info:
        size_groups[size].append((name, h))

    duplicate_groups = []
    unique_count = 0

    for size, items in size_groups.items():
        if len(items) == 1:
            unique_count += 1
            continue

        # 같은 크기 내에서 해시별 그룹화
        hash_groups = defaultdict(list)
        for name, h in items:
            hash_groups[h].append(name)

        # 중복이 있는 그룹만 수집
        for h, names in hash_groups.items():
            if len(names) > 1:
                duplicate_groups.append((size, len(names), names))
            else:
                unique_count += 1

    # 결과 출력
    print(f"중복 없는 고유 파일 수: {unique_count}개")
    print(f"중복된 그룹 수: {len(duplicate_groups)}개")
    print(f"중복으로 인해 절약 가능한 파일 수: {total_files - unique_count - len(duplicate_groups)}개\n")

    if duplicate_groups:
        print("중복된 파일 그룹 목록 (크기 → 개수 → 파일명들):")
        print("-" * 80)
        for size, count, names in sorted(duplicate_groups, key=lambda x: -x[1]):
            print(f"크기: {size:,} bytes | 중복 개수: {count}")
            for name in names:
                print(f"  - {name}")
            print()
    else:
        print("중복된 파일이 없습니다! 모든 파일이 고유합니다.")

    # 중복 비율 요약
    dup_ratio = (total_files - unique_count) / total_files * 100 if total_files > 0 else 0
    print(f"중복 비율: {dup_ratio:.2f}% (중복 파일 수 / 전체 파일 수)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="바이너리 파일 중복 확인 스크립트")
    parser.add_argument("--dir", default="/app/binaries/aarch64/O0/nostrip",
                        help="확인할 디렉토리 경로 (기본값: /app/binaries/aarch64/O0/nostrip)")
    args = parser.parse_args()

    check_duplicates(args.dir)