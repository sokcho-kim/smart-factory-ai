"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DefectBadge } from "./defect-badge";
import { useApi } from "@/hooks/use-api";
import { fetchInspectStream } from "@/lib/api";
import { fmtTime, fmtPct } from "@/lib/constants";
import type { Verdict } from "@/lib/types";
import { ChevronLeft, ChevronRight } from "lucide-react";

type Filter = "all" | "ok" | "defect";

const PAGE_SIZE = 60;

export function InspectTab() {
  const [offset, setOffset] = useState(0);
  const [filter, setFilter] = useState<Filter>("all");

  const { data, loading, error } = useApi(
    () => fetchInspectStream(offset, PAGE_SIZE),
    [offset],
    { refreshInterval: 5000 },
  );

  const filtered = useMemo(() => {
    if (!data) return [];
    if (filter === "all") return data.results;
    return data.results.filter((r) => r.verdict === filter);
  }, [data, filter]);

  if (error) {
    return (
      <Card className="mt-4">
        <CardContent className="flex h-96 items-center justify-center text-zinc-400">
          서버 연결 실패
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mt-4">
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>실시간 검사 현황</CardTitle>
        <div className="flex items-center gap-4">
          {/* 필터 */}
          <div className="flex gap-1">
            {(["all", "ok", "defect"] as const).map((f) => (
              <Button
                key={f}
                variant={filter === f ? "default" : "outline"}
                size="xs"
                onClick={() => setFilter(f)}
              >
                {f === "all" ? "전체" : f === "ok" ? "양품" : "불량"}
              </Button>
            ))}
          </div>
          {/* 페이지네이션 */}
          {data && (
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <Button
                variant="outline"
                size="icon-xs"
                disabled={offset === 0}
                onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span>
                {offset + 1}–{Math.min(offset + PAGE_SIZE, data.total)} / {data.total}
              </span>
              <Button
                variant="outline"
                size="icon-xs"
                disabled={offset + PAGE_SIZE >= data.total}
                onClick={() => setOffset((o) => o + PAGE_SIZE)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-10 animate-pulse rounded bg-zinc-100" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-zinc-500">
                  <th className="pb-2 font-medium">시간</th>
                  <th className="pb-2 font-medium">라인</th>
                  <th className="pb-2 font-medium">판정</th>
                  <th className="pb-2 font-medium">불량 유형</th>
                  <th className="pb-2 text-right font-medium">신뢰도</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r, i) => (
                  <tr
                    key={`${r.inspected_at}-${i}`}
                    className={
                      r.verdict === "defect"
                        ? "border-l-2 border-l-red-500 bg-red-50/50"
                        : "hover:bg-zinc-50"
                    }
                  >
                    <td className="py-2 font-mono text-xs">
                      {fmtTime(r.inspected_at)}
                    </td>
                    <td className="py-2">{r.line_id}</td>
                    <td className="py-2">
                      <DefectBadge
                        verdict={r.verdict}
                        defectType={r.defect_type}
                      />
                    </td>
                    <td className="py-2 text-zinc-600">
                      {r.defect_type ?? "-"}
                    </td>
                    <td className="py-2 text-right font-mono text-xs">
                      {fmtPct(r.confidence)}
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="py-8 text-center text-zinc-400"
                    >
                      해당 조건의 검사 결과 없음
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
