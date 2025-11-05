export interface Result {
  id: string
  title: string
  score: number
  snippet: string
  matchedWords?: string[]  // Palavras encontradas no snippet (exatas, lematizadas ou similares)
  filename?: string  // Nome do arquivo PDF
}

export interface Metrics {
  preprocessTime: number
  tfidfTime: number
  bm25Time: number
}

export interface SearchResponse {
  tfidf: Result[]
  bm25: Result[]
  metrics: Metrics
}

export interface SearchRequest {
  query: string
  k1: number
  b: number
  tfIdfWeight: "log" | "raw" | "binary"
  topK?: number | null  // Número máximo de resultados por modelo (null = retornar todos)
}

