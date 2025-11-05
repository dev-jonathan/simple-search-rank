"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ControlPanel } from "@/components/control-panel"
import { ConfigurationPanel } from "@/components/configuration-panel"
import { ResultsDisplay } from "@/components/results-display"
import { MetricsPanel } from "@/components/metrics-panel"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"
import { searchDocuments } from "@/lib/api"
import type { SearchResponse } from "@/lib/types"

export default function Home() {
  const [selectedCorpus, setSelectedCorpus] = useState("wikipedia")
  const [searchQuery, setSearchQuery] = useState("")
  const [k1, setK1] = useState(1.2)
  const [b, setB] = useState(0.75)
  const [tfIdfWeight, setTfIdfWeight] = useState<"log" | "raw" | "binary">("log")
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [hasInitialSearch, setHasInitialSearch] = useState(false)

  const handleSearch = async (query?: string) => {
    const queryToUse = query || searchQuery
    if (!queryToUse.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const searchResults = await searchDocuments({
        query: queryToUse,
        k1,
        b,
        tfIdfWeight,
      })
      setResults(searchResults)
      // Atualizar o campo de busca se foi passada uma query diferente
      if (query && query !== searchQuery) {
        setSearchQuery(query)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro desconhecido ao realizar a busca"
      setError(errorMessage)
      console.error("Erro na busca:", err)
    } finally {
      setIsLoading(false)
    }
  }

  // Busca automática ao carregar a página
  useEffect(() => {
    if (!hasInitialSearch) {
      setHasInitialSearch(true)
      // Executar busca por "ranking" automaticamente
      const performInitialSearch = async () => {
        setIsLoading(true)
        setError(null)
        try {
          const searchResults = await searchDocuments({
            query: "ranking",
            k1,
            b,
            tfIdfWeight,
          })
          setResults(searchResults)
          setSearchQuery("ranking")
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : "Erro desconhecido ao realizar a busca"
          setError(errorMessage)
          console.error("Erro na busca:", err)
        } finally {
          setIsLoading(false)
        }
      }
      performInitialSearch()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Executa apenas uma vez ao montar o componente

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header />

      <main className="container mx-auto px-4 py-8 space-y-8 flex-1">
        <ControlPanel
          selectedCorpus={selectedCorpus}
          onCorpusChange={setSelectedCorpus}
          searchQuery={searchQuery}
          onSearchQueryChange={setSearchQuery}
          onSearch={handleSearch}
          isLoading={isLoading}
          uploadedFiles={uploadedFiles}
          onFilesChange={setUploadedFiles}
          isUploading={isUploading}
          onUploadingChange={setIsUploading}
          settingsButton={
            <ConfigurationPanel
              k1={k1}
              b={b}
              tfIdfWeight={tfIdfWeight}
              onK1Change={setK1}
              onBChange={setB}
              onTfIdfWeightChange={(value) => {
                if (value === "log" || value === "raw" || value === "binary") {
                  setTfIdfWeight(value)
                }
              }}
              onApply={handleSearch}
              trigger={
                <Button variant="outline" size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
              }
            />
          }
        />

        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
            <p className="text-destructive font-medium">Erro na busca</p>
            <p className="text-sm text-destructive/80 mt-1">{error}</p>
          </div>
        )}

        {results && (
          <>
            <ResultsDisplay tfidfResults={results.tfidf} bm25Results={results.bm25} searchQuery={searchQuery} />

            <MetricsPanel 
              metrics={results.metrics} 
              tfidfResults={results.tfidf}
              bm25Results={results.bm25}
            />
          </>
        )}
      </main>

      <Footer />
    </div>
  )
}
