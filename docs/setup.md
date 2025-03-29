# WebCapture Pro 개선 PRD

## 1. 제품 개요: 다중 디바이스 지원 강화

**WebCapture Pro**는 PC와 모바일 환경을 모두 지원하는 웹 디자인 수집 자동화 도구로, 디자이너와 개발자가 참고용 웹사이트 디자인을 체계적으로 수집하고 관리할 수 있습니다.

### 핵심 차별점

- **다중 디바이스 캡처**: PC, 태블릿, 모바일 화면 너비를 선택적으로 캡처
- **태깅 시스템**: 사이트 및 개별 페이지 수준의 세밀한 태그 지정
- **이미지 관리**: 캡처된 이미지의 수동 교체 및 버전 관리
- **컴포넌트 기반 설계**: 재사용 가능한 컴포넌트로 확장성 보장

## 2. 기술 아키텍처: 컴포넌트 중심 설계

### 향상된 모노레포 구조

```
├── apps/
│   ├── web/                   # NextJS 웹 앱 (대시보드)
│   │   ├── components/        # 페이지별 컴포넌트
│   │   ├── contexts/          # 상태 관리 컨텍스트
│   │   ├── hooks/             # 커스텀 훅
│   ├── api/                   # FastAPI 백엔드 서버
│   │   ├── services/          # 비즈니스 로직 서비스
│   │   ├── routers/           # API 엔드포인트 라우터
│   ├── chrome-extension/      # Chrome 확장 프로그램
│   ├── capture-worker/        # 캡처 작업 처리 서비스
│
├── packages/
│   ├── ui/                    # 공유 UI 컴포넌트 라이브러리
│   │   ├── atoms/             # 기본 컴포넌트
│   │   ├── molecules/         # 복합 컴포넌트
│   │   ├── organisms/         # 섹션 수준 컴포넌트
│   │   ├── templates/         # 페이지 레이아웃
│   ├── database/              # Supabase 클라이언트 및 타입
│   ├── langchain-agents/      # LangGraph + Claude 에이전트
│   ├── capture-engine/        # Playwright 캡처 엔진
│   │   ├── device-profiles/   # 디바이스별 설정 프로필
│   │   ├── capture-strategies/# 캡처 전략 모듈
│   ├── config/                # 공유 구성
│   ├── utils/                 # 공통 유틸리티
```

### 컴포넌트 설계 원칙

- **원자적 디자인 시스템**: UI 컴포넌트를 원자-분자-유기체 패턴으로 구성
- **비즈니스 로직 분리**: 상태 관리와 UI 표현 분리
- **모듈형 서비스**: 서비스 기능을 독립적인 모듈로 분리
- **재사용 가능한 훅**: 일반적인 기능을 커스텀 훅으로 추상화

## 3. 다중 디바이스 지원 캡처 시스템

### 디바이스 프로필 설정

- **기본 디바이스 프로필**:
  - 데스크톱: 1920×1080
  - 태블릿: 768×1024
  - 모바일: 375×667
- **사용자 정의 프로필**: 맞춤형 뷰포트 크기 설정 가능

### 캡처 프로세스 변경 사항

1. **캡처 설정 단계 추가**: 캡처 전 디바이스 선택 UI 제공
2. **병렬 처리 최적화**: 디바이스별 병렬 캡처 처리
3. **디바이스별 스토리지 구조**: 디바이스 타입에 따른 저장 분류

### 캡처 구성 옵션

```typescript
interface CaptureConfig {
  deviceTypes: ("desktop" | "tablet" | "mobile")[]
  customSizes?: Array<{
    name: string
    width: number
    height: number
  }>
  captureFullPage: boolean
  captureDynamicElements: boolean
  initialTags?: string[]
}
```

## 4. 이미지 관리 및 태그 시스템

### 개선된 이미지 관리 기능

- **이미지 버전 관리**: 교체 이미지의 이력 저장 및 복원
- **이미지 교체 워크플로우**:
  1. 페이지 및 디바이스 타입 선택
  2. 새 이미지 업로드 (드래그 앤 드롭 지원)
  3. 이전/이후 비교 미리보기
  4. 확인 후 교체

