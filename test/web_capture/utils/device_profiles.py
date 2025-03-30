"""
디바이스 프로필 정의
"""

from typing import Dict
from ..models.models import DeviceType, DeviceProfile


# 기본 디바이스 프로필 정의
DEVICE_PROFILES: Dict[DeviceType, DeviceProfile] = {
    DeviceType.DESKTOP: DeviceProfile(
        width=1920,
        height=1080,
        device_scale_factor=1.0,
        is_mobile=False,
        has_touch=False,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    ),
    DeviceType.TABLET: DeviceProfile(
        width=768,
        height=1024,
        device_scale_factor=2.0,
        is_mobile=True,
        has_touch=True,
        user_agent="Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    ),
    DeviceType.MOBILE: DeviceProfile(
        width=375,
        height=812,
        device_scale_factor=3.0,
        is_mobile=True,
        has_touch=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    ),
}


def get_device_profile(device_type: DeviceType) -> DeviceProfile:
    """
    디바이스 유형에 해당하는 프로필을 반환합니다.

    Args:
        device_type: 디바이스 유형

    Returns:
        해당 디바이스의 프로필
    """
    return DEVICE_PROFILES.get(device_type, DEVICE_PROFILES[DeviceType.DESKTOP])
