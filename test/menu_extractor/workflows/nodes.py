import traceback
from playwright.sync_api import sync_playwright
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from ..config.config import logger, ModelConfig, PlaywrightConfig
from ..models.models import MenuExtractorState, MenuItem, MenuStructure, MenuItemModel
from ..utils.utils import (
    normalize_url as normalize_url_util,
    extract_menu_candidates_from_html,
    extract_json_from_llm_response,
    normalize_menu_links,
)


def normalize_url(state: MenuExtractorState) -> MenuExtractorState:
    """
    사용자가 입력한 URL에서 루트 도메인(메인 페이지)을 추출합니다.
    """
    logger.info(f"정규화 전 URL: {state.user_url}")

    try:
        # URL 정규화
        root_url = normalize_url_util(state.user_url)

        # 상태 업데이트
        state.root_url = root_url
        state.status = "url_normalized"

        logger.info(f"정규화 후 URL: {root_url}")
    except Exception as e:
        state.error = f"URL 정규화 오류: {str(e)}"
        state.status = "error"
        logger.error(f"URL 정규화 오류: {str(e)}")

    return state


def render_html(state: MenuExtractorState) -> MenuExtractorState:
    """
    Playwright를 사용하여 웹페이지를 동적으로 렌더링하고 HTML을 가져옵니다.
    """
    if state.status == "error":
        return state

    logger.info(f"HTML 렌더링 시작: {state.root_url}")

    try:
        with sync_playwright() as p:
            logger.info("Playwright 초기화 완료")
            # 브라우저 실행 설정
            browser = p.chromium.launch(
                headless=PlaywrightConfig.HEADLESS, slow_mo=PlaywrightConfig.SLOW_MO
            )

            # 브라우저 컨텍스트 설정
            context = browser.new_context(user_agent=PlaywrightConfig.USER_AGENT)

            # 페이지 생성 및 타임아웃 설정
            page = context.new_page()
            page.set_default_timeout(PlaywrightConfig.TIMEOUT)

            # 페이지 접속
            logger.info(f"페이지 접속 시도: {state.root_url}")
            page.goto(state.root_url, wait_until="domcontentloaded")

            # 페이지 로드 대기
            logger.info("페이지 로드 대기 중...")
            page.wait_for_load_state("load")

            # 스크린샷 저장 (디버깅용)
            page.screenshot(path="screenshot.png")
            logger.info("스크린샷 저장 완료: screenshot.png")

            # HTML 가져오기
            html_content = page.content()

            # 브라우저 정리
            context.close()
            browser.close()

            if html_content:
                state.page_html = html_content
                state.status = "html_fetched"
                logger.info(f"HTML 가져오기 성공: {len(state.page_html)} 바이트")
                # HTML 앞부분 로깅
                html_preview = (
                    state.page_html[:200] + "..."
                    if len(state.page_html) > 200
                    else state.page_html
                )
                logger.info(f"HTML 미리보기: {html_preview}")
            else:
                state.error = "HTML을 가져오지 못했습니다."
                state.status = "error"
                logger.error("HTML 내용이 비어 있음")
    except Exception as e:
        state.error = f"HTML 렌더링 오류: {str(e)}"
        state.status = "error"
        logger.error(f"HTML 렌더링 오류: {str(e)}")
        logger.error(traceback.format_exc())

    return state


def extract_menu_candidates(state: MenuExtractorState) -> MenuExtractorState:
    """
    BeautifulSoup을 사용하여 HTML에서 메뉴로 보이는 영역을 추출합니다.
    """
    if state.status == "error" or not state.page_html:
        return state

    logger.info("메뉴 후보 추출 시작")

    try:
        # 메뉴 후보 추출
        menu_html = extract_menu_candidates_from_html(state.page_html)

        if menu_html:
            state.menu_html_snippet = menu_html
            state.status = "menu_extracted"
            logger.info(f"메뉴 HTML 추출 성공: {len(state.menu_html_snippet)} 바이트")
        else:
            state.error = "메뉴 후보를 찾을 수 없습니다."
            state.status = "error"
            logger.error("메뉴 후보를 찾을 수 없음")
    except Exception as e:
        state.error = f"메뉴 후보 추출 오류: {str(e)}"
        state.status = "error"
        logger.error(f"메뉴 후보 추출 오류: {str(e)}")
        logger.error(traceback.format_exc())

    return state