### 고급 태그 시스템

- **다중 수준 태그 지원**:
  - 웹사이트 수준 태그: 전체 사이트 분류
  - 페이지 수준 태그: 개별 페이지 특성 분류
- **태그 필터링 및 검색**: 다중 태그 기반 검색
- **스마트 태그 제안**: 유사 페이지 기반 태그 추천
- **태그 일괄 적용**: 여러 페이지에 동시 태그 지정

```typescript
// 태그 타입 정의
interface Tag {
  id: string
  name: string
  color: string
  description?: string
}

// 태그 적용 인터페이스
interface Taggable {
  getTags(): Tag[]
  addTag(tag: Tag): void
  removeTag(tagId: string): void
  hasTag(tagId: string): boolean
}
```

## 5. 컴포넌트 아키텍처 및 확장성

### 핵심 UI 컴포넌트 구성

- **SiteExplorer**: 사이트 탐색 및 관리
- **DeviceSwitcher**: 디바이스 뷰 전환
- **TagManager**: 태그 생성 및 관리
- **ImageReplacer**: 이미지 교체 인터페이스
- **MenuVisualizer**: 사이트 구조 시각화

### 확장 가능한 설계 패턴

- **플러그인 아키텍처**: 기능 모듈 동적 로드
- **어댑터 패턴**: 외부 서비스 통합 인터페이스
- **전략 패턴**: 캡처 방식 교체 가능

### 상태 관리 전략

```typescript
// 페이지별 컨텍스트 분리 예시
const SiteContext = createContext<SiteContextValue | undefined>(undefined)
const CaptureContext = createContext<CaptureContextValue | undefined>(undefined)
const TagContext = createContext<TagContextValue | undefined>(undefined)

// 컴포저블 훅 패턴
function useSiteWithCaptures(siteId: string) {
  const site = useSite(siteId)
  const captures = useCaptures(siteId)

  return {
    site,
    captures,
    isLoading: site.isLoading || captures.isLoading,
    error: site.error || captures.error,
  }
}
```

## 6. 데이터 모델 개선

### 스크린샷 관리를 위한 스키마 변경

- **페이지-스크린샷 분리**: 다중 디바이스 스크린샷 관리
- **버전 관리 지원**: 이전 스크린샷 보존
- **메타데이터 강화**: 캡처 환경 및 설정 저장

### 저장소 구조 업데이트

```
storage/
├── websites/
│   ├── [website_id]/
│   │   ├── [capture_id]/
│   │   │   ├── pages/
│   │   │   │   ├── [page_id]/
│   │   │   │   │   ├── desktop/
│   │   │   │   │   │   ├── current.png
│   │   │   │   │   │   ├── [timestamp].png  # 이전 버전
│   │   │   │   │   │   ├── thumbnail.png
│   │   │   │   │   ├── tablet/
│   │   │   │   │   │   ├── ...
│   │   │   │   │   ├── mobile/
│   │   │   │   │   │   ├── ...
```

## 7. API 엔드포인트 확장

### 이미지 관리 API

```
POST /api/screenshots/{page_id}/replace
GET /api/screenshots/{page_id}/versions
POST /api/screenshots/{page_id}/restore/{version_id}
```

### 태그 관리 API

```
GET /api/tags
POST /api/tags
GET /api/sites/{site_id}/tags
POST /api/sites/{site_id}/tags
GET /api/pages/{page_id}/tags
POST /api/pages/{page_id}/tags
DELETE /api/pages/{page_id}/tags/{tag_id}
```

### 다중 디바이스 캡처 API

```
POST /api/captures
{
  "url": "https://example.com",
  "devices": ["desktop", "mobile"],
  "initialTags": ["reference", "e-commerce"]
}
```

## 8. 개발 로드맵: 기능 중심 우선순위

### 1단계: 기본 인프라 및 다중 디바이스 지원 (3주)

- 모노레포 및 기본 컴포넌트 설정
- 다중 디바이스 프로필 구현
- 기본 캡처 엔진 개발

### 2단계: 이미지 관리 및 태그 시스템 (3주)

