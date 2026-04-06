# Lua Custom Engine Generator

`Lua Custom Engine Generator`는 원본 Lua 소스 코드를 기반으로 다양한 커스텀 Lua 엔진 변형을 대량 생성하기 위한 연구용 파이프라인입니다.

이 프로젝트는 Lua 인터프리터를 하나의 고정된 타겟으로 다루지 않고, 특정 소스 위치에 제어된 변형을 삽입하고, 여러 템플릿 조합을 적용한 뒤, 그 결과를 바이너리로 빌드하는 흐름을 제공합니다. 목적은 서로 유사하지만 완전히 같지는 않은 Lua 엔진 바이너리 집합을 체계적으로 만들어내는 것이며, 이는 차후 더 큰 LLM 기반 프로젝트를 위한 첫 단계로 볼 수 있습니다.

## 이 프로젝트가 하는 일

이 프로젝트는 다음 작업을 수행합니다.

- 원본 Lua 소스 코드를 입력으로 사용
- 샘플별 작업 디렉토리로 소스 복사
- 미리 지정한 마커 위치에 템플릿 코드 삽입
- 어떤 패치가 적용되었는지 로그로 기록
- 여러 아키텍처와 최적화 옵션으로 크로스 컴파일 수행
- 생성된 결과에 대해 중복 확인 및 패치 분포 요약 지원

즉, 단순한 빌드 스크립트가 아니라, 변형된 Lua 엔진 소스 생성기이자 바이너리 생산 파이프라인입니다.

## 왜 필요한가

바이너리 분석이나 리버스 엔지니어링 관련 실험에서는 서로 관련은 있지만 동일하지 않은 바이너리 집합이 중요할 때가 많습니다. 단일 소스, 단일 빌드 설정만으로는 변형 폭이 제한적이기 때문에, 이 프로젝트는 소스 코드 단계에서부터 제어된 다양성을 만들어내는 데 초점을 둡니다.

이 프로젝트는 다음과 같은 목적에 유용합니다.

- 실험용 바이너리 코퍼스 구축
- 소스 레벨 변형이 결과 바이너리에 어떤 차이를 만드는지 관찰
- 특정 코드 변화가 컴파일 이후에도 어떤 형태로 남는지 분석
- 차후 LLM 기반 실험을 위한 초기 데이터 생성 단계 구성

## 핵심 아이디어

이 프로젝트의 핵심은 마커 기반 소스 패치 방식입니다.

Lua 소스 파일 내부에 특정 마커 주석을 넣어두고, 생성 단계에서 해당 위치를 찾아 템플릿 코드로 교체합니다. 이때 적용되는 템플릿은 다음과 같은 범주로 나뉩니다.

- decryptor
- stream decryptor
- dummy logic
- opcode remap
- wrapper registration

이 패치 위치와 생성 정책은 [`config.yaml`](/Users/test2000/Desktop/01_project/01_AI_Project/03_Lua_Mapper/Lua_custom_engine_generator/config.yaml)에 정리되어 있어, 생성 로직과 실험 설정이 분리되어 있습니다. 덕분에 스크립트 자체를 크게 수정하지 않고도 실험 조건을 반복하거나 확장하기 쉽습니다.

## 폴더 구조

```text
Lua_custom_engine_generator/
├── config.yaml
├── docker-compose.yml
├── dockerfile
├── requirements.txt
├── engine_templates/
│   ├── decryptors/
│   ├── streamdecryptors/
│   ├── dummy/
│   ├── remap/
│   └── wrappers/
├── generators/
│   ├── 03_generate_custom_lua_engines.py
│   ├── 04_cross_compile_lua_engines.py
│   ├── 05_binaries_hash_check.py
│   └── 06_patch_log_summary.py
└── lua_source_tmp/
```

### 주요 디렉토리 설명

- `engine_templates/`: Lua 소스에 삽입될 템플릿 코드 모음
- `generators/`: 생성, 컴파일, 점검을 수행하는 스크립트 모음
- `lua_source_tmp/`: 원본 Lua 소스 아카이브 및 패치 대상 소스 보관 위치
- `generated_lua_custom/`: 생성된 커스텀 Lua 소스 결과물
- `binaries/`: 최종 컴파일된 바이너리와 빌드 로그 저장 위치

