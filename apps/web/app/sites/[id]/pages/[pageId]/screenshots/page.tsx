"use client"

import React, { useEffect, useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@workspace/ui/components/button"
import { ArrowLeft, TrashIcon, UploadIcon } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { Badge } from "@workspace/ui/components/badge"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"
import { pageApi, pageScreenshotApi } from "@/lib/api"
import { toast } from "sonner"

// 인터페이스 정의
interface Page {
  id: string
  site_id: string
  capture_id: string
  title: string
  url: string
  menu_path: string
}

interface Screenshot {
  id: string
  page_id: string
  device_type: string
  width: number
  screenshot_path: string
  thumbnail_path?: string
  is_current: boolean
  created_at: string
}

export default function ScreenshotsPage({
  params,
}: {
  params: { id: string; pageId: string }
}) {
  const [page, setPage] = useState<Page | null>(null)
  const [screenshots, setScreenshots] = useState<Screenshot[]>([])
  const [deviceTypes, setDeviceTypes] = useState<string[]>([])
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadPage()
    loadScreenshots()
  }, [])

  useEffect(() => {
    if (screenshots.length > 0) {
      // 스크린샷에서 디바이스 타입 추출 (중복 제거)
      const types = [...new Set(screenshots.map((s) => s.device_type))]
      setDeviceTypes(types)

      // 기본 선택 디바이스 설정
      if (!selectedDevice && types.length > 0) {
        setSelectedDevice(types[0])
      }
    }
  }, [screenshots])

  const loadPage = async () => {
    try {
      const data = await pageApi.getById(params.pageId)
      setPage(data)
    } catch (error) {
      console.error("Error loading page:", error)
      toast.error("페이지 정보를 불러오는 중 오류가 발생했습니다.")
    }
  }

  const loadScreenshots = async () => {
    try {
      setIsLoading(true)
      const data = await pageScreenshotApi.getAll({ page_id: params.pageId })
      setScreenshots(data)
    } catch (error) {
      console.error("Error loading screenshots:", error)
      toast.error("스크린샷을 불러오는 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteScreenshot = async (id: string) => {
    try {
      await pageScreenshotApi.delete(id)
      toast.success("스크린샷이 삭제되었습니다.")
      loadScreenshots()
    } catch (error) {
      console.error("Error deleting screenshot:", error)
      toast.error("스크린샷 삭제 중 오류가 발생했습니다.")
    }
  }

  // 디바이스 타입으로 필터링된 스크린샷
  const filteredScreenshots = selectedDevice
    ? screenshots.filter((s) => s.device_type === selectedDevice)
    : screenshots

  // 현재 스크린샷과 기록 구분
  const currentScreenshots = filteredScreenshots.filter((s) => s.is_current)
  const historicalScreenshots = filteredScreenshots.filter((s) => !s.is_current)

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <Link href={`/sites/${params.id}/pages`}>
          <Button variant="outline" size="sm" className="mr-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> 페이지 목록으로
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">
          {page
            ? `'${page.title || "제목 없음"}' 페이지 스크린샷`
            : "스크린샷 관리"}
        </h1>
      </div>

      {page && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>페이지 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">URL</h3>
                <a
                  href={page.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {page.url}
                </a>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">
                  메뉴 경로
                </h3>
                <p>{page.menu_path || "-"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="text-center my-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4">불러오는 중...</p>
        </div>
      ) : screenshots.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>스크린샷 없음</CardTitle>
            <CardDescription>
              이 페이지에 등록된 스크린샷이 없습니다.
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button>
              <UploadIcon className="w-4 h-4 mr-1" /> 스크린샷 업로드
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <>
          <div className="mb-6">
            <TabsList className="mb-4">
              {deviceTypes.map((deviceType) => (
                <TabsTrigger
                  key={deviceType}
                  value={deviceType}
                  onClick={() => deviceType && setSelectedDevice(deviceType)}
                  className={
                    selectedDevice === deviceType
                      ? "bg-primary text-primary-foreground"
                      : ""
                  }
                >
                  {deviceType}
                </TabsTrigger>
              ))}
            </TabsList>

            <Button className="ml-2">
              <UploadIcon className="w-4 h-4 mr-1" /> 새 스크린샷 업로드
            </Button>
          </div>

          {currentScreenshots.length > 0 && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">현재 스크린샷</h2>
              <div className="grid grid-cols-1 gap-6">
                {currentScreenshots.map((screenshot) => (
                  <Card key={screenshot.id} className="overflow-hidden">
                    <CardHeader className="bg-gray-50 dark:bg-gray-800">
                      <div className="flex justify-between items-center">
                        <div>
                          <CardTitle className="text-base">
                            {screenshot.device_type} ({screenshot.width}px)
                          </CardTitle>
                          <CardDescription>
                            {new Date(screenshot.created_at).toLocaleString()}
                          </CardDescription>
                        </div>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteScreenshot(screenshot.id)}
                        >
                          <TrashIcon className="w-4 h-4 mr-1" /> 삭제
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="relative">
                        <a
                          href={screenshot.screenshot_path}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <img
                            src={screenshot.screenshot_path}
                            alt={`${page?.title || "페이지"} 스크린샷 - ${screenshot.device_type}`}
                            className="w-full h-auto border-t"
                          />
                        </a>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {historicalScreenshots.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">
                이전 스크린샷 ({historicalScreenshots.length}개)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {historicalScreenshots.map((screenshot) => (
                  <Card key={screenshot.id} className="overflow-hidden">
                    <div className="relative aspect-video">
                      <a
                        href={screenshot.screenshot_path}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <img
                          src={screenshot.screenshot_path}
                          alt={`${page?.title || "페이지"} 스크린샷 - ${screenshot.device_type}`}
                          className="object-cover w-full h-full"
                        />
                      </a>
                    </div>
                    <CardFooter className="flex justify-between py-2">
                      <div className="text-sm">
                        {new Date(screenshot.created_at).toLocaleDateString()}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteScreenshot(screenshot.id)}
                      >
                        <TrashIcon className="w-4 h-4" />
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
