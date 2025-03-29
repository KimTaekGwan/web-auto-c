"use client"

import React, { useEffect, useState } from "react"
import Link from "next/link"
import useSWR from "swr"
import { useParams } from "next/navigation"
import { Button } from "@workspace/ui/components/button"
import { ArrowLeft, Edit, LayoutGrid, ListTree, Scan } from "lucide-react"
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
import { Separator } from "@workspace/ui/components/separator"
import { siteApi, captureApi, demoApi } from "@/lib/api"
import { toast } from "sonner"

// 사이트 및 캡처 인터페이스 정의
interface Site {
  id: string
  name: string
  url: string
  description: string
  status: string
  notes: string
  first_captured_at: string | null
  last_captured_at: string | null
  capture_count: number
  created_at: string
  updated_at: string
  tags: Array<{
    id: string
    name: string
    color: string
  }>
}

interface Capture {
  id: string
  site_id: string
  url: string
  status: string
  created_at: string
  started_at: string | null
  completed_at: string | null
}

// SWR 패쳐 함수 정의
const siteFetcher = (url: string) => {
  // ID에서 하이픈(-) 제거하여 백엔드가 기대하는 형식으로 변환
  const formattedId = url.replace(/-/g, "")
  return siteApi.getById(formattedId)
}

const capturesFetcher = ([url, siteId]: [string, string]) =>
  captureApi.getAll({ site_id: siteId, limit: 5 })

