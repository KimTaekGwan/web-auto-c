import uuid
import sqlite3
from datetime import datetime, timedelta
import json
import random

# 실제같은 URL 목록
real_sites = [
    {"url": "https://naver.com", "name": "네이버"},
    {"url": "https://coupang.com", "name": "쿠팡"},
    {"url": "https://toss.im", "name": "토스"},
    {"url": "https://woowahan.com", "name": "우아한형제들"},
    {"url": "https://kakao.com", "name": "카카오"},
]

# 데이터베이스 연결
conn = sqlite3.connect("webcapture.db")
cursor = conn.cursor()

# 현재 시간 기준
now = datetime.utcnow()

# 태그 생성
tags = [
    {"id": str(uuid.uuid4()), "name": "쇼핑몰", "color": "#FF5733"},
    {"id": str(uuid.uuid4()), "name": "포털", "color": "#33FF57"},
    {"id": str(uuid.uuid4()), "name": "핀테크", "color": "#3357FF"},
]

for tag in tags:
    cursor.execute(
        "INSERT INTO tags (id, name, color, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (tag["id"], tag["name"], tag["color"], now, now),
    )
    print(f"태그 생성: {tag['name']}")

# 사이트 및 관련 데이터 생성
for site_info in real_sites:
    # 사이트 생성
    site_id = str(uuid.uuid4())
    first_captured = now - timedelta(days=random.randint(5, 30))

    cursor.execute(
        "INSERT INTO sites (id, name, url, description, first_captured_at, last_captured_at, capture_count, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            site_id,
            site_info["name"],
            site_info["url"],
            f"{site_info['name']} 웹사이트",
            first_captured,
            now - timedelta(days=random.randint(0, 5)),
            random.randint(1, 5),
            "active",
            now - timedelta(days=random.randint(30, 60)),
            now,
        ),
    )

    # 사이트-태그 연결
    site_tags = random.sample(tags, random.randint(1, 2))
    for tag in site_tags:
        cursor.execute(
            "INSERT INTO site_tags (site_id, tag_id) VALUES (?, ?)",
            (site_id, tag["id"]),
        )

    # 캡처 생성
    device_options = [
        ["desktop"],
        ["desktop", "mobile"],
        ["desktop", "tablet", "mobile"],
    ]

    # 각 사이트당 1-3개의 캡처 생성
    for i in range(random.randint(1, 3)):
        capture_id = str(uuid.uuid4())
        devices = random.choice(device_options)
        created_at = now - timedelta(
            days=random.randint(0, 10), hours=random.randint(0, 24)
        )

        cursor.execute(
            "INSERT INTO captures (id, site_id, url, status, devices, created_at, started_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                capture_id,
                site_id,
                site_info["url"],
                random.choice(["PENDING", "IN_PROGRESS", "COMPLETED"]),
                json.dumps(devices),
                created_at,
                created_at + timedelta(minutes=random.randint(1, 5)),
                created_at + timedelta(minutes=random.randint(10, 30)),
            ),
        )

        # 메뉴 구조 생성
        menu_id = str(uuid.uuid4())
        menu_structure = {
            "main_menu": [
                {"title": "홈", "url": site_info["url"], "depth": 0},
                {"title": "소개", "url": f"{site_info['url']}/about", "depth": 0},
                {"title": "서비스", "url": f"{site_info['url']}/services", "depth": 0},
            ],
            "sub_menus": [
                {
                    "parent": "서비스",
                    "title": "서비스 1",
                    "url": f"{site_info['url']}/services/1",
                    "depth": 1,
                },
                {
                    "parent": "서비스",
                    "title": "서비스 2",
                    "url": f"{site_info['url']}/services/2",
                    "depth": 1,
                },
            ],
        }

        cursor.execute(
            "INSERT INTO menu_structures (id, site_id, capture_id, structure, extraction_method, verified, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                menu_id,
                site_id,
                capture_id,
                json.dumps(menu_structure),
                "AI",
                True,
                created_at,
                created_at,
            ),
        )

        # 페이지 생성
        pages = []
        # 메인 메뉴 페이지
        for item in menu_structure["main_menu"]:
            page_id = str(uuid.uuid4())
            pages.append(
                {
                    "id": page_id,
                    "url": item["url"],
                    "title": item["title"],
                    "depth": item["depth"],
                }
            )

            cursor.execute(
                "INSERT INTO pages (id, site_id, capture_id, url, title, menu_path, depth, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    page_id,
                    site_id,
                    capture_id,
                    item["url"],
                    item["title"],
                    f"/{item['title']}",
                    item["depth"],
                    "captured",
                    created_at,
                    created_at,
                ),
            )

        # 서브 메뉴 페이지
        for item in menu_structure["sub_menus"]:
            page_id = str(uuid.uuid4())
            pages.append(
                {
                    "id": page_id,
                    "url": item["url"],
                    "title": item["title"],
                    "depth": item["depth"],
                }
            )

            cursor.execute(
                "INSERT INTO pages (id, site_id, capture_id, url, title, menu_path, depth, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    page_id,
                    site_id,
                    capture_id,
                    item["url"],
                    item["title"],
                    f"/{item['parent']}/{item['title']}",
                    item["depth"],
                    "captured",
                    created_at,
                    created_at,
                ),
            )

        # 스크린샷 생성
        for device in devices:
            width = (
                1920 if device == "desktop" else (768 if device == "tablet" else 375)
            )

            # 메인 스크린샷
            screenshot_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO screenshots (id, capture_id, device, url, width, height, screenshot_path, thumbnail_path, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    screenshot_id,
                    capture_id,
                    device,
                    site_info["url"],
                    width,
                    random.randint(1000, 2000),
                    f"screenshots/{site_id}/{device}_{width}_main.jpg",
                    f"thumbnails/{site_id}/{device}_{width}_main_thumb.jpg",
                    created_at,
                ),
            )

            # 페이지별 스크린샷
            for page in pages:
                page_screenshot_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO page_screenshots (id, page_id, device_type, width, screenshot_path, thumbnail_path, is_current, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        page_screenshot_id,
                        page["id"],
                        device,
                        width,
                        f"screenshots/{site_id}/{device}_{width}_{page['title'].lower()}.jpg",
                        f"thumbnails/{site_id}/{device}_{width}_{page['title'].lower()}_thumb.jpg",
                        True,
                        created_at,
                        created_at,
                    ),
                )

# 커밋 및 연결 종료
conn.commit()
conn.close()

print("테스트 데이터 생성이 완료되었습니다!")
