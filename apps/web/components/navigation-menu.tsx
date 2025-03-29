import Link from "next/link"
import {
  NavigationMenu as NavMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@workspace/ui/components/navigation-menu"

export function NavigationMenu() {
  return (
    <NavMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <Link href="/" legacyBehavior passHref>
            <NavigationMenuLink className="font-bold">
              WebCapture Pro
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger>사이트 관리</NavigationMenuTrigger>
          <NavigationMenuContent>
            <div className="grid gap-3 p-4 w-[400px]">
              <Link
                href="/sites"
                className="block p-2 hover:bg-accent rounded-md"
              >
                사이트 목록
              </Link>
              <Link
                href="/sites/new"
                className="block p-2 hover:bg-accent rounded-md"
              >
                새 사이트 추가
              </Link>
            </div>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger>캡처 관리</NavigationMenuTrigger>
          <NavigationMenuContent>
            <div className="grid gap-3 p-4 w-[400px]">
              <Link
                href="/captures"
                className="block p-2 hover:bg-accent rounded-md"
              >
                캡처 목록
              </Link>
              <Link
                href="/captures/new"
                className="block p-2 hover:bg-accent rounded-md"
              >
                새 캡처 시작
              </Link>
            </div>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <Link href="/tags" legacyBehavior passHref>
            <NavigationMenuLink>태그 관리</NavigationMenuLink>
          </Link>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavMenu>
  )
}
