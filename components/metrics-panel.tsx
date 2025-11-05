"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Bar,
  BarChart,
  Line,
  LineChart,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  CartesianGrid,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import type { Result } from "@/lib/types";

interface MetricsPanelProps {
  metrics: {
    tfidfTime: number;
    bm25Time: number;
    preprocessTime: number;
  };
  tfidfResults: Result[];
  bm25Results: Result[];
}

export function MetricsPanel({ metrics, tfidfResults, bm25Results }: MetricsPanelProps) {
  const timeChartData = [
    { model: "TF-IDF", time: metrics.tfidfTime, fill: "var(--color-tfidf)" },
    { model: "BM25", time: metrics.bm25Time, fill: "var(--color-bm25)" },
  ];

  // Preparar dados para gráfico de comparação de scores
  const maxResults = Math.max(tfidfResults.length, bm25Results.length)
  const topN = Math.min(12, maxResults) // Top x resultados
  
  // Criar um mapa de doc_id para score para facilitar comparação
  const tfidfScoreMap = new Map(tfidfResults.map(r => [r.id, r.score]))
  const bm25ScoreMap = new Map(bm25Results.map(r => [r.id, r.score]))
  
  // Obter todos os documentos únicos dos top resultados
  const allDocIds = new Set([
    ...tfidfResults.slice(0, topN).map(r => r.id),
    ...bm25Results.slice(0, topN).map(r => r.id)
  ])
  
  const scoreChartData = Array.from(allDocIds)
    .slice(0, topN)
    .map((docId, i) => {
      const tfidfScore = tfidfScoreMap.get(docId)
      const bm25Score = bm25ScoreMap.get(docId)
      
      return {
        rank: i + 1,
        tfidf: tfidfScore ?? null,
        bm25: bm25Score ?? null,
      }
    })
    .filter(item => item.tfidf !== null || item.bm25 !== null)
    .sort((a, b) => {
      // Ordenar por maior score (TF-IDF, BM25)
      const aMax = Math.max(a.tfidf ?? 0, a.bm25 ?? 0)
      const bMax = Math.max(b.tfidf ?? 0, b.bm25 ?? 0)
      return bMax - aMax
    })
    .map((item, i) => ({ ...item, rank: i + 1 }))

  const timeChartConfig = {
    time: {
      label: "Tempo (ms)",
    },
    tfidf: {
      label: "TF-IDF",
      color: "var(--chart-1)",
    },
    bm25: {
      label: "BM25",
      color: "var(--chart-2)",
    },
  };

  const scoreChartConfig = {
    tfidf: {
      color: "var(--chart-1)",
    },
    bm25: {
      color: "var(--chart-2)",
    },
  };


  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Análise de Desempenho</h2>
        {/* <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Exportar Resultados
        </Button> */}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Tempo de Execução da Busca</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={timeChartConfig} className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="model" />
                  <YAxis />
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent 
                      hideLabel
                      formatter={(value: any, name: any, item: any) => {
                        const color = item.payload?.fill || item.color;
                        return (
                          <div className="flex w-full items-center gap-2">
                            <div
                              className="shrink-0 rounded-[2px] h-2.5 w-2.5"
                              style={{ backgroundColor: color }}
                            />
                            <div className="flex flex-1 justify-between items-center leading-none gap-2">
                              <span className="text-muted-foreground">{name}</span>
                              <span className="text-foreground font-mono font-medium tabular-nums">
                                {value.toFixed(2)}
                              </span>
                            </div>
                          </div>
                        );
                      }}
                    />}
                  />
                  <Legend wrapperStyle={{ marginTop: '20px' }} />
                  <Bar
                    dataKey="time"
                    name="Tempo (ms)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <div className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">
                  Pré-processamento:
                </span>
                <span className="font-mono">
                  {metrics.preprocessTime.toFixed(1)}ms
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">TF-IDF Total:</span>
                <span className="font-mono">
                  {metrics.tfidfTime.toFixed(1)}ms
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">BM25 Total:</span>
                <span className="font-mono">
                  {metrics.bm25Time.toFixed(1)}ms
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{`Comparação de Scores (Top ${topN})`}</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={scoreChartConfig} className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={scoreChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="rank" 
                    label={{ value: "Ranking", position: "insideBottom", offset: -5 }}
                  />
                  <YAxis 
                    label={{ value: "Score", angle: -90, position: "insideLeft" }}
                  />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend align="right" verticalAlign="bottom" wrapperStyle={{ paddingTop: '10px' }} />
                  <Line
                    type="monotone"
                    dataKey="tfidf"
                    stroke="var(--color-tfidf)"
                    strokeWidth={2}
                    dot={{ r: 3, fill: "var(--color-tfidf)" }}
                    name="TF-IDF"
                  />
                  <Line
                    type="monotone"
                    dataKey="bm25"
                    stroke="var(--color-bm25)"
                    strokeWidth={2}
                    dot={{ r: 3, fill: "var(--color-bm25)" }}
                    name="BM25"
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
            <p className="text-xs text-muted-foreground mt-2">
              Comparação dos scores dos top {topN.toString()} resultados entre TF-IDF e BM25
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{`Similaridade em Radar (Top ${Math.min(6, topN)})`}</CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              // Preparar dados para radar chart - top x resultados
              const radarTopN = Math.min(6, topN)
              
              if (scoreChartData.length === 0) {
                return (
                  <div className="h-[250px] flex items-center justify-center text-muted-foreground">
                    <p>Nenhum dado disponível para visualização</p>
                  </div>
                )
              }
              
              const radarData = scoreChartData.slice(0, radarTopN).map((item) => {
                // Normalizar scores para o radar (0-100% relativo ao máximo)
                const maxScore = Math.max(
                  ...scoreChartData.map(d => Math.max(d.tfidf ?? 0, d.bm25 ?? 0))
                )
                
                if (maxScore === 0) {
                  return {
                    rank: item.rank,
                    tfidf: 0,
                    bm25: 0,
                  }
                }
                
                return {
                  rank: item.rank,
                  tfidf: item.tfidf !== null ? ((item.tfidf / maxScore) * 100) : 0,
                  bm25: item.bm25 !== null ? ((item.bm25 / maxScore) * 100) : 0,
                }
              })

              const radarConfig = {
                tfidf: {
                  label: "TF-IDF",
                  color: "var(--chart-1)",
                },
                bm25: {
                  label: "BM25",
                  color: "var(--chart-2)",
                },
              }

              console.log('Radar data:', radarData)
              
              return (
                <div className="h-[250px] w-full">
                  <ChartContainer config={radarConfig} className="h-full w-full">
                    <RadarChart
                      data={radarData}
                      margin={{
                        top: 20,
                        right: 20,
                        bottom: 20,
                        left: 20,
                      }}
                    >
                    <ChartTooltip
                      cursor={false}
                      content={<ChartTooltipContent indicator="line" hideLabel />}
                    />
                    <PolarAngleAxis
                      dataKey="rank"
                      tick={({ x, y, textAnchor, value, index, ...props }) => {
                        const data = radarData[index]
                        if (!data) {
                          return <text x={x} y={y} textAnchor={textAnchor} fontSize={13} {...props} />
                        }

                        return (
                          <text
                            x={x}
                            y={index === 0 ? y - 10 : y}
                            textAnchor={textAnchor}
                            fontSize={13}
                            fontWeight={500}
                            {...props}
                          >
                            <tspan fill="var(--color-tfidf)">{data.tfidf.toFixed(0)}</tspan>
                            <tspan fill="var(--foreground)"> - </tspan>
                            <tspan fill="var(--color-bm25)">{data.bm25.toFixed(0)}</tspan>
                            <tspan
                              x={x}
                              dy={"1rem"}
                              fontSize={12}
                              className="fill-muted-foreground"
                            >
                            </tspan>
                          </text>
                        )
                      }}
                    />
                    <PolarGrid />
                    <Radar
                      name="TF-IDF"
                      dataKey="tfidf"
                      stroke="var(--color-tfidf)"
                      fill="var(--color-tfidf)"
                      fillOpacity={0.8}
                      strokeWidth={2}
                    />
                    <Radar
                      name="BM25"
                      dataKey="bm25"
                      stroke="var(--color-bm25)"
                      fill="var(--color-bm25)"
                      fillOpacity={0.6}
                      strokeWidth={2}
                    />
                    <Legend 
                      wrapperStyle={{ marginTop: '20px' }}
                      content={({ payload }) => (
                        <div className="flex items-center justify-center gap-4">
                          {payload?.map((entry, index) => (
                            <div
                              key={index}
                              className="flex items-center gap-1.5"
                              style={{ cursor: 'pointer' }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.opacity = '0.8'
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.opacity = '1'
                              }}
                            >
                              <div
                                className="h-2 w-2 shrink-0 rounded-[2px]"
                                style={{
                                  backgroundColor: entry.color,
                                }}
                              />
                              <span className="text-sm">{entry.value}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    />
                    </RadarChart>
                  </ChartContainer>
                </div>
              )
            })()}
            <p className="text-xs text-muted-foreground mt-2">
              Visualização em radar dos scores normalizados dos top resultados. Valores são normalizados em relação ao maior score encontrado.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Por que os resultados diferem?</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-3">
            <p>
              O{" "}
              <strong className="text-foreground">
                <a
                  href="https://en-wikipedia-org.translate.goog/wiki/Tf%E2%80%93idf?_x_tr_sl=en&_x_tr_tl=pt&_x_tr_hl=pt&_x_tr_pto=tc"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  TF-IDF
                </a>
              </strong>{" "}
              valoriza documentos com alta frequência de termos da consulta,
              ponderados pela raridade dos termos na coleção. Documentos longos
              com muitas ocorrências tendem a ter scores mais altos.{" "}
            </p>
            <p>
              O{" "}
              <strong className="text-foreground">
                <a
                  href="https://en.wikipedia.org/wiki/Okapi_BM25"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  BM25
                </a>
              </strong>{" "}
              aplica saturação de frequência (controlada por k₁) e normalização
              por tamanho (controlada por b), o que pode favorecer documentos
              mais curtos e evitar que termos muito frequentes dominem o score.{" "}
            </p>
            <p className="text-xs pt-2 border-t border-border">
              💡 Dica: Ajuste os parâmetros k₁ e b nas configurações avançadas
              para ver como eles afetam o ranqueamento do BM25.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
