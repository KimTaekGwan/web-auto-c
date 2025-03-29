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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"
import { Button } from "@workspace/ui/components/button"
import { Skeleton } from "@workspace/ui/components/skeleton"
import { toast } from "sonner"
import Link from "next/link"
import { tagApi } from "../../lib/api"

interface Tag {
  id: string
  name: string
  color: string
  created_at: string
  updated_at: string
}

export default function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadTags() {
      try {
        const data = await tagApi.getAll()
        setTags(data)
      } catch (error) {
        console.error(error)
        toast.error("태그 목록을 불러오는데 실패했습니다.")
      } finally {
        setLoading(false)
      }
    }

    loadTags()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">태그 관리</h1>
          <p className="text-muted-foreground">
            사이트와 페이지에 사용되는 태그들을 관리합니다.
          </p>
        </div>
        <Button asChild>
          <Link href="/tags/new">새 태그 추가</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>태그 목록</CardTitle>
          <CardDescription>생성된 모든 태그들</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>태그명</TableHead>
                <TableHead>색상</TableHead>
                <TableHead>사용 횟수</TableHead>
                <TableHead>생성일</TableHead>
                <TableHead>마지막 업데이트</TableHead>
                <TableHead className="text-right">관리</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Skeleton className="h-4 w-[100px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-[60px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-[30px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-[80px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-[80px]" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-[60px]" />
                    </TableCell>
                  </TableRow>
                ))
              ) : tags.length > 0 ? (
                tags.map((tag) => (
                  <TableRow key={tag.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: tag.color || "#ccc" }}
                        ></div>
                        {tag.name}
                      </div>
                    </TableCell>
                    <TableCell>{tag.color || "지정안됨"}</TableCell>
                    <TableCell>-</TableCell>
                    <TableCell>
                      {new Date(tag.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {tag.updated_at
                        ? new Date(tag.updated_at).toLocaleDateString()
                        : "-"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/tags/${tag.id}`}>수정</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    className="text-center text-muted-foreground"
                  >
                    생성된 태그가 없습니다.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
