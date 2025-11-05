"use client"

import type React from "react"

import { Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

interface ConfigurationPanelProps {
  k1: number
  b: number
  tfIdfWeight: string
  onK1Change: (value: number) => void
  onBChange: (value: number) => void
  onTfIdfWeightChange: (value: string) => void
  onApply: () => void
  trigger?: React.ReactNode
}

export function ConfigurationPanel({
  k1,
  b,
  tfIdfWeight,
  onK1Change,
  onBChange,
  onTfIdfWeightChange,
  onApply,
  trigger,
}: ConfigurationPanelProps) {
  return (
    <Dialog>
      {trigger ? (
        <DialogTrigger asChild>{trigger}</DialogTrigger>
      ) : (
        <DialogTrigger asChild>
          <Button variant="outline" className="w-full justify-start bg-transparent">
            <Settings className="h-4 w-4 mr-2" />
            Configurações Avançadas
          </Button>
        </DialogTrigger>
      )}
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Configurações Avançadas</DialogTitle>
        </DialogHeader>
        <div className="space-y-6 pt-4">
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Parâmetro k₁ (BM25)</Label>
                  <span className="text-sm text-muted-foreground">{k1.toFixed(2)}</span>
                </div>
                <Slider value={[k1]} onValueChange={([value]) => onK1Change(value)} min={0.5} max={2.0} step={0.1} />
                <p className="text-xs text-muted-foreground">Controla a saturação de frequência do termo</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Parâmetro b (BM25)</Label>
                  <span className="text-sm text-muted-foreground">{b.toFixed(2)}</span>
                </div>
                <Slider value={[b]} onValueChange={([value]) => onBChange(value)} min={0.0} max={1.0} step={0.05} />
                <p className="text-xs text-muted-foreground">Controla a normalização pelo tamanho do documento</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Ponderação TF-IDF</Label>
                <Select value={tfIdfWeight} onValueChange={onTfIdfWeightChange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="log">1 + log(f)</SelectItem>
                    <SelectItem value="raw">f (frequência bruta)</SelectItem>
                    <SelectItem value="binary">Binário</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">Função de peso para frequência do termo</p>
              </div>
            </div>
          </div>

          <Button onClick={onApply} className="w-full">
            Aplicar Configurações
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
