"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  PaginationEllipsis,
} from "@/components/ui/pagination"
import { ExternalLink } from "lucide-react"

// Constantes configuráveis para fácil ajuste
const RESULTS_PER_PAGE = 8 // Total de resultados por página
const RESULTS_PER_COLUMN = 4 // Resultados por coluna (TF-IDF e BM25)

interface Result {
  id: string
  title: string
  score: number
  snippet: string
  matchedWords?: string[]  // Palavras encontradas no snippet (exatas, lematizadas ou similares)
  filename?: string  // Nome do arquivo PDF
}

interface ResultsDisplayProps {
  tfidfResults: Result[]
  bm25Results: Result[]
  searchQuery: string
}

function highlightSearchTerms(text: string, query: string, matchedWords?: string[]) {
  if (!query.trim() && (!matchedWords || matchedWords.length === 0)) return <span>{text}</span>


  const queryTerms = query
    .toLowerCase()
    .split(/\s+/)
    .filter((term) => term.length > 0)
    .map(term => term.replace(/[^\wáéíóúâêîôûãõç]/g, '')) // Remove pontuação, mantém acentos
    .filter(term => term.length > 0)

  // Combinar termos da query com palavras encontradas pelo backend (fuzzy matching)
  const allTerms = new Set<string>()
  queryTerms.forEach(term => allTerms.add(term.toLowerCase()))
  if (matchedWords) {
    matchedWords.forEach(word => allTerms.add(word.toLowerCase()))
  }

  const terms = Array.from(allTerms).filter(term => term.length > 0)

  if (terms.length === 0) return <span>{text}</span>

  //cria um padrão de regex que corresponde aos termos da query

  const escapedTerms = terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const pattern = new RegExp(`\\b(${escapedTerms.join("|")})\\b`, "gi")

  // Separa o texto em partes que correspondem aos termos da query
  const parts = text.split(pattern)

  return (
    <>
      {parts.map((part, index) => {
        if (!part) return null
        // Verificar se a parte corresponde a algum termo (case insensitive)
        const isMatch = terms.some((term) => part.toLowerCase() === term.toLowerCase())
        return isMatch ? (
          <strong
            key={index}
            style={{
              textDecoration: "underline",
              fontWeight: "bold",
              backgroundColor: "rgba(255, 255, 0, 0.23)" // Destaque amarelo suave
            }}
          >
            {part}
          </strong>
        ) : (
          <span key={index}>{part}</span>
        )
      })}
    </>
  )
}

const GITHUB_REPO = "dev-jonathan/wiki-popular-articles-to-pdf"
const GITHUB_BRANCH = "main"
const PDF_DATASET_PATH = "pdf_dataset"

