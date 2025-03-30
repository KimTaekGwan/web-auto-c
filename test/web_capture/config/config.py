"""
설정 및 로깅 관련 유틸리티
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 기본 설정
DEFAULT_CONFIG = {
    "output_dir": "./captures",
    "log_dir": "./logs",
    "log_level": "INFO",
    "max_parallel": 3,
    "browser_type": "chromium",  # chromium, firefox, webkit
}


# 환경 변수에서 설정 로드
def load_config_from_env():
    """환경 변수에서 설정 로드"""
    config = DEFAULT_CONFIG.copy()

    if os.environ.get("WEB_CAPTURE_OUTPUT_DIR"):
        config["output_dir"] = os.environ.get("WEB_CAPTURE_OUTPUT_DIR")

    if os.environ.get("WEB_CAPTURE_LOG_DIR"):
        config["log_dir"] = os.environ.get("WEB_CAPTURE_LOG_DIR")

    if os.environ.get("WEB_CAPTURE_LOG_LEVEL"):
        config["log_level"] = os.environ.get("WEB_CAPTURE_LOG_LEVEL")

    if os.environ.get("WEB_CAPTURE_MAX_PARALLEL"):
        try:
            config["max_parallel"] = int(os.environ.get("WEB_CAPTURE_MAX_PARALLEL"))
        except (ValueError, TypeError):
            pass

    if os.environ.get("WEB_CAPTURE_BROWSER_TYPE"):
        config["browser_type"] = os.environ.get("WEB_CAPTURE_BROWSER_TYPE")

    return config


# 로거 설정
def setup_logger(name="web_capture", log_dir=None, level=None):
    """로깅 설정"""
    config = load_config_from_env()

    if log_dir is None:
        log_dir = config["log_dir"]

    if level is None:
        level = config["log_level"]

    # 로그 디렉토리 생성
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 로그 레벨 변환
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 핸들러 설정
    log_file = os.path.join(log_dir, f"{name}.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )

    # 포맷터 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # 핸들러 추가
    if not logger.handlers:
        logger.addHandler(file_handler)

        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# 기본 로거 생성
logger = setup_logger()
