import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Products Portfolio',
  description: 'A collection of AI-powered web applications',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  )
}