export function ResultsDisplay({ tfidfResults, bm25Results, searchQuery }: ResultsDisplayProps) {
  const [currentPage, setCurrentPage] = useState(1)

  // Resetar para primeira página quando os resultados mudarem
  useEffect(() => {
    setCurrentPage(1)
  }, [tfidfResults.length, bm25Results.length])

  const getPdfUrl = (result: Result) => {
    // Se tiver filename, usar diretamente
    if (result.filename) {
      const encodedFilename = encodeURIComponent(result.filename)
      return `https://github.com/${GITHUB_REPO}/blob/${GITHUB_BRANCH}/${PDF_DATASET_PATH}/${encodedFilename}`
    }
    
    // Fallback: converter título para nome de arquivo (espaços -> underscores)
    const filename = result.title.replace(/\s+/g, "_") + ".pdf"
    const encodedFilename = encodeURIComponent(filename)
    return `https://github.com/${GITHUB_REPO}/blob/${GITHUB_BRANCH}/${PDF_DATASET_PATH}/${encodedFilename}`
  }

  // Calcular paginação
  const totalPages = Math.max(
    Math.ceil(tfidfResults.length / RESULTS_PER_COLUMN),
    Math.ceil(bm25Results.length / RESULTS_PER_COLUMN)
  )

  // Obter resultados paginados para cada coluna
  const startIndex = (currentPage - 1) * RESULTS_PER_COLUMN
  const endIndex = startIndex + RESULTS_PER_COLUMN

  const paginatedTfidf = tfidfResults.slice(startIndex, endIndex)
  const paginatedBm25 = bm25Results.slice(startIndex, endIndex)

  // IDs dos resultados da página atual para badge "Ambos"
  const tfidfIds = new Set(paginatedTfidf.map((r) => r.id))
  const bm25Ids = new Set(paginatedBm25.map((r) => r.id))

  // Calcular índices reais (global) para cada resultado
  const getRealIndex = (localIndex: number, model: "tfidf" | "bm25") => {
    return startIndex + localIndex + 1
  }

  // Gerar números de página para exibir na paginação
  const getPageNumbers = () => {
    const pages: (number | "ellipsis")[] = []
    
    if (totalPages <= 7) {
      // Mostrar todas as páginas se for 7 ou menos
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Lógica para mostrar páginas com ellipsis
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i)
        pages.push("ellipsis")
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        pages.push(1)
        pages.push("ellipsis")
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
      } else {
        pages.push(1)
        pages.push("ellipsis")
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i)
        pages.push("ellipsis")
        pages.push(totalPages)
      }
    }
    
    return pages
  }

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            Ranqueamento Vetorial (TF-IDF)
            <Badge variant="secondary" className="text-xs">
              {tfidfResults.length} resultados
            </Badge>
          </h2>

          <div className="space-y-3">
            {paginatedTfidf.length > 0 ? (
              paginatedTfidf.map((result, localIndex) => {
                const realIndex = getRealIndex(localIndex, "tfidf")
                return (
                  <Card key={result.id} className="hover:border-primary transition-colors relative">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3 flex-1">
                          <Badge variant="outline" className="mt-0.5">
                            #{realIndex}
                          </Badge>
                          <div className="flex-1 min-w-0">
                            <CardTitle className="text-base">{result.title}</CardTitle>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-sm font-mono text-primary">{result.score.toFixed(4)}</span>
                              {bm25Ids.has(result.id) && (
                                <Badge variant="secondary" className="text-xs">
                                  Ambos
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 shrink-0"
                          asChild
                        >
                          <a
                            href={getPdfUrl(result)}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="Abrir PDF no GitHub"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {highlightSearchTerms(result.snippet, searchQuery, result.matchedWords)}
                      </p>
                    </CardContent>
                  </Card>
                )
              })
            ) : (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  Nenhum resultado encontrado
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            Ranqueamento Probabilístico (BM25)
            <Badge variant="secondary" className="text-xs">
              {bm25Results.length} resultados
            </Badge>
          </h2>

          <div className="space-y-3">
            {paginatedBm25.length > 0 ? (
              paginatedBm25.map((result, localIndex) => {
                const realIndex = getRealIndex(localIndex, "bm25")
                return (
                  <Card key={result.id} className="hover:border-primary transition-colors relative">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3 flex-1">
                          <Badge variant="outline" className="mt-0.5">
                            #{realIndex}
                          </Badge>
                          <div className="flex-1 min-w-0">
                            <CardTitle className="text-base">{result.title}</CardTitle>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-sm font-mono text-primary">{result.score.toFixed(2)}</span>
                              {tfidfIds.has(result.id) && (
                                <Badge variant="secondary" className="text-xs">
                                  Ambos
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 shrink-0"
                          asChild
                        >
                          <a
                            href={getPdfUrl(result)}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="Abrir PDF no GitHub"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {highlightSearchTerms(result.snippet, searchQuery, result.matchedWords)}
                      </p>
                    </CardContent>
                  </Card>
                )
              })
            ) : (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  Nenhum resultado encontrado
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>

              {getPageNumbers().map((page, index) => (
                <PaginationItem key={index}>
                  {page === "ellipsis" ? (
                    <PaginationEllipsis />
                  ) : (
                    <PaginationLink
                      onClick={() => setCurrentPage(page)}
                      isActive={currentPage === page}
                      className="cursor-pointer"
                    >
                      {page}
                    </PaginationLink>
                  )}
                </PaginationItem>
              ))}

              <PaginationItem>
                <PaginationNext
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  )
}
