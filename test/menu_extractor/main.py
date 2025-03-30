"""
메뉴 추출 모듈 메인 파일
"""

from .config.config import logger
from .models.models import MenuExtractorState
from .workflows import create_menu_extractor_workflow


def extract_website_menu(url: str) -> dict:
    """
    URL에서 웹사이트 메뉴 구조를 추출합니다.

    Args:
        url: 메뉴 구조를 추출할 웹사이트 URL

    Returns:
        추출된 메뉴 구조를 포함한 딕셔너리
    """
    logger.info(f"메뉴 추출 시작: {url}")

    # 워크플로우 생성
    workflow = create_menu_extractor_workflow()
    logger.info("워크플로우 생성 완료")

    # 초기 상태 설정
    initial_state = MenuExtractorState(user_url=url)
    logger.info("초기 상태 설정 완료")

    # 워크플로우 실행
    result = workflow.invoke(initial_state)
    logger.info(f"워크플로우 실행 완료, 최종 상태: {result['status']}")

    # 결과 반환
    if result["status"] == "completed":
        logger.info("메뉴 추출 성공")
        # Pydantic 모델을 dict로 변환
        menu_structure_dict = [item.model_dump() for item in result["menu_structure"]]
        return {
            "success": True,
            "root_url": result["root_url"],
            "menu_structure": menu_structure_dict,
        }
    else:
        logger.error(f"메뉴 추출 실패: {result.get('error', '알 수 없는 오류')}")
        return {
            "success": False,
            "error": result.get("error") or "알 수 없는 오류가 발생했습니다.",
        }


if __name__ == "__main__":
    # 예시 사용법
    example_url = "https://www.example.com"
    result = extract_website_menu(example_url)

    if result["success"]:
        print(f"메뉴 추출 성공: {example_url}")
        print(f"루트 URL: {result['root_url']}")
        print(f"메뉴 항목 수: {len(result['menu_structure'])}")

        # 최상위 메뉴 항목만 출력 (예시)
        print("\n최상위 메뉴 항목:")
        for item in result["menu_structure"]:
            if item.get("depth", 0) == 1:
                print(
                    f"- {item.get('title', '제목 없음')}: {item.get('url', '링크 없음')}"
                )
    else:
        print(f"메뉴 추출 실패: {result.get('error', '알 수 없는 오류')}")
