"""
웹페이지 스크롤링 GIF 생성 모듈
"""

import io
import asyncio
from typing import Optional

from playwright.async_api import Page
from ...config.config import logger
from ...models.models import CaptureConfig


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
