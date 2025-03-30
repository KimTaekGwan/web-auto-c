import logging
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


# 로깅 설정
def setup_logging():
    """
    애플리케이션 로깅 설정을 구성합니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("menu_extractor")


# 로거 생성
logger = setup_logging()


# 모델 설정
class ModelConfig:
    """
    LLM 모델 설정을 위한 클래스
    """

    # 기본 모델 설정
    DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
    DEFAULT_TEMPERATURE = 0


# 플레이어라이트 설정
class PlaywrightConfig:
    """
    Playwright 설정을 위한 클래스
    """

    HEADLESS = True
    TIMEOUT = 30000  # 30초
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    SLOW_MO = 100  # 100ms