def parse_menu_with_llm(state: MenuExtractorState) -> MenuExtractorState:
    """
    LLM을 사용하여 HTML 메뉴 구조를 구조화된 형식으로 파싱합니다.
    """
    if state.status == "error" or not state.menu_html_snippet:
        return state

    logger.info("LLM 메뉴 파싱 시작")

    try:
        # LLM 설정
        # llm = ChatAnthropic(
        #     model=ModelConfig.DEFAULT_ANTHROPIC_MODEL,
        #     temperature=ModelConfig.DEFAULT_TEMPERATURE,
        # )
        llm = ChatOpenAI(
            model=ModelConfig.DEFAULT_OPENAI_MODEL,
            temperature=ModelConfig.DEFAULT_TEMPERATURE,
        )
        logger.info("LLM 초기화 완료")

        # 메뉴 HTML 스니펫 미리보기 로깅
        html_preview = (
            state.menu_html_snippet[:200] + "..."
            if len(state.menu_html_snippet) > 200
            else state.menu_html_snippet
        )
        logger.info(f"메뉴 HTML 스니펫 미리보기: {html_preview}")

        # 3단계 접근법: 각 단계는 이전 단계가 실패할 경우 시도됩니다

        # 1. with_structured_output 접근법
        try:
            # 구조화된 출력을 위한 LLM 설정
            structured_llm = llm.with_structured_output(
                MenuStructure, method="function_calling"
            )

            # 간단한 프롬프트 템플릿
            prompt = ChatPromptTemplate.from_template(
                """
                아래는 웹사이트의 메인 메뉴로 추정되는 HTML 코드입니다:
                ```html
                {html_snippet}
                ```
                
                이 HTML을 분석하여 웹사이트의 메뉴 구조를 추출해주세요.
                """
            )

            # LLM 호출
            chain = prompt | structured_llm
            logger.info("구조화된 LLM 체인 생성 완료")

            # LLM 호출 및 응답 처리
            response = chain.invoke(
                {"html_snippet": state.menu_html_snippet, "root_url": state.root_url}
            )
            logger.info(f"구조화된 LLM 응답 받음: {type(response)}")

            # 응답에서 메뉴 구조 추출하여 MenuItem 객체로 변환
            if hasattr(response, "menu_items"):
                # 직접 MenuItem 객체 리스트 생성
                menu_items = []

                # 중첩 함수로 메뉴 아이템 변환
                def convert_to_menu_item(item_data):
                    submenu = None
                    if hasattr(item_data, "submenu") and item_data.submenu:
                        submenu = [
                            convert_to_menu_item(sub_item)
                            for sub_item in item_data.submenu
                        ]

                    return MenuItem(
                        title=item_data.title,
                        link=item_data.link,
                        submenu=submenu,
                    )

                # 각 메뉴 아이템 변환
                for item in response.menu_items:
                    menu_items.append(convert_to_menu_item(item))

                state.menu_structure = menu_items
                logger.info(f"메뉴 아이템 변환 완료: {len(menu_items)}개")
            else:
                raise ValueError("응답에 menu_items 속성이 없습니다")

        except Exception as structured_error:
            # 2. PydanticOutputParser 접근법
            logger.warning(f"구조화된 출력 방식 실패: {str(structured_error)}")
            logger.info("대체 방법으로 시도합니다: PydanticOutputParser 사용")

            # 파서 설정
            parser = PydanticOutputParser(pydantic_object=MenuStructure)

            # 프롬프트 템플릿에 format_instructions 추가
            prompt = ChatPromptTemplate.from_template(
                """
                아래는 웹사이트의 메인 메뉴로 추정되는 HTML 코드입니다:
                ```html
                {html_snippet}
                ```
                
                이 HTML을 분석하여 메뉴 구조를 추출해주세요.
                
                {format_instructions}
                
                중요:
                - 응답은 반드시 위 스키마에 맞는 유효한 JSON 형식이어야 합니다.
                - 응답을 ```json과 ``` 태그로 감싸주세요.
                - 메뉴 항목명은 보이는 텍스트로 추출하고, 불필요한 공백은 제거해주세요.
                - 절대 경로가 아닌 상대 경로의 링크는 "{root_url}"을 앞에 추가하여 절대 경로로 변환해주세요.
                - 서브메뉴가 없는 메뉴 항목은 submenu 필드를 null로 설정하세요.
                """
            ).partial(format_instructions=parser.get_format_instructions())

            try:
                # LLM 호출 체인 설정
                chain = prompt | llm | parser
                logger.info("파서 기반 LLM 체인 생성 완료")

                # LLM 호출 및 응답 처리
                response = chain.invoke(
                    {
                        "html_snippet": state.menu_html_snippet,
                        "root_url": state.root_url,
                    }
                )
                logger.info(f"파서 기반 LLM 응답 받음: {type(response)}")

                # 응답 처리
                if hasattr(response, "menu_items"):
                    # 직접 MenuItem 객체 리스트 생성
                    menu_items = []

                    # 중첩 함수로 메뉴 아이템 변환
                    def convert_to_menu_item(item_data):
                        submenu = None
                        if hasattr(item_data, "submenu") and item_data.submenu:
                            submenu = [
                                convert_to_menu_item(sub_item)
                                for sub_item in item_data.submenu
                            ]

                        return MenuItem(
                            title=item_data.title,
                            link=item_data.link,
                            submenu=submenu,
                        )

                    # 각 메뉴 아이템 변환
                    for item in response.menu_items:
                        menu_items.append(convert_to_menu_item(item))

                    state.menu_structure = menu_items
                    logger.info(f"메뉴 아이템 변환 완료: {len(menu_items)}개")
                else:
                    raise ValueError("응답에 menu_items 속성이 없습니다")

            except Exception as parser_error:
                # 3. 명시적 JSON 요청 및 수동 파싱
                logger.warning(f"파서 기반 방식 실패: {str(parser_error)}")
                logger.info("최종 대체 방법으로 시도합니다: 명시적 JSON 지시")

                # 명시적 JSON 요청
                strict_prompt = ChatPromptTemplate.from_template(
                    """
                    아래는 웹사이트의 메인 메뉴로 추정되는 HTML 코드입니다:
                    ```html
                    {html_snippet}
                    ```
                    
                    이 HTML을 분석하여 다음과 같은 구조의 JSON만 반환해주세요:
                    
                    ```json
                    {{
                      "menu_items": [
                        {{
                          "title": "메뉴 항목 1",
                          "link": "링크 URL",
                          "submenu": [
                            {{
                              "title": "서브메뉴 항목 1",
                              "link": "서브메뉴 링크 URL",
                              "submenu": null
                            }}
                          ]
                        }}
                      ]
                    }}
                    ```
                    
                    절대로 다른 텍스트는 포함하지 말고 오직 JSON만 반환하세요.
                    응답은 반드시 ```json으로 시작하고 ```로 끝나야 합니다.
                    메뉴 항목명은 보이는 텍스트로 추출하고, 불필요한 공백은 제거해주세요.
                    절대 경로가 아닌 상대 경로의 링크는 "{root_url}"을 앞에 추가하여 절대 경로로 변환해주세요.
                    """
                )

                # 체인 생성 및 호출
                strict_chain = strict_prompt | llm
                strict_response = strict_chain.invoke(
                    {
                        "html_snippet": state.menu_html_snippet,
                        "root_url": state.root_url,
                    }
                )

                # 응답 텍스트 추출
                content = (
                    strict_response.content
                    if hasattr(strict_response, "content")
                    else str(strict_response)
                )

                # JSON 추출 및 파싱
                menu_data = extract_json_from_llm_response(content)

                if menu_data and "menu_items" in menu_data:
                    # MenuItem 객체 생성
                    menu_items = []

                    # 중첩 함수로 메뉴 아이템 변환
                    def convert_to_menu_item(item_data):
                        submenu = None
                        if "submenu" in item_data and item_data["submenu"]:
                            submenu = [
                                convert_to_menu_item(sub_item)
                                for sub_item in item_data["submenu"]
                            ]

                        return MenuItem(
                            title=item_data["title"],
                            link=item_data["link"],
                            submenu=submenu,
                        )

                    # 각 메뉴 아이템 변환
                    for item in menu_data["menu_items"]:
                        menu_items.append(convert_to_menu_item(item))

                    state.menu_structure = menu_items
                    logger.info(f"메뉴 아이템 변환 완료: {len(menu_items)}개")
                else:
                    raise ValueError("응답에서 유효한 메뉴 데이터를 찾을 수 없습니다")

        # 상태 업데이트
        state.status = "menu_parsed"
        logger.info(f"메뉴 구조 생성 완료: {len(state.menu_structure)}개 항목")

    except Exception as e:
        state.error = f"메뉴 파싱 오류: {str(e)}"
        state.status = "error"
        logger.error(f"메뉴 파싱 오류: {str(e)}")
        logger.error(traceback.format_exc())

    return state


def finalize_output(state: MenuExtractorState) -> MenuExtractorState:
    """
    최종 메뉴 구조를 정리하고 결과를 준비합니다.
    """
    logger.info(f"최종 결과 정리 시작, 현재 상태: {state.status}")

    if state.status == "error":
        logger.error(f"오류 상태로 종료: {state.error}")
        return state

    # 메뉴 구조가 있는 경우 링크 정규화
    if state.menu_structure:
        normalize_menu_links(state.menu_structure, state.root_url)
        state.status = "completed"
        logger.info("메뉴 구조 처리 완료")
    else:
        state.error = "메뉴 구조를 생성하지 못했습니다."
        state.status = "error"
        logger.error("메뉴 구조 생성 실패")

    return state