마지막 두 디렉토리는 실행 중 생성되는 결과물이며, 일반적으로 Git에는 포함하지 않습니다.

## 생성 흐름

현재 작업 흐름은 다음과 같이 구성되어 있습니다.

1. `config.yaml`에서 Lua 버전, 패치 위치, 생성 개수, 빌드 옵션 등을 설정
2. 원본 Lua 소스를 복사하여 샘플별 커스텀 소스 트리 생성
3. 마커 위치에 랜덤 또는 설정 기반 템플릿 적용
4. 생성된 소스를 여러 빌드 조건으로 크로스 컴파일
5. 결과 바이너리에 대해 중복 여부와 패치 통계 확인

각 샘플에는 `patch_log.json`이 함께 저장되므로, 어떤 변형이 어떤 소스와 바이너리에 반영되었는지 추적할 수 있습니다.

## 설정 파일

[`config.yaml`](/Users/test2000/Desktop/01_project/01_AI_Project/03_Lua_Mapper/Lua_custom_engine_generator/config.yaml)은 이 프로젝트의 핵심 제어 파일입니다.

여기에는 다음 정보가 들어 있습니다.

- 사용할 Lua 버전
- 원본 소스 경로
- 생성 개수와 랜덤 시드
- 적용 가능한 변형 범주
- 파일별 마커 위치
- 아키텍처, 최적화 수준, strip 여부 등 빌드 옵션

즉, 이 파일 하나를 중심으로 실험 조건을 조절할 수 있게 설계되어 있습니다.

## 실행 환경

이 프로젝트는 Docker 기반 환경을 포함하고 있어 재현 가능한 빌드를 목표로 합니다.

- [`dockerfile`](/Users/test2000/Desktop/01_project/01_AI_Project/03_Lua_Mapper/Lua_custom_engine_generator/dockerfile): Python 및 크로스 컴파일러 설치
- [`docker-compose.yml`](/Users/test2000/Desktop/01_project/01_AI_Project/03_Lua_Mapper/Lua_custom_engine_generator/docker-compose.yml): 프로젝트를 `/app`에 마운트하여 실행

필요한 Python 패키지는 최소한으로 유지되어 있습니다.

- `pyyaml`
- `tqdm`

## 빠른 시작

### 1. 컨테이너 빌드 및 실행

```bash
docker compose up -d --build
docker exec -it lua-cross-compiler bash
```

### 2. Python 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 커스텀 Lua 소스 생성

```bash
python generators/03_generate_custom_lua_engines.py
```

### 4. 생성된 소스 크로스 컴파일

```bash
python generators/04_cross_compile_lua_engines.py
```

### 5. 결과 점검

```bash
python generators/05_binaries_hash_check.py --dir /app/binaries/aarch64/O0/nostrip
python generators/06_patch_log_summary.py
```

## 현재 프로젝트 범위

현재 이 저장소는 다음 범위에 집중하고 있습니다.

- Lua 소스 커스터마이징
- 제어된 변형 생성
- 다양한 빌드 조건에서의 바이너리 생산
- 추적 가능한 패치 로그 관리

즉, 완성형 사용자 도구라기보다는, 더 큰 연구 흐름을 위한 첫 단계의 생성 파이프라인에 가깝습니다.

## 참고 사항

- 원본 Lua 소스 아카이브 및 대부분의 추출 소스는 Git에서 제외됩니다.
- 생성된 바이너리와 중간 빌드 산출물도 Git에 포함하지 않습니다.
- 재현 가능한 생성 과정을 위해 필요한 설정 파일과 패치 대상 소스만 저장소에 유지합니다.

## 라이선스 및 원본 소스

이 프로젝트는 공식 Lua 소스 코드를 기반으로 동작합니다. 원본 Lua의 배포 및 라이선스 관련 정보는 공식 Lua 프로젝트를 함께 확인하는 것을 권장합니다.
