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

export default function NewTagPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">새 태그 생성</h1>
        <p className="text-muted-foreground">새로운 태그를 생성합니다.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>태그 정보</CardTitle>
          <CardDescription>생성할 태그의 정보를 입력하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">태그명</Label>
              <Input id="name" placeholder="예: 포트폴리오" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">설명</Label>
              <Input id="description" placeholder="태그에 대한 설명" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="color">색상</Label>
              <Input id="color" type="color" className="h-10 px-2" />
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline">취소</Button>
              <Button>생성</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
