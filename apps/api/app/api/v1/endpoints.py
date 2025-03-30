from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models import (
    Site,
    Capture,
    Screenshot,
    Tag,
    MenuStructure,
    Page,
    PageScreenshot,
    CaptureStatus,
)
from ...schemas import (
    SiteCreate,
    SiteDetail,
    Site as SiteSchema,
    CaptureCreate,
    CaptureDetail,
    Capture as CaptureSchema,
    ScreenshotCreate,
    Screenshot as ScreenshotSchema,
    TagCreate,
    Tag as TagSchema,
    MenuStructureCreate,
    MenuStructure as MenuStructureSchema,
    PageCreate,
    PageDetail,
    Page as PageSchema,
    PageScreenshotCreate,
    PageScreenshot as PageScreenshotSchema,
    DashboardStats,
)
from ...utils import generate_dummy_data

router = APIRouter()


# 대시보드 통계 엔드포인트
@router.get("/dashboard", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # 사이트 수 조회
    sites_result = await db.execute(select(func.count()).select_from(Site))
    total_sites = sites_result.scalar_one()

    # 캡처 수 조회
    captures_result = await db.execute(select(func.count()).select_from(Capture))
    total_captures = captures_result.scalar_one()

    # 태그 수 조회
    tags_result = await db.execute(select(func.count()).select_from(Tag))
    total_tags = tags_result.scalar_one()

    # 최근 캡처 목록 조회
    recent_captures_query = select(Capture).order_by(Capture.created_at.desc()).limit(5)
    recent_captures_result = await db.execute(recent_captures_query)
    recent_captures_db = recent_captures_result.scalars().all()

    recent_captures = []
    for capture in recent_captures_db:
        site_result = await db.execute(select(Site).filter(Site.id == capture.site_id))
        site = site_result.scalar_one_or_none()

        # 디바이스 형식 변환
        devices = []
        if isinstance(capture.devices, list):
            devices = capture.devices
        elif isinstance(capture.devices, dict):
            devices = [k for k, v in capture.devices.items() if v]
        else:
            try:
                # JSON 문자열인 경우 파싱
                import json

                devices_data = json.loads(capture.devices)
                if isinstance(devices_data, list):
                    devices = devices_data
                elif isinstance(devices_data, dict):
                    devices = [k for k, v in devices_data.items() if v]
            except:
                # 파싱 실패시 빈 리스트
                devices = []

        recent_captures.append(
            {
                "id": str(capture.id),
                "url": capture.url,
                "status": (
                    capture.status.value
                    if isinstance(capture.status, CaptureStatus)
                    else str(capture.status)
                ),
                "createdAt": (
                    capture.created_at.isoformat() if capture.created_at else None
                ),
                "devices": devices,
                "siteName": site.name if site else "Unknown",
            }
        )

    # 디바이스별 통계 - 직접 순회 방식으로 변경
    all_captures_query = select(Capture)
    all_captures_result = await db.execute(all_captures_query)
    all_captures = all_captures_result.scalars().all()

    desktop_count = 0
    tablet_count = 0
    mobile_count = 0

    for capture in all_captures:
        devices_data = None
        # JSON 데이터 파싱
        try:
            if isinstance(capture.devices, str):
                import json

                devices_data = json.loads(capture.devices)
            else:
                devices_data = capture.devices

            # 리스트 형태인 경우
            if isinstance(devices_data, list):
                if "desktop" in devices_data:
                    desktop_count += 1
                if "tablet" in devices_data:
                    tablet_count += 1
                if "mobile" in devices_data:
                    mobile_count += 1
            # 딕셔너리 형태인 경우
            elif isinstance(devices_data, dict):
                if devices_data.get("desktop"):
                    desktop_count += 1
                if devices_data.get("tablet"):
                    tablet_count += 1
                if devices_data.get("mobile"):
                    mobile_count += 1
        except:
            # 파싱 실패시 무시
            pass

    return {
        "totalSites": total_sites,
        "totalCaptures": total_captures,
        "totalTags": total_tags,
        "recentCaptures": recent_captures,
        "deviceStats": {
            "desktop": desktop_count,
            "tablet": tablet_count,
            "mobile": mobile_count,
        },
    }


# 더미 데이터 생성 엔드포인트
@router.post("/demo/generate", tags=["Demo"])
async def generate_demo_data(num_sites: int = 5, db: AsyncSession = Depends(get_db)):
    try:
        await generate_dummy_data(db, num_sites)
        return {"message": f"생성 완료: {num_sites}개의 사이트와 관련 캡처 및 스크린샷"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"더미 데이터 생성 중 오류 발생: {str(e)}"
        )


# Tag endpoints
@router.post("/tags", response_model=TagSchema, tags=["Tags"])
async def create_tag(tag: TagCreate, db: AsyncSession = Depends(get_db)):
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag


@router.get("/tags", response_model=List[TagSchema], tags=["Tags"])
async def read_tags(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Tag).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/tags/{tag_id}", response_model=TagSchema, tags=["Tags"])
async def read_tag(tag_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_tag_id = str(tag_id).replace("-", "")

    result = await db.execute(select(Tag).filter(Tag.id == normalized_tag_id))
    db_tag = result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag


@router.put("/tags/{tag_id}", response_model=TagSchema, tags=["Tags"])
async def update_tag(tag_id: UUID, tag: TagCreate, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_tag_id = str(tag_id).replace("-", "")

    result = await db.execute(select(Tag).filter(Tag.id == normalized_tag_id))
    db_tag = result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    for key, value in tag.model_dump().items():
        setattr(db_tag, key, value)

    await db.commit()
    await db.refresh(db_tag)
    return db_tag


@router.delete("/tags/{tag_id}", tags=["Tags"])
async def delete_tag(tag_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_tag_id = str(tag_id).replace("-", "")

    result = await db.execute(select(Tag).filter(Tag.id == normalized_tag_id))
    db_tag = result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    await db.delete(db_tag)
    await db.commit()
    return {"ok": True}


# Site endpoints
@router.post("/sites", response_model=SiteSchema, tags=["Sites"])
async def create_site(site: SiteCreate, db: AsyncSession = Depends(get_db)):
    db_site = Site(**site.model_dump())
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site


@router.get("/sites", response_model=List[SiteSchema], tags=["Sites"])
async def read_sites(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    query = select(Site).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sites/{site_id}", response_model=SiteDetail, tags=["Sites"])
async def read_site(site_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_site_id = str(site_id).replace("-", "")

    result = await db.execute(
        select(Site)
        .options(
            selectinload(Site.captures),
            selectinload(Site.menu_structures),
            selectinload(Site.pages),
        )
        .filter(Site.id == normalized_site_id)
    )
    db_site = result.scalar_one_or_none()
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    return db_site


@router.put("/sites/{site_id}", response_model=SiteSchema, tags=["Sites"])
async def update_site(
    site_id: UUID, site: SiteCreate, db: AsyncSession = Depends(get_db)
):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_site_id = str(site_id).replace("-", "")

    result = await db.execute(select(Site).filter(Site.id == normalized_site_id))
    db_site = result.scalar_one_or_none()
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")

    for key, value in site.model_dump().items():
        setattr(db_site, key, value)

    await db.commit()
    await db.refresh(db_site)
    return db_site


@router.delete("/sites/{site_id}", tags=["Sites"])
async def delete_site(site_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_site_id = str(site_id).replace("-", "")

    result = await db.execute(select(Site).filter(Site.id == normalized_site_id))
    db_site = result.scalar_one_or_none()
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")

    await db.delete(db_site)
    await db.commit()
    return {"ok": True}


# Site Tags 관리
@router.post("/sites/{site_id}/tags/{tag_id}", tags=["Sites", "Tags"])
async def add_tag_to_site(
    site_id: UUID, tag_id: UUID, db: AsyncSession = Depends(get_db)
):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_site_id = str(site_id).replace("-", "")
    normalized_tag_id = str(tag_id).replace("-", "")

    site_result = await db.execute(select(Site).filter(Site.id == normalized_site_id))
    db_site = site_result.scalar_one_or_none()
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")

    tag_result = await db.execute(select(Tag).filter(Tag.id == normalized_tag_id))
    db_tag = tag_result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db_site.tags.append(db_tag)
    await db.commit()
    return {"message": "Tag added to site successfully"}


@router.delete("/sites/{site_id}/tags/{tag_id}", tags=["Sites", "Tags"])
async def remove_tag_from_site(
    site_id: UUID, tag_id: UUID, db: AsyncSession = Depends(get_db)
):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_site_id = str(site_id).replace("-", "")
    normalized_tag_id = str(tag_id).replace("-", "")

    site_result = await db.execute(select(Site).filter(Site.id == normalized_site_id))
    db_site = site_result.scalar_one_or_none()
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")

    tag_result = await db.execute(select(Tag).filter(Tag.id == normalized_tag_id))
    db_tag = tag_result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    if db_tag in db_site.tags:
        db_site.tags.remove(db_tag)
        await db.commit()

    return {"message": "Tag removed from site successfully"}


# Capture endpoints
@router.post("/captures", response_model=CaptureSchema, tags=["Captures"])
async def create_capture(capture: CaptureCreate, db: AsyncSession = Depends(get_db)):
    db_capture = Capture(**capture.model_dump())
    db.add(db_capture)
    await db.commit()
    await db.refresh(db_capture)
    return db_capture


@router.get("/captures", response_model=List[CaptureSchema], tags=["Captures"])
async def read_captures(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    device: str = None,
    site_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Capture)

    # 상태, 디바이스, 사이트 필터링
    if status:
        query = query.filter(Capture.status == status)
    if device:
        query = query.filter(Capture.devices.contains([{"name": device}]))
    if site_id:
        # UUID 형식 정규화 (하이픈 제거)
        normalized_site_id = str(site_id).replace("-", "")
        query = query.filter(Capture.site_id == normalized_site_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/captures/{capture_id}", response_model=CaptureDetail, tags=["Captures"])
async def read_capture(capture_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_capture_id = str(capture_id).replace("-", "")

    result = await db.execute(
        select(Capture)
        .options(
            selectinload(Capture.screenshots),
            selectinload(Capture.menu_structures),
            selectinload(Capture.pages),
        )
        .filter(Capture.id == normalized_capture_id)
    )
    db_capture = result.scalar_one_or_none()
    if db_capture is None:
        raise HTTPException(status_code=404, detail="Capture not found")
    return db_capture


@router.put("/captures/{capture_id}", response_model=CaptureSchema, tags=["Captures"])
async def update_capture(
    capture_id: UUID, capture: CaptureCreate, db: AsyncSession = Depends(get_db)
):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_capture_id = str(capture_id).replace("-", "")

    result = await db.execute(
        select(Capture).filter(Capture.id == normalized_capture_id)
    )
    db_capture = result.scalar_one_or_none()
    if db_capture is None:
        raise HTTPException(status_code=404, detail="Capture not found")

    for key, value in capture.model_dump().items():
        setattr(db_capture, key, value)

    await db.commit()
    await db.refresh(db_capture)
    return db_capture


@router.delete("/captures/{capture_id}", tags=["Captures"])
async def delete_capture(capture_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_capture_id = str(capture_id).replace("-", "")

    result = await db.execute(
        select(Capture).filter(Capture.id == normalized_capture_id)
    )
    db_capture = result.scalar_one_or_none()
    if db_capture is None:
        raise HTTPException(status_code=404, detail="Capture not found")

    await db.delete(db_capture)
    await db.commit()
    return {"ok": True}


# 캡처 상태 업데이트 엔드포인트
@router.patch(
    "/captures/{capture_id}/status", response_model=CaptureSchema, tags=["Captures"]
)
async def update_capture_status(
    capture_id: UUID, status: str, db: AsyncSession = Depends(get_db)
):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_capture_id = str(capture_id).replace("-", "")

    result = await db.execute(
        select(Capture).filter(Capture.id == normalized_capture_id)
    )
    db_capture = result.scalar_one_or_none()
    if db_capture is None:
        raise HTTPException(status_code=404, detail="Capture not found")

    db_capture.status = status
    if status == "IN_PROGRESS":
        from datetime import datetime

        db_capture.started_at = datetime.utcnow()
    elif status in ["COMPLETED", "FAILED"]:
        from datetime import datetime

        db_capture.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_capture)
    return db_capture


# MenuStructure endpoints
@router.post(
    "/menu-structures", response_model=MenuStructureSchema, tags=["Menu Structures"]
)
async def create_menu_structure(
    menu_structure: MenuStructureCreate, db: AsyncSession = Depends(get_db)
):
    db_menu_structure = MenuStructure(**menu_structure.model_dump())
    db.add(db_menu_structure)
    await db.commit()
    await db.refresh(db_menu_structure)
    return db_menu_structure


@router.get(
    "/menu-structures",
    response_model=List[MenuStructureSchema],
    tags=["Menu Structures"],
)
async def read_menu_structures(
    skip: int = 0,
    limit: int = 100,
    site_id: Optional[UUID] = None,
    capture_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MenuStructure)

    if site_id:
        query = query.filter(MenuStructure.site_id == site_id)
    if capture_id:
        query = query.filter(MenuStructure.capture_id == capture_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/menu-structures/{menu_structure_id}",
    response_model=MenuStructureSchema,
    tags=["Menu Structures"],
)
async def read_menu_structure(
    menu_structure_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MenuStructure).filter(MenuStructure.id == menu_structure_id)
    )
    db_menu_structure = result.scalar_one_or_none()
    if db_menu_structure is None:
        raise HTTPException(status_code=404, detail="Menu structure not found")
    return db_menu_structure


@router.put(
    "/menu-structures/{menu_structure_id}",
    response_model=MenuStructureSchema,
    tags=["Menu Structures"],
)
async def update_menu_structure(
    menu_structure_id: UUID,
    menu_structure: MenuStructureCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MenuStructure).filter(MenuStructure.id == menu_structure_id)
    )
    db_menu_structure = result.scalar_one_or_none()
    if db_menu_structure is None:
        raise HTTPException(status_code=404, detail="Menu structure not found")

    for key, value in menu_structure.model_dump().items():
        setattr(db_menu_structure, key, value)

    await db.commit()
    await db.refresh(db_menu_structure)
    return db_menu_structure


@router.delete("/menu-structures/{menu_structure_id}", tags=["Menu Structures"])
async def delete_menu_structure(
    menu_structure_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MenuStructure).filter(MenuStructure.id == menu_structure_id)
    )
    db_menu_structure = result.scalar_one_or_none()
    if db_menu_structure is None:
        raise HTTPException(status_code=404, detail="Menu structure not found")

    await db.delete(db_menu_structure)
    await db.commit()
    return {"ok": True}


# Page endpoints
@router.post("/pages", response_model=PageSchema, tags=["Pages"])
async def create_page(page: PageCreate, db: AsyncSession = Depends(get_db)):
    db_page = Page(**page.model_dump())
    db.add(db_page)
    await db.commit()
    await db.refresh(db_page)
    return db_page


@router.get("/pages", response_model=List[PageSchema], tags=["Pages"])
async def read_pages(
    skip: int = 0,
    limit: int = 100,
    site_id: Optional[UUID] = None,
    capture_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Page)

    if site_id:
        query = query.filter(Page.site_id == site_id)
    if capture_id:
        query = query.filter(Page.capture_id == capture_id)
    if status:
        query = query.filter(Page.status == status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/pages/{page_id}", response_model=PageDetail, tags=["Pages"])
async def read_page(page_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_page_id = str(page_id).replace("-", "")

    result = await db.execute(
        select(Page)
        .options(
            selectinload(Page.screenshots),
        )
        .filter(Page.id == normalized_page_id)
    )
    db_page = result.scalar_one_or_none()
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return db_page


@router.put("/pages/{page_id}", response_model=PageSchema, tags=["Pages"])
async def update_page(
    page_id: UUID, page: PageCreate, db: AsyncSession = Depends(get_db)
):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_page_id = str(page_id).replace("-", "")

    result = await db.execute(select(Page).filter(Page.id == normalized_page_id))
    db_page = result.scalar_one_or_none()
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    for key, value in page.model_dump().items():
        setattr(db_page, key, value)

    await db.commit()
    await db.refresh(db_page)
    return db_page


@router.delete("/pages/{page_id}", tags=["Pages"])
async def delete_page(page_id: UUID, db: AsyncSession = Depends(get_db)):
    # UUID 형식 정규화 (하이픈 제거)
    normalized_page_id = str(page_id).replace("-", "")

    result = await db.execute(select(Page).filter(Page.id == normalized_page_id))
    db_page = result.scalar_one_or_none()
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    await db.delete(db_page)
    await db.commit()
    return {"ok": True}


# Page Tags 관리
@router.post("/pages/{page_id}/tags/{tag_id}", tags=["Pages", "Tags"])
async def add_tag_to_page(
    page_id: UUID, tag_id: UUID, db: AsyncSession = Depends(get_db)
):
    page_result = await db.execute(select(Page).filter(Page.id == page_id))
    db_page = page_result.scalar_one_or_none()
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    tag_result = await db.execute(select(Tag).filter(Tag.id == tag_id))
    db_tag = tag_result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db_page.tags.append(db_tag)
    await db.commit()
    return {"message": "Tag added to page successfully"}


@router.delete("/pages/{page_id}/tags/{tag_id}", tags=["Pages", "Tags"])
async def remove_tag_from_page(
    page_id: UUID, tag_id: UUID, db: AsyncSession = Depends(get_db)
):
    page_result = await db.execute(select(Page).filter(Page.id == page_id))
    db_page = page_result.scalar_one_or_none()
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    tag_result = await db.execute(select(Tag).filter(Tag.id == tag_id))
    db_tag = tag_result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    if db_tag in db_page.tags:
        db_page.tags.remove(db_tag)
        await db.commit()

    return {"message": "Tag removed from page successfully"}


# PageScreenshot endpoints
@router.post(
    "/page-screenshots", response_model=PageScreenshotSchema, tags=["Page Screenshots"]
)
async def create_page_screenshot(
    page_screenshot: PageScreenshotCreate, db: AsyncSession = Depends(get_db)
):
    # 같은 페이지와 디바이스 타입을 가진 기존 스크린샷을 모두 is_current=False로 설정
    query = (
        update(PageScreenshot)
        .where(
            (PageScreenshot.page_id == page_screenshot.page_id)
            & (PageScreenshot.device_type == page_screenshot.device_type)
        )
        .values(is_current=False)
    )
    await db.execute(query)

    db_page_screenshot = PageScreenshot(**page_screenshot.model_dump())
    db.add(db_page_screenshot)
    await db.commit()
    await db.refresh(db_page_screenshot)
    return db_page_screenshot


@router.get(
    "/page-screenshots",
    response_model=List[PageScreenshotSchema],
    tags=["Page Screenshots"],
)
async def read_page_screenshots(
    skip: int = 0,
    limit: int = 100,
    page_id: Optional[UUID] = None,
    device_type: Optional[str] = None,
    is_current: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(PageScreenshot)

    if page_id:
        query = query.filter(PageScreenshot.page_id == page_id)
    if device_type:
        query = query.filter(PageScreenshot.device_type == device_type)
    if is_current is not None:
        query = query.filter(PageScreenshot.is_current == is_current)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/page-screenshots/{page_screenshot_id}",
    response_model=PageScreenshotSchema,
    tags=["Page Screenshots"],
)
async def read_page_screenshot(
    page_screenshot_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PageScreenshot).filter(PageScreenshot.id == page_screenshot_id)
    )
    db_page_screenshot = result.scalar_one_or_none()
    if db_page_screenshot is None:
        raise HTTPException(status_code=404, detail="Page screenshot not found")
    return db_page_screenshot


@router.delete("/page-screenshots/{page_screenshot_id}", tags=["Page Screenshots"])
async def delete_page_screenshot(
    page_screenshot_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PageScreenshot).filter(PageScreenshot.id == page_screenshot_id)
    )
    db_page_screenshot = result.scalar_one_or_none()
    if db_page_screenshot is None:
        raise HTTPException(status_code=404, detail="Page screenshot not found")

    await db.delete(db_page_screenshot)
    await db.commit()
    return {"ok": True}


# Screenshot endpoints
@router.post("/screenshots", response_model=ScreenshotSchema, tags=["Screenshots"])
async def create_screenshot(
    screenshot: ScreenshotCreate, db: AsyncSession = Depends(get_db)
):
    db_screenshot = Screenshot(**screenshot.model_dump())
    db.add(db_screenshot)
    await db.commit()
    await db.refresh(db_screenshot)
    return db_screenshot


@router.get("/screenshots", response_model=List[ScreenshotSchema], tags=["Screenshots"])
async def read_screenshots(
    skip: int = 0,
    limit: int = 100,
    device: str = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Screenshot)

    # 디바이스 필터링
    if device:
        query = query.filter(Screenshot.device == device)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/screenshots/{screenshot_id}",
    response_model=ScreenshotSchema,
    tags=["Screenshots"],
)
async def read_screenshot(screenshot_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Screenshot).filter(Screenshot.id == screenshot_id))
    db_screenshot = result.scalar_one_or_none()
    if db_screenshot is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return db_screenshot


@router.delete("/screenshots/{screenshot_id}", tags=["Screenshots"])
async def delete_screenshot(screenshot_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Screenshot).filter(Screenshot.id == screenshot_id))
    db_screenshot = result.scalar_one_or_none()
    if db_screenshot is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")

    await db.delete(db_screenshot)
    await db.commit()
    return {"ok": True}
