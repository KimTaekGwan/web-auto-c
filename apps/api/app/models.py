from datetime import datetime
import enum
import uuid
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
    Boolean,
    Table,
    TypeDecorator,
)
from sqlalchemy.types import CHAR
from sqlalchemy.orm import relationship
from .database import Base


# SQLite와 호환되는 UUID 타입 정의
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses CHAR(36) as underlying storage, stores as string.
    """

    impl = CHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "sqlite":
            return str(value)
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class CaptureStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# 태그와 사이트의 연결 테이블
site_tags = Table(
    "site_tags",
    Base.metadata,
    Column(
        "site_id",
        GUID(),
        ForeignKey("sites.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        GUID(),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# 태그와 페이지의 연결 테이블
page_tags = Table(
    "page_tags",
    Base.metadata,
    Column(
        "page_id",
        GUID(),
        ForeignKey("pages.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        GUID(),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 정의
    sites = relationship("Site", secondary=site_tags, back_populates="tags")
    pages = relationship("Page", secondary=page_tags, back_populates="tags")


class Site(Base):
    __tablename__ = "sites"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    first_captured_at = Column(DateTime, nullable=True)
    last_captured_at = Column(DateTime, nullable=True)
    capture_count = Column(Integer, default=0)
    status = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 정의
    captures = relationship(
        "Capture", back_populates="site", cascade="all, delete-orphan"
    )
    menu_structures = relationship(
        "MenuStructure", back_populates="site", cascade="all, delete-orphan"
    )
    pages = relationship("Page", back_populates="site", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=site_tags, back_populates="sites")


class Capture(Base):
    __tablename__ = "captures"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    site_id = Column(GUID(), ForeignKey("sites.id", ondelete="CASCADE"))
    url = Column(Text, nullable=False)
    status = Column(Enum(CaptureStatus), default=CaptureStatus.PENDING)
    devices = Column(JSON, nullable=False)
    options = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 관계 정의
    site = relationship("Site", back_populates="captures")
    screenshots = relationship(
        "Screenshot", back_populates="capture", cascade="all, delete-orphan"
    )
    menu_structures = relationship(
        "MenuStructure", back_populates="capture", cascade="all, delete-orphan"
    )
    pages = relationship("Page", back_populates="capture", cascade="all, delete-orphan")


class MenuStructure(Base):
    __tablename__ = "menu_structures"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    site_id = Column(GUID(), ForeignKey("sites.id", ondelete="CASCADE"))
    capture_id = Column(GUID(), ForeignKey("captures.id", ondelete="CASCADE"))
    structure = Column(JSON, nullable=False)
    extraction_method = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 정의
    site = relationship("Site", back_populates="menu_structures")
    capture = relationship("Capture", back_populates="menu_structures")


class Page(Base):
    __tablename__ = "pages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    site_id = Column(GUID(), ForeignKey("sites.id", ondelete="CASCADE"))
    capture_id = Column(GUID(), ForeignKey("captures.id", ondelete="CASCADE"))
    url = Column(Text, nullable=False)
    title = Column(String, nullable=True)
    menu_path = Column(String, nullable=True)
    depth = Column(Integer, default=0)
    status = Column(String, nullable=True)
    page_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 정의
    site = relationship("Site", back_populates="pages")
    capture = relationship("Capture", back_populates="pages")
    screenshots = relationship(
        "PageScreenshot", back_populates="page", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=page_tags, back_populates="pages")


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    capture_id = Column(GUID(), ForeignKey("captures.id", ondelete="CASCADE"))
    device = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    screenshot_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 정의
    capture = relationship("Capture", back_populates="screenshots")


class PageScreenshot(Base):
    __tablename__ = "page_screenshots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    page_id = Column(GUID(), ForeignKey("pages.id", ondelete="CASCADE"))
    device_type = Column(String, nullable=False)
    width = Column(Integer, nullable=False)
    screenshot_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 정의
    page = relationship("Page", back_populates="screenshots")
