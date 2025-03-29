import axios from "axios"

// API 기본 클라이언트 설정
const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-type": "application/json",
  },
})

// 오류 디버깅을 위한 인터셉터 추가
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 서버 응답이 있는 경우 (2xx 외의 상태 코드)
      console.error("API 응답 오류:", {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      })
    } else if (error.request) {
      // 요청은 이루어졌으나 응답이 없는 경우
      console.error("API 요청 오류: 응답 없음", error.request)
    } else {
      // 요청 설정 과정에서 오류가 발생한 경우
      console.error("API 설정 오류:", error.message)
    }
    return Promise.reject(error)
  }
)

// 대시보드 API
export const dashboardApi = {
  getStats: async () => {
    try {
      console.log(
        "대시보드 통계 요청 중...",
        apiClient.defaults.baseURL + "/dashboard"
      )
      const response = await apiClient.get("/dashboard")
      return response.data
    } catch (error) {
      console.error("대시보드 통계 요청 실패:", error)
      throw error
    }
  },
}

// 태그 API
export const tagApi = {
  getAll: async (params?: { skip?: number; limit?: number }) => {
    const response = await apiClient.get("/tags", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/tags/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/tags", data)
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/tags/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/tags/${id}`)
    return response.data
  },
}

// 사이트 API
export const siteApi = {
  getAll: async (params?: { skip?: number; limit?: number }) => {
    const response = await apiClient.get("/sites", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/sites/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/sites", data)
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/sites/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/sites/${id}`)
    return response.data
  },
  addTag: async (siteId: string, tagId: string) => {
    const response = await apiClient.post(`/sites/${siteId}/tags/${tagId}`)
    return response.data
  },
  removeTag: async (siteId: string, tagId: string) => {
    const response = await apiClient.delete(`/sites/${siteId}/tags/${tagId}`)
    return response.data
  },
}

// 메뉴 구조 API
export const menuStructureApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    site_id?: string
    capture_id?: string
  }) => {
    const response = await apiClient.get("/menu-structures", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/menu-structures/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/menu-structures", data)
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/menu-structures/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/menu-structures/${id}`)
    return response.data
  },
}

// 페이지 API
export const pageApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    site_id?: string
    capture_id?: string
    status?: string
  }) => {
    const response = await apiClient.get("/pages", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/pages/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/pages", data)
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/pages/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/pages/${id}`)
    return response.data
  },
  addTag: async (pageId: string, tagId: string) => {
    const response = await apiClient.post(`/pages/${pageId}/tags/${tagId}`)
    return response.data
  },
  removeTag: async (pageId: string, tagId: string) => {
    const response = await apiClient.delete(`/pages/${pageId}/tags/${tagId}`)
    return response.data
  },
}

// 캡처 API
export const captureApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    status?: string
    device?: string
    site_id?: string
  }) => {
    const response = await apiClient.get("/captures", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/captures/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/captures", data)
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/captures/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/captures/${id}`)
    return response.data
  },
  updateStatus: async (id: string, status: string) => {
    const response = await apiClient.patch(
      `/captures/${id}/status?status=${status}`
    )
    return response.data
  },
}

// 페이지 스크린샷 API
export const pageScreenshotApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    page_id?: string
    device_type?: string
    is_current?: boolean
  }) => {
    const response = await apiClient.get("/page-screenshots", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/page-screenshots/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/page-screenshots", data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/page-screenshots/${id}`)
    return response.data
  },
}

// 스크린샷 API
export const screenshotApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    device?: string
  }) => {
    const response = await apiClient.get("/screenshots", { params })
    return response.data
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/screenshots/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post("/screenshots", data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/screenshots/${id}`)
    return response.data
  },
}

// 데모 데이터 생성 API
export const demoApi = {
  generateData: async (numSites: number = 5) => {
    const response = await apiClient.post(
      `/demo/generate?num_sites=${numSites}`
    )
    return response.data
  },
}

export default {
  dashboard: dashboardApi,
  tag: tagApi,
  site: siteApi,
  menuStructure: menuStructureApi,
  page: pageApi,
  capture: captureApi,
  pageScreenshot: pageScreenshotApi,
  screenshot: screenshotApi,
  demo: demoApi,
}
