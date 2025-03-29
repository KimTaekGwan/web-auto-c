import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from .models import (
    Site,
    Capture,
    Screenshot,
    CaptureStatus,
    Tag,
    MenuStructure,
    Page,
    PageScreenshot,
)

# 더미 디바이스 목록
DEVICES = [
    {"name": "iPhone 13", "width": 390, "height": 844},
    {"name": "iPhone SE", "width": 375, "height": 667},
    {"name": "iPad Pro", "width": 1024, "height": 1366},
    {"name": "Samsung Galaxy S21", "width": 360, "height": 800},
    {"name": "Desktop", "width": 1920, "height": 1080},
    {"name": "MacBook Pro", "width": 1440, "height": 900},
]

# 더미 태그 목록
TAG_DATA = [
    {"name": "e-commerce", "color": "#FF5733"},
    {"name": "blog", "color": "#33FF57"},
    {"name": "portfolio", "color": "#3357FF"},
    {"name": "landing-page", "color": "#FF33F5"},
    {"name": "news", "color": "#F5FF33"},
    {"name": "dashboard", "color": "#33FFF5"},
    {"name": "docs", "color": "#F533FF"},
]

# 더미 URL 목록
URLS = [
    "https://example.com",
    "https://demo-site.org",
    "https://test-shop.com/products",
    "https://blog-demo.net/posts",
    "https://dashboard.example.io",
    "https://portfolio-sample.com",
    "https://docs.example.org",
]

# 더미 메뉴 구조 예시
DUMMY_MENU_STRUCTURE = {
    "main_menu": [
        {"title": "Home", "url": "", "depth": 0},
        {"title": "Products", "url": "products", "depth": 0},
        {"title": "Services", "url": "services", "depth": 0},
        {"title": "About", "url": "about", "depth": 0},
        {"title": "Contact", "url": "contact", "depth": 0},
    ],
    "sub_menu": [
        {"parent": "Products", "title": "Product 1", "url": "products/1", "depth": 1},
        {"parent": "Products", "title": "Product 2", "url": "products/2", "depth": 1},
        {"parent": "Services", "title": "Service 1", "url": "services/1", "depth": 1},
        {"parent": "Services", "title": "Service 2", "url": "services/2", "depth": 1},
    ],
}


# 더미 이미지 URL (placeholder 이미지)
def get_dummy_image_url(width: int, height: int, id: int) -> str:
    return f"https://picsum.photos/id/{id}/{width}/{height}"


# 더미 태그 생성 함수
async def create_dummy_tags(db) -> List[Tag]:
    tags = []
    for tag_data in TAG_DATA:
        tag = Tag(**tag_data)
        db.add(tag)
        tags.append(tag)
    await db.flush()
    return tags


# 더미 사이트 생성 함수
def create_dummy_site() -> Dict[str, Any]:
    return {
        "name": f"Test Site {random.randint(1, 1000)}",
        "url": random.choice(URLS),
        "description": f"This is a test site description {random.randint(1, 100)}",
        "status": random.choice(["active", "inactive", "pending"]),
        "notes": f"Some notes about this site {random.randint(1, 100)}",
        "capture_count": random.randint(0, 10),
        "first_captured_at": (
            datetime.utcnow() - timedelta(days=random.randint(1, 30))
            if random.choice([True, False])
            else None
        ),
        "last_captured_at": (
            datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            if random.choice([True, False])
            else None
        ),
    }


# 더미 캡처 생성 함수
def create_dummy_capture(site_id) -> Dict[str, Any]:
    selected_devices = random.sample(DEVICES, random.randint(1, 4))

    # 상태를 결정 - 모든 상태가 고르게 분포
    status = random.choice([status.value for status in CaptureStatus])

    # 상태에 따른 시간 설정
    now = datetime.utcnow()
    started_at = (
        now - timedelta(hours=random.randint(1, 24)) if status != "PENDING" else None
    )
    completed_at = (
        now - timedelta(minutes=random.randint(10, 300))
        if status in ["COMPLETED", "FAILED"]
        else None
    )

    error = "An error occurred during capture" if status == "FAILED" else None

    return {
        "site_id": site_id,
        "url": random.choice(URLS),
        "status": status,
        "devices": selected_devices,
        "options": {
            "fullPage": random.choice([True, False]),
            "waitTime": random.randint(1, 10),
        },
        "error": error,
        "started_at": started_at,
        "completed_at": completed_at,
    }


