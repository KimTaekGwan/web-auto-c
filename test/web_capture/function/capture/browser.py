"""
브라우저 인스턴스 관리 모듈
"""

import asyncio
from typing import Optional

from playwright.async_api import async_playwright, Browser
from ...config.config import logger, load_config_from_env

# 브라우저 싱글톤 인스턴스
_browser_instance = None


async def get_browser(browser_type: str = "chromium") -> Browser:
    """
    Playwright 브라우저 인스턴스 가져오기 (싱글톤)

    Args:
        browser_type: 브라우저 유형 (chromium, firefox, webkit)

    Returns:
        브라우저 인스턴스
    """
    global _browser_instance

    if _browser_instance is None:
        # 설정 로드
        config = load_config_from_env()

        # Playwright 시작
        playwright = await async_playwright().start()

        # 브라우저 선택
        if browser_type == "firefox":
            _browser_instance = await playwright.firefox.launch(headless=True)
        elif browser_type == "webkit":
            _browser_instance = await playwright.webkit.launch(headless=True)
        else:
            _browser_instance = await playwright.chromium.launch(headless=True)

        logger.info(f"{browser_type} 브라우저 시작")

    return _browser_instance


async def close_browser():
    """브라우저 인스턴스 종료"""
    global _browser_instance

    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None
        logger.info("브라우저 종료")
