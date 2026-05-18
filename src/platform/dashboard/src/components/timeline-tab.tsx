"use client";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusLight } from "./status-light";
import { useApi } from "@/hooks/use-api";
import { fetchTimeline } from "@/lib/api";
import {
  UCL,
  fmtPct,
  fmtNum,
  fmtTimeShort,
  getDefectLabel,
  getStatusLevel,
} from "@/lib/constants";
import { TriangleAlert } from "lucide-react";

interface DotProps {
  cx?: number;
  cy?: number;
  payload?: { defect_rate: number };
}

function AnomalyDot({ cx, cy, payload }: DotProps) {
  if (!cx || !cy || !payload) return null;
  if (payload.defect_rate > UCL) {
    return (
      <circle
        cx={cx}
        cy={cy}
        r={5}
        fill="var(--color-red-500, #ef4444)"
        stroke="white"
        strokeWidth={2}
      />
    );
  }
  return <circle cx={cx} cy={cy} r={2} fill="#a1a1aa" />;
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: Record<string, unknown> }>;
}) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-md border bg-white px-3 py-2 text-xs shadow-sm">
      <p className="font-medium">{fmtTimeShort(d.timestamp as string)}</p>
      <p>
        불량률: <strong>{fmtPct(d.defect_rate as number)}</strong>
      </p>
      <p>
        검사: {fmtNum(d.total as number)} / 불량: {fmtNum(d.defects as number)}
      </p>
      {d.top_defect_type ? (
        <p>주요 유형: {getDefectLabel(d.top_defect_type as string)}</p>
      ) : null}
    </div>
  );
}

export function TimelineTab() {
  const { data, loading, error } = useApi(() => fetchTimeline(), [], {
    refreshInterval: 5000,
  });

  if (error) {
    return (
      <Card className="mt-4">
        <CardContent className="flex h-96 items-center justify-center text-zinc-400">
          서버 연결 실패
        </CardContent>
      </Card>
    );
  }

  if (loading || !data) {
    return (
      <Card className="mt-4">
        <CardContent className="flex h-96 items-center justify-center">
          <div className="h-64 w-full animate-pulse rounded bg-zinc-100" />
        </CardContent>
      </Card>
    );
  }

  const { entries, summary, alerts } = data;

  return (
    <div className="mt-4 space-y-4">
      {/* SPC 차트 */}
      <Card>
        <CardHeader>
          <CardTitle>SPC 관리도 — 불량률 추이</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={340}>
            <AreaChart data={entries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={fmtTimeShort}
                tick={{ fontSize: 11, fill: "#a1a1aa" }}
                interval="preserveStartEnd"
              />
              <YAxis
                tickFormatter={(v: number) => fmtPct(v)}
                tick={{ fontSize: 11, fill: "#a1a1aa" }}
                domain={[0, "auto"]}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine
                y={UCL}
                stroke="#ef4444"
                strokeDasharray="6 3"
                label={{
                  value: `UCL ${fmtPct(UCL)}`,
                  position: "right",
                  fill: "#ef4444",
                  fontSize: 11,
                }}
              />
              <Area
                type="monotone"
                dataKey="defect_rate"
                stroke="#71717a"
                fill="#e4e4e7"
                fillOpacity={0.4}
                strokeWidth={2}
                dot={<AnomalyDot />}
                activeDot={{ r: 5 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* 요약 + 알림 */}
      <div className="grid grid-cols-3 gap-4">
        {/* 요약 */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-500">요약</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-zinc-500">총 검사량</span>
              <span className="font-mono font-medium">
                {fmtNum(summary.total_inspected)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">전체 불량률</span>
              <span className="flex items-center gap-1.5 font-mono font-medium">
                <StatusLight
                  status={getStatusLevel(summary.overall_defect_rate)}
                  size="sm"
                />
                {fmtPct(summary.overall_defect_rate)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">피크 시간</span>
              <span className="font-mono font-medium">
                {summary.peak_time
                  ? `${fmtTimeShort(summary.peak_time)} (${fmtPct(summary.peak_defect_rate)})`
                  : "-"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">주요 불량</span>
              <span className="font-medium">
                {getDefectLabel(summary.dominant_defect_type)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* 알림 리스트 */}
        <Card className="col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-zinc-500">
              <TriangleAlert className="h-4 w-4" />
              이상 알림 ({alerts.length}건)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {alerts.length === 0 ? (
              <p className="py-4 text-center text-sm text-zinc-400">
                정상 범위 내 운영 중
              </p>
            ) : (
              <div className="max-h-48 space-y-2 overflow-y-auto">
                {alerts.map((a, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 rounded border-l-2 border-l-red-500 bg-red-50/50 px-3 py-2 text-sm"
                  >
                    <span className="shrink-0 font-mono text-xs text-zinc-500">
                      {fmtTimeShort(a.timestamp)}
                    </span>
                    <span className="text-zinc-700">{a.message}</span>
                    <Badge variant="destructive" className="ml-auto shrink-0">
                      {fmtPct(a.defect_rate)}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
