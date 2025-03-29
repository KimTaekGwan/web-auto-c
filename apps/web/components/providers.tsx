"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { SWRConfig } from "swr"
import swrDefaultOptions from "@/lib/swr-config"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      enableColorScheme
    >
      <SWRConfig value={swrDefaultOptions}>{children}</SWRConfig>
    </NextThemesProvider>
  )
}
