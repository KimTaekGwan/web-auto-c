# URL 기반 스크린샷 페이지 추출 AI 모듈 설계 요구사항 정의서

## 1. 개요

WebCapture Pro의 핵심 기능을 강화하기 위한 AI 모듈로, 주어진 URL로부터 효율적인 웹사이트 캡처를 위한 최적의 페이지 리스트를 자동으로 추출합니다. 이 모듈은 LangGraph, Pydantic, 다중 에이전트 아키텍처를 활용하여 구현됩니다.

## 2. 기술 스택

- **LangGraph**: 에이전트 워크플로우 및 상태 관리
- **Pydantic**: 데이터 모델 검증 및 관리
- **Claude API**: 각 에이전트의 추론 엔진
- **FastAPI**: 모듈 API 엔드포인트 제공
- **Playwright/Selenium**: 웹 페이지 접근 및 분석

## 3. 에이전트 구조 설계

### 3.1 에이전트 유형 및 역할

#### CoordinatorAgent

- 작업 계획 수립 및 조율
- 다른 에이전트 작업 할당 및 모니터링
- 최종 결과 통합 및 검증

#### SitemapAgent

- sitemap.xml 파일 찾기 및 파싱
- URL 정규화 및 필터링
- 우선순위 및 빈도 데이터 추출

#### HTMLParserAgent

- 웹사이트 DOM 분석
- 메뉴 구조 식별 (nav, ul-li, 시맨틱 태그 활용)
- 중요 페이지 추론

#### VerificationAgent

- URL 유효성 검증 (404, 접근성 확인)
- 결과 중복 제거 및 통합
- 최종 스크린샷 대상 페이지 선별

### 3.2 Pydantic 모델

```python
from pydantic import BaseModel, Field, AnyUrl, validator
from typing import List, Dict, Optional, Set
from enum import Enum

class DeviceType(str, Enum):
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"

class AgentType(str, Enum):
    COORDINATOR = "coordinator"
    SITEMAP = "sitemap"
    HTML_PARSER = "html_parser"
    VERIFICATION = "verification"

class ModuleConfig(BaseModel):
    min_urls: int = Field(5, description="최소 추출 URL 개수")
    max_urls: int = Field(20, description="최대 추출 URL 개수")
    max_iterations: int = Field(3, description="최대 작업 반복 횟수")
    prioritize_main_sections: bool = Field(True, description="주요 섹션 우선 추출")
    include_dynamic_pages: bool = Field(False, description="동적 페이지 포함 여부")
    device_types: List[DeviceType] = Field(
        [DeviceType.DESKTOP], description="캡처할 디바이스 유형"
    )
    normalize_urls: bool = Field(True, description="URL 정규화 수행 여부")

class PageInfo(BaseModel):
    url: AnyUrl
    title: Optional[str] = None
    priority: float = 1.0
    depth: int = 0
    parent_url: Optional[AnyUrl] = None
    is_valid: Optional[bool] = None
    source: List[AgentType] = []
    metadata: Dict = Field(default_factory=dict)

class MenuStructure(BaseModel):
    base_url: AnyUrl
    pages: List[PageInfo] = []

    @validator('pages')
    def unique_urls(cls, v):
        urls = set()
        result = []
        for page in v:
            if page.url not in urls:
                urls.add(page.url)
                result.append(page)
        return result

class AgentContext(BaseModel):
    module_config: ModuleConfig
    base_url: AnyUrl
    normalized_url: Optional[AnyUrl] = None
    iteration: int = 0
    sitemap_result: Optional[MenuStructure] = None
    html_result: Optional[MenuStructure] = None
    final_result: Optional[MenuStructure] = None
    errors: Dict[str, List[str]] = Field(default_factory=dict)
    status: str = "initialized"
```

## 4. LangGraph 워크플로우 설계

