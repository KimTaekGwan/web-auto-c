#!/usr/bin/env python3
"""
웹 캡처 CLI 진입점
"""

import sys
import os
import argparse
from datetime import datetime

# 현재 스크립트의 경로를 가져옵니다
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리(프로젝트 루트)를 시스템 경로에 추가합니다
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 직접 필요한 모듈 임포트
from web_capture.models.models import DeviceType, CaptureConfig
from web_capture.function.capture import capture_multiple_pages
from web_capture.utils.utils import parse_url_list, ensure_dir
from web_capture.utils.storage import save_metadata, create_report
from web_capture.config.config import logger
from web_capture.version import __version__


def main():
    """메인 CLI 인터페이스"""
    parser = argparse.ArgumentParser(description="웹페이지 캡처 도구")

    # URL 관련 인자
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument("--url", "-u", help="캡처할 단일 URL")
    url_group.add_argument(
        "--file", "-f", default="menu_urls.txt", help="URL 목록이 있는 파일 경로"
    )

    # 디바이스 관련 인자
    parser.add_argument(
        "--devices",
        "-d",
        choices=["desktop", "tablet", "mobile", "all"],
        default="desktop",
        help="캡처할 디바이스 유형 (기본값: desktop)",
    )

    # 출력 관련 인자
    parser.add_argument(
        "--output",
        "-o",
        default="./data/captures",
        help="캡처 이미지 저장 디렉토리 (기본값: ./data/captures)",
    )

    # 캡처 옵션
    parser.add_argument(
        "--wait",
        "-w",
        type=float,
        default=2.0,
        help="페이지 로딩 후 캡처 전 대기 시간(초) (기본값: 2.0)",
    )

    parser.add_argument(
        "--scroll", action="store_true", help="페이지 전체를 스크롤하면서 캡처"
    )

    parser.add_argument(
        "--full-page",
        action="store_true",
        help="전체 페이지 캡처 (뷰포트만 캡처하지 않음)",
    )

    # 움짤(GIF) 생성 옵션 그룹
    gif_group = parser.add_argument_group("움짤(GIF) 생성 옵션")

    gif_group.add_argument(
        "--create-gif",
        action="store_true",
        help="페이지를 스크롤하면서 움짤(GIF)을 생성합니다",
    )

    gif_group.add_argument(
        "--gif-duration",
        type=float,
        default=5.0,
        help="생성된 GIF의 총 재생 시간(초) (기본값: 5.0)",
    )

    gif_group.add_argument(
        "--gif-fps",
        type=int,
        default=10,
        help="생성된 GIF의 초당 프레임 수 (기본값: 10)",
    )

    gif_group.add_argument(
        "--scroll-speed",
        type=float,
        default=0.7,
        help="스크롤 속도 배율 (1.0=기본, 2.0=2배 빠름, 0.5=2배 느림) (기본값: 0.7)",
    )

    parser.add_argument(
        "--parallel",
        "-p",
        type=int,
        default=3,
        help="병렬 캡처 프로세스 수 (기본값: 3)",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=30,
        help="페이지 로딩 타임아웃(초) (기본값: 30)",
    )

    parser.add_argument(
        "--retries",
        "-r",
        type=int,
        default=2,
        help="캡처 실패 시 최대 재시도 횟수 (기본값: 2)",
    )

    parser.add_argument("--report", action="store_true", help="HTML 보고서 생성")

    parser.add_argument(
        "--version", "-v", action="version", version=f"웹 캡처 도구 v{__version__}"
    )

    # 인자 파싱
    args = parser.parse_args()

    # URL 목록 준비
    urls = []
    if args.url:
        urls = [args.url]
    elif args.file:
        urls = parse_url_list(args.file)
        if not urls:
            logger.error(f"URL 파일에서 유효한 URL을 찾을 수 없습니다: {args.file}")
            sys.exit(1)

    # 디바이스 유형 처리
    devices = []
    if args.devices == "all":
        devices = [DeviceType.DESKTOP, DeviceType.TABLET, DeviceType.MOBILE]
    elif args.devices == "desktop":
        devices = [DeviceType.DESKTOP]
    elif args.devices == "tablet":
        devices = [DeviceType.TABLET]
    elif args.devices == "mobile":
        devices = [DeviceType.MOBILE]

    # 출력 디렉토리 확인
    output_dir = ensure_dir(args.output)

    # GIF 생성 옵션이 활성화되어 있으면 스크롤도 활성화
    scroll_page = args.scroll
    if args.create_gif:
        scroll_page = True

    # 캡처 설정 구성
    config = CaptureConfig(
        devices=devices,
        wait_time=args.wait,
        scroll_page=scroll_page,
        viewport_only=not args.full_page,
        output_dir=output_dir,
        parallel_count=args.parallel,
        max_retries=args.retries,
        timeout=args.timeout,
        create_gif=args.create_gif,
        gif_duration=args.gif_duration,
        gif_fps=args.gif_fps,
        scroll_speed=args.scroll_speed,
    )

    logger.info(f"웹 캡처 시작: {len(urls)}개 URL, {len(devices)}개 디바이스 유형")
    start_time = datetime.now()

    # 캡처 실행
    result = capture_multiple_pages(urls, config)

    # 메타데이터 저장
    metadata_file = save_metadata(result, output_dir)

    # 보고서 생성
    report_file = None
    if args.report:
        report_file = create_report(result, output_dir)

    # 결과 보고
    print(f"\n캡처 완료:")
    print(f"  - 총 캡처: {result.success_count + result.error_count}")
    print(f"  - 성공: {result.success_count}")
    print(f"  - 실패: {result.error_count}")
    print(f"  - 소요 시간: {result.total_duration:.2f}초")
    print(f"  - 저장 위치: {output_dir}")

    # 보고서 출력
    if report_file:
        print(f"  - 보고서: {report_file}")

    # GIF 결과 출력
    if args.create_gif:
        gif_files = [
            cap.gif_path
            for cap in result.captures
            if hasattr(cap, "gif_path") and cap.gif_path
        ]
        if gif_files:
            print(f"  - 생성된 GIF 파일 수: {len(gif_files)}")
            for gif_file in gif_files[:5]:  # 첫 5개만 출력
                print(f"    * {gif_file}")
            if len(gif_files) > 5:
                print(f"      ... 외 {len(gif_files) - 5}개")


if __name__ == "__main__":
    main()
