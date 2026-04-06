# patch_log_summary.py
import json
from pathlib import Path
from collections import Counter

log_dir = Path("/app/generated_lua_custom")
logs = list(log_dir.glob("lua_547_*/patch_log.json"))

print(f"총 로그 파일 수: {len(logs)}개\n")

decryptor_counter = Counter()
dummy_counter = Counter()
remap_counter = Counter()
inline_count = 0

for log_path in logs:
    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for patch in data.get("patches", []):
        cat = patch.get("category")
        if cat == "decryptor":
            tpl = patch.get("template_name", "unknown")
            decryptor_counter[tpl] += 1
            if patch.get("inline_chosen"):
                inline_count += 1
        elif cat == "dummy":
            lvl = patch.get("template_name", "unknown")
            dummy_counter[lvl] += 1
        elif cat == "remap":
            lvl = patch.get("template_name", "unknown")
            remap_counter[lvl] += 1

print("=== Decryptor 통계 ===")
for k, v in decryptor_counter.most_common():
    print(f"{k:15}: {v}회")
print(f"인라인 적용 비율: {inline_count / (inline_count + sum(decryptor_counter.values())) * 100:.1f}% (예상 70%)")
print(f"inline {inline_count} sum:{(decryptor_counter.values())}")
print("\n=== Dummy 통계 ===")
for k, v in dummy_counter.most_common():
    print(f"{k:15}: {v}회")

print("\n=== Remap 통계 ===")
for k, v in remap_counter.most_common():
    print(f"{k:15}: {v}회")

print(f"\n총 패치 적용 횟수: {sum(decryptor_counter.values()) + sum(dummy_counter.values()) + sum(remap_counter.values())}")