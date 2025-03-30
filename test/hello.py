from pydantic import BaseModel, Field, AnyUrl, HttpUrl, validator
from typing import List, Dict, Optional, Set, Any, Union
from enum import Enum
import asyncio
from langgraph.graph import StateGraph, END


# 기본 열거형 및 데이터 모델
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
    url: HttpUrl
    title: Optional[str] = None
    priority: float = 1.0
    depth: int = 0
    parent_url: Optional[HttpUrl] = None
    is_valid: Optional[bool] = None
    source: List[AgentType] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SiteStructure(BaseModel):
    base_url: HttpUrl
    pages: List[PageInfo] = []

    @validator("pages")
    def unique_urls(cls, v):
        urls = set()
        result = []
        for page in v:
            if page.url not in urls:
                urls.add(page.url)
                result.append(page)
        return result


class ContextState(BaseModel):
    config: ModuleConfig
    base_url: HttpUrl
    normalized_url: Optional[HttpUrl] = None
    iteration: int = 0
    sitemap_result: Optional[SiteStructure] = None
    html_result: Optional[SiteStructure] = None
    final_result: Optional[SiteStructure] = None
    errors: Dict[str, List[str]] = Field(default_factory=dict)
    status: str = "initialized"


# 워크플로우 상태 정의
class GraphState(BaseModel):
    context: ContextState
    messages: List[Dict[str, Any]] = Field(default_factory=list)


# 각 에이전트 함수 정의
async def plan_task(state: GraphState) -> GraphState:
    """
    작업 계획 수립 및 상태 초기화

    Input: GraphState(현재 상태)
    Output: 업데이트된 GraphState
    """
    # 여기서 CoordinatorAgent 로직 구현
    return state


async def normalize_url(state: GraphState) -> GraphState:
    """
    입력 URL 정규화

    Input: GraphState(base_url이 설정된 상태)
    Output: GraphState(normalized_url이 설정된 상태)
    """
    # URL 정규화 로직 구현
    # 만약 정규화 옵션이 False면 그냥 base_url을 사용
    if not state.context.config.normalize_urls:
        state.context.normalized_url = state.context.base_url
        state.context.status = "url_normalized"
        return state

    # 여기에 실제 URL 정규화 로직 구현
    state.context.normalized_url = state.context.base_url  # 임시로 동일하게 설정
    state.context.status = "url_normalized"
    return state


async def extract_sitemap(state: GraphState) -> GraphState:
    """
    sitemap.xml 찾기 및 파싱

    Input: GraphState(normalized_url이 설정된 상태)
    Output: GraphState(sitemap_result가 설정된 상태)
    """
    # 사용할 URL 결정
    url_to_use = state.context.normalized_url or state.context.base_url

    # 여기에 사이트맵 추출 로직 구현
    # 1. robots.txt 확인
    # 2. 일반적인 sitemap 위치 확인
    # 3. 발견된 sitemap 파싱

    # 임시 결과
    state.context.sitemap_result = SiteStructure(
        base_url=url_to_use, pages=[]  # 실제 구현 시 페이지 정보 추가
    )

    state.context.status = "sitemap_extracted"
    return state


async def parse_html(state: GraphState) -> GraphState:
    """
    웹페이지 HTML 분석하여 메뉴 구조 추출

    Input: GraphState(normalized_url이 설정된 상태)
    Output: GraphState(html_result가 설정된 상태)
    """
    # HTMLParserAgent 로직 구현
    return state


async def verify_results(state: GraphState) -> GraphState:
    """
    추출된 결과 검증 및 통합

    Input: GraphState(sitemap_result와 html_result가 설정된 상태)
    Output: GraphState(검증된 최종 결과가 통합된 상태)
    """
    # VerificationAgent 로직 구현
    return state


async def finalize_output(state: GraphState) -> GraphState:
    """
    최종 결과 정리 및 반환

    Input: GraphState(sitemap_result가 설정된 상태)
    Output: GraphState(최종 결과가 포맷팅된 상태)
    """
    # 사이트맵 결과에서 최대 URL 수 제한
    if (
        state.context.sitemap_result
        and len(state.context.sitemap_result.pages) > state.context.config.max_urls
    ):
        # 우선순위에 따라 정렬
        pages = sorted(
            state.context.sitemap_result.pages, key=lambda p: p.priority, reverse=True
        )[: state.context.config.max_urls]

        # 결과 업데이트
        state.context.sitemap_result.pages = pages

    state.context.status = "completed"
    return state


def decision_function(state: GraphState) -> str:
    """sitemap 결과에 따라 HTML 파싱 여부 결정"""
    if (
        not state.context.sitemap_result
        or len(state.context.sitemap_result.pages) < state.context.config.min_urls
    ):
        return "continue"  # HTML 파싱 진행
    return "skip_html"  # 충분한 URL이 있으면 HTML 파싱 건너뛰기


def check_completion(state: GraphState) -> str:
    """작업 완료 여부 확인"""
    context = state.context

    # 충분한 URL을 찾았거나 최대 반복 횟수에 도달했는지 확인
    if (
        context.final_result
        and len(context.final_result.pages) >= context.config.min_urls
    ):
        return "complete"
    elif context.iteration >= context.config.max_iterations:
        return "complete"
    return "retry"  # 더 많은 URL이 필요하면 다시 시도


# LangGraph 워크플로우 생성 함수
def create_workflow(config: Optional[ModuleConfig] = None):
    """간소화된 LangGraph 워크플로우 생성"""
    if config is None:
        config = ModuleConfig()

    # 그래프 생성
    workflow = StateGraph(GraphState)

    # 간소화된 노드 추가
    workflow.add_node("normalize_url", normalize_url)
    workflow.add_node("extract_sitemap", extract_sitemap)
    workflow.add_node("finalize_output", finalize_output)

    # 에지 정의 - 단순한 순차적 흐름
    workflow.add_edge("normalize_url", "extract_sitemap")
    workflow.add_edge("extract_sitemap", "finalize_output")
    workflow.add_edge("finalize_output", END)

    return workflow.compile()


# API 인터페이스
class ExtractionRequest(BaseModel):
    url: HttpUrl
    config: Optional[ModuleConfig] = None


class ExtractionTask(BaseModel):
    task_id: str
    url: HttpUrl
    status: str = "processing"


class ExtractionResult(BaseModel):
    task_id: str
    url: HttpUrl
    status: str
    pages: Optional[List[PageInfo]] = None
    errors: Dict[str, List[str]] = Field(default_factory=dict)
