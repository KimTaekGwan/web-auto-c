#!/usr/bin/env python3
"""
메뉴 추출기 CLI 진입점
"""

import sys
import os
import json
import argparse

# 현재 스크립트의 경로를 가져옵니다
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리(프로젝트 루트)를 시스템 경로에 추가합니다
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from menu_extractor.main import extract_website_menu


def main():
    """CLI 인터페이스 메인 함수"""
    # 인자 파서 설정
    parser = argparse.ArgumentParser(description="웹사이트 메뉴 구조 추출 도구")
    parser.add_argument("url", help="메뉴를 추출할 웹사이트 URL")
    parser.add_argument(
        "--output",
        "-o",
        help="결과를 저장할 파일 경로 (기본값: 표준 출력)",
        default=None,
    )
    parser.add_argument(
        "--pretty", "-p", help="JSON 출력을 보기 좋게 포맷팅", action="store_true"
    )

    # 인자 파싱
    args = parser.parse_args()

    # 메뉴 추출 실행
    result = extract_website_menu(args.url)

    # 결과 처리
    indent = 2 if args.pretty else None
    ensure_ascii = False

    # 결과 출력
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=indent, ensure_ascii=ensure_ascii)
        print(f"결과가 {args.output}에 저장되었습니다.")
    else:
        print(json.dumps(result, indent=indent, ensure_ascii=ensure_ascii))


if __name__ == "__main__":
    main()
