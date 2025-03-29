"use client"

import { useEffect, useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"
import { Button } from "@workspace/ui/components/button"
import { Badge } from "@workspace/ui/components/badge"
import { Skeleton } from "@workspace/ui/components/skeleton"
import Link from "next/link"
import { toast } from "sonner"
import { dashboardApi } from "../lib/api"

interface DashboardStats {
  totalSites: number
  totalCaptures: number
  totalTags: number
  recentCaptures: {
    id: string
    url: string
    status: string
    createdAt: string
    devices: string[]
    siteName?: string
  }[]
  deviceStats: {
    desktop: number
    tablet: number
    mobile: number
  }
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await dashboardApi.getStats()
        setStats(data)
      } catch (error) {
        console.error(error)
        toast.error("통계 데이터를 불러오는데 실패했습니다.")
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">대시보드</h1>
          <p className="text-muted-foreground">
            웹 캡처 현황을 한눈에 확인하세요.
          </p>
        </div>
        <div className="flex space-x-2">
          <Button asChild>
            <Link href="/sites/new">새 사이트 추가</Link>
          </Button>
          <Button asChild>
            <Link href="/captures/new">새 캡처 시작</Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="recent">최근 캡처</TabsTrigger>
          <TabsTrigger value="stats">통계</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  전체 사이트
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <div className="text-2xl font-bold">{stats?.totalSites}</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">전체 캡처</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <div className="text-2xl font-bold">
                    {stats?.totalCaptures}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">전체 태그</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <div className="text-2xl font-bold">{stats?.totalTags}</div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>최근 활동</CardTitle>
                <CardDescription>최근 수행된 작업들</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  아직 활동이 없습니다.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>인기 태그</CardTitle>
                <CardDescription>자주 사용되는 태그들</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  아직 태그가 없습니다.
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="recent">
          <Card>
            <CardHeader>
              <CardTitle>최근 캡처 목록</CardTitle>
              <CardDescription>최근에 수행된 캡처 작업들</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  <Skeleton className="h-12" />
                  <Skeleton className="h-12" />
                </div>
              ) : (
                <div className="space-y-2">
                  {stats?.recentCaptures.map((capture) => (
                    <div
                      key={capture.id}
                      className="flex items-center justify-between p-2 border rounded"
                    >
                      <div>
                        <div className="font-medium truncate max-w-[300px]">
                          {capture.url}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(capture.createdAt).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="flex -space-x-1">
                          {capture.devices.map((device) => (
                            <Badge key={device} variant="outline">
                              {device}
                            </Badge>
                          ))}
                        </div>
                        <Badge
                          variant={
                            capture.status === "COMPLETED" ||
                            capture.status === "completed"
                              ? "outline"
                              : "secondary"
                          }
                        >
                          {capture.status === "COMPLETED" ||
                          capture.status === "completed"
                            ? "완료"
                            : "진행 중"}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats">
          <Card>
            <CardHeader>
              <CardTitle>통계</CardTitle>
              <CardDescription>캡처 및 사이트 통계</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  <Skeleton className="h-8" />
                  <Skeleton className="h-8" />
                  <Skeleton className="h-8" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">데스크톱</div>
                      <div>{stats?.deviceStats.desktop}</div>
                    </div>
                    <div className="h-2 bg-muted rounded overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{
                          width: `${
                            ((stats?.deviceStats.desktop ?? 0) /
                              (stats?.totalCaptures ?? 1)) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">태블릿</div>
                      <div>{stats?.deviceStats.tablet}</div>
                    </div>
                    <div className="h-2 bg-muted rounded overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{
                          width: `${
                            ((stats?.deviceStats.tablet ?? 0) /
                              (stats?.totalCaptures ?? 1)) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">모바일</div>
                      <div>{stats?.deviceStats.mobile}</div>
                    </div>
                    <div className="h-2 bg-muted rounded overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{
                          width: `${
                            ((stats?.deviceStats.mobile ?? 0) /
                              (stats?.totalCaptures ?? 1)) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
