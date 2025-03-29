"use client"

import React, { useEffect, useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { Button } from "@workspace/ui/components/button"
import { ArrowLeft, ChevronRight, Eye, Pencil, Trash } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { Badge } from "@workspace/ui/components/badge"
import { siteApi, menuStructureApi } from "@/lib/api"
import { toast } from "sonner"

// 메뉴 구조 및 사이트 인터페이스 정의
interface MenuStructure {
  id: string
  site_id: string
  capture_id: string
  structure: any
  extraction_method: string
  verified: boolean
  created_at: string
  updated_at: string
}

interface Site {
  id: string
  name: string
  url: string
}

export default function MenuStructuresPage() {
  // useParams 훅을 사용하여 클라이언트 측에서 params에 접근
  const params = useParams()
  const siteId = params.id as string

  const [site, setSite] = useState<Site | null>(null)
  const [menuStructures, setMenuStructures] = useState<MenuStructure[]>([])
  const [selectedMenu, setSelectedMenu] = useState<MenuStructure | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadSiteData()
    loadMenuStructures()
  }, [])

  const loadSiteData = async () => {
    try {
      const data = await siteApi.getById(siteId)
      setSite(data)
    } catch (error) {
      console.error("Error loading site:", error)
      toast.error("사이트 정보를 불러오는 중 오류가 발생했습니다.")
    }
  }

  const loadMenuStructures = async () => {
    try {
      setIsLoading(true)
      const data = await menuStructureApi.getAll({ site_id: siteId })
      setMenuStructures(data)
      if (data.length > 0) {
        setSelectedMenu(data[0])
      }
    } catch (error) {
      console.error("Error loading menu structures:", error)
      toast.error("메뉴 구조 정보를 불러오는 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  // 메뉴 구조 삭제 처리
  const handleDeleteMenuStructure = async (id: string) => {
    try {
      await menuStructureApi.delete(id)
      toast.success("메뉴 구조가 삭제되었습니다.")
      loadMenuStructures()
    } catch (error) {
      console.error("Error deleting menu structure:", error)
      toast.error("메뉴 구조 삭제 중 오류가 발생했습니다.")
    }
  }

  // 메뉴 구조 시각화 렌더링 함수
  const renderMenuStructure = (structure: any) => {
    if (!structure) return null

    const { main_menu = [], sub_menu = [] } = structure

    // 메인 메뉴와 서브 메뉴를 조합하여 트리 생성
    const menuTree = {}

    // 메인 메뉴 항목 추가
    main_menu.forEach((item) => {
      menuTree[item.title] = {
        ...item,
        children: [],
      }
    })

    // 서브 메뉴 항목 추가
    sub_menu.forEach((item) => {
      if (item.parent && menuTree[item.parent]) {
        menuTree[item.parent].children.push(item)
      }
    })

    return (
      <div className="space-y-4">
        {Object.values(menuTree).map((menuItem: any) => (
          <div key={menuItem.title} className="border rounded-lg p-3">
            <div className="flex justify-between items-center">
              <div className="font-semibold flex items-center">
                {menuItem.url ? (
                  <a
                    href={`${site?.url}/${menuItem.url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {menuItem.title}
                  </a>
                ) : (
                  <span>{menuItem.title}</span>
                )}
                <Badge variant="outline" className="ml-2">
                  깊이: {menuItem.depth}
                </Badge>
              </div>
              <Eye className="w-4 h-4 text-gray-500" />
            </div>

            {menuItem.children.length > 0 && (
              <div className="ml-6 mt-2 space-y-2 border-l pl-4">
                {menuItem.children.map((child: any) => (
                  <div
                    key={child.title}
                    className="flex justify-between items-center"
                  >
                    <div className="flex items-center">
                      <ChevronRight className="w-3 h-3 mr-1 text-gray-400" />
                      {child.url ? (
                        <a
                          href={`${site?.url}/${child.url}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {child.title}
                        </a>
                      ) : (
                        <span>{child.title}</span>
                      )}
                      <Badge variant="outline" className="ml-2 text-xs">
                        깊이: {child.depth}
                      </Badge>
                    </div>
                    <Eye className="w-3 h-3 text-gray-500" />
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <Link href={`/sites/${siteId}`}>
          <Button variant="outline" size="sm" className="mr-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> 사이트로 돌아가기
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">
          {site ? `${site.name}의 메뉴 구조` : "메뉴 구조 관리"}
        </h1>
      </div>

      {isLoading ? (
        <div className="text-center my-10">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4">불러오는 중...</p>
        </div>
      ) : menuStructures.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>메뉴 구조 없음</CardTitle>
            <CardDescription>
              이 사이트에 등록된 메뉴 구조가 없습니다.
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button>캡처 생성하기</Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>메뉴 구조 목록</CardTitle>
                <CardDescription>캡처별 메뉴 구조를 확인하세요</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {menuStructures.map((menu) => (
                    <div
                      key={menu.id}
                      className={`p-3 rounded-md cursor-pointer flex justify-between items-center ${
                        selectedMenu?.id === menu.id
                          ? "bg-gray-100 dark:bg-gray-800"
                          : "hover:bg-gray-50 dark:hover:bg-gray-900"
                      }`}
                      onClick={() => setSelectedMenu(menu)}
                    >
                      <div>
                        <div className="font-medium">
                          {new Date(menu.created_at).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          방식: {menu.extraction_method}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={menu.verified ? "default" : "outline"}>
                          {menu.verified ? "검증됨" : "미검증"}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteMenuStructure(menu.id)
                          }}
                        >
                          <Trash className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>메뉴 구조 상세</CardTitle>
                    <CardDescription>
                      {selectedMenu
                        ? `${new Date(
                            selectedMenu.created_at
                          ).toLocaleString()} 생성됨 (${
                            selectedMenu.extraction_method
                          } 방식)`
                        : "메뉴 구조를 선택하세요"}
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm">
                    <Pencil className="w-4 h-4 mr-1" /> 수정
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {selectedMenu ? (
                  renderMenuStructure(selectedMenu.structure)
                ) : (
                  <div className="text-center py-10 text-gray-500">
                    왼쪽에서 메뉴 구조를 선택하세요
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}
