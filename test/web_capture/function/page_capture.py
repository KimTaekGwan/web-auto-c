"""
웹페이지 캡처 기능 (리팩토링됨)

이 모듈은 기존 기능 호환성을 위해 존재하며 새로운 구현은
capture/ 디렉토리 아래의 모듈에 있습니다.
"""

import os
import asyncio
import time
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page
from ..config.config import logger, load_config_from_env
from ..models.models import DeviceType, CaptureConfig, PageCapture, CaptureResult
from ..utils.device_profiles import get_device_profile
from ..utils.utils import normalize_url, generate_filename, ensure_dir
from ..utils.queue_manager import CaptureTask
from .capture import (
    capture_page,
    capture_multiple_pages,
    capture_single_page,
    capture_multiple_pages_async,
)


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


async def create_scrolling_gif(
    page: Page, url: str, output_path: str, config: CaptureConfig
) -> str:
    """
    페이지를 방향키로 스크롤하면서 GIF 생성

    Args:
        page: Playwright 페이지 객체
        url: 캡처할 URL
        output_path: 출력 파일 경로
        config: 캡처 설정

    Returns:
        생성된 GIF 파일 경로
    """
    try:
        # Pillow 라이브러리 import (필요시 pip install Pillow)
        from PIL import Image

        logger.info(f"GIF 생성 시작 (방향키 스크롤): {output_path}")

        # 총 프레임 수 계산
        total_frames = int(config.gif_duration * config.gif_fps)

        # 페이지 맨 위로 스크롤
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2.0)  # 초기 대기 시간 증가 (페이지 안정화)

        # 채널톡 메신저 닫기 시도
        try:
            await page.evaluate("window.ChannelIO('hideMessenger')")
            logger.info("GIF 생성 전 채널톡 메신저 닫기 실행")
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"GIF 생성 전 채널톡 메신저 닫기 실패 (무시)")

        # 이스케이프 키 눌러서 모달 닫기 (만약 있다면)
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)

        # 페이지 중앙 클릭하여 포커스 얻기
        width = await page.evaluate("window.innerWidth")
        height = await page.evaluate("window.innerHeight")
        await page.mouse.click(width // 2, height // 2)
        await asyncio.sleep(0.5)

        # document 요소에 포커스
        await page.evaluate(
            """
            document.documentElement.focus();
            document.body.focus();
            window.focus();
        """
        )

        # 프레임 캡처를 위한 설정
        frames = []

        # 키 입력 횟수 계산
        key_presses = max(20, total_frames // 3)  # 더 많은 키 입력 (최소 20회)

        # 키 입력 간격 계산 (GIF 길이에 맞춰서)
        key_press_interval = (config.gif_duration / key_presses) * config.scroll_speed

        logger.info(
            f"GIF 프레임 캡처 시작: 총 {total_frames}개 프레임, {key_presses}회 키 입력"
        )

        # 스크롤 카운터
        scroll_count = 0

        # 직접 스크롤 JS 명령 시도 횟수
        js_scroll_attempts = 0

        # 각 프레임 캡처 (맨 처음 프레임은 스크롤 없이 캡처)
        screenshot_bytes = await page.screenshot(type="png")
        image = Image.open(io.BytesIO(screenshot_bytes))
        frames.append(image)
        logger.debug(f"GIF 프레임 1/{total_frames} 캡처 완료 (초기 화면)")

        # 나머지 프레임 캡처
        for i in range(1, total_frames):
            curr_frame = i + 1

            # 프레임마다 스크롤 시도 (다양한 방법으로)
            if i % (total_frames // key_presses) == 0 and scroll_count < key_presses:
                scroll_count += 1
                js_scroll_attempts += 1

                # 다양한 스크롤 방법 시도 (스크롤 위치 저장)
                prev_scroll_pos = await page.evaluate("window.scrollY")

                # 방법 1: 단일 키 입력
                key_to_press = ["ArrowDown", "PageDown", "Space"][scroll_count % 3]
                await page.keyboard.press(key_to_press)
                logger.debug(f"키 입력: {key_to_press}")
                await asyncio.sleep(0.2)

                # 스크롤 위치 변화 확인
                new_scroll_pos = await page.evaluate("window.scrollY")
                scroll_change = new_scroll_pos - prev_scroll_pos

                # 스크롤이 효과가 없으면 다른 방법 시도
                if scroll_change < 10 and js_scroll_attempts <= 5:
                    # 방법 2: JS로 직접 스크롤
                    scroll_amount = 300 * (
                        js_scroll_attempts * 0.5 + 1
                    )  # 점점 더 크게 스크롤
                    await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                    logger.debug(f"JS 스크롤: {scroll_amount}px")
                    await asyncio.sleep(0.2)

                # 여전히 스크롤이 안 되면 마우스 휠 이벤트 발생
                new_scroll_pos = await page.evaluate("window.scrollY")
                if new_scroll_pos == prev_scroll_pos:
                    # 방법 3: 마우스 휠 이벤트
                    await page.mouse.wheel(0, 300)
                    logger.debug("마우스 휠 이벤트 발생")
                    await asyncio.sleep(0.2)

                    # 방법 4: 복합 키 이벤트 시뮬레이션
                    if js_scroll_attempts % 2 == 0:
                        # 탭 키로 포커스 이동 후 스페이스바
                        await page.keyboard.press("Tab")
                        await asyncio.sleep(0.1)
                        await page.keyboard.press("Space")
                        logger.debug("탭 + 스페이스바")

                # 키 입력 후 약간 대기 (스크롤 효과 적용)
                await asyncio.sleep(0.3)

            # 스크린샷 캡처
            screenshot_bytes = await page.screenshot(type="png")
            image = Image.open(io.BytesIO(screenshot_bytes))
            frames.append(image)

            # 현재 스크롤 위치 로깅
            scroll_y = await page.evaluate("window.scrollY")
            logger.debug(
                f"GIF 프레임 {curr_frame}/{total_frames} 캡처 완료 (스크롤 위치: {scroll_y}px)"
            )

            # 프레임 간 간격 유지
            remain_delay = (
                key_press_interval - 0.5  # 키 입력 및 대기 시간 감안
                if i % (total_frames // key_presses) == 0
                else key_press_interval
            )
            if remain_delay > 0:
                await asyncio.sleep(remain_delay)

        # 페이지를 맨 위로 다시 스크롤
        await page.evaluate("window.scrollTo(0, 0)")

        # GIF 저장
        if frames:
            # 이미지 최적화: 크기와 색상 수 줄이기
            for idx, frame in enumerate(frames):
                if frame.size[0] > 800:  # 너무 넓은 경우 리사이즈
                    ratio = 800 / frame.size[0]
                    new_height = int(frame.size[1] * ratio)
                    frames[idx] = frame.resize((800, new_height), Image.LANCZOS)

            # 기본 GIF 저장 속성
            gif_options = {
                "format": "GIF",
                "save_all": True,
                "append_images": frames[1:],
                "duration": int(1000 / config.gif_fps),  # 밀리초 단위
                "loop": 0,  # 무한 반복
                "optimize": True,  # 파일 크기 최적화
            }

            # 컬러 팔레트 최적화 시도
            try:
                frames[0].save(output_path, **gif_options)
            except Exception as e:
                logger.warning(f"최적화된 GIF 저장 실패, 기본 설정으로 시도: {str(e)}")
                # 컬러 옵션 제외하고 다시 시도
                frames[0].save(
                    output_path,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=int(1000 / config.gif_fps),
                    loop=0,
                )

            logger.info(f"GIF 생성 완료: {output_path}")
            return output_path
        else:
            logger.error("GIF 생성 실패: 캡처된 프레임 없음")
            return ""

    except ImportError:
        logger.error(
            "GIF 생성 실패: PIL 라이브러리가 설치되지 않음. 'pip install Pillow' 명령으로 설치하세요."
        )
        return ""
    except Exception as e:
        logger.error(f"GIF 생성 오류: {str(e)}")
        return ""


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
                    logger.warning(
                        f"채널톡 메신저 닫기 실패 (무시하고 계속 진행): {str(e)}"
                    )

                # GIF 생성
                if create_gif:
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


async def capture_multiple_pages_async(
    urls: List[str], config: CaptureConfig
) -> CaptureResult:
    """
    여러 페이지 캡처 (비동기 방식)

    Args:
        urls: 캡처할 URL 목록
        config: 캡처 설정

    Returns:
        캡처 결과
    """
    result = CaptureResult()

    # 출력 디렉토리 확인
    ensure_dir(config.output_dir)

    # 동시 실행 작업 수 제한
    semaphore = asyncio.Semaphore(config.parallel_count)

    async def capture_with_semaphore(url, device_type):
        async with semaphore:
            capture = await capture_single_page(
                url=url,
                device_type=device_type,
                output_dir=config.output_dir,
                wait_time=config.wait_time,
                scroll_page=config.scroll_page,
                viewport_only=config.viewport_only,
                max_retries=config.max_retries,
                timeout=config.timeout,
                create_gif=config.create_gif,
                gif_duration=config.gif_duration,
                gif_fps=config.gif_fps,
                scroll_speed=config.scroll_speed,
            )
            result.add_capture(capture)

    # 모든 작업 생성
    tasks = []
    for url in urls:
        for device_type in config.devices:
            tasks.append(capture_with_semaphore(url, device_type))

    # 모든 작업 실행
    logger.info(f"{len(tasks)}개 캡처 작업 시작")
    await asyncio.gather(*tasks)

    # 브라우저 종료
    await close_browser()

    # 결과 완료 처리
    result.complete()
    logger.info(
        f"캡처 작업 완료 (성공: {result.success_count}, 실패: {result.error_count})"
    )

    return result


def process_capture_task(task: CaptureTask) -> Optional[PageCapture]:
    """
    캡처 작업 처리 (큐 관리자용)

    Args:
        task: 캡처 작업

    Returns:
        캡처 결과
    """
    try:
        # 비동기 코드를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        capture = loop.run_until_complete(
            capture_single_page(
                url=task.url, device_type=task.device_type, output_dir=task.output_dir
            )
        )

        loop.close()
        return capture

    except Exception as e:
        logger.error(f"작업 처리 오류: {str(e)}")
        return None


def capture_page(url: str, config: CaptureConfig = None) -> PageCapture:
    """
    단일 페이지 캡처 (동기식 API)

    Args:
        url: 캡처할 URL
        config: 캡처 설정

    Returns:
        캡처 결과
    """
    if config is None:
        config = CaptureConfig()

    # 첫 번째 디바이스 유형 사용
    device_type = config.devices[0] if config.devices else DeviceType.DESKTOP

    # 비동기 코드를 동기적으로 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        capture = loop.run_until_complete(
            capture_single_page(
                url=url,
                device_type=device_type,
                output_dir=config.output_dir,
                wait_time=config.wait_time,
                scroll_page=config.scroll_page,
                viewport_only=config.viewport_only,
                max_retries=config.max_retries,
                timeout=config.timeout,
                create_gif=config.create_gif,
                gif_duration=config.gif_duration,
                gif_fps=config.gif_fps,
                scroll_speed=config.scroll_speed,
            )
        )
        return capture
    finally:
        loop.close()


def capture_multiple_pages(
    urls: List[str], config: CaptureConfig = None
) -> CaptureResult:
    """
    여러 페이지 캡처 (동기식 API)

    Args:
        urls: 캡처할 URL 목록
        config: 캡처 설정

    Returns:
        캡처 결과
    """
    if config is None:
        config = CaptureConfig()

    # 비동기 코드를 동기적으로 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(capture_multiple_pages_async(urls, config))
        return result
    finally:
        loop.close()


# 기존 API 호환성 유지
process_capture_task = lambda task: capture_page(
    url=task.url, device_type=task.device_type, output_dir=task.output_dir
)
