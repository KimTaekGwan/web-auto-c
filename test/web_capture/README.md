# Web Capture (웹 캡처)

웹페이지 캡처 모듈 - 다양한 디바이스 해상도에서 URL 목록을 자동으로 캡처합니다.

## 버전
- 현재 버전: 0.1.0

## 기능

- 다양한 디바이스 유형(데스크톱, 태블릿, 모바일)에서 캡처
- 병렬 처리로 빠른 캡처 속도
- 전체 페이지 또는 뷰포트만 캡처 옵션
- HTML 보고서 생성
- 메타데이터 저장 및 관리
- CLI 및 Python API 제공
- 로깅 및 오류 처리

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install
```

## 사용법

### CLI

```bash
# 단일 URL 캡처 (기본 데스크톱)
python -m web_capture.cli --url https://example.com

# URL 목록 파일에서 캡처
python -m web_capture.cli --file urls.txt

# 모든 디바이스에서 캡처
python -m web_capture.cli --url https://example.com --devices all

# 캡처 결과 보고서 생성
python -m web_capture.cli --url https://example.com --report

# 전체 페이지 캡처
python -m web_capture.cli --url https://example.com --full-page

# 추가 옵션 확인
python -m web_capture.cli --help
```

### Python API

```python
from web_capture import capture_multiple_pages
from web_capture.models.models import DeviceType, CaptureConfig

# 단일 URL, 모든 디바이스 유형
config = CaptureConfig(
    urls=["https://example.com"],
    devices=[DeviceType.DESKTOP, DeviceType.TABLET, DeviceType.MOBILE],
    output_dir="./my_captures",
    create_html_report=True
)

result = capture_multiple_pages(config)

# 결과 확인
print(f"성공: {result.success_count}, 실패: {result.error_count}")
print(f"출력 디렉토리: {result.output_dir}")
print(f"보고서: {result.report_file}")

# URL 목록 처리
urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net"
]

config = CaptureConfig(
    urls=urls,
    devices=[DeviceType.DESKTOP],
    parallel_count=5
)

result = capture_multiple_pages(config)
```

## 환경 변수 설정

다음 환경 변수를 통해 기본 설정을 변경할 수 있습니다:

| 환경 변수 | 설명 | 기본값 |
|-----------|------|--------|
| `WEB_CAPTURE_OUTPUT_DIR` | 캡처 이미지 저장 디렉토리 | `./captures` |
| `WEB_CAPTURE_LOG_DIR` | 로그 파일 저장 디렉토리 | `./logs` |
| `WEB_CAPTURE_LOG_LEVEL` | 로깅 레벨 | `INFO` |
| `WEB_CAPTURE_MAX_PARALLEL` | 최대 병렬 처리 수 | `3` |
| `WEB_CAPTURE_BROWSER_TYPE` | 브라우저 유형 | `chromium` |

## 설정 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `devices` | 캡처할 디바이스 유형 | `[DeviceType.DESKTOP]` |
| `output_dir` | 캡처 이미지 저장 디렉토리 | `./captures` |
| `wait_time` | 페이지 로딩 후 대기 시간(초) | `2.0` |
| `scroll_page` | 페이지 스크롤 여부 | `False` |
| `viewport_only` | 뷰포트만 캡처 여부 | `True` |
| `parallel_count` | 병렬 처리 수 | `3` |
| `max_retries` | 최대 재시도 횟수 | `2` |
| `timeout` | 페이지 로딩 타임아웃(초) | `30` |

## 디바이스 프로필

| 디바이스 유형 | 해상도 | 스케일 팩터 |
|-------------|-------|------------|
| 데스크톱 | 1920x1080 | 1.0 |
| 태블릿 | 768x1024 | 2.0 |
| 모바일 | 375x812 | 3.0 |

## 디렉토리 구조

```
web_capture/
  ├── __init__.py        # 모듈 초기화 및 API 노출
  ├── cli.py             # 명령줄 인터페이스
  ├── main.py            # 메인 기능 구현
  ├── version.py         # 버전 정보
  ├── config/            # 설정 관련 모듈
  │   └── config.py      # 설정 및 로깅 유틸리티
  ├── data/              # 데이터 파일 저장
  ├── function/          # 핵심 기능 구현
  ├── logs/              # 로그 파일 저장
  ├── models/            # 데이터 모델 정의
  └── utils/             # 유틸리티 함수
```

## 로깅

로그는 기본적으로 `./logs` 디렉토리에 저장되며, 로그 레벨은 환경 변수 `WEB_CAPTURE_LOG_LEVEL`로 설정할 수 있습니다. 