```python
from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, Annotated

# 메인 워크플로우 정의
def create_workflow(config: ModuleConfig = None):
    # 기본 설정 적용
    if config is None:
        config = ModuleConfig()

    # 상태 정의
    class GraphState(TypedDict):
        context: AgentContext
        messages: List[Dict[str, Any]]

    # 그래프 생성
    workflow = StateGraph(GraphState)

    # 각 노드 추가
    workflow.add_node("plan", plan_task)
    workflow.add_node("normalize_url", normalize_url)
    workflow.add_node("extract_sitemap", extract_sitemap)
    workflow.add_node("parse_html", parse_html)
    workflow.add_node("verify_results", verify_results)
    workflow.add_node("finalize", finalize_results)

    # 에지 및 조건 정의
    workflow.add_edge("plan", "normalize_url")
    workflow.add_edge("normalize_url", "extract_sitemap")

    # 병렬 처리를 위한 분기
    workflow.add_conditional_edges(
        "extract_sitemap",
        decision_function,
        {
            "continue": "parse_html",
            "skip_html": "verify_results"
        }
    )

    workflow.add_edge("parse_html", "verify_results")
    workflow.add_edge("verify_results", "finalize")

    # 반복 처리를 위한 조건부 에지
    workflow.add_conditional_edges(
        "finalize",
        check_completion,
        {
            "complete": END,
            "retry": "plan"
        }
    )

    return workflow.compile()
```

## 5. 에이전트 구현 상세

### 5.1 CoordinatorAgent

```python
class CoordinatorAgent:
    def __init__(self, config: ModuleConfig, model_name: str = "claude-3-5-sonnet"):
        self.config = config
        self.model_name = model_name

    async def plan_task(self, context: AgentContext) -> AgentContext:
        """작업 계획 수립 및 상태 초기화"""
        context.iteration += 1

        if context.iteration > self.config.max_iterations:
            # 반복 횟수 초과 시 현재까지의 결과로 마무리
            context.status = "max_iterations_reached"
            return context

        # 작업 계획 수립 로직
        planning_prompt = f"""
        URL: {context.base_url}
        작업: 웹사이트 구조 분석 및 스크린샷할 핵심 페이지 추출
        현재 반복: {context.iteration}/{self.config.max_iterations}

        이전 결과: {context.final_result if context.final_result else "없음"}
        이전 오류: {context.errors if context.errors else "없음"}

        다음 단계 계획을 수립해주세요:
        1. URL 정규화 필요성 판단
        2. 사이트맵 추출 전략
        3. HTML 분석 접근 방법
        4. 검증 단계에서 확인할 사항
        """

        # Claude API 호출하여 계획 수립
        # 결과를 기반으로 context 업데이트

        context.status = "planning_completed"
        return context
```

### 5.2 SitemapAgent

```python
class SitemapAgent:
    def __init__(self, config: ModuleConfig):
        self.config = config

    async def extract_sitemap(self, context: AgentContext) -> AgentContext:
        """sitemap.xml 찾기 및 파싱"""
        base_url = context.normalized_url or context.base_url

        try:
            # 1. robots.txt 확인
            robots_url = f"{base_url}/robots.txt"
            # robots.txt 파싱하여 sitemap 위치 확인

            # 2. 일반적인 sitemap 위치 확인
            standard_locations = [
                f"{base_url}/sitemap.xml",
                f"{base_url}/sitemap_index.xml",
                f"{base_url}/sitemap/sitemap.xml"
            ]

            # 3. 발견된 sitemap 파싱
            # sitemap 내의 URL 추출 및 정규화

            # 4. MenuStructure 생성
            sitemap_result = MenuStructure(
                base_url=base_url,
                pages=[]  # 추출된 페이지 정보
            )

            context.sitemap_result = sitemap_result
            context.status = "sitemap_extracted"

        except Exception as e:
            # 오류 기록
            if "sitemap" not in context.errors:
                context.errors["sitemap"] = []
            context.errors["sitemap"].append(str(e))
            context.status = "sitemap_failed"

        return context
```