# 더미 메뉴 구조 생성 함수
def create_dummy_menu_structure(site_id, capture_id) -> Dict[str, Any]:
    return {
        "site_id": site_id,
        "capture_id": capture_id,
        "structure": DUMMY_MENU_STRUCTURE,
        "extraction_method": random.choice(["ai", "html", "sitemap"]),
        "verified": random.choice([True, False]),
    }


# 더미 페이지 생성 함수
def create_dummy_page(
    site_id, capture_id, menu_item: Dict[str, Any], base_url: str
) -> Dict[str, Any]:
    url = f"{base_url}/{menu_item['url']}" if menu_item["url"] else base_url

    return {
        "site_id": site_id,
        "capture_id": capture_id,
        "url": url,
        "title": menu_item["title"],
        "menu_path": (
            menu_item.get("parent", "") + "/" + menu_item["title"]
            if "parent" in menu_item
            else menu_item["title"]
        ),
        "depth": menu_item["depth"],
        "status": random.choice(["pending", "captured", "failed"]),
        "page_metadata": {
            "meta_title": f"{menu_item['title']} | Test Site",
            "meta_description": f"This is a description for {menu_item['title']} page",
            "has_forms": random.choice([True, False]),
            "has_images": random.choice([True, False]),
        },
    }


# 더미 페이지 스크린샷 생성 함수
def create_dummy_page_screenshot(
    page_id, device_info: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "page_id": page_id,
        "device_type": device_info["name"],
        "width": device_info["width"],
        "screenshot_path": get_dummy_image_url(
            device_info["width"], device_info["height"], random.randint(1, 200)
        ),
        "thumbnail_path": get_dummy_image_url(
            device_info["width"] // 4,
            device_info["height"] // 4,
            random.randint(1, 200),
        ),
        "is_current": True,
    }


# 더미 스크린샷 생성 함수
def create_dummy_screenshot(capture_id, device: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "capture_id": capture_id,
        "device": device["name"],
        "url": random.choice(URLS),
        "width": device["width"],
        "height": device["height"],
        "screenshot_path": get_dummy_image_url(
            device["width"], device["height"], random.randint(1, 200)
        ),
        "thumbnail_path": get_dummy_image_url(
            device["width"] // 4, device["height"] // 4, random.randint(1, 200)
        ),
    }


# 더미 데이터 생성 함수
async def generate_dummy_data(db, num_sites=5):
    # 더미 태그 생성
    tags = await create_dummy_tags(db)

    # 더미 사이트 생성
    sites = []
    for _ in range(num_sites):
        site_data = create_dummy_site()
        site = Site(**site_data)

        # 랜덤하게 태그 할당
        site_tags = random.sample(tags, random.randint(1, 3))
        site.tags = site_tags

        db.add(site)
        await db.flush()
        sites.append(site)

    # 각 사이트에 대한 더미 캡처 생성
    all_captures = []
    for site in sites:
        num_captures = random.randint(1, 3)
        site_captures = []

        for _ in range(num_captures):
            capture_data = create_dummy_capture(site.id)
            capture = Capture(**capture_data)
            db.add(capture)
            await db.flush()
            site_captures.append((capture, capture_data["devices"]))
            all_captures.append((capture, capture_data["devices"]))

            # 메뉴 구조 생성
            menu_structure_data = create_dummy_menu_structure(site.id, capture.id)
            menu_structure = MenuStructure(**menu_structure_data)
            db.add(menu_structure)
            await db.flush()

            # 페이지 생성
            pages = []
            menu_items = (
                menu_structure_data["structure"]["main_menu"]
                + menu_structure_data["structure"]["sub_menu"]
            )

            for menu_item in menu_items:
                page_data = create_dummy_page(site.id, capture.id, menu_item, site.url)
                page = Page(**page_data)

                # 랜덤하게 태그 할당
                page_tags = random.sample(tags, random.randint(0, 2))
                page.tags = page_tags

                db.add(page)
                await db.flush()
                pages.append((page, menu_item))

                # 디바이스별 페이지 스크린샷 생성
                if page.status == "captured":
                    for device in random.sample(DEVICES, random.randint(1, 3)):
                        screenshot_data = create_dummy_page_screenshot(page.id, device)
                        page_screenshot = PageScreenshot(**screenshot_data)
                        db.add(page_screenshot)

    # 각 캡처에 대한 더미 스크린샷 생성
    for capture, devices in all_captures:
        if capture.status in ["COMPLETED", "IN_PROGRESS"]:
            for device in devices:
                screenshot_data = create_dummy_screenshot(capture.id, device)
                screenshot = Screenshot(**screenshot_data)
                db.add(screenshot)

    await db.commit()  # 모든 변경사항을 커밋
