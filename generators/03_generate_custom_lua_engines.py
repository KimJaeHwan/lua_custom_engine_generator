# generators/01_generate_lua_custom.py
import os
import shutil
import random
import yaml
import json
from pathlib import Path
from datetime import datetime

# ====================== 설정 ======================
BASE_DIR = Path("/app")
CONFIG_PATH = BASE_DIR / "config.yaml"
TEMPLATE_DIR = BASE_DIR / "engine_templates"
SOURCE_TMP = BASE_DIR / "lua_source_tmp"
OUTPUT_DIR = BASE_DIR / "generated_lua_custom"

config = yaml.safe_load(open(CONFIG_PATH, encoding="utf-8"))
random.seed(config["generation"]["seed"])
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_template(cat: str, name: str) -> str:
    p = TEMPLATE_DIR / cat / f"{name}.cpp"
    if not p.exists():
        raise FileNotFoundError(f"템플릿 파일 없음: {p}")
    return p.read_text(encoding="utf-8")


def copy_lua_source(version: str, index: int) -> Path:
    src_path = Path(config["source_paths"][version])
    dest_path = OUTPUT_DIR / f"lua_{version.replace('.', '')}_{index:04d}"
    if dest_path.exists():
        shutil.rmtree(dest_path)
    shutil.copytree(src_path, dest_path)
    return dest_path


def apply_patches(source_dir: Path, index: int, version: str):
    patch_logs = []  # 로깅용 리스트 초기화

    for category, files in config["patch_locations"].items():
        for file_name, patches in files.items():
            file_path = source_dir / "src" / file_name
            if not file_path.exists():
                print(f"파일 없음: {file_path}")
                continue

            content = file_path.read_text(encoding="utf-8")

            # patches가 리스트인지 확인
            patch_list = patches if isinstance(patches, list) else [patches]

            for idx, patch in enumerate(patch_list, 1):
                # marker 이름 가져오기
                marker = patch.get("marker", f"CUSTOM_{category.upper()}_CODE_{idx}")
                marker_str = f"// {{{{{marker}}}}}"
        
                # if marker_str not in content:
                #     print(f"마커 없음: {marker_str} in {file_path}")
                #     continue

                inline_chosen = False
                template_cat = None
                template_name = None
                used_marker_str = marker_str
                define_added = False

                # 카테고리별 랜덤 코드 선택
                if category == "decryptor":
                    inline_chosen = random.random() < config["customization"]["inline_chance"]
                    if(file_name == "lua.c"): 
                        inline_chosen = False # 함수 구현부는 반드시 lua.c에 구현되어 있어야 함
                    
                    print(f'File[{file_name}]inline chose{inline_chosen}\n')
                    if inline_chosen:
                        template_cat = "streamdecryptors"
                        template_name = random.choice(config["customization"]["decryptors"])
                        used_marker_str = f"// {{{{{marker}_STREAM}}}}"
                        marker_str = used_marker_str
                        # DEFINE 마커 치환
                        content = content.replace(
                            r"// {{DEFINE_CUSTOM_INLINE_1}}",
                            r"#define LUA_CUSTOM_INLINE true"
                        )
                        define_added = True
                    else:
                        template_cat = "decryptors"
                        template_name = random.choice(config["customization"]["decryptors"])

                    code = load_template(template_cat, template_name)

                elif category == "dummy":
                    level = random.choice(config["customization"]["dummy_levels"])
                    template_name = f"level{level}"
                    code = load_template("dummy", template_name)

                elif category == "remap":
                    level = random.choice(config["customization"]["remap_levels"])
                    template_name = f"level{level}"
                    code = load_template("remap", template_name)
                elif category == "wrappers":
                    wrapp = random.choice(config["customization"]["wrappers"])
                    code = load_template("wrappers", wrapp)
                else:
                    code = "// Unknown category\n"

                # 실제 치환
                content = content.replace(marker_str, code)

                # 로깅 데이터 추가
                log_entry = {
                    "category": category,
                    "file": file_name,
                    "marker": marker,
                    "used_marker_str": used_marker_str,
                    "template_category": template_cat,
                    "template_name": template_name,
                    "inline_chosen": inline_chosen,
                    "define_added": define_added if category == "decryptor" else None
                }
                patch_logs.append(log_entry)

            # 파일 저장
            file_path.write_text(content, encoding="utf-8")

    # 패치 로그 저장
    log_data = {
        "index": index,
        "lua_version": version,
        "generated_at": datetime.now().isoformat(),
        "patches": patch_logs
    }

    log_path = source_dir / "patch_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    print(f"Patch log saved: {log_path}")


# ====================== 메인 실행 ======================
print(f"[{datetime.now()}] Lua 커스텀 소스 생성 시작 ({config['generation']['num_test']}개)")

for i in range(config["generation"]["num_test"]):
    version = random.choice(config["lua_versions"])
    src_dir = copy_lua_source(version, i)
    apply_patches(src_dir, i, version)
    print(f"[{i+1:03d}/{config['generation']['num_test']}] 생성 완료: {version} → {src_dir}")

print(f"\n생성 완료! 위치: {OUTPUT_DIR}")
print("다음 단계: 02_build_custom.py로 빌드")