### 5.3 HTMLParserAgent

```python
class HTMLParserAgent:
    def __init__(self, config: ModuleConfig, model_name: str = "claude-3-5-sonnet"):
        self.config = config
        self.model_name = model_name

    async def parse_html(self, context: AgentContext) -> AgentContext:
        """웹페이지 HTML 분석하여 메뉴 구조 추출"""
        base_url = context.normalized_url or context.base_url

        try:
            # 1. 메인 페이지 HTML 가져오기
            # Playwright 또는 Selenium 활용

            # 2. 메뉴 요소 식별
            # nav, ul-li, header 등 시맨틱 태그 활용

            # 3. Claude API로 메뉴 구조 분석
            analysis_prompt = f"""
            다음 HTML에서 웹사이트 메뉴 구조를 분석해주세요:

            {html_content}

            다음 요소에 주목하세요:
            - 주요 네비게이션 메뉴
            - 드롭다운 서브메뉴
            - 푸터 메뉴
            - 사이트맵 링크

            결과는 JSON 형식으로 반환해주세요:
            {{
                "main_menu": [
                    {{"title": "메뉴명", "url": "링크", "depth": 0}},
                    ...
                ],
                "sub_menus": [
                    {{"parent": "상위메뉴", "title": "메뉴명", "url": "링크", "depth": 1}},
                    ...
                ]
            }}
            """

            # 4. MenuStructure 생성
            html_result = MenuStructure(
                base_url=base_url,
                pages=[]  # 분석된 페이지 정보
            )

            context.html_result = html_result
            context.status = "html_parsed"

        except Exception as e:
            # 오류 기록
            if "html" not in context.errors:
                context.errors["html"] = []
            context.errors["html"].append(str(e))
            context.status = "html_failed"

        return context
```

### 5.4 VerificationAgent

```python
class VerificationAgent:
    def __init__(self, config: ModuleConfig):
        self.config = config

    async def verify_results(self, context: AgentContext) -> AgentContext:
        """결과 검증 및 통합"""
        # 두 결과 중 하나라도 있으면 진행
        sitemap_pages = context.sitemap_result.pages if context.sitemap_result else []
        html_pages = context.html_result.pages if context.html_result else []

        if not sitemap_pages and not html_pages:
            context.status = "verification_failed"
            context.errors["verification"] = ["No pages found from either sitemap or HTML analysis"]
            return context

        # 페이지 통합 및 중복 제거
        all_pages = {}  # URL을 키로 한 딕셔너리

        # sitemap 결과 추가
        for page in sitemap_pages:
            all_pages[str(page.url)] = page

        # HTML 결과 병합
        for page in html_pages:
            page_url = str(page.url)
            if page_url in all_pages:
                # 기존 페이지 정보 업데이트
                existing = all_pages[page_url]
                existing.source.append(AgentType.HTML_PARSER)
                # 우선순위 병합 로직
                existing.priority = max(existing.priority, page.priority)
                if page.title and not existing.title:
                    existing.title = page.title
            else:
                all_pages[page_url] = page

        # URL 유효성 검증 (선택적)
        if context.iteration < self.config.max_iterations:
            # 모든 URL 검증은 시간이 많이 소요될 수 있으므로,
            # 우선순위가 높은 URL만 선택적으로 검증
            high_priority_urls = sorted(
                all_pages.values(),
                key=lambda p: p.priority,
                reverse=True
            )[:10]  # 상위 10개만

            for page in high_priority_urls:
                # URL 접근 가능 여부 확인
                # 상태 코드 확인 (200 OK, 404 Not Found 등)
                pass

        # 우선순위에 따라 정렬 및 개수 제한
        final_pages = sorted(
            all_pages.values(),
            key=lambda p: p.priority,
            reverse=True
        )[:self.config.max_urls]

        # 최종 결과 저장
        context.final_result = MenuStructure(
            base_url=context.normalized_url or context.base_url,
            pages=final_pages
        )

        context.status = "verification_completed"
        return context
```

