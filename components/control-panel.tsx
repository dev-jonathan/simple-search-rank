"use client"

import type React from "react"

import { Search, Upload, X, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState, useRef } from "react"
import { cn } from "@/lib/utils"

interface ControlPanelProps {
  selectedCorpus: string
  onCorpusChange: (value: string) => void
  searchQuery: string
  onSearchQueryChange: (value: string) => void
  onSearch: () => void
  isLoading: boolean
  uploadedFiles: File[]
  onFilesChange: (files: File[]) => void
  isUploading: boolean
  onUploadingChange: (isUploading: boolean) => void
  settingsButton?: React.ReactNode
}

export function ControlPanel({
  selectedCorpus,
  onCorpusChange,
  searchQuery,
  onSearchQueryChange,
  onSearch,
  isLoading,
  uploadedFiles,
  onFilesChange,
  isUploading,
  onUploadingChange,
  settingsButton,
}: ControlPanelProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "application/pdf" || file.type === "text/plain",
    )

    if (files.length > 0) {
      handleFiles(files)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : []
    if (files.length > 0) {
      handleFiles(files)
    }
  }

  const handleFiles = (files: File[]) => {
    onUploadingChange(true)
    // Simulate upload processing
    setTimeout(() => {
      onFilesChange([...uploadedFiles, ...files])
      onUploadingChange(false)
    }, 1000)
  }

  const removeFile = (index: number) => {
    onFilesChange(uploadedFiles.filter((_, i) => i !== index))
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1 space-y-2">
            <Label htmlFor="corpus">Corpus</Label>
            <Select value={selectedCorpus} onValueChange={onCorpusChange}>
              <SelectTrigger id="corpus">
                <SelectValue placeholder="Selecione um corpus" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="wikipedia">Artigos Wikipedia</SelectItem>
                <SelectItem value="custom">Upload Personalizado</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end gap-2">
            {settingsButton}
          </div>
        </div>

        {selectedCorpus === "custom" && (
          <div className="space-y-4">
            <Label>Upload de Documentos</Label>

            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                isDragging ? "border-primary bg-primary/5" : "border-border",
                isUploading && "opacity-50 pointer-events-none",
              )}
            >
              <Upload className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
              <p className="text-sm font-medium mb-2">
                {isUploading ? "Processando arquivos..." : "Arraste e solte seus arquivos aqui"}
              </p>
              <p className="text-xs text-muted-foreground mb-4">Suporta PDF e TXT</p>
              <Button variant="secondary" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                Ou selecione arquivos
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.txt"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>

            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <Label className="text-sm">Arquivos carregados ({uploadedFiles.length})</Label>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between gap-2 p-2 bg-muted rounded-md">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <span className="text-sm truncate">{file.name}</span>
                        <span className="text-xs text-muted-foreground flex-shrink-0">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 flex-shrink-0"
                        onClick={() => removeFile(index)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="search">Consulta de Busca</Label>
        <div className="flex gap-2">
          <Input
            id="search"
            placeholder='Digite sua consulta de busca (e.g., "borboleta voando")'
            value={searchQuery}
            onChange={(e) => onSearchQueryChange(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSearch()}
            className="flex-1"
          />
          <Button onClick={onSearch} disabled={isLoading}>
            <Search className="h-4 w-4 mr-2" />
            {isLoading ? "Buscando..." : "Buscar"}
          </Button>
        </div>
      </div>
    </div>
  )
}
