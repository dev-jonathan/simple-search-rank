import type { SearchRequest, SearchResponse } from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function searchDocuments(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Erro na busca: ${response.status} ${response.statusText}. ${errorText}`)
  }

  const data = await response.json()
  return data
}