## 6. 모듈 설정 및 제약 조건

### 6.1 기본 설정 옵션

```python
default_config = ModuleConfig(
    min_urls=5,                       # 최소 추출 URL 개수
    max_urls=20,                      # 최대 추출 URL 개수
    max_iterations=3,                 # 최대 작업 반복 횟수
    prioritize_main_sections=True,    # 주요 섹션 우선 추출
    include_dynamic_pages=False,      # 동적 페이지 포함 여부
    device_types=[DeviceType.DESKTOP], # 캡처할 디바이스 유형
    normalize_urls=True               # URL 정규화 수행 여부
)
```

### 6.2 API 인터페이스

```python
from fastapi import FastAPI, BackgroundTasks
from typing import Optional

app = FastAPI()

@app.post("/api/extract-pages")
async def extract_pages(
    url: str,
    background_tasks: BackgroundTasks,
    config: Optional[ModuleConfig] = None
):
    """주어진 URL에서 스크린샷할 페이지 리스트 추출 API"""
    task_id = generate_task_id()

    # 기본 설정 적용
    if config is None:
        config = default_config

    # 백그라운드 작업 등록
    background_tasks.add_task(process_extraction, task_id, url, config)

    return {
        "task_id": task_id,
        "url": url,
        "status": "processing"
    }

@app.get("/api/extract-pages/{task_id}")
async def get_extraction_result(task_id: str):
    """작업 결과 조회 API"""
    # 데이터베이스 또는 캐시에서 결과 조회
    pass
```

## 7. 구현 로드맵

1. **Phase 1: 핵심 에이전트 구현** (2주)

   - 기본 데이터 모델 구현
   - 에이전트 클래스 구현
   - 단위 테스트 작성

2. **Phase 2: LangGraph 워크플로우 구현** (2주)

   - 상태 관리 로직 구현
   - 조건부 흐름 구현
   - 에이전트 통합

3. **Phase 3: API 및 통합** (1주)

   - FastAPI 엔드포인트 구현
   - WebCapture Pro 기존 시스템과 통합
   - 오류 처리 및 로깅 구현

4. **Phase 4: 테스트 및 최적화** (1주)
   - 다양한 웹사이트에 대한 테스트
   - 성능 최적화 및 튜닝
   - 문서화

## 8. 기술적 고려사항

### 8.1 확장성

- **플러그인 아키텍처**: 새로운 페이지 추출 전략을 플러그인 형태로 추가 가능
- **커스텀 필터**: 사용자 정의 필터링 로직 지원
- **다양한 웹사이트 유형 대응**: SPA, 다국어 사이트, 인증 필요 사이트 등

### 8.2 성능 최적화

- **병렬 처리**: sitemap과 HTML 분석을 병렬로 수행
- **캐싱**: 반복된 요청에 대한 결과 캐싱
- **점진적 검증**: 우선순위가 높은 URL부터 단계적 검증

### 8.3 오류 처리

- **그레이스풀 디그레이데이션**: 일부 단계 실패 시에도 전체 프로세스 진행
- **재시도 메커니즘**: 일시적 오류에 대한 자동 재시도
- **상세한 오류 보고**: 각 단계별 오류 정보 기록 및 분석

## 9. 결론

이 AI 모듈은 WebCapture Pro의 핵심 기능을 강화하여, 단일 URL 입력만으로 웹사이트의 중요 페이지를 자동으로 식별하고 최적의 스크린샷 대상 목록을 생성합니다. LangGraph와 다중 에이전트 아키텍처를 활용한 이 모듈은 확장성과 유연성을 갖추고 있으며, 다양한 웹사이트 구조에 적응할 수 있습니다.
