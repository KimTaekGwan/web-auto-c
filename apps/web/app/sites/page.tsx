"use client"

import React, { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@workspace/ui/components/button"
import { PlusIcon } from "lucide-react"
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
import { siteApi, demoApi, tagApi } from "@/lib/api"
import { toast } from "sonner"

interface Tag {
  id: string
  name: string
  color: string
}

interface Site {
  id: string
  name: string
  url: string
  description: string
  status: string
  notes: string
  created_at: string
  updated_at: string
  tags: Tag[]
}

export default function SitesPage() {
  const [sites, setSites] = useState<Site[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedTag, setSelectedTag] = useState<string | null>(null)

  useEffect(() => {
    fetchSites()
    fetchTags()
  }, [])

  const fetchSites = async () => {
    try {
      setIsLoading(true)
      const data = await siteApi.getAll()
      setSites(data)
    } catch (error) {
      console.error("Error fetching sites:", error)
      toast.error("사이트 정보를 불러오는 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  const fetchTags = async () => {
    try {
      const data = await tagApi.getAll()
      setTags(data)
    } catch (error) {
      console.error("Error fetching tags:", error)
      toast.error("태그 정보를 불러오는 중 오류가 발생했습니다.")
    }
  }

  const handleGenerateDemoData = async () => {
    try {
      setIsLoading(true)
      await demoApi.generateData(5)
      toast.success("더미 데이터가 성공적으로 생성되었습니다.")
      await fetchSites()
      await fetchTags()
    } catch (error) {
      console.error("Error generating demo data:", error)
      toast.error("데모 데이터 생성 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteSite = async (id: string) => {
    try {
      await siteApi.delete(id)
      toast.success("사이트가 성공적으로 삭제되었습니다.")
      await fetchSites()
    } catch (error) {
      console.error("Error deleting site:", error)
      toast.error("사이트 삭제 중 오류가 발생했습니다.")
    }
  }

  const filteredSites = sites
    .filter(
      (site) =>
        site.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        site.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (site.description &&
          site.description.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .filter((site) =>
      selectedTag ? site.tags.some((tag) => tag.id === selectedTag) : true
    )

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">사이트 관리</h1>
        <div className="flex gap-2">
          <Button onClick={handleGenerateDemoData} variant="outline">
            더미 데이터 생성
          </Button>
          <Link href="/sites/add">
            <Button>
              <PlusIcon className="mr-2 h-4 w-4" /> 사이트 추가
            </Button>
          </Link>
        </div>
      </div>

      <div className="mb-6 flex gap-4">
        <Input
          type="text"
          placeholder="사이트 검색..."
          className="max-w-sm"
          value={searchTerm}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setSearchTerm(e.target.value)
          }
        />

        <div className="flex gap-2 items-center flex-wrap">
          <Badge
            variant={selectedTag === null ? "secondary" : "outline"}
            className="cursor-pointer"
            onClick={() => setSelectedTag(null)}
          >
            전체
          </Badge>
          {tags.map((tag) => (
            <Badge
              key={tag.id}
              variant={selectedTag === tag.id ? "secondary" : "outline"}
              className="cursor-pointer"
              style={{
                backgroundColor:
                  selectedTag === tag.id ? tag.color : "transparent",
                borderColor: tag.color,
              }}
              onClick={() =>
                setSelectedTag(tag.id === selectedTag ? null : tag.id)
              }
            >
              {tag.name}
            </Badge>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="text-center my-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4">불러오는 중...</p>
        </div>
      ) : (
        <>
          {filteredSites.length === 0 ? (
            <div className="text-center my-10">
              <p className="text-lg text-gray-500">
                {sites.length === 0
                  ? "등록된 사이트가 없습니다. 새 사이트를 추가하거나 더미 데이터를 생성해보세요."
                  : "검색 결과가 없습니다."}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>이름</TableHead>
                  <TableHead>URL</TableHead>
                  <TableHead>설명</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>태그</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSites.map((site) => (
                  <TableRow key={site.id}>
                    <TableCell className="font-medium">
                      <Link
                        href={`/sites/${site.id}`}
                        className="text-blue-600 hover:underline"
                      >
                        {site.name}
                      </Link>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      <a
                        href={site.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {site.url}
                      </a>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {site.description}
                    </TableCell>
                    <TableCell>
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
                            ? "bg-green-500 hover:bg-green-600"
                            : site.status === "pending"
                              ? "bg-yellow-500 hover:bg-yellow-600"
                              : ""
                        }
                      >
                        {site.status || "없음"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {site.tags?.map((tag) => (
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
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      {new Date(site.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Link href={`/sites/${site.id}/edit`}>
                          <Button size="sm" variant="outline">
                            편집
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteSite(site.id)}
                        >
                          삭제
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </>
      )}
    </div>
  )
}
