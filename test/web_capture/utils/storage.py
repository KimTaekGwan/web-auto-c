"""
캡처 결과 저장 관련 기능
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..config.config import logger
from ..models.models import CaptureResult, PageCapture
from .utils import ensure_dir


def save_image(image_data: bytes, output_path: str) -> bool:
    """
    이미지 데이터 저장

    Args:
        image_data: 저장할 이미지 바이너리 데이터
        output_path: 저장할 경로

    Returns:
        성공 여부
    """
    try:
        # 디렉토리 확인
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 이미지 저장
        with open(output_path, "wb") as f:
            f.write(image_data)

        logger.debug(f"이미지 저장 완료: {output_path}")
        return True

    except Exception as e:
        logger.error(f"이미지 저장 실패: {str(e)}")
        return False


def save_metadata(result: CaptureResult, output_dir: str) -> str:
    """
    캡처 결과 메타데이터 저장

    Args:
        result: 캡처 결과
        output_dir: 저장 디렉토리

    Returns:
        저장된 메타데이터 파일 경로
    """
    try:
        # 디렉토리 확인
        ensure_dir(output_dir)

        # 메타데이터 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_file = os.path.join(output_dir, f"metadata_{timestamp}.json")

        # Pydantic 모델을 dict로 변환
        metadata = result.model_dump()

        # JSON으로 저장
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"메타데이터 저장 완료: {metadata_file}")
        return metadata_file

    except Exception as e:
        logger.error(f"메타데이터 저장 실패: {str(e)}")
        return ""


def create_report(result: CaptureResult, output_dir: str) -> str:
    """
    캡처 결과 보고서 생성

    Args:
        result: 캡처 결과
        output_dir: 저장 디렉토리

    Returns:
        생성된 보고서 파일 경로
    """
    try:
        # 디렉토리 확인
        ensure_dir(output_dir)

        # 보고서 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"report_{timestamp}.html")

        # 간단한 HTML 보고서 생성
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("<html><head>")
            f.write("<meta charset='utf-8'>")
            f.write("<title>웹 캡처 보고서</title>")
            f.write("<style>")
            f.write("body { font-family: Arial, sans-serif; margin: 20px; }")
            f.write("h1 { color: #333; }")
            f.write("table { border-collapse: collapse; width: 100%; }")
            f.write(
                "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }"
            )
            f.write("th { background-color: #f2f2f2; }")
            f.write("tr:nth-child(even) { background-color: #f9f9f9; }")
            f.write(".success { color: green; }")
            f.write(".error { color: red; }")
            f.write("</style>")
            f.write("</head><body>")

            # 제목 및 요약
            f.write("<h1>웹 캡처 보고서</h1>")
            f.write(f"<p>생성 시간: {result.end_time}</p>")
            f.write(f"<p>총 캡처: {result.success_count + result.error_count}</p>")
            f.write(f"<p>성공: {result.success_count} / 실패: {result.error_count}</p>")
            f.write(f"<p>소요 시간: {result.total_duration:.2f}초</p>")

            # 캡처 결과 표
            f.write("<h2>캡처 결과</h2>")
            f.write("<table>")
            f.write(
                "<tr><th>URL</th><th>디바이스</th><th>상태</th><th>파일</th><th>시간</th></tr>"
            )

            for capture in result.captures:
                status_class = "success" if capture.success else "error"
                status_text = "성공" if capture.success else f"실패: {capture.error}"

                f.write("<tr>")
                f.write(f"<td>{capture.url}</td>")
                f.write(f"<td>{capture.device_type}</td>")
                f.write(f"<td class='{status_class}'>{status_text}</td>")

                if capture.success:
                    filename = os.path.basename(capture.file_path)
                    rel_path = os.path.relpath(capture.file_path, output_dir)
                    f.write(f"<td><a href='{rel_path}'>{filename}</a></td>")
                else:
                    f.write("<td>-</td>")

                f.write(f"<td>{capture.timestamp}</td>")
                f.write("</tr>")

            f.write("</table>")
            f.write("</body></html>")

        logger.info(f"보고서 생성 완료: {report_file}")
        return report_file

    except Exception as e:
        logger.error(f"보고서 생성 실패: {str(e)}")
        return ""