- 이미지 교체 워크플로우 구현
- 태그 시스템 개발
- 스크린샷 버전 관리 기능

### 3단계: AI 분석 및 크롬 확장 프로그램 (3주)

- LangGraph 에이전트 시스템 개발
- 크롬 확장 프로그램 구현
- 메뉴 구조 분석 기능

### 4단계: 대시보드 UI 및 통합 (3주)

- 고급 UI 컴포넌트 개발
- 전체 시스템 통합
- 성능 최적화

## 9. 기술적 고려사항 및 도전과제

### 확장성 고려사항

- **대용량 이미지 처리**: 청크 업로드, 스트리밍 다운로드
- **컴포넌트 재사용성**: Props API 설계, 합성 패턴
- **상태 관리 복잡성**: Context API와 Zustand 결합

### 성능 최적화 전략

- **이미지 지연 로딩**: 뷰포트 진입 시 로드
- **가상화 목록**: 대량의 페이지 목록 효율적 렌더링
- **데이터 쿼리 최적화**: 정확한 인덱싱, 필요한 필드만 요청

### UI/UX 설계 원칙

- **일관된 디자인 시스템**: 모든 컴포넌트에 동일한 디자인 언어 적용
- **점진적 공개**: 복잡한 기능을 단계적으로 소개
- **상태 피드백**: 모든 작업의 진행 상태 명확히 표시

## 10. 구현 세부사항

### 이미지 교체 구현 예시

```typescript
// ImageReplacement.tsx
const ImageReplacement: React.FC<Props> = ({ pageId, deviceType }) => {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [currentImage, setCurrentImage] = useState<string | null>(null)

  // 파일 업로드 처리
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)

      // 미리보기 생성
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(selectedFile)
    }
  }

  // 이미지 교체 요청
  const handleReplacement = async () => {
    if (!file) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append("file", file)

      await fetch(
        `/api/screenshots/${pageId}/replace?deviceType=${deviceType}`,
        {
          method: "POST",
          body: formData,
        }
      )

      // 성공 처리
    } catch (error) {
      // 오류 처리
    } finally {
      setIsUploading(false)
    }
  }

  return <div className="image-replacement">{/* UI 구현 */}</div>
}
```

### 다중 디바이스 캡처 엔진

Playwright를 활용한 다중 디바이스 캡처 구현:

```python
# capture_engine.py
from playwright.async_api import async_playwright
import asyncio

class DeviceCapture:
    DEVICE_PROFILES = {
        "desktop": {"width": 1920, "height": 1080},
        "tablet": {"width": 768, "height": 1024},
        "mobile": {"width": 375, "height": 667}
    }

    def __init__(self, url, device_types=None):
        self.url = url
        self.device_types = device_types or ["desktop"]
        self.results = {}

    async def capture_for_device(self, device_type):
        profile = self.DEVICE_PROFILES[device_type]

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport=profile,
                device_scale_factor=2.0
            )
            page = await context.new_page()

            await page.goto(self.url, wait_until="networkidle")

            # 전체 페이지 스크린샷
            screenshot = await page.screenshot(full_page=True)

            # 썸네일 생성을 위한 설정
            await page.set_viewport_size({"width": profile["width"], "height": 400})
            thumbnail = await page.screenshot()

            await browser.close()

            return {
                "screenshot": screenshot,
                "thumbnail": thumbnail,
                "device_type": device_type,
                "width": profile["width"],
                "height": profile["height"]
            }

    async def capture_all(self):
        tasks = [self.capture_for_device(device) for device in self.device_types]
        results = await asyncio.gather(*tasks)

        # 결과 구성
        for result in results:
            self.results[result["device_type"]] = result

        return self.results
```

## 결론

WebCapture Pro는 다중 디바이스 캡처, 이미지 관리, 세밀한 태그 지정 기능을 갖춘 고도의 웹 디자인 수집 자동화 도구입니다. 컴포넌트 기반 설계와 확장성을 우선시하는 아키텍처를 통해 유연하고 강력한 기능을 제공합니다. 이 PRD를 통해 디자이너와 개발자는 참조용 디자인을 보다 효율적으로 수집하고 관리할 수 있습니다.
