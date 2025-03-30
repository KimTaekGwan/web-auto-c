"""
웹페이지 캡처 핵심 기능
"""

import os
import asyncio
from datetime import datetime
from typing import Optional

from playwright.async_api import Page

from ...config.config import logger
from ...models.models import DeviceType, PageCapture
from ...utils.device_profiles import get_device_profile
from ...utils.utils import normalize_url, generate_filename, ensure_dir

from .browser import get_browser
from .gif_generator import create_scrolling_gif


async def capture_single_page(
    url: str,
    device_type: DeviceType,
    output_dir: str,
    wait_time: float = 2.0,
    scroll_page: bool = False,
    viewport_only: bool = True,
    max_retries: int = 2,
    timeout: int = 30,
    create_gif: bool = False,
    gif_duration: float = 5.0,
    gif_fps: int = 10,
    scroll_speed: float = 1.0,
) -> PageCapture:
    """
    단일 페이지 캡처

    Args:
        url: 캡처할 URL
        device_type: 디바이스 유형
        output_dir: 출력 디렉토리
        wait_time: 페이지 로딩 후 대기 시간
        scroll_page: 페이지를 스크롤하면서 캡처할지 여부
        viewport_only: 뷰포트만 캡처할지 여부
        max_retries: 최대 재시도 횟수
        timeout: 페이지 로딩 타임아웃
        create_gif: GIF 생성 여부
        gif_duration: GIF 지속 시간(초)
        gif_fps: GIF 프레임 레이트
        scroll_speed: 스크롤 속도 배율

    Returns:
        캡처 결과 객체
    """
    browser = None
    page = None
    retry_count = 0
    error_msg = None
    gif_path = None

    # 디바이스 프로필 가져오기
    device_profile = get_device_profile(device_type)

    try:
        # URL 정규화
        normalized_url = normalize_url(url)

        # 출력 디렉토리 생성
        ensure_dir(output_dir)

        # 파일명 생성
        filename = generate_filename(url, device_type.value)
        file_path = os.path.join(output_dir, f"{filename}.png")

        # GIF 파일 경로 생성
        gif_filename = None
        if create_gif:
            gif_filename = f"{filename}_scroll.gif"
            gif_path = os.path.join(output_dir, gif_filename)

        # 브라우저 가져오기
        browser = await get_browser()

        while retry_count <= max_retries:
            try:
                # 페이지 생성
                page = await browser.new_page()

                # 뷰포트 및 디바이스 설정
                await page.set_viewport_size(
                    {"width": device_profile.width, "height": device_profile.height}
                )

                # 유저 에이전트 설정
                if device_profile.user_agent:
                    await page.set_extra_http_headers(
                        {"User-Agent": device_profile.user_agent}
                    )

                # 페이지 로딩
                logger.info(f"페이지 로딩 중: {normalized_url} ({device_type})")
                await page.goto(
                    normalized_url, timeout=timeout * 1000, wait_until="networkidle"
                )

                # 추가 대기 시간
                await asyncio.sleep(wait_time)

                # 채널톡 메신저 닫기
                try:
                    await page.evaluate("window.ChannelIO('hideMessenger')")
                    logger.info("채널톡 메신저 닫기 실행")
                    await asyncio.sleep(0.5)  # 실행 후 약간의 대기 시간
                except Exception as e:
                    logger.warning(f"채널톡 메신저 닫기 실패 (무시하고 계속 진행)")

                # GIF 생성
                if create_gif:
                    from ...models.models import CaptureConfig

                    gif_path = await create_scrolling_gif(
                        page=page,
                        url=normalized_url,
                        output_path=gif_path,
                        config=CaptureConfig(
                            gif_duration=gif_duration,
                            gif_fps=gif_fps,
                            scroll_speed=scroll_speed,
                        ),
                    )
                    # GIF 생성 후 페이지 맨 위로 스크롤
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)

                # 스크린샷 옵션 설정
                screenshot_options = {
                    "path": file_path,
                    "full_page": not viewport_only,
                }

                # 스크롤 캡처
                if scroll_page and not viewport_only and not create_gif:
                    # 페이지 스크롤 및 로딩 대기
                    for scroll_pos in range(0, 10000, device_profile.height):
                        await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                        await asyncio.sleep(0.2)

                    # 페이지 맨 위로 스크롤
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)

                # 스크린샷 촬영
                await page.screenshot(**screenshot_options)
                logger.info(f"캡처 완료: {filename}.png")

                # 성공적인 캡처 결과 반환
                return PageCapture(
                    url=normalized_url,
                    device_type=device_type,
                    file_path=file_path,
                    timestamp=datetime.now(),
                    width=device_profile.width,
                    height=device_profile.height,
                    success=True,
                    gif_path=gif_path,
                    metadata={
                        "device_scale_factor": device_profile.device_scale_factor,
                        "is_mobile": device_profile.is_mobile,
                        "viewport_only": viewport_only,
                    },
                )

            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                logger.warning(f"캡처 실패 ({retry_count}/{max_retries}): {error_msg}")

                # 페이지 닫기
                if page:
                    await page.close()
                    page = None

                if retry_count <= max_retries:
                    # 잠시 대기 후 재시도
                    await asyncio.sleep(1.0)
                else:
                    # 최대 재시도 횟수 초과
                    break

    except Exception as e:
        error_msg = str(e)
        logger.error(f"캡처 오류: {error_msg}")

    finally:
        # 페이지 닫기
        if page:
            await page.close()

    # 실패한 경우
    return PageCapture(
        url=url,
        device_type=device_type,
        file_path="",
        timestamp=datetime.now(),
        width=device_profile.width,
        height=device_profile.height,
        success=False,
        error=error_msg or "알 수 없는 오류",
        metadata={},
    )


def capture_page(
    url: str, device_type: DeviceType, output_dir: str, **kwargs
) -> PageCapture:
    """
    단일 페이지 캡처 (동기식 API)

    Args:
        url: 캡처할 URL
        device_type: 디바이스 유형
        output_dir: 출력 디렉토리
        **kwargs: 추가 캡처 옵션

    Returns:
        캡처 결과
    """
    # 비동기 코드를 동기적으로 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        capture = loop.run_until_complete(
            capture_single_page(
                url=url, device_type=device_type, output_dir=output_dir, **kwargs
            )
        )
        return capture
    finally:
        loop.close()
