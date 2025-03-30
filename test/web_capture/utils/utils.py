"""
유틸리티 함수
"""

import os
import re
import hashlib
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Union

from ..config.config import logger


def normalize_url(url: str) -> str:
    """
    URL을 정규화합니다.

    Args:
        url: 정규화할 URL

    Returns:
        정규화된 URL
    """
    # URL에 프로토콜이 없는 경우 추가
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # URL 끝에 슬래시 추가
    parsed = urlparse(url)
    if not parsed.path:
        url = f"{url}/"

    return url


def generate_filename(
    url: str, device_type: str, template: str = "{timestamp}_{device}_{url_hash}"
) -> str:
    """
    캡처 파일 이름 생성

    Args:
        url: 캡처할 URL
        device_type: 디바이스 유형
        template: 파일명 템플릿

    Returns:
        생성된 파일명 (확장자 제외)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    domain = urlparse(url).netloc.replace("www.", "")

    # 템플릿 적용
    filename = template.format(
        timestamp=timestamp,
        device=device_type.lower(),
        url_hash=url_hash,
        domain=domain,
    )

    # 파일명에 유효하지 않은 문자 제거
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)

    return filename


def ensure_dir(directory: str) -> str:
    """
    디렉토리가 존재하는지 확인하고, 없으면 생성합니다.

    Args:
        directory: 확인할 디렉토리 경로

    Returns:
        생성된 디렉토리 경로
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def clean_url_for_display(url: str, max_length: int = 50) -> str:
    """
    표시용 URL 정리

    Args:
        url: 정리할 URL
        max_length: 최대 길이

    Returns:
        정리된 URL
    """
    # 프로토콜 제거
    cleaned = re.sub(r"^https?://", "", url)

    # 길이 제한
    if len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + "..."

    return cleaned


def parse_url_list(input_file: str) -> List[str]:
    """
    파일에서 URL 목록을 읽어옵니다.

    Args:
        input_file: URL 목록이 있는 파일 경로

    Returns:
        URL 목록
    """
    urls = []

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                # 주석 및 빈 줄 제외
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)

        logger.info(f"{len(urls)}개의 URL을 로드했습니다.")
        return urls

    except Exception as e:
        logger.error(f"URL 파일 읽기 오류: {str(e)}")
        return []
