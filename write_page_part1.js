import fs from 'fs'
import path from 'path'

const part1 = `"use client"

import { Search, Building2, Filter, X, Loader2 } from "lucide-react"
import { useState } from "react"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Toaster } from "@/components/ui/toaster"
import { useRouter } from "next/navigation"

const ADVANCED_FIELDS = [
  { key: "vkn", label: "VKN", placeholder: "10 hane vergi no", maxLength: 10 },
  { key: "mersis", label: "MERSİS No", placeholder: "16 hane", maxLength: 16 },
  { key: "unvan", label: "Ünvan", placeholder: "Şirket unvanı" },
  { key: "sicil", label: "Ticaret Sicil No", placeholder: "Sicil numarası" },
  { key: "il", label: "İl", placeholder: "İl seçin" },
]

export default function HomePage() {
  const [open, setOpen] = useState(true)
  const [advanced, setAdvanced] = useState(false)
  const [query, setQuery] = useState("")
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (query.trim()) params.set("q", query.trim())
    Object.entries(filters).forEach(([k, v]) => {
      if (v.trim()) params.set(k, v.trim())
    })
    router.push(\`/firma/sonuc?\${params.toString()}\`)
  }

  return (
    <div className="min-h-screen bg-background">
      <Toaster />
      <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/5" />
        <div className="relative z-10 w-full max-w-4xl px-4 py-20 text-center">`

const filePath = path.join(process.cwd(), 'frontend', 'src', 'app', 'page.tsx')
fs.writeFileSync(filePath, part1, 'utf-8')
console.log('part1 yazildi')