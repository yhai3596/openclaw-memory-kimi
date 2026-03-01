'use client'

import { ExternalLink } from 'lucide-react'

interface Product {
  id: string
  title: string
  description: string
  tags: string[]
  link: string
  gradient: string
}

const products: Product[] = [
  {
    id: '1',
    title: 'AI 写作助手',
    description: '智能内容生成工具，支持文章、邮件、社交媒体文案一键生成',
    tags: ['GPT-4', 'Next.js', 'Tailwind'],
    link: '#',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    id: '2',
    title: '图像生成器',
    description: '基于 Stable Diffusion 的在线图像创作平台，支持多种风格',
    tags: ['SDXL', 'React', 'Python'],
    link: '#',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    id: '3',
    title: '代码审查助手',
    description: '自动分析代码质量，提供优化建议和潜在问题检测',
    tags: ['Claude', 'TypeScript', 'Node.js'],
    link: '#',
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    id: '4',
    title: '语音转文字',
    description: '高精度语音识别服务，支持多语言和实时转录',
    tags: ['Whisper', 'WebRTC', 'FastAPI'],
    link: '#',
    gradient: 'from-orange-500 to-red-500',
  },
  {
    id: '5',
    title: '智能客服机器人',
    description: '基于知识库的 AI 客服系统，支持多轮对话',
    tags: ['RAG', 'LangChain', 'PostgreSQL'],
    link: '#',
    gradient: 'from-indigo-500 to-violet-500',
  },
  {
    id: '6',
    title: 'PPT 生成器',
    description: '输入主题自动生成精美演示文稿，支持多种模板',
    tags: ['GPT-4', 'Python', 'React'],
    link: '#',
    gradient: 'from-rose-500 to-pink-500',
  },
  {
    id: '7',
    title: '视频摘要工具',
    description: '自动提取视频核心内容，生成文字摘要和关键帧',
    tags: ['Gemini', 'FFmpeg', 'Vue.js'],
    link: '#',
    gradient: 'from-amber-500 to-orange-500',
  },
  {
    id: '8',
    title: '数据可视化助手',
    description: '自然语言描述即可生成专业图表和数据报告',
    tags: ['D3.js', 'Python', 'OpenAI'],
    link: '#',
    gradient: 'from-cyan-500 to-blue-500',
  },
]

function ProductCard({ product, index }: { product: Product; index: number }) {
  return (
    <a
      href={product.link}
      target="_blank"
      rel="noopener noreferrer"
      className="group relative overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 transition-all duration-300 hover:border-zinc-700 hover:bg-zinc-900"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div
        className={`absolute inset-0 bg-gradient-to-br ${product.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-5`}
      />
      
      <div className="relative">
        <div className="mb-4 flex items-start justify-between">
          <h3 className="text-lg font-semibold text-white group-hover:text-zinc-200">
            {product.title}
          </h3>
          <ExternalLink className="h-4 w-4 text-zinc-600 transition-colors group-hover:text-zinc-400" />
        </div>
        
        <p className="mb-4 text-sm text-zinc-400">{product.description}</p>
        
        <div className="flex flex-wrap gap-2">
          {product.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs text-zinc-500"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </a>
  )
}

export default function ProductGrid() {
  return (
    <section id="products" className="px-6 py-16 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white">产品展示</h2>
          <p className="mt-2 text-zinc-400">共 {products.length} 个 AI 应用</p>
        </div>
        
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {products.map((product, index) => (
            <ProductCard key={product.id} product={product} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}
