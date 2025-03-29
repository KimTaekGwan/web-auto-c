"use client"

import { useEffect, useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"
import { Button } from "@workspace/ui/components/button"
import { Input } from "@workspace/ui/components/input"
import { Badge } from "@workspace/ui/components/badge"
import { Skeleton } from "@workspace/ui/components/skeleton"
import Link from "next/link"
import { toast } from "sonner"
import { captureApi } from "../../lib/api"

interface Capture {
  id: string
  site_id: string
  site?: {
    name: string
  }
  url: string
  status: string
  devices: string[]
  created_at: string
  completed_at: string | null
  error: string | null
}

export default function CapturesPage() {
  const [captures, setCaptures] = useState<Capture[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    async function loadCaptures() {
      try {
        const data = await captureApi.getAll()
        setCaptures(data)
      } catch (error) {
        console.error(error)
        toast.error("캡처 목록을 불러오는데 실패했습니다.")
      } finally {
        setLoading(false)
      }
    }

    loadCaptures()
  }, [])

  const filteredCaptures = captures.filter((capture) => {
    const siteName = capture.site?.name?.toLowerCase() || ""
    const url = capture.url.toLowerCase()
    const query = searchQuery.toLowerCase()

    return siteName.includes(query) || url.includes(query)
  })

  const getStatusBadge = (status: string) => {
    const statusLower = status.toLowerCase()
    switch (statusLower) {
      case "pending":
        return <Badge variant="secondary">대기 중</Badge>
      case "in_progress":
        return <Badge>진행 중</Badge>
      case "completed":
        return <Badge variant="outline">완료</Badge>
      case "failed":
        return <Badge variant="destructive">실패</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">캡처 관리</h1>
          <p className="text-muted-foreground">
            웹 페이지 캡처 목록을 관리합니다.
          </p>
        </div>
        <Button asChild>
          <Link href="/captures/new">새 캡처 시작</Link>
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Input
          placeholder="사이트명, URL로 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>상태</TableHead>
              <TableHead>사이트</TableHead>
              <TableHead>URL</TableHead>
              <TableHead>디바이스</TableHead>
              <TableHead>시작 시간</TableHead>
              <TableHead>완료 시간</TableHead>
              <TableHead className="text-right">작업</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Skeleton className="h-4 w-[60px]" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-[150px]" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-[200px]" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-[100px]" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-[120px]" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-[120px]" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-[100px]" />
                  </TableCell>
                </TableRow>
              ))
            ) : filteredCaptures.length > 0 ? (
              filteredCaptures.map((capture) => (
                <TableRow key={capture.id}>
                  <TableCell>{getStatusBadge(capture.status)}</TableCell>
                  <TableCell>
                    <Link
                      href={`/sites/${capture.site_id}`}
                      className="font-medium hover:underline"
                    >
                      {capture.site?.name || "Unknown Site"}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <a
                      href={capture.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      {capture.url}
                    </a>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {Array.isArray(capture.devices) ? (
                        capture.devices.map((device) => (
                          <Badge key={device} variant="outline">
                            {device}
                          </Badge>
                        ))
                      ) : (
                        <Badge variant="outline">알 수 없음</Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {capture.created_at
                      ? new Date(capture.created_at).toLocaleString()
                      : "-"}
                  </TableCell>
                  <TableCell>
                    {capture.completed_at
                      ? new Date(capture.completed_at).toLocaleString()
                      : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      asChild
                      className="mr-2"
                    >
                      <Link href={`/captures/${capture.id}`}>상세</Link>
                    </Button>
                    {capture.status.toLowerCase() === "failed" && (
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/captures/new?retry=${capture.id}`}>
                          재시도
                        </Link>
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="text-center">
                  {searchQuery
                    ? "검색 결과가 없습니다."
                    : "캡처 내역이 없습니다."}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
