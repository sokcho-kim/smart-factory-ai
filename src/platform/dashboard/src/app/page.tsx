import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { AndonHeader } from "@/components/andon-header";
import { InspectTab } from "@/components/inspect-tab";
import { TimelineTab } from "@/components/timeline-tab";
import { RootCauseTab } from "@/components/rootcause-tab";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-100 dark:bg-zinc-950">
      {/* Header */}
      <header className="border-b bg-white px-6 py-4 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">PunchLine</h1>
            <Badge variant="secondary">MVP</Badge>
          </div>
          <p className="text-sm text-zinc-500">
            AI 비전 기반 품질 자동 기록 및 불량 원인 추적
          </p>
        </div>
      </header>

      {/* Andon KPI Header */}
      <div className="mx-auto max-w-7xl px-6 py-6">
        <AndonHeader />
      </div>

      {/* Main Tabs */}
      <div className="mx-auto max-w-7xl px-6 pb-12">
        <Tabs defaultValue="timeline" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="inspect">실시간 검사</TabsTrigger>
            <TabsTrigger value="timeline">시계열 추적</TabsTrigger>
            <TabsTrigger value="rootcause">원인 분석</TabsTrigger>
          </TabsList>

          <TabsContent value="inspect">
            <InspectTab />
          </TabsContent>

          <TabsContent value="timeline">
            <TimelineTab />
          </TabsContent>

          <TabsContent value="rootcause">
            <RootCauseTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
