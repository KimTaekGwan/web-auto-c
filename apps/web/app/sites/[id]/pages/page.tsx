"use client"

import React, { useEffect, useState, useCallback } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { Button } from "@workspace/ui/components/button"
import { ArrowLeft, Eye, ImageIcon, Pencil, Trash } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"
import { Input } from "@workspace/ui/components/input"
import { Badge } from "@workspace/ui/components/badge"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"
import { siteApi, pageApi, captureApi } from "@/lib/api"
import { toast } from "sonner"

// 페이지 및 캡처 인터페이스 정의
interface Page {
  id: string
  site_id: string
  capture_id: string
  url: string
  title: string
  menu_path: string
  depth: number
  status: string
  created_at: string
  updated_at: string
  tags: any[]
}

interface Capture {
  id: string
  site_id: string
  url: string
  status: string
  created_at: string
}

interface Site {
  id: string
  name: string
  url: string
}

export default function PagesPage() {
  // useParams 훅을 사용하여 클라이언트 측에서 params에 접근
  const params = useParams()
  const siteId = params.id as string

  const [site, setSite] = useState<Site | null>(null)
  const [pages, setPages] = useState<Page[]>([])
  const [captures, setCaptures] = useState<Capture[]>([])
  const [selectedCapture, setSelectedCapture] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")

  // useCallback으로 함수 메모이제이션
  const loadSiteData = useCallback(async () => {
    try {
      const data = await siteApi.getById(siteId)
      setSite(data)
    } catch (error) {
      console.error("Error loading site:", error)
      toast.error("사이트 정보를 불러오는 중 오류가 발생했습니다.")
    }
  }, [siteId])

  const loadCaptures = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await captureApi.getAll({ site_id: siteId })
      setCaptures(data)
    } catch (error) {
      console.error("Error loading captures:", error)
      toast.error("캡처 정보를 불러오는 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }, [siteId])

  const loadPages = useCallback(async (captureId: string) => {
    try {
      setIsLoading(true)
      const data = await pageApi.getAll({ capture_id: captureId })
      setPages(data)
    } catch (error) {
      console.error("Error loading pages:", error)
      toast.error("페이지 정보를 불러오는 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }, [])

  // 초기 데이터 로딩
  useEffect(() => {
    loadSiteData()
    loadCaptures()
  }, [loadSiteData, loadCaptures])

  // 캡처 선택 처리
  useEffect(() => {
    if (captures.length > 0 && !selectedCapture) {
      setSelectedCapture(captures[0].id)
    }
  }, [captures, selectedCapture])

  // 선택된 캡처의 페이지 로딩
  useEffect(() => {
    if (selectedCapture) {
      loadPages(selectedCapture)
    }
  }, [selectedCapture, loadPages])

  const handleDeletePage = async (id: string) => {
    try {
      await pageApi.delete(id)
      toast.success("페이지가 삭제되었습니다.")
      if (selectedCapture) {
        loadPages(selectedCapture)
      }
    } catch (error) {
      console.error("Error deleting page:", error)
      toast.error("페이지 삭제 중 오류가 발생했습니다.")
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "captured":
        return (
          <Badge variant="default" className="bg-green-500 hover:bg-green-600">
            캡처됨
          </Badge>
        )
      case "pending":
        return (
          <Badge
            variant="secondary"
            className="bg-yellow-500 hover:bg-yellow-600"
          >
            대기중
          </Badge>
        )
      case "failed":
        return <Badge variant="destructive">실패</Badge>
      default:
        return <Badge variant="outline">{status || "상태 없음"}</Badge>
    }
  }

  const filteredPages = pages.filter(
    (page) =>
      page.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      page.url?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      page.menu_path?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <Link href={`/sites/${siteId}`}>
          <Button variant="outline" size="sm" className="mr-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> 사이트로 돌아가기
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">
          {site ? `${site.name}의 페이지 관리` : "페이지 관리"}
        </h1>
      </div>

      {isLoading && !captures.length ? (
        <div className="text-center my-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4">불러오는 중...</p>
        </div>
      ) : captures.length === 0 ? (
        <div className="text-center my-10 p-6 border rounded-lg">
          <p className="text-lg text-gray-500">캡처 기록이 없습니다.</p>
          <Button className="mt-4">새 캡처 생성하기</Button>
        </div>
      ) : (
        <>
          <Tabs
            defaultValue={selectedCapture || ""}
            onValueChange={setSelectedCapture}
            className="mb-6"
          >
            <div className="flex items-center justify-between mb-4">
              <TabsList>
                {captures.map((capture) => (
                  <TabsTrigger key={capture.id} value={capture.id}>
                    {new Date(capture.created_at).toLocaleDateString()} 캡처
                  </TabsTrigger>
                ))}
              </TabsList>
              <Input
                type="text"
                placeholder="페이지 검색..."
                className="max-w-xs"
                value={searchTerm}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setSearchTerm(e.target.value)
                }
              />
            </div>

            {captures.map((capture) => (
              <TabsContent key={capture.id} value={capture.id}>
                {isLoading ? (
                  <div className="text-center my-10">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mx-auto"></div>
                    <p className="mt-4">불러오는 중...</p>
                  </div>
                ) : filteredPages.length === 0 ? (
                  <div className="text-center my-10 p-6 border rounded-lg">
                    <p className="text-lg text-gray-500">
                      {pages.length === 0
                        ? "이 캡처에 등록된 페이지가 없습니다."
                        : "검색 결과가 없습니다."}
                    </p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>제목</TableHead>
                        <TableHead>URL</TableHead>
                        <TableHead>메뉴 경로</TableHead>
                        <TableHead>깊이</TableHead>
                        <TableHead>상태</TableHead>
                        <TableHead>스크린샷</TableHead>
                        <TableHead>작업</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredPages.map((page) => (
                        <TableRow key={page.id}>
                          <TableCell className="font-medium">
                            <Link
                              href={`/sites/${siteId}/pages/${page.id}`}
                              className="text-blue-600 hover:underline"
                            >
                              {page.title || "제목 없음"}
                            </Link>
                          </TableCell>
                          <TableCell className="max-w-xs truncate">
                            <a
                              href={page.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline"
                            >
                              {page.url}
                            </a>
                          </TableCell>
                          <TableCell>{page.menu_path || "-"}</TableCell>
                          <TableCell>{page.depth}</TableCell>
                          <TableCell>{getStatusBadge(page.status)}</TableCell>
                          <TableCell>
                            <Link
                              href={`/sites/${siteId}/pages/${page.id}/screenshots`}
                            >
                              <Button variant="outline" size="sm">
                                <ImageIcon className="w-4 h-4 mr-1" /> 스크린샷
                                보기
                              </Button>
                            </Link>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Link href={`/sites/${siteId}/pages/${page.id}`}>
                                <Button variant="ghost" size="sm">
                                  <Eye className="w-4 h-4" />
                                </Button>
                              </Link>
                              <Link
                                href={`/sites/${siteId}/pages/${page.id}/edit`}
                              >
                                <Button variant="ghost" size="sm">
                                  <Pencil className="w-4 h-4" />
                                </Button>
                              </Link>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeletePage(page.id)}
                              >
                                <Trash className="w-4 h-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </>
      )}
    </div>
  )
}
