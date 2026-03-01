'use client'

import { Sparkles } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/50 px-4 py-1.5 text-sm text-zinc-400">
          <Sparkles className="h-4 w-4" />
          <span>AI 产品合集</span>
        </div>
        
        <h1 className="mb-6 text-4xl font-bold tracking-tight text-white sm:text-6xl">
          探索 AI 的
          <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            无限可能
          </span>
        </h1>
        
        <p className="mx-auto max-w-2xl text-lg text-zinc-400">
          这里汇集了我开发的 AI 驱动应用，从智能对话到创意生成，
          每一个产品都致力于让 AI 技术更贴近生活。
        </p>
        
        <div className="mt-10 flex items-center justify-center gap-4">
          <a
            href="#products"
            className="rounded-lg bg-white px-6 py-3 text-sm font-medium text-black transition-all hover:bg-zinc-200"
          >
            浏览产品
          </a>
          <a
            href="#contact"
            className="rounded-lg border border-zinc-800 px-6 py-3 text-sm font-medium text-white transition-all hover:border-zinc-700 hover:bg-zinc-900"
          >
            联系我
          </a>
        </div>
      </div>
    </section>
  )
}
