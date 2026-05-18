import { cn } from "@/lib/utils";
import type { StatusLevel } from "@/lib/constants";

const COLOR: Record<StatusLevel, string> = {
  green: "bg-emerald-500",
  yellow: "bg-yellow-400",
  red: "bg-red-500",
};

const SIZE = {
  sm: "h-2.5 w-2.5",
  md: "h-3.5 w-3.5",
  lg: "h-5 w-5",
} as const;

interface StatusLightProps {
  status: StatusLevel;
  size?: keyof typeof SIZE;
}

export function StatusLight({ status, size = "md" }: StatusLightProps) {
  return (
    <span
      className={cn(
        "inline-block rounded-full",
        COLOR[status],
        SIZE[size],
        status === "red" && "animate-pulse",
      )}
      aria-label={status}
    />
  );
}
