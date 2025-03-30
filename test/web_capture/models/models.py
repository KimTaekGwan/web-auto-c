"""
데이터 모델 정의
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class DeviceType(str, Enum):
    """디바이스 유형 정의"""

    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class DeviceProfile(BaseModel):
    """디바이스 프로필 정의"""

    width: int
    height: int
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False
    user_agent: Optional[str] = None


class CaptureConfig(BaseModel):
    """캡처 설정"""

    devices: List[DeviceType] = Field(
        default=[DeviceType.DESKTOP], description="캡처할 디바이스 유형 목록"
    )
    wait_time: float = Field(
        default=2.0, description="페이지 로딩 후 캡처 전 대기 시간(초)"
    )
    scroll_page: bool = Field(
        default=False, description="페이지 전체를 스크롤하면서 캡처할지 여부"
    )
    max_height: Optional[int] = Field(
        default=None, description="스크롤 캡처 시 최대 높이 (픽셀)"
    )
    viewport_only: bool = Field(default=True, description="뷰포트만 캡처할지 여부")
    output_dir: str = Field(
        default="./captures", description="캡처 이미지 저장 디렉토리"
    )
    filename_template: str = Field(
        default="{timestamp}_{device}_{url_hash}", description="파일명 템플릿"
    )
    parallel_count: int = Field(default=3, description="병렬 캡처 프로세스 수")
    max_retries: int = Field(default=2, description="캡처 실패 시 최대 재시도 횟수")
    timeout: int = Field(default=30, description="페이지 로딩 타임아웃(초)")
    create_gif: bool = Field(
        default=False, description="스크롤하면서 움짤(GIF)을 생성할지 여부"
    )
    gif_duration: float = Field(
        default=5.0, description="생성된 GIF의 총 재생 시간(초)"
    )
    gif_fps: int = Field(default=10, description="생성된 GIF의 초당 프레임 수")
    scroll_speed: float = Field(
        default=1.0, description="스크롤 속도 배율 (1.0=기본, 2.0=2배 빠름)"
    )


class PageCapture(BaseModel):
    """개별 페이지 캡처 정보"""

    url: str
    device_type: DeviceType
    file_path: str
    timestamp: datetime = Field(default_factory=datetime.now)
    width: int
    height: int
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    gif_path: Optional[str] = None


class CaptureResult(BaseModel):
    """캡처 결과"""

    captures: List[PageCapture] = Field(default_factory=list)
    success_count: int = 0
    error_count: int = 0
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None  # 초 단위

    def add_capture(self, capture: PageCapture):
        """캡처 결과 추가"""
        self.captures.append(capture)
        if capture.success:
            self.success_count += 1
        else:
            self.error_count += 1

    def complete(self):
        """캡처 작업 완료 처리"""
        self.end_time = datetime.now()
        if self.start_time:
            self.total_duration = (self.end_time - self.start_time).total_seconds()