export default function SiteDetailPage() {
  // useParams 훅을 사용하여 클라이언트 측에서 params에 접근
  const params = useParams()
  const siteId = params.id as string

  // 데모 데이터 생성 함수
  const generateDemoData = async () => {
    try {
      await demoApi.generateData(3)
      toast.success("데모 데이터가 생성되었습니다.")
      window.location.reload()
    } catch (error) {
      console.error("Error generating demo data:", error)
      toast.error("데모 데이터 생성 중 오류가 발생했습니다.")
    }
  }

  // SWR을 사용한 데이터 페칭
  const {
    data: site,
    error: siteError,
    isLoading: siteIsLoading,
  } = useSWR(siteId, siteFetcher, {
    onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
      // 404 에러(존재하지 않는 사이트)나 422 에러(유효하지 않은 사이트 ID)의 경우 재시도 중지
      if (
        (error.response?.status === 404 || error.response?.status === 422) &&
        retryCount >= 1
      )
        return

      // 기본 재시도 로직 (최대 3번)
      if (retryCount >= 3) return

      // 1초 후 재시도
      setTimeout(() => revalidate({ retryCount }), 1000)
    },
  })

  const { data: latestCaptures, error: capturesError } = useSWR(
    siteId ? ["captures", siteId] : null,
    capturesFetcher,
    {
      onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
        // 404나 422 오류의 경우 재시도 중지
        if (
          (error.response?.status === 404 || error.response?.status === 422) &&
          retryCount >= 1
        )
          return
        if (retryCount >= 3) return
        setTimeout(() => revalidate({ retryCount }), 1000)
      },
    }
  )

  // 에러 처리 (로그만 남기고 화면에는 반영하지 않음)
  if (siteError) {
    console.error("Error loading site:", siteError)

    // 토스트 메시지만 표시하고 UI는 !site 조건에서 처리
    if (siteError.response?.status !== 404) {
      toast.error(`사이트 정보를 불러오는 중 오류가 발생했습니다.`)
    }
  }

  if (capturesError) {
    console.error("Error loading captures:", capturesError)
    if (capturesError.response?.status !== 404) {
      toast.error(`캡처 정보를 불러오는 중 오류가 발생했습니다.`)
    }
  }

  if (siteIsLoading) {
    return (
      <div className="container mx-auto py-6">
        <div className="text-center my-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4">불러오는 중...</p>
        </div>
      </div>
    )
  }

  if (!site) {
    return (
      <div className="container mx-auto py-6">
        <div className="text-center my-10">
          <h1 className="text-2xl font-bold text-red-500">
            사이트를 찾을 수 없습니다
          </h1>
          <div className="flex flex-col items-center gap-4 mt-4">
            <Link href="/sites">
              <Button className="mb-2">
                <ArrowLeft className="w-4 h-4 mr-1" /> 사이트 목록으로 돌아가기
              </Button>
            </Link>
            <Button onClick={generateDemoData} variant="outline">
              데모 데이터 생성하기
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Link href="/sites">
            <Button variant="outline" size="sm" className="mr-2">
              <ArrowLeft className="w-4 h-4 mr-1" /> 목록으로
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">{site.name}</h1>
          {site.status && (
            <Badge
              variant={
                site.status === "active"
                  ? "default"
                  : site.status === "pending"
                    ? "secondary"
                    : "outline"
              }
              className={
                site.status === "active"
                  ? "ml-3 bg-green-500 hover:bg-green-600"
                  : site.status === "pending"
                    ? "ml-3 bg-yellow-500 hover:bg-yellow-600"
                    : "ml-3"
              }
            >
              {site.status}
            </Badge>
          )}
        </div>

        <div className="flex gap-2">
          <Link href={`/sites/${site.id}/edit`}>
            <Button variant="outline">
              <Edit className="w-4 h-4 mr-1" /> 사이트 편집
            </Button>
          </Link>
          <Link href={`/captures/new?site_id=${site.id}`}>
            <Button>
              <Scan className="w-4 h-4 mr-1" /> 새 캡처 시작
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card className="md:col-span-3">
          <CardHeader>
            <CardTitle>사이트 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">URL</h3>
                <a
                  href={site.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {site.url}
                </a>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">
                  생성일
                </h3>
                <p>{new Date(site.created_at).toLocaleString()}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">설명</h3>
                <p>{site.description || "설명 없음"}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">
                  마지막 캡처
                </h3>
                <p>
                  {site.last_captured_at
                    ? new Date(site.last_captured_at).toLocaleString()
                    : "없음"}
                </p>
              </div>
              <div className="md:col-span-2">
                <h3 className="text-sm font-medium text-gray-500 mb-1">메모</h3>
                <p className="whitespace-pre-line">
                  {site.notes || "메모 없음"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>통계</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">
                  캡처 횟수
                </h3>
                <p className="text-2xl font-bold">{site.capture_count}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">태그</h3>
                <div className="flex flex-wrap gap-1 mt-1">
                  {site.tags?.length > 0 ? (
                    site.tags.map(
                      (tag: { id: string; name: string; color: string }) => (
                        <Badge
                          key={tag.id}
                          variant="outline"
                          style={{
                            backgroundColor: "transparent",
                            borderColor: tag.color,
                            color: tag.color,
                          }}
                        >
                          {tag.name}
                        </Badge>
                      )
                    )
                  ) : (
                    <span className="text-gray-500">태그 없음</span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <Link href={`/sites/${site.id}/captures`}>
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Scan className="w-5 h-5 mr-2" /> 캡처 관리
              </CardTitle>
              <CardDescription>
                이 사이트의 모든 캡처 기록을 관리합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>총 {site.capture_count}개의 캡처가 있습니다.</p>
              <div className="space-y-2">
                {latestCaptures?.length > 0 ? (
                  latestCaptures.map((capture: Capture) => (
                    <div
                      key={capture.id}
                      className="p-2 border rounded hover:bg-gray-50"
                    >
                      {new Date(capture.created_at).toLocaleDateString()} (
                      {capture.status})
                    </div>
                  ))
                ) : (
                  <span className="text-gray-500">최근 캡처 없음</span>
                )}
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">
                캡처 관리로 이동
              </Button>
            </CardFooter>
          </Card>
        </Link>

        <Link href={`/sites/${site.id}/menu-structures`}>
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <ListTree className="w-5 h-5 mr-2" /> 메뉴 구조
              </CardTitle>
              <CardDescription>
                웹사이트의 메뉴 구조와 페이지 계층을 확인합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>메뉴 구조는 사이트 탐색의 기본입니다.</p>
              <p className="mt-2 text-sm text-gray-500">
                AI를 통해 추출된 메뉴 구조를 검증하고 관리할 수 있습니다.
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">
                메뉴 구조 확인
              </Button>
            </CardFooter>
          </Card>
        </Link>

        <Link href={`/sites/${site.id}/pages`}>
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <LayoutGrid className="w-5 h-5 mr-2" /> 페이지 관리
              </CardTitle>
              <CardDescription>
                캡처된 모든 페이지와 스크린샷을 관리합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>
                캡처된 페이지의 상세 정보와 스크린샷을 확인하고 관리할 수
                있습니다.
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">
                페이지 관리로 이동
              </Button>
            </CardFooter>
          </Card>
        </Link>
      </div>
    </div>
  )
}
