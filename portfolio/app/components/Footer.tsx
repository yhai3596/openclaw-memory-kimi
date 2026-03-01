'use client'

import { Github, Twitter, Mail } from 'lucide-react'

export default function Footer() {
  return (
    <footer id="contact" className="border-t border-zinc-800 px-6 py-12 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <div className="text-center sm:text-left">
            <p className="text-sm text-zinc-400">
              持续探索 AI 的可能性
            </p>
            <p className="mt-1 text-xs text-zinc-600">
              © 2024 AI Products Portfolio
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-zinc-800 p-2 text-zinc-400 transition-all hover:border-zinc-700 hover:text-white"
            >
              <Github className="h-5 w-5" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-zinc-800 p-2 text-zinc-400 transition-all hover:border-zinc-700 hover:text-white"
            >
              <Twitter className="h-5 w-5" />
            </a>
            <a
              href="mailto:hello@example.com"
              className="rounded-lg border border-zinc-800 p-2 text-zinc-400 transition-all hover:border-zinc-700 hover:text-white"
            >
              <Mail className="h-5 w-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
