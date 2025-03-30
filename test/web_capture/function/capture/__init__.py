"""
웹페이지 캡처 기능 모듈

이 모듈은 Playwright를 사용하여 웹 페이지를 다양한 디바이스 유형으로
캡처하는 기능을 제공합니다.
"""

from .browser import get_browser, close_browser
from .page_capture import capture_single_page, capture_page
from .batch_capture import capture_multiple_pages, capture_multiple_pages_async
from .gif_generator import create_scrolling_gif
from .utils import close_popups, prepare_page_for_capture, create_capture_directory

__all__ = [
    "get_browser",
    "close_browser",
    "capture_single_page",
    "capture_page",
    "capture_multiple_pages",
    "capture_multiple_pages_async",
    "create_scrolling_gif",
    "close_popups",
    "prepare_page_for_capture",
    "create_capture_directory",
]
