"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useRouter } from "next/navigation"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"
import { Input } from "@workspace/ui/components/input"
import { Label } from "@workspace/ui/components/label"
import { Button } from "@workspace/ui/components/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@workspace/ui/components/select"
import { Checkbox } from "@workspace/ui/components/checkbox"
import { toast } from "sonner"
import { useEffect, useState } from "react"
import { captureApi, siteApi } from "../../../lib/api"

interface Site {
  id: string
  name: string
  url: string
}

const captureFormSchema = z.object({
  siteId: z.string().min(1, "사이트를 선택해주세요"),
  url: z.string().url("올바른 URL을 입력해주세요"),
  devices: z
    .object({
      desktop: z.boolean(),
      tablet: z.boolean(),
      mobile: z.boolean(),
    })
    .refine((data) => data.desktop || data.tablet || data.mobile, {
      message: "최소 하나의 디바이스를 선택해주세요",
    }),
  options: z.object({
    fullPage: z.boolean(),
    dynamicElements: z.boolean(),
  }),
  tags: z.string().optional(),
})

type CaptureFormValues = z.infer<typeof captureFormSchema>

export default function NewCapturePage() {
  const router = useRouter()
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(true)

  const form = useForm<CaptureFormValues>({
    resolver: zodResolver(captureFormSchema),
    defaultValues: {
      siteId: "",
      url: "",
      devices: {
        desktop: true,
        tablet: false,
        mobile: false,
      },
      options: {
        fullPage: true,
        dynamicElements: false,
      },
      tags: "",
    },
  })

  useEffect(() => {
    async function loadSites() {
      try {
        // FastAPI 직접 호출
        const data = await siteApi.getAll()
        setSites(data)
      } catch (error) {
        console.error(error)
        toast.error("사이트 목록을 불러오는데 실패했습니다.")
      } finally {
        setLoading(false)
      }
    }

    loadSites()
  }, [])

  async function onSubmit(data: CaptureFormValues) {
    try {
      // FastAPI 직접 호출
      const result = await captureApi.create(data)

      toast.success("캡처가 성공적으로 시작되었습니다.")
      router.push("/captures")
    } catch (error) {
      console.error(error)
      toast.error(
        error instanceof Error ? error.message : "서버 오류가 발생했습니다."
      )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">새 캡처 시작</h1>
        <p className="text-muted-foreground">
          새로운 웹 페이지 캡처를 시작합니다.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>캡처 설정</CardTitle>
          <CardDescription>캡처할 페이지와 설정을 입력하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="site">사이트 선택</Label>
              <Select onValueChange={(value) => form.setValue("siteId", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="사이트를 선택하세요" />
                </SelectTrigger>
                <SelectContent>
                  {loading ? (
                    <SelectItem value="loading" disabled>
                      로딩 중...
                    </SelectItem>
                  ) : sites.length > 0 ? (
                    sites.map((site) => (
                      <SelectItem key={site.id} value={site.id}>
                        {site.name}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="empty" disabled>
                      등록된 사이트가 없습니다
                    </SelectItem>
                  )}
                  <SelectItem
                    value="new"
                    onClick={() => router.push("/sites/new")}
                  >
                    새 사이트 추가...
                  </SelectItem>
                </SelectContent>
              </Select>
              {form.formState.errors.siteId && (
                <p className="text-sm text-red-500">
                  {form.formState.errors.siteId.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="url">페이지 URL</Label>
              <Input
                id="url"
                type="url"
                placeholder="https://example.com/page"
                {...form.register("url")}
              />
              {form.formState.errors.url && (
                <p className="text-sm text-red-500">
                  {form.formState.errors.url.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label>캡처 디바이스</Label>
              <div className="grid gap-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="desktop"
                    checked={form.watch("devices.desktop")}
                    onCheckedChange={(checked: boolean) =>
                      form.setValue("devices.desktop", checked)
                    }
                  />
                  <Label htmlFor="desktop">데스크톱 (1920×1080)</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="tablet"
                    checked={form.watch("devices.tablet")}
                    onCheckedChange={(checked: boolean) =>
                      form.setValue("devices.tablet", checked)
                    }
                  />
                  <Label htmlFor="tablet">태블릿 (768×1024)</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="mobile"
                    checked={form.watch("devices.mobile")}
                    onCheckedChange={(checked: boolean) =>
                      form.setValue("devices.mobile", checked)
                    }
                  />
                  <Label htmlFor="mobile">모바일 (375×667)</Label>
                </div>
              </div>
              {form.formState.errors.devices && (
                <p className="text-sm text-red-500">
                  {form.formState.errors.devices.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label>캡처 옵션</Label>
              <div className="grid gap-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="fullPage"
                    checked={form.watch("options.fullPage")}
                    onCheckedChange={(checked: boolean) =>
                      form.setValue("options.fullPage", checked)
                    }
                  />
                  <Label htmlFor="fullPage">전체 페이지 캡처</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="dynamicElements"
                    checked={form.watch("options.dynamicElements")}
                    onCheckedChange={(checked: boolean) =>
                      form.setValue("options.dynamicElements", checked)
                    }
                  />
                  <Label htmlFor="dynamicElements">동적 요소 포함</Label>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="tags">태그</Label>
              <Input
                id="tags"
                placeholder="쉼표로 구분하여 입력"
                {...form.register("tags")}
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                취소
              </Button>
              <Button type="submit">캡처 시작</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
