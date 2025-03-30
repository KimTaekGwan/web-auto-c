"""
캡처 관련 유틸리티 함수 모듈

웹페이지 캡처에 필요한 보조 기능들을 제공합니다.
"""

import os
import re
import asyncio
import hashlib
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urlparse, quote

from playwright.async_api import Page, Error as PlaywrightError
from ...config.config import logger


async def close_popups(page: Page) -> None:
    """
    웹페이지에서 일반적인 팝업/모달 닫기 시도

    일반적인 웹사이트의 팝업, 모달, 쿠키 동의 창 등을 자동으로 닫습니다.

    Args:
        page: Playwright 페이지 객체
    """
    try:
        # 채널톡 닫기 시도
        try:
            await page.evaluate("window.ChannelIO && window.ChannelIO('hideMessenger')")
            logger.debug("채널톡 메신저 닫기 시도")
            await asyncio.sleep(0.3)
        except Exception:
            pass

        # ESC 키 눌러서 모달 닫기 시도
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.2)

        # 일반적인 닫기 버튼 클릭 시도 (팝업/모달/쿠키 동의)
        selectors = [
            ".modal-close",
            ".close-button",
            ".popup-close",
            "[aria-label='닫기']",
            "[aria-label='close']",
            ".cookie-consent-accept",
            "#accept-cookies",
            ".agree-button",
            ".consent-button",
            ".consent-accept",
            ".modal .btn-close",
            ".modal .close",
        ]

        # 언어별 닫기 버튼 텍스트
        close_texts = ["닫기", "Close", "close", "Accept", "동의", "확인", "OK", "Ok"]

        # 텍스트가 있는 버튼 찾기
        for text in close_texts:
            try:
                button = await page.get_by_text(text, exact=True).first.element_handle()
                if button:
                    await button.click()
                    logger.debug(f"'{text}' 텍스트가 있는 버튼 클릭")
                    await asyncio.sleep(0.2)
            except Exception:
                pass

        # 선택자로 버튼 찾기
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible():
                        await element.click()
                        logger.debug(f"팝업/모달 닫기 버튼 클릭: {selector}")
                        await asyncio.sleep(0.2)
            except Exception:
                continue

    except Exception as e:
        logger.warning(f"팝업/모달 닫기 실패 (무시하고 계속): {str(e)}")


async def prepare_page_for_capture(
    page: Page, wait_time: float = 1.0, stabilize: bool = True
) -> None:
    """
    캡처 전 페이지 준비 (스크롤, 대기, 팝업 닫기 등)

    페이지가 완전히 로딩되고 안정화될 때까지 준비합니다.

    Args:
        page: Playwright 페이지 객체
        wait_time: 추가 대기 시간 (초)
        stabilize: 페이지 안정화 시도 여부
    """
    try:
        # 페이지 로딩 완료 대기
        await page.wait_for_load_state("load")

        # 네트워크 활동 대기
        if stabilize:
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightError:
                logger.debug("네트워크 활동 대기 시간 초과 (계속 진행)")

        # 팝업/모달 닫기
        await close_popups(page)

        # 페이지 맨 위로 스크롤
        await page.evaluate("window.scrollTo(0, 0)")

        # 페이지 안정화를 위한 추가 대기
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        # 애니메이션 정지 시도
        if stabilize:
            try:
                await page.evaluate(
                    """() => {
                    document.querySelectorAll('*').forEach(el => {
                        if (window.getComputedStyle(el).getPropertyValue('animation-name') !== 'none') {
                            el.style.animationPlayState = 'paused';
                        }
                    });
                }"""
                )
            except Exception:
                pass

    except Exception as e:
        logger.warning(f"페이지 준비 중 오류 발생 (계속 진행): {str(e)}")


def get_domain_from_url(url: str) -> str:
    """
    URL에서 도메인 이름 추출

    입력된 URL에서 메인 도메인 부분만 추출합니다.

    Args:
        url: 웹 URL

    Returns:
        str: 도메인 이름
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # www 제거
        if domain.startswith("www."):
            domain = domain[4:]

        # 포트 번호 제거
        domain = domain.split(":")[0]

        return domain
    except Exception:
        # URL 파싱 실패시 원본 반환
        return url


def get_safe_filename(url: str) -> str:
    """
    URL을 안전한 파일명으로 변환

    URL을 파일 시스템에서 사용 가능한 안전한 문자열로 변환합니다.

    Args:
        url: 웹 URL

    Returns:
        str: 파일 시스템에 안전한 문자열
    """
    # 도메인과 경로 추출
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path

        if not path or path == "/":
            return domain.replace("www.", "")

        # 경로의 마지막 부분 추출
        path_parts = path.rstrip("/").split("/")
        last_part = path_parts[-1]

        # 파일명으로 적합하지 않은 문자 제거
        safe_part = re.sub(r"[^\w\-\.]", "_", last_part)

        # 너무 긴 경우 해시 사용
        if len(safe_part) > 50:
            path_hash = hashlib.md5(path.encode()).hexdigest()[:8]
            return f"{domain.replace('www.', '')}_{path_hash}"

        return f"{domain.replace('www.', '')}_{safe_part}"

    except Exception:
        # URL 해시값 반환
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"url_{url_hash}"


def create_capture_directory(base_dir: str, url: str) -> str:
    """
    URL별 캡처 디렉토리 생성

    URL 기반으로 캡처 결과를 저장할 디렉토리를 생성합니다.

    Args:
        base_dir: 기본 디렉토리
        url: 캡처할 URL

    Returns:
        str: 생성된 디렉토리 경로
    """
    domain = get_domain_from_url(url)

    # 디렉토리 생성
    output_dir = os.path.join(base_dir, domain)
    os.makedirs(output_dir, exist_ok=True)

    return output_dir


def get_url_hash(url: str) -> str:
    """
    URL의 해시값 생성

    URL을 고유하게 식별할 수 있는 짧은 해시값을 생성합니다.

    Args:
        url: 웹 URL

    Returns:
        str: URL의 해시값
    """
    return hashlib.md5(url.encode()).hexdigest()[:10]
