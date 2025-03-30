"""
여러 페이지 동시 캡처 모듈
"""

import asyncio
from typing import List, Optional

from ...config.config import logger
from ...models.models import CaptureConfig, CaptureResult
from ...utils.utils import ensure_dir
from ...utils.queue_manager import CaptureTask

from .browser import get_browser, close_browser
from .page_capture import capture_single_page


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


def process_capture_task(task: CaptureTask) -> Optional[object]:
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
