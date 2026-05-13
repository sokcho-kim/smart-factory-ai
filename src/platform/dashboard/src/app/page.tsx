import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <header className="border-b bg-white dark:bg-zinc-900 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">PunchLine</h1>
            <Badge variant="secondary">MVP</Badge>
          </div>
          <p className="text-sm text-zinc-500">
            AI 비전 기반 품질 자동 기록 및 불량 원인 추적
          </p>
        </div>
      </header>

      {/* KPI Summary */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                오늘 검사량
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">1,247</p>
              <p className="text-xs text-zinc-400 mt-1">실시간 집계</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                불량률
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-red-500">2.3%</p>
              <p className="text-xs text-green-600 mt-1">전주 대비 -0.8%</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                주요 불량 유형
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">크랙</p>
              <p className="text-xs text-zinc-400 mt-1">전체 불량의 58%</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                추정 원인
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">금형온도</p>
              <p className="text-xs text-zinc-400 mt-1">SHAP 기여도 73%</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Main Tabs */}
      <div className="max-w-7xl mx-auto px-6 pb-12">
        <Tabs defaultValue="inspect" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="inspect">실시간 검사</TabsTrigger>
            <TabsTrigger value="timeline">시계열 추적</TabsTrigger>
            <TabsTrigger value="rootcause">원인 분석</TabsTrigger>
          </TabsList>

          <TabsContent value="inspect">
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>실시간 검사 현황</CardTitle>
              </CardHeader>
              <CardContent className="h-96 flex items-center justify-center text-zinc-400">
                Phase 2: 이미지 스트림 + 양품/불량 실시간 판정 뷰
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="timeline">
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>시계열 품질 추적</CardTitle>
              </CardHeader>
              <CardContent className="h-96 flex items-center justify-center text-zinc-400">
                Phase 2: 시간대별 불량률 Recharts 차트
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="rootcause">
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>불량 원인 분석</CardTitle>
              </CardHeader>
              <CardContent className="h-96 flex items-center justify-center text-zinc-400">
                Phase 2: SHAP 분석 결과 + 원인 변수 Top 3 + 조치 가이드
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
