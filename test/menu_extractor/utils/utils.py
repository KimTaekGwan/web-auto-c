import re
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any

from config.config import logger
from models.models import MenuItem


def normalize_url(url: str) -> str:
    """
    URL에서 루트 도메인(메인 페이지)을 추출합니다.

    Args:
        url: 정규화할 URL 문자열

    Returns:
        루트 도메인 URL (예: https://openai.com/)

    Raises:
        Exception: URL 파싱 오류 발생 시
    """
    parsed = urlparse(url)
    # 스키마와 도메인만 추출
    return f"{parsed.scheme}://{parsed.netloc}/"


def extract_menu_candidates_from_html(html: str) -> Optional[str]:
    """
    HTML에서 메뉴 후보가 될 수 있는 요소를 추출합니다.

    Args:
        html: 분석할 전체 HTML 문자열

    Returns:
        메뉴로 추정되는 HTML 요소 문자열 또는 None
    """
    soup = BeautifulSoup(html, "html.parser")
    logger.info("HTML 파싱 완료")

    # 메뉴 후보 요소 찾기
    candidates = []

    # 1. header>nav 태그
    header_navs = soup.select("header nav")
    logger.info(f"header>nav 태그 찾음: {len(header_navs)}개")
    for nav_tag in header_navs:
        candidates.append(nav_tag)

    # 2. nav 태그
    navs = soup.find_all("nav")
    logger.info(f"nav 태그 찾음: {len(navs)}개")
    for nav_tag in navs:
        if nav_tag not in candidates:
            candidates.append(nav_tag)

    # 3. class/id에 menu, navigation 등의 키워드가 포함된 요소
    menu_keywords = [
        "menu",
        "nav",
        "navigation",
        "gnb",
        "main-menu",
        "header-menu",
        "navbar",
    ]

    class_elements = []
    for element in soup.find_all(attrs={"class": True}):
        class_names = " ".join(element.get("class", []))
        if any(keyword in class_names.lower() for keyword in menu_keywords):
            class_elements.append(element)
            candidates.append(element)
    logger.info(f"class에 메뉴 키워드가 포함된 요소: {len(class_elements)}개")

    id_elements = []
    for element in soup.find_all(attrs={"id": True}):
        id_value = element.get("id", "")
        if any(keyword in id_value.lower() for keyword in menu_keywords):
            id_elements.append(element)
            candidates.append(element)
    logger.info(f"id에 메뉴 키워드가 포함된 요소: {len(id_elements)}개")

    # 4. header 태그 (메뉴가 없을 경우 헤더 전체를 시도)
    headers = []
    if not candidates:
        headers = soup.find_all("header")
        logger.info(f"header 태그 찾음: {len(headers)}개")
        for header in headers:
            candidates.append(header)

    # 5. 링크가 많은 div 요소 (일부 사이트는 특별한 구조 없이 div만 사용)
    div_candidates = []
    if not candidates:
        divs_with_links = []
        for div in soup.find_all("div"):
            links = div.find_all("a")
            if len(links) >= 3:  # 최소 3개 이상의 링크가 있는 div만 고려
                divs_with_links.append((div, len(links)))

        # 링크가 많은 순서로 정렬
        divs_with_links.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"링크가 3개 이상인 div 요소: {len(divs_with_links)}개")

        # 링크가 가장 많은 상위 3개 div 추가
        for div, link_count in divs_with_links[:3]:
            logger.info(f"링크 {link_count}개가 있는 div 추가")
            div_candidates.append(div)
            candidates.append(div)

    # 후보 정렬 및 선택 (링크가 많은 순서로)
    def count_links(element):
        links = element.find_all("a")
        return len(links)

    candidates = sorted(candidates, key=count_links, reverse=True)
    logger.info(f"총 메뉴 후보: {len(candidates)}개")

    if candidates:
        # 가장 많은 링크를 포함하는 요소 선택
        top_candidate = candidates[0]
        link_count = count_links(top_candidate)
        logger.info(f"선택된 최종 후보: 링크 {link_count}개 포함")

        # 최종 후보 요소의 태그 정보 로깅
        logger.info(f"최종 후보 태그: {top_candidate.name}")
        if top_candidate.get("class"):
            logger.info(f"최종 후보 클래스: {top_candidate.get('class')}")
        if top_candidate.get("id"):
            logger.info(f"최종 후보 ID: {top_candidate.get('id')}")

        return str(top_candidate)

    # 최후의 수단: body 태그 전체를 LLM에 전달하고 메뉴를 찾도록 요청
    body = soup.find("body")
    if body:
        # 너무 큰 HTML을 방지하기 위해 body의 처음 부분만 사용
        return str(body)[:15000]  # 처음 15000자만 사용

    return None


def normalize_menu_links(menu_items: List[MenuItem], root_url: str) -> None:
    """
    메뉴 아이템의 상대 경로 링크를 절대 경로로 변환합니다.

    Args:
        menu_items: 변환할 메뉴 아이템 리스트
        root_url: 루트 URL 문자열
    """
    for item in menu_items:
        # 상대 경로를 절대 경로로 변환
        if hasattr(item, "link") and item.link and item.link.startswith("/"):
            item.link = urljoin(root_url, item.link)
            logger.info(f"링크 정규화: {item.link}")

        # 서브메뉴가 있으면 재귀적으로 처리
        if hasattr(item, "submenu") and item.submenu:
            normalize_menu_links(item.submenu, root_url)


def extract_json_from_llm_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    LLM 응답에서 JSON 데이터를 추출합니다.

    Args:
        response_text: LLM 응답 텍스트

    Returns:
        파싱된 JSON 데이터 또는 None

    Raises:
        ValueError: JSON 파싱 오류 발생 시
    """
    # 코드 블록 안의 JSON 검색
    json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)

    if json_match:
        json_str = json_match.group(1)
        logger.info(f"JSON 문자열 추출: {json_str[:100]}...")
        return json.loads(json_str)

    # 전체 텍스트에서 중괄호 부분 찾기
    json_candidates = re.findall(r"\{.*?\}", response_text, re.DOTALL)

    for candidate in json_candidates:
        try:
            menu_data = json.loads(candidate)
            if "menu_items" in menu_data:
                return menu_data
        except json.JSONDecodeError:
            continue

    return None
