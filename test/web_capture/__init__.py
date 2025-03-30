"""
web_capture - 웹페이지 캡처 모듈

이 모듈은 URL 목록을 기반으로 다양한 디바이스 크기에서 웹페이지를 캡처합니다.
"""

from .version import __version__

from .models.models import CaptureConfig, CaptureResult, DeviceType
from .function.page_capture import capture_page, capture_multiple_pages


__all__ = [
    "CaptureConfig",
    "CaptureResult",
    "DeviceType",
    "capture_page",
    "capture_multiple_pages",
    "__version__",
]
