"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusLight } from "./status-light";
import { useApi } from "@/hooks/use-api";
import { fetchKPI } from "@/lib/api";
import {
  getStatusLevel,
  getDefectLabel,
  fmtPct,
  fmtNum,
} from "@/lib/constants";
import { ArrowDown, ArrowUp, TriangleAlert } from "lucide-react";

function Skeleton() {
  return <div className="h-9 w-24 animate-pulse rounded bg-zinc-200" />;
}

export function AndonHeader() {
  const { data: kpi, loading, error } = useApi(() => fetchKPI(), [], {
    refreshInterval: 3000,
  });

  if (error) {
    return (
      <div className="grid grid-cols-4 gap-4">
        <Card className="col-span-4">
          <CardContent className="py-6 text-center text-zinc-400">
            서버 연결 실패 — AI 서버(port 8000)가 실행 중인지 확인하세요
          </CardContent>
        </Card>
      </div>
    );
  }

  const status = kpi ? getStatusLevel(kpi.defect_rate) : "green";
  const deltaPositive = kpi ? kpi.defect_rate_delta > 0 : false;

  return (
    <div className="grid grid-cols-4 gap-4">
      {/* 검사량 */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-zinc-500">
            오늘 검사량
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton />
          ) : (
            <>
              <p className="font-mono text-4xl font-bold tracking-tight">
                {fmtNum(kpi!.total_inspected)}
              </p>
              <p className="mt-1 text-xs text-zinc-400">실시간 집계</p>
            </>
          )}
        </CardContent>
      </Card>

      {/* 불량률 */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-zinc-500">
            불량률
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton />
          ) : (
            <>
              <div className="flex items-center gap-2">
                <StatusLight status={status} size="lg" />
                <p
                  className={`font-mono text-4xl font-bold tracking-tight ${
                    status === "red"
                      ? "text-red-500"
                      : status === "yellow"
                        ? "text-yellow-600"
                        : ""
                  }`}
                >
                  {fmtPct(kpi!.defect_rate)}
                </p>
              </div>
              <div className="mt-1 flex items-center gap-1 text-xs">
                {deltaPositive ? (
                  <ArrowUp className="h-3 w-3 text-red-500" />
                ) : (
                  <ArrowDown className="h-3 w-3 text-emerald-500" />
                )}
                <span
                  className={
                    deltaPositive ? "text-red-500" : "text-emerald-500"
                  }
                >
                  {fmtPct(Math.abs(kpi!.defect_rate_delta))}
                </span>
                <span className="text-zinc-400">전기 대비</span>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* 주요 불량 유형 */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-zinc-500">
            주요 불량 유형
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton />
          ) : (
            <>
              <p className="font-mono text-4xl font-bold tracking-tight">
                {getDefectLabel(kpi!.top_defect_type)}
              </p>
              <p className="mt-1 text-xs text-zinc-400">
                전체 불량의 {fmtPct(kpi!.top_defect_pct)}
              </p>
            </>
          )}
        </CardContent>
      </Card>

      {/* 알림 */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-zinc-500">
            이상 알림
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton />
          ) : (
            <>
              <div className="flex items-center gap-2">
                <p className="font-mono text-4xl font-bold tracking-tight">
                  {kpi!.active_alerts}
                </p>
                {kpi!.active_alerts > 0 && (
                  <Badge variant="destructive" className="gap-1">
                    <TriangleAlert className="h-3 w-3" />
                    주의
                  </Badge>
                )}
              </div>
              <p className="mt-1 text-xs text-zinc-400">
                {kpi!.top_cause_name}
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
