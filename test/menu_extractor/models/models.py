from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# 메뉴 아이템 모델 (기본)
class MenuItem(BaseModel):
    """웹사이트 메뉴 항목"""

    title: str
    link: str
    submenu: Optional[List["MenuItem"]] = None


# 메뉴 아이템 모델 (LLM 사용)
class MenuItemModel(BaseModel):
    """웹사이트 메뉴 항목에 대한 정보"""

    title: str = Field(description="메뉴 항목의 표시 텍스트")
    link: str = Field(description="메뉴 항목의 링크 URL")
    submenu: Optional[List["MenuItemModel"]] = Field(
        None, description="하위 메뉴 항목 목록 (있는 경우)"
    )


# 메뉴 구조 모델
class MenuStructure(BaseModel):
    """웹사이트의 전체 메뉴 구조"""

    menu_items: List[MenuItemModel] = Field(
        default=[],
        description="최상위 메뉴 항목 목록",
        example=[
            {"title": "Home", "link": "/", "submenu": None},
            {"title": "About", "link": "/about", "submenu": None},
        ],
    )


# 워크플로우 상태 정의
class MenuExtractorState(BaseModel):
    # 입력 상태
    user_url: str

    # 처리 중간 상태
    root_url: Optional[str] = None
    page_html: Optional[str] = None
    menu_html_snippet: Optional[str] = None

    # 출력 상태
    menu_structure: Optional[List[MenuItem]] = None
    error: Optional[str] = None
    status: Literal[
        "init",
        "url_normalized",
        "html_fetched",
        "menu_extracted",
        "menu_parsed",
        "completed",
        "error",
    ] = "init"
