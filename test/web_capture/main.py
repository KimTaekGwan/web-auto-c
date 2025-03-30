"""
웹 캡처 모듈 메인 파일

이 모듈은 웹 캡처 라이브러리 사용 예제를 보여줍니다.
실제 기능 구현은 function/capture/ 디렉토리의 모듈들에 있습니다.

호환성을 위해 run_capture() 함수가 유지되었지만,
새로운 코드에서는 CaptureConfig와 capture_multiple_pages를 직접 사용하는 것이 좋습니다.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models.models import CaptureConfig, DeviceType, CaptureResult
from .function.capture import capture_multiple_pages
from .utils.storage import save_metadata, create_report
from .utils.utils import ensure_dir


def run_capture(
    urls: List[str],
    devices: List[DeviceType] = None,
    output_dir: str = "./captures",
    wait_time: float = 2.0,
    scroll_page: bool = False,
    viewport_only: bool = True,
    parallel_count: int = 3,
    max_retries: int = 2,
    timeout: int = 30,
    create_html_report: bool = False,
    create_gif: bool = False,
    gif_duration: float = 5.0,
    gif_fps: int = 10,
    scroll_speed: float = 1.0,
) -> Dict[str, Any]:
    """
    Python API용 캡처 실행 함수 (호환성 유지용)

    새로운 코드에서는 다음과 같이 사용하는 것이 권장됩니다:

    ```python
    from web_capture import capture_multiple_pages, CaptureConfig, DeviceType

    config = CaptureConfig(
        devices=[DeviceType.DESKTOP],
        output_dir="./captures"
    )

    result = capture_multiple_pages(urls, config)
    ```

    Args:
        urls: 캡처할 URL 목록
        devices: 캡처할 디바이스 유형 목록 (기본값: [DeviceType.DESKTOP])
        output_dir: 출력 디렉토리 (기본값: ./captures)
        wait_time: 페이지 로딩 후 대기 시간 (기본값: 2.0)
        scroll_page: 페이지 스크롤 여부 (기본값: False)
        viewport_only: 뷰포트만 캡처 여부 (기본값: True)
        parallel_count: 병렬 처리 수 (기본값: 3)
        max_retries: 캡처 실패 시 최대 재시도 횟수 (기본값: 2)
        timeout: 페이지 로딩 타임아웃(초) (기본값: 30)
        create_html_report: HTML 보고서 생성 여부 (기본값: False)
        create_gif: 스크롤하면서 움짤(GIF) 생성 여부 (기본값: False)
        gif_duration: 생성된 GIF의 총 재생 시간(초) (기본값: 5.0)
        gif_fps: 생성된 GIF의 초당 프레임 수 (기본값: 10)
        scroll_speed: 스크롤 속도 배율 (1.0=기본, 2.0=2배 빠름) (기본값: 1.0)

    Returns:
        캡처 결과 정보를 담은 딕셔너리
    """
    # 기본값 설정
    if devices is None:
        devices = [DeviceType.DESKTOP]

    # 출력 디렉토리 확인
    output_dir = ensure_dir(output_dir)

    # GIF 생성이 활성화되어 있으면 스크롤도 활성화
    if create_gif:
        scroll_page = True

    # 캡처 설정
    config = CaptureConfig(
        devices=devices,
        wait_time=wait_time,
        scroll_page=scroll_page,
        viewport_only=viewport_only,
        output_dir=output_dir,
        parallel_count=parallel_count,
        max_retries=max_retries,
        timeout=timeout,
        create_gif=create_gif,
        gif_duration=gif_duration,
        gif_fps=gif_fps,
        scroll_speed=scroll_speed,
    )

    # 캡처 실행
    result = capture_multiple_pages(urls, config)

    # 메타데이터 저장
    metadata_file = save_metadata(result, output_dir)

    # 보고서 생성
    report_file = None
    if create_html_report:
        report_file = create_report(result, output_dir)

    # GIF 파일 목록
    gif_files = []
    if create_gif:
        for capture in result.captures:
            if hasattr(capture, "gif_path") and capture.gif_path:
                gif_files.append(capture.gif_path)

    # 결과 반환 (이전 버전 호환성을 위한 딕셔너리 형태)
    return {
        "success": result.success_count > 0,
        "total": result.success_count + result.error_count,
        "success_count": result.success_count,
        "error_count": result.error_count,
        "duration": result.total_duration,
        "output_dir": output_dir,
        "metadata_file": metadata_file,
        "report_file": report_file,
        "captures": [capture.model_dump() for capture in result.captures],
        "gif_files": gif_files if create_gif else None,
    }


if __name__ == "__main__":
    # 현대적인 사용법 예시
    from web_capture import CaptureConfig, DeviceType, capture_multiple_pages

    # 캡처 설정
    config = CaptureConfig(
        devices=[DeviceType.DESKTOP, DeviceType.MOBILE],
        output_dir="./example_captures",
        wait_time=3.0,
        scroll_page=True,
        viewport_only=False,
        create_gif=True,
        gif_duration=8.0,
        gif_fps=15,
    )

    # 캡처 실행
    result = capture_multiple_pages(["https://www.example.com"], config)

    # 메타데이터 및 보고서 생성
    metadata_file = save_metadata(result, config.output_dir)
    report_file = create_report(result, config.output_dir)

    # 결과 출력
    print(f"캡처 성공: {result.success_count > 0}")
    print(f"총 캡처: {result.success_count + result.error_count}")
    print(f"성공한 캡처: {result.success_count}")
    print(f"실패한 캡처: {result.error_count}")
    print(f"소요 시간: {result.total_duration:.2f}초")
    print(f"저장 위치: {config.output_dir}")

    if report_file:
        print(f"보고서 파일: {report_file}")

    # GIF 파일 출력
    gif_files = [
        cap.gif_path
        for cap in result.captures
        if hasattr(cap, "gif_path") and cap.gif_path
    ]
    if gif_files:
        print(f"생성된 GIF 파일:")
        for gif_file in gif_files:
            print(f"  - {gif_file}")
