"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface UseApiOptions {
  /** 자동 갱신 간격 (ms). 0이면 비활성. */
  refreshInterval?: number;
}

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
  options: UseApiOptions = {},
): UseApiResult<T> {
  const { refreshInterval = 0 } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const hasData = useRef(false);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    let cancelled = false;
    // 첫 로드만 loading 표시, 갱신 시에는 표시하지 않음
    if (!hasData.current) setLoading(true);
    setError(null);

    fetcher()
      .then((d) => {
        if (!cancelled) {
          setData(d);
          hasData.current = true;
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, ...deps]);

  // 자동 갱신
  useEffect(() => {
    if (refreshInterval <= 0) return;
    const id = setInterval(refetch, refreshInterval);
    return () => clearInterval(id);
  }, [refreshInterval, refetch]);

  return { data, loading, error, refetch };
}
