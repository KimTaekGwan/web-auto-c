from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, HttpUrl, UUID4, AnyUrl, Field
from uuid import UUID


class TagBase(BaseModel):
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SiteBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SiteCreate(SiteBase):
    pass


class Site(SiteBase):
    id: UUID4
    first_captured_at: Optional[datetime] = None
    last_captured_at: Optional[datetime] = None
    capture_count: Optional[int] = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MenuStructureBase(BaseModel):
    structure: Dict[str, Any]
    extraction_method: Optional[str] = None
    verified: bool = False


class MenuStructureCreate(MenuStructureBase):
    site_id: UUID4
    capture_id: UUID4


class MenuStructure(MenuStructureBase):
    id: UUID4
    site_id: UUID4
    capture_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PageBase(BaseModel):
    url: str
    title: Optional[str] = None
    menu_path: Optional[str] = None
    depth: int = 0
    status: Optional[str] = None
    page_metadata: Optional[Dict[str, Any]] = None


class PageCreate(PageBase):
    site_id: UUID4
    capture_id: UUID4


class Page(PageBase):
    id: UUID4
    site_id: UUID4
    capture_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PageScreenshotBase(BaseModel):
    device_type: str
    width: int
    screenshot_path: str
    thumbnail_path: Optional[str] = None
    is_current: bool = True


class PageScreenshotCreate(PageScreenshotBase):
    page_id: UUID4


class PageScreenshot(PageScreenshotBase):
    id: UUID4
    page_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaptureBase(BaseModel):
    url: str
    devices: Dict[str, bool] = {"desktop": True, "mobile": False, "tablet": False}
    options: Optional[Dict[str, Any]] = None


class CaptureCreate(CaptureBase):
    site_id: UUID4


class Capture(CaptureBase):
    id: UUID4
    site_id: UUID4
    status: str
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScreenshotBase(BaseModel):
    device: str
    url: str
    width: int
    height: int
    screenshot_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


class ScreenshotCreate(ScreenshotBase):
    capture_id: UUID4


class Screenshot(ScreenshotBase):
    id: UUID4
    capture_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class PageDetail(Page):
    screenshots: List[PageScreenshot] = []
    tags: List[Tag] = []

    class Config:
        from_attributes = True


class CaptureDetail(Capture):
    screenshots: List[Screenshot] = []
    menu_structures: List[MenuStructure] = []
    pages: List[Page] = []
    site: Optional[Site] = None

    class Config:
        from_attributes = True


class SiteDetail(Site):
    captures: List[Capture] = []
    menu_structures: List[MenuStructure] = []
    pages: List[Page] = []
    tags: List[Tag] = []

    class Config:
        from_attributes = True


# 대시보드 통계 스키마
class RecentCapture(BaseModel):
    id: str
    url: str
    status: str
    createdAt: Optional[str] = None
    devices: List[str] = []
    siteName: Optional[str] = None


class DeviceStats(BaseModel):
    desktop: int = 0
    tablet: int = 0
    mobile: int = 0


class DashboardStats(BaseModel):
    totalSites: int = 0
    totalCaptures: int = 0
    totalTags: int = 0
    recentCaptures: List[RecentCapture] = []
    deviceStats: DeviceStats = Field(default_factory=DeviceStats)


# 순환 참조 해결
SiteDetail.model_rebuild()
CaptureDetail.model_rebuild()
PageDetail.model_rebuild()
