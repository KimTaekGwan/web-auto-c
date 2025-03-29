import { Geist, Geist_Mono } from "next/font/google"
import type { Metadata } from "next"
import "@workspace/ui/globals.css"
import { Providers } from "@/components/providers"
import { NavigationMenu } from "@/components/navigation-menu"
import { Toaster } from "sonner"

const fontSans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

export const metadata: Metadata = {
  title: "Web Capture Pro",
  description: "웹 페이지 캡처 자동화 도구",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body
        className={`${fontSans.variable} ${fontMono.variable} font-sans antialiased min-h-screen`}
      >
        <Providers>
          <div className="flex flex-col min-h-screen">
            <header className="border-b">
              <div className="container mx-auto py-4">
                <NavigationMenu />
              </div>
            </header>
            <main className="flex-1 container mx-auto py-6">{children}</main>
          </div>
        </Providers>
        <Toaster />
      </body>
    </html>
  )
}
