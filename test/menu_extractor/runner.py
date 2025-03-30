#!/usr/bin/env python3

if __name__ == "__main__":
    # 패키지 실행을 위한 진입점
    import sys
    import os

    # 상위 디렉토리(프로젝트 루트)를 경로에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

    from menu_extractor.main import main

    sys.exit(main())
