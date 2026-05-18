"use client";

import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { postRootCause } from "@/lib/api";
import { fmtPct } from "@/lib/constants";
import type { RootCauseResult, CauseVariable } from "@/lib/types";
import { Search, Loader2 } from "lucide-react";

/** 기본 시간 범위 (시뮬레이션 데이터 첫 1시간) */
const DEFAULT_START = "2026-05-22T09:00:00";
const DEFAULT_END = "2026-05-22T10:00:00";

function RangeBar({ cause }: { cause: CauseVariable }) {
  const [lo, hi] = cause.normal_range;
  const range = hi - lo;
  const padding = range * 0.3;
  const min = lo - padding;
  const max = hi + padding;
  const totalWidth = max - min;

  const normalLeft = ((lo - min) / totalWidth) * 100;
  const normalWidth = (range / totalWidth) * 100;
  const dotPos = ((cause.current_value - min) / totalWidth) * 100;
  const clampedDot = Math.max(2, Math.min(98, dotPos));

  return (
    <div className="flex items-center gap-3">
      <div className="w-28 shrink-0 text-right text-sm text-zinc-600">
        {cause.display_name}
      </div>
      <div className="relative h-6 flex-1 rounded bg-zinc-100">
        {/* 정상 범위 */}
        <div
          className="absolute top-1 bottom-1 rounded bg-emerald-200"
          style={{ left: `${normalLeft}%`, width: `${normalWidth}%` }}
        />
        {/* 현재값 dot */}
        <div
          className={`absolute top-0.5 h-5 w-2.5 rounded-full ${
            cause.is_abnormal ? "bg-red-500" : "bg-zinc-600"
          }`}
          style={{ left: `calc(${clampedDot}% - 5px)` }}
        />
        {/* 범위 레이블 */}
        <span
          className="absolute -bottom-4 text-[10px] text-zinc-400"
          style={{ left: `${normalLeft}%` }}
        >
          {lo.toFixed(1)}
        </span>
        <span
          className="absolute -bottom-4 text-[10px] text-zinc-400"
          style={{ left: `${normalLeft + normalWidth}%` }}
        >
          {hi.toFixed(1)}
        </span>
      </div>
      <div className="w-16 shrink-0 text-right font-mono text-sm">
        {cause.current_value.toFixed(1)}
        {cause.is_abnormal && (
          <span className="ml-1 text-red-500">!</span>
        )}
      </div>
    </div>
  );
}

function ParetoTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: CauseVariable }>;
}) {
  if (!active || !payload?.[0]) return null;
  const c = payload[0].payload;
  return (
    <div className="rounded-md border bg-white px-3 py-2 text-xs shadow-sm">
      <p className="font-medium">{c.display_name}</p>
      <p>SHAP 기여도: {c.shap_value.toFixed(3)}</p>
      <p>
        현재값: {c.current_value.toFixed(1)} (정상:{" "}
        {c.normal_range[0].toFixed(1)}–{c.normal_range[1].toFixed(1)})
      </p>
      <p>{c.is_abnormal ? "이상" : "정상"}</p>
    </div>
  );
}

export function RootCauseTab() {
  const [timeStart, setTimeStart] = useState(DEFAULT_START);
  const [timeEnd, setTimeEnd] = useState(DEFAULT_END);
  const [result, setResult] = useState<RootCauseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function analyze() {
    setLoading(true);
    setError(null);
    try {
      const data = await postRootCause({
        line_id: "A",
        time_start: timeStart,
        time_end: timeEnd,
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-4 space-y-4">
      {/* 시간 범위 + 분석 버튼 */}
      <Card>
        <CardContent className="flex items-end gap-4 pt-6">
          <div className="flex-1">
            <label className="mb-1 block text-xs text-zinc-500">시작</label>
            <input
              type="text"
              value={timeStart}
              onChange={(e) => setTimeStart(e.target.value)}
              className="w-full rounded border border-zinc-200 bg-white px-3 py-1.5 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-zinc-300"
            />
          </div>
          <div className="flex-1">
            <label className="mb-1 block text-xs text-zinc-500">종료</label>
            <input
              type="text"
              value={timeEnd}
              onChange={(e) => setTimeEnd(e.target.value)}
              className="w-full rounded border border-zinc-200 bg-white px-3 py-1.5 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-zinc-300"
            />
          </div>
          <Button onClick={analyze} disabled={loading} className="gap-2">
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            원인 분석
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card>
          <CardContent className="py-6 text-center text-zinc-400">
            분석 실패: {error}
          </CardContent>
        </Card>
      )}

      {result && (
        <>
          {/* Pareto 차트 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                공정 파라미터 기여도 (SHAP)
                <Badge variant="secondary">
                  불량 {result.defect_count}건 분석
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={result.causes} layout="vertical">
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e4e4e7"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    tick={{ fontSize: 11, fill: "#a1a1aa" }}
                    tickFormatter={(v: number) => v.toFixed(2)}
                  />
                  <YAxis
                    type="category"
                    dataKey="display_name"
                    width={100}
                    tick={{ fontSize: 12, fill: "#52525b" }}
                  />
                  <Tooltip content={<ParetoTooltip />} />
                  <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
                    {result.causes.map((c, i) => (
                      <Cell
                        key={i}
                        fill={c.is_abnormal ? "#ef4444" : "#a1a1aa"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* 현재값 vs 정상범위 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-zinc-500">
                현재값 vs 정상 범위
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 pb-8">
              {result.causes.map((c) => (
                <RangeBar key={c.name} cause={c} />
              ))}
            </CardContent>
          </Card>

          {/* 조치 가이드 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-zinc-500">
                조치 가이드
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-700">
                {result.recommendation}
              </pre>
              {result.similar_cases > 0 && (
                <p className="mt-3 text-xs text-zinc-400">
                  유사 사례 {result.similar_cases}건 발견
                </p>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {!result && !loading && !error && (
        <Card>
          <CardContent className="flex h-64 items-center justify-center text-zinc-400">
            시간 범위를 설정하고 &ldquo;원인 분석&rdquo; 버튼을 눌러주세요
          </CardContent>
        </Card>
      )}
    </div>
  );
}
