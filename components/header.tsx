"use client"

import { Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

export function Header() {
  return (
    <header className="border-b border-border bg-card">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="shrink-0">
              <svg 
                stroke="white" 
                fill="white" 
                strokeWidth="0" 
                viewBox="0 0 460 512" 
                height="48px" 
                width="48px" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M220.6 130.3l-67.2 28.2V43.2L98.7 233.5l54.7-24.2v130.3l67.2-209.3zm-83.2-96.7l-1.3 4.7-15.2 52.9C80.6 106.7 52 145.8 52 191.5c0 52.3 34.3 95.9 83.4 105.5v53.6C57.5 340.1 0 272.4 0 191.6c0-80.5 59.8-147.2 137.4-158zm311.4 447.2c-11.2 11.2-23.1 12.3-28.6 10.5-5.4-1.8-27.1-19.9-60.4-44.4-33.3-24.6-33.6-35.7-43-56.7-9.4-20.9-30.4-42.6-57.5-52.4l-9.7-14.7c-24.7 16.9-53 26.9-81.3 28.7l2.1-6.6 15.9-49.5c46.5-11.9 80.9-54 80.9-104.2 0-54.5-38.4-102.1-96-107.1V32.3C254.4 37.4 320 106.8 320 191.6c0 33.6-11.2 64.7-29 90.4l14.6 9.6c9.8 27.1 31.5 48 52.4 57.4s32.2 9.7 56.8 43c24.6 33.2 42.7 54.9 44.5 60.3s.7 17.3-10.5 28.5zm-9.9-17.9c0-4.4-3.6-8-8-8s-8 3.6-8 8 3.6 8 8 8 8-3.6 8-8z"></path>
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-balance">Comparador de Modelos de RI</h1>
              <p className="text-muted-foreground mt-1">Análise comparativa: TF-IDF vs. BM25</p>
            </div>
          </div>

          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="icon">
                <Info className="h-5 w-5" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Sobre os Modelos de RI</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 text-left">
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Modelo Vetorial (TF-IDF)</h3>
                  <div className="text-sm text-muted-foreground">
                    O modelo vetorial representa documentos e consultas como vetores em um espaço multidimensional.
                    TF-IDF (Term Frequency-Inverse Document Frequency) pondera a importância de termos baseado em sua
                    frequência no documento e raridade na coleção.
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-foreground mb-2">Modelo Probabilístico (BM25)</h3>
                  <div className="text-sm text-muted-foreground">
                    BM25 é um modelo probabilístico que estima a relevância de documentos baseado em probabilidades. Ele
                    considera a saturação de frequência de termos e normalização por tamanho do documento.
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-foreground mb-2">Parâmetros BM25</h3>
                  <div className="text-sm text-muted-foreground">
                    <strong>k₁</strong> (0.5-2.0): Controla a saturação da frequência do termo. Valores maiores permitem
                    que termos frequentes tenham mais impacto.
                    <br />
                    <strong>b</strong> (0.0-1.0): Controla a normalização pelo tamanho do documento. 0 = sem
                    normalização, 1 = normalização completa.
                  </div>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </header>
  )
}
