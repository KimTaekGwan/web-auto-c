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
import { toast } from "sonner"
import { siteApi } from "../../../lib/api"

const siteFormSchema = z.object({
  name: z.string().min(1, "사이트명을 입력해주세요"),
  url: z.string().url("올바른 URL을 입력해주세요"),
  description: z.string().optional(),
  tags: z.string().optional(),
})

type SiteFormValues = z.infer<typeof siteFormSchema>

export default function NewSitePage() {
  const router = useRouter()
  const form = useForm<SiteFormValues>({
    resolver: zodResolver(siteFormSchema),
    defaultValues: {
      name: "",
      url: "",
      description: "",
      tags: "",
    },
  })

  async function onSubmit(data: SiteFormValues) {
    try {
      // FastAPI 직접 호출
      await siteApi.create(data)

      toast.success("사이트가 성공적으로 등록되었습니다.")
      router.push("/sites")
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
        <h1 className="text-3xl font-bold">새 사이트 추가</h1>
        <p className="text-muted-foreground">새로운 웹사이트를 등록합니다.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>사이트 정보</CardTitle>
          <CardDescription>
            등록할 사이트의 기본 정보를 입력하세요.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">사이트명</Label>
              <Input
                id="name"
                placeholder="예: 나의 포트폴리오"
                {...form.register("name")}
              />
              {form.formState.errors.name && (
                <p className="text-sm text-red-500">
                  {form.formState.errors.name.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="url">URL</Label>
              <Input
                id="url"
                type="url"
                placeholder="https://example.com"
                {...form.register("url")}
              />
              {form.formState.errors.url && (
                <p className="text-sm text-red-500">
                  {form.formState.errors.url.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">설명</Label>
              <Input
                id="description"
                placeholder="사이트에 대한 간단한 설명"
                {...form.register("description")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tags">초기 태그</Label>
              <Input
                id="tags"
                placeholder="쉼표로 구분하여 입력 (예: 포트폴리오, 개인)"
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
              <Button type="submit">등록</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
