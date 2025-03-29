"use client"

import React, { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { Button } from "@workspace/ui/components/button"
import { Badge } from "@workspace/ui/components/badge"
import { Skeleton } from "@workspace/ui/components/skeleton"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"
import Link from "next/link"
import { toast } from "sonner"

interface CaptureDetail {
  id: string
  siteId: string
  siteName: string
  url: string
  status: "pending" | "in_progress" | "completed" | "failed"
  devices: string[]
  createdAt: string
  completedAt: string | null
  error: string | null
  tags: string
  options: {
    fullPage: boolean
    dynamicElements: boolean
  }
  screenshots: {
    device: string
    url: string
    width: number
    height: number
  }[]
}

export default function CaptureDetailPage() {
  const params = useParams()
  const captureId = params.id as string

  const router = useRouter()
  const [capture, setCapture] = useState<CaptureDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null)

  useEffect(() => {
    async function loadCapture() {
      try {
        const response = await fetch(`/api/captures/${captureId}`)
        if (!response.ok) {
          throw new Error("캡처 정보를 불러오는데 실패했습니다.")
        }
        const data = await response.json()
        setCapture(data)
        if (data.devices.length > 0) {
          setSelectedDevice(data.devices[0])
        }
      } catch (error) {
        console.error(error)
        toast.error("캡처 정보를 불러오는데 실패했습니다.")
      } finally {
        setLoading(false)
      }
    }

    loadCapture()
  }, [captureId])

  const getStatusBadge = (status: CaptureDetail["status"]) => {
    switch (status) {
      case "pending":
        return <Badge variant="secondary">대기 중</Badge>
      case "in_progress":
        return <Badge>진행 중</Badge>
      case "completed":
        return <Badge variant="outline">완료</Badge>
      case "failed":
        return <Badge variant="destructive">실패</Badge>
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-[200px]" />
            <Skeleton className="h-4 w-[300px] mt-2" />
          </div>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-[150px]" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!capture) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh]">
        <h2 className="text-2xl font-bold">캡처를 찾을 수 없습니다.</h2>
        <p className="text-muted-foreground mt-2">
          요청하신 캡처 정보가 존재하지 않습니다.
        </p>
        <Button asChild className="mt-4">
          <Link href="/captures">목록으로 돌아가기</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold">캡처 상세</h1>
            {getStatusBadge(capture.status)}
          </div>
          <p className="text-muted-foreground mt-1">
            {capture.siteName} - {capture.url}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/captures">목록으로</Link>
          </Button>
          {capture.status === "failed" && (
            <Button asChild>
              <Link href={`/captures/new?retry=${capture.id}`}>재시도</Link>
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>기본 정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium">사이트</div>
              <Link
                href={`/sites/${capture.siteId}`}
                className="text-blue-500 hover:underline"
              >
                {capture.siteName}
              </Link>
            </div>
            <div>
              <div className="text-sm font-medium">URL</div>
              <a
                href={capture.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                {capture.url}
              </a>
            </div>
            <div>
              <div className="text-sm font-medium">시작 시간</div>
              <div>{new Date(capture.createdAt).toLocaleString()}</div>
            </div>
            {capture.completedAt && (
              <div>
                <div className="text-sm font-medium">완료 시간</div>
                <div>{new Date(capture.completedAt).toLocaleString()}</div>
              </div>
            )}
            <div>
              <div className="text-sm font-medium">태그</div>
              <div className="flex gap-1 mt-1">
                {capture.tags.split(",").map((tag) => (
                  <Badge key={tag} variant="outline">
                    {tag.trim()}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>캡처 설정</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium">디바이스</div>
              <div className="flex gap-1 mt-1">
                {capture.devices.map((device) => (
                  <Badge key={device} variant="outline">
                    {device}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium">옵션</div>
              <div className="space-y-2 mt-1">
                <div className="flex items-center gap-2">
                  <Badge
                    variant={capture.options.fullPage ? "default" : "outline"}
                  >
                    전체 페이지 캡처
                  </Badge>
                  <Badge
                    variant={
                      capture.options.dynamicElements ? "default" : "outline"
                    }
                  >
                    동적 요소 포함
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {capture.status === "failed" && capture.error && (
        <Card>
          <CardHeader>
            <CardTitle>오류 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-red-50 text-red-900 rounded p-4">
              {capture.error}
            </div>
          </CardContent>
        </Card>
      )}

      {capture.status === "completed" && capture.screenshots && (
        <Card>
          <CardHeader>
            <CardTitle>캡처 결과</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs
              value={selectedDevice || undefined}
              onValueChange={setSelectedDevice}
            >
              <TabsList>
                {capture.screenshots.map((screenshot) => (
                  <TabsTrigger
                    key={screenshot.device}
                    value={screenshot.device}
                  >
                    {screenshot.device}
                  </TabsTrigger>
                ))}
              </TabsList>
              {capture.screenshots.map((screenshot) => (
                <TabsContent key={screenshot.device} value={screenshot.device}>
                  <div className="border rounded p-4">
                    <img
                      src={screenshot.url}
                      alt={`${screenshot.device} 캡처 이미지`}
                      className="w-full h-auto"
                    />
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
