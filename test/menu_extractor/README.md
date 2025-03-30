# Menu Extractor (메뉴 추출기)

웹사이트의 메뉴 구조를 자동으로 추출하는 Python 유틸리티입니다.

## 개요

이 도구는 다음과 같은 기능을 제공합니다:

- 웹사이트 URL을 입력하면 메인 메뉴 구조를 자동으로 추출
- 동적 웹페이지 렌더링 지원 (JavaScript로 생성된 메뉴 포함)
- 메뉴 및 서브메뉴 계층 구조 식별
- JSON 형식으로 메뉴 데이터 제공

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

## 사용법

### 명령줄 인터페이스

```bash
# 기본 사용법
python -m menu_extractor.main https://example.com

# 결과를 파일로 저장
python -m menu_extractor.main https://example.com -o menu.json

# 보기 좋게 출력
python -m menu_extractor.main https://example.com -p
```

### Python API

```python
from menu_extractor import extract_website_menu

# 메뉴 추출
result = extract_website_menu("https://example.com")

# 결과 확인
if result["success"]:
    print(f"루트 URL: {result['root_url']}")
    print("메뉴 구조:")
    for item in result["menu_structure"]:
        print(f"- {item['title']} ({item['link']})")
else:
    print(f"오류: {result['error']}")
```

## 작동 방식

이 도구는 다음과 같은 단계로 작동합니다:

1. URL 정규화: 입력된 URL에서 루트 도메인 추출
2. HTML 렌더링: Playwright를 사용하여 동적 웹페이지 렌더링
3. 메뉴 후보 추출: HTML에서 메뉴로 추정되는 요소 식별
4. LLM 메뉴 파싱: LLM을 사용하여 메뉴 구조를 인식하고 JSON으로 변환
5. 결과 정리: 메뉴 구조 정리 및 결과 반환

## 아키텍처

```
menu_extractor/
├── __init__.py          # 패키지 초기화
├── config.py            # 설정 및 로깅
├── main.py              # 메인 실행 코드
├── models.py            # Pydantic 모델 정의
├── utils.py             # 유틸리티 함수
├── version.py           # 버전 정보
└── workflows/           # 워크플로우 정의
    ├── __init__.py
    ├── nodes.py         # 워크플로우 노드
    └── workflow.py      # 워크플로우 생성
```

## 의존성

- Python 3.8 이상
- LangChain: LLM 통합 및 워크플로우 관리
- LangGraph: 워크플로우 파이프라인 구성
- Playwright: 동적 웹페이지 렌더링
- Anthropic Claude / OpenAI: LLM 모델 (API 키 필요)
- BeautifulSoup4: HTML 파싱
- Pydantic: 데이터 모델 및 유효성 검사

## 라이센스

MIT
