from langgraph.graph import StateGraph, END

from ..models.models import MenuExtractorState
from .nodes import (
    normalize_url,
    render_html,
    extract_menu_candidates,
    parse_menu_with_llm,
    finalize_output,
)


def create_menu_extractor_workflow():
    """
    메뉴 구조 추출 워크플로우를 생성합니다.
    """
    # 그래프 생성
    workflow = StateGraph(MenuExtractorState)

    # 노드 추가
    workflow.add_node("normalize_url", normalize_url)
    workflow.add_node("render_html", render_html)
    workflow.add_node("extract_menu_candidates", extract_menu_candidates)
    workflow.add_node("parse_menu_with_llm", parse_menu_with_llm)
    workflow.add_node("finalize_output", finalize_output)

    # 시작점 설정
    workflow.set_entry_point("normalize_url")

    # 조건부 에지 설정
    def route_on_error(state):
        return "error" if state.status == "error" else "continue"

    # 노드 간 에지(전이) 설정
    workflow.add_conditional_edges(
        "normalize_url",
        route_on_error,
        {"error": "finalize_output", "continue": "render_html"},
    )

    workflow.add_conditional_edges(
        "render_html",
        route_on_error,
        {"error": "finalize_output", "continue": "extract_menu_candidates"},
    )

    workflow.add_conditional_edges(
        "extract_menu_candidates",
        route_on_error,
        {"error": "finalize_output", "continue": "parse_menu_with_llm"},
    )

    workflow.add_conditional_edges(
        "parse_menu_with_llm",
        route_on_error,
        {"error": "finalize_output", "continue": "finalize_output"},
    )

    # 종료 노드 설정
    workflow.add_edge("finalize_output", END)

    # 워크플로우 컴파일
    return workflow.compile